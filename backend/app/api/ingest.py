import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Endpoint, Event, DeliveryAttempt, DeliveryStatus
from app.verifiers import get_verifier
from app.services.sse_manager import sse_manager

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])

@router.post("/{endpoint_id}")
async def ingest_webhook(endpoint_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)):
    # Fetch endpoint
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Ingestion endpoint not found")

    if not endpoint.is_active:
        raise HTTPException(status_code=400, detail="Ingestion endpoint is inactive")

    # Read raw body & headers
    raw_body_bytes = await request.body()
    raw_body_str = raw_body_bytes.decode("utf-8", errors="replace")
    
    headers_dict = dict(request.headers)

    try:
        payload_json = json.loads(raw_body_str) if raw_body_str else {}
    except Exception:
        payload_json = {"raw": raw_body_str}

    # Signature verification
    verifier = get_verifier(endpoint.provider)
    is_valid, sig_msg = verifier.verify(headers_dict, raw_body_str, endpoint.secret_key)

    event_type = payload_json.get("type") or payload_json.get("event") or headers_dict.get("x-github-event")

    # Persist event log to partitioned events table
    now = datetime.now(timezone.utc)
    event_id = uuid.uuid4()
    
    event = Event(
        id=event_id,
        endpoint_id=endpoint.id,
        provider=endpoint.provider,
        event_type=event_type,
        headers=headers_dict,
        payload=payload_json,
        raw_body=raw_body_str,
        signature_valid=is_valid,
        created_at=now
    )
    db.add(event)

    # Initial delivery attempt staged for worker pickup
    attempt = DeliveryAttempt(
        event_id=event_id,
        event_created_at=now,
        endpoint_id=endpoint.id,
        attempt_count=1,
        status=DeliveryStatus.PENDING,
        next_retry_at=now
    )
    db.add(attempt)

    await db.commit()

    # SSE Realtime Broadcast
    await sse_manager.broadcast("new_event", {
        "event_id": str(event_id),
        "endpoint_id": str(endpoint.id),
        "endpoint_name": endpoint.name,
        "provider": endpoint.provider.value,
        "event_type": event_type,
        "signature_valid": is_valid,
        "sig_msg": sig_msg,
        "created_at": now.isoformat()
    })

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "event_id": str(event_id),
            "signature_valid": is_valid,
            "signature_message": sig_msg
        }
    )

