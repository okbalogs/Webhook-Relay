from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
import uuid

from app.db.database import get_db
from app.db.models import Endpoint, ProviderType

router = APIRouter(prefix="/api/v1/endpoints", tags=["Endpoints"])

class EndpointCreate(BaseModel):
    name: str
    target_url: str
    provider: ProviderType = ProviderType.GENERIC
    secret_key: str = ""
    max_retries: int = 5
    timeout_seconds: int = 10

class EndpointResponse(BaseModel):
    id: uuid.UUID
    name: str
    secret_key: str
    provider: ProviderType
    target_url: str
    ingest_url: str
    is_active: bool
    max_retries: int
    timeout_seconds: int

    model_config = ConfigDict(from_attributes=True)

@router.post("", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(data: EndpointCreate, db: AsyncSession = Depends(get_db)):
    secret = data.secret_key if data.secret_key else f"sec_{uuid.uuid4().hex[:16]}"
    
    endpoint = Endpoint(
        name=data.name,
        target_url=str(data.target_url),
        provider=data.provider,
        secret_key=secret,
        max_retries=data.max_retries,
        timeout_seconds=data.timeout_seconds
    )
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)

    return EndpointResponse(
        id=endpoint.id,
        name=endpoint.name,
        secret_key=endpoint.secret_key,
        provider=endpoint.provider,
        target_url=endpoint.target_url,
        ingest_url=f"/api/v1/ingest/{endpoint.id}",
        is_active=endpoint.is_active,
        max_retries=endpoint.max_retries,
        timeout_seconds=endpoint.timeout_seconds
    )

@router.get("", response_model=List[EndpointResponse])
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).order_by(Endpoint.created_at.desc()))
    endpoints = result.scalars().all()
    
    return [
        EndpointResponse(
            id=ep.id,
            name=ep.name,
            secret_key=ep.secret_key,
            provider=ep.provider,
            target_url=ep.target_url,
            ingest_url=f"/api/v1/ingest/{ep.id}",
            is_active=ep.is_active,
            max_retries=ep.max_retries,
            timeout_seconds=ep.timeout_seconds
        ) for ep in endpoints
    ]

@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    return EndpointResponse(
        id=ep.id,
        name=ep.name,
        secret_key=ep.secret_key,
        provider=ep.provider,
        target_url=ep.target_url,
        ingest_url=f"/api/v1/ingest/{ep.id}",
        is_active=ep.is_active,
        max_retries=ep.max_retries,
        timeout_seconds=ep.timeout_seconds
    )

@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    await db.delete(ep)
    await db.commit()

