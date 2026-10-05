import asyncio
import random
import time
import logging
from datetime import datetime, timezone, timedelta
import httpx
from sqlalchemy import select, update, text
from app.config import settings
from app.db.database import AsyncSessionLocal
from app.db.models import DeliveryAttempt, DeliveryStatus, Endpoint, Event
from app.services.sse_manager import sse_manager

logger = logging.getLogger("retry_worker")
logger.setLevel(logging.INFO)

def calculate_next_retry(attempt_count: int) -> datetime:
    """
    Calculates next retry time using exponential backoff with randomized jitter.
    Formula: wait_seconds = min(MAX_BACKOFF, INITIAL_BACKOFF * 2^attempt + jitter)
    """
    base_backoff = settings.INITIAL_BACKOFF_SECONDS * (2 ** (attempt_count - 1))
    jitter = random.uniform(0, settings.JITTER_MAX_SECONDS)
    total_seconds = min(settings.MAX_BACKOFF_SECONDS, base_backoff + jitter)
    return datetime.now(timezone.utc) + timedelta(seconds=total_seconds)

async def process_single_attempt(attempt_id: str):
    """
    Executes a single delivery attempt against the target endpoint URL.
    """
    async with AsyncSessionLocal() as session:
        # Fetch delivery attempt, event, and endpoint
        stmt = (
            select(DeliveryAttempt, Event, Endpoint)
            .join(Event, DeliveryAttempt.event_id == Event.id)
            .join(Endpoint, DeliveryAttempt.endpoint_id == Endpoint.id)
            .where(DeliveryAttempt.id == attempt_id)
        )
        result = await session.execute(stmt)
        row = result.first()
        if not row:
            return

        attempt, event, endpoint = row

        if not endpoint.is_active:
            attempt.status = DeliveryStatus.EXHAUSTED
            attempt.error_message = "Endpoint marked inactive by system"
            await session.commit()
            return

        # Prepare HTTP delivery payload
        headers = dict(event.headers) if event.headers else {}
        headers["X-Relay-Event-ID"] = str(event.id)
        headers["X-Relay-Attempt"] = str(attempt.attempt_count)

        start_time = time.time()
        response_status = None
        response_headers = None
        response_body = None
        error_msg = None
        is_success = False

        try:
            async with httpx.AsyncClient(timeout=endpoint.timeout_seconds, follow_redirects=True) as client:
                response = await client.post(
                    endpoint.target_url,
                    json=event.payload,
                    headers=headers
                )
                duration_ms = int((time.time() - start_time) * 1000)
                response_status = response.status_code
                response_headers = dict(response.headers)
                response_body = response.text[:4096] # Limit stored body to 4KB

                if 200 <= response_status < 300:
                    is_success = True
                else:
                    error_msg = f"HTTP {response_status} received from destination endpoint"

        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Delivery failed: {str(exc)}"

        # Update attempt status
        attempt.execution_duration_ms = duration_ms
        attempt.response_status = response_status
        attempt.response_headers = response_headers
        attempt.response_body = response_body
        attempt.error_message = error_msg
        attempt.updated_at = datetime.now(timezone.utc)

        if is_success:
            attempt.status = DeliveryStatus.SUCCESS
            attempt.next_retry_at = None
        else:
            if attempt.attempt_count >= endpoint.max_retries:
                attempt.status = DeliveryStatus.EXHAUSTED
                attempt.next_retry_at = None
            else:
                attempt.status = DeliveryStatus.RETRYING
                attempt.next_retry_at = calculate_next_retry(attempt.attempt_count)

        await session.commit()

        # Broadcast update via SSE
        await sse_manager.broadcast("delivery_update", {
            "attempt_id": str(attempt.id),
            "event_id": str(event.id),
            "endpoint_id": str(endpoint.id),
            "attempt_count": attempt.attempt_count,
            "status": attempt.status.value,
            "response_status": response_status,
            "execution_duration_ms": duration_ms,
            "error_message": error_msg,
            "next_retry_at": attempt.next_retry_at.isoformat() if attempt.next_retry_at else None
        })

async def run_retry_worker_loop():
    """
    Background worker loop polling pending deliveries efficiently via partial index.
    Uses `FOR UPDATE SKIP LOCKED` for concurrent worker safety.
    """
    logger.info("Starting background webhook retry worker loop...")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                now = datetime.now(timezone.utc)
                # Raw SQL query utilizing partial index `idx_delivery_pending_retries`
                query = text("""
                    SELECT id FROM delivery_attempts
                    WHERE status IN ('pending', 'retrying')
                      AND (next_retry_at IS NULL OR next_retry_at <= :now)
                    ORDER BY next_retry_at ASC NULLS FIRST
                    LIMIT 50
                    FOR UPDATE SKIP LOCKED
                """)
                res = await session.execute(query, {"now": now})
                pending_ids = [str(r[0]) for r in res.fetchall()]
                await session.commit()

            if pending_ids:
                tasks = [process_single_attempt(aid) for aid in pending_ids]
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                await asyncio.sleep(1.5)

        except asyncio.CancelledError:
            logger.info("Retry worker loop cancelled.")
            break
        except Exception as exc:
            logger.error(f"Error in retry worker loop: {exc}")
            await asyncio.sleep(3)

