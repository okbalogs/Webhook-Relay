import pytest
import hmac
import hashlib
import json
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_full_webhook_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Ingestion Endpoint
        ep_resp = await ac.post("/api/v1/endpoints", json={
            "name": "Stripe E2E Test Endpoint",
            "provider": "stripe",
            "target_url": "http://httpbin.org/post",
            "secret_key": "whsec_test_secret_key_123"
        })
        assert ep_resp.status_code == 201
        ep_data = ep_resp.json()
        endpoint_id = ep_data["id"]

        # 2. Ingest valid Stripe Webhook
        raw_payload = json.dumps({"type": "payment_intent.succeeded", "data": {"amount": 5000}})
        t = "1614000000"
        signed_payload = f"{t}.{raw_payload}".encode('utf-8')
        sig = hmac.new("whsec_test_secret_key_123".encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
        
        headers = {
            "Stripe-Signature": f"t={t},v1={sig}",
            "Content-Type": "application/json"
        }

        ingest_resp = await ac.post(f"/api/v1/ingest/{endpoint_id}", content=raw_payload, headers=headers)
        assert ingest_resp.status_code == 202
        ingest_data = ingest_resp.json()
        assert ingest_data["status"] == "accepted"
        assert ingest_data["signature_valid"] is True
        event_id = ingest_data["event_id"]

        # 3. Fetch Event Detail
        ev_resp = await ac.get(f"/api/v1/events/{event_id}")
        assert ev_resp.status_code == 200
        ev_detail = ev_resp.json()
        assert ev_detail["provider"] == "stripe"
        assert ev_detail["signature_valid"] is True
        assert len(ev_detail["attempts"]) >= 1

        # 4. Trigger Manual Replay
        replay_resp = await ac.post(f"/api/v1/events/{event_id}/replay", json={
            "override_payload": {"type": "payment_intent.succeeded", "data": {"amount": 10000}}
        })
        assert replay_resp.status_code == 202
        assert replay_resp.json()["status"] == "replay_initiated"

