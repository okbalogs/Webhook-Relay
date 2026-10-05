import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Event, Endpoint, DeliveryAttempt, DeliveryStatus
from app.services.retry_worker import process_single_attempt
from app.services.sse_manager import sse_manager

router = APIRouter(prefix="/api/v1/events", tags=["Replay"])

class ReplayRequest(BaseModel):
    override_payload: Optional[Dict[str, Any]] = None
    override_headers: Optional[Dict[str, str]] = None
    override_target_url: Optional[str] = None

@router.post("/{event_id}/replay", status_code=status.HTTP_202_ACCEPTED)
async def replay_event(
    event_id: uuid.UUID,
    data: Optional[ReplayRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    # Fetch original event
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch endpoint
    ep_result = await db.execute(select(Endpoint).where(Endpoint.id == event.endpoint_id))
    endpoint = ep_result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Apply overrides if supplied
    if data and data.override_payload is not None:
        event.payload = data.override_payload

    if data and data.override_headers is not None:
        merged_headers = dict(event.headers)
        merged_headers.update(data.override_headers)
        event.headers = merged_headers

    if data and data.override_target_url:
        endpoint.target_url = data.override_target_url

    # Fetch highest attempt count
    count_res = await db.execute(
        select(DeliveryAttempt)
        .where(DeliveryAttempt.event_id == event_id)
        .order_by(DeliveryAttempt.attempt_count.desc())
    )
    latest_attempt = count_res.scalars().first()
    next_attempt_num = (latest_attempt.attempt_count + 1) if latest_attempt else 1

    now = datetime.now(timezone.utc)
    new_attempt = DeliveryAttempt(
        event_id=event.id,
        event_created_at=event.created_at,
        endpoint_id=endpoint.id,
        attempt_count=next_attempt_num,
        status=DeliveryStatus.PENDING,
        next_retry_at=now
    )
    db.add(new_attempt)
    await db.commit()
    await db.refresh(new_attempt)

    # Immediately trigger processing in background
    attempt_id_str = str(new_attempt.id)
    import asyncio
    asyncio.create_task(process_single_attempt(attempt_id_str))

    await sse_manager.broadcast("replay_triggered", {
        "event_id": str(event.id),
        "endpoint_id": str(endpoint.id),
        "attempt_id": attempt_id_str,
        "attempt_count": next_attempt_num
    })

    return {
        "status": "replay_initiated",
        "event_id": str(event.id),
        "attempt_id": attempt_id_str,
        "attempt_count": next_attempt_num
    }

