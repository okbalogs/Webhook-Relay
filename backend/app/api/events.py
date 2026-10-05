import asyncio
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Event, DeliveryAttempt, Endpoint
from app.services.sse_manager import sse_manager

router = APIRouter(prefix="/api/v1/events", tags=["Events"])

class EventListResponse(BaseModel):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    provider: str
    event_type: Optional[str]
    signature_valid: bool
    created_at: str

class DeliveryAttemptSchema(BaseModel):
    id: uuid.UUID
    attempt_count: int
    status: str
    response_status: Optional[int]
    execution_duration_ms: Optional[int]
    error_message: Optional[str]
    next_retry_at: Optional[str]
    created_at: str

class EventDetailResponse(BaseModel):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    provider: str
    event_type: Optional[str]
    headers: dict
    payload: dict
    raw_body: str
    signature_valid: bool
    created_at: str
    attempts: List[DeliveryAttemptSchema]

@router.get("", response_model=List[EventListResponse])
async def list_events(
    endpoint_id: Optional[uuid.UUID] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Event)
    if endpoint_id:
        stmt = stmt.where(Event.endpoint_id == endpoint_id)
    
    stmt = stmt.order_by(desc(Event.created_at)).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        EventListResponse(
            id=ev.id,
            endpoint_id=ev.endpoint_id,
            provider=ev.provider.value,
            event_type=ev.event_type,
            signature_valid=ev.signature_valid,
            created_at=ev.created_at.isoformat()
        ) for ev in events
    ]

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event_detail(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch attempts
    att_result = await db.execute(
        select(DeliveryAttempt)
        .where(DeliveryAttempt.event_id == event_id)
        .order_by(DeliveryAttempt.attempt_count.asc())
    )
    attempts = att_result.scalars().all()

    return EventDetailResponse(
        id=ev.id,
        endpoint_id=ev.endpoint_id,
        provider=ev.provider.value,
        event_type=ev.event_type,
        headers=ev.headers,
        payload=ev.payload,
        raw_body=ev.raw_body,
        signature_valid=ev.signature_valid,
        created_at=ev.created_at.isoformat(),
        attempts=[
            DeliveryAttemptSchema(
                id=att.id,
                attempt_count=att.attempt_count,
                status=att.status.value,
                response_status=att.response_status,
                execution_duration_ms=att.execution_duration_ms,
                error_message=att.error_message,
                next_retry_at=att.next_retry_at.isoformat() if att.next_retry_at else None,
                created_at=att.created_at.isoformat()
            ) for att in attempts
        ]
    )

@router.get("/stream/live")
async def sse_event_stream():
    """
    Server-Sent Events endpoint streaming live webhook ingestions & delivery attempts to frontend UI.
    """
    queue = await sse_manager.subscribe()

    async def event_generator():
        try:
            while True:
                msg = await queue.get()
                yield {
                    "event": msg["event"],
                    "data": json_dumps(msg["data"])
                }
        except asyncio.CancelledError:
            await sse_manager.unsubscribe(queue)

    return EventSourceResponse(event_generator())

def json_dumps(obj):
    import json
    return json.dumps(obj)

