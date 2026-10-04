import pytest
import asyncio
import hmac
import hashlib
from app.verifiers.stripe import StripeVerifier
from app.verifiers.github import GitHubVerifier
from app.verifiers.shopify import ShopifyVerifier
from app.services.retry_worker import calculate_next_retry

def test_github_verifier():
    verifier = GitHubVerifier()
    secret = "my_github_secret"
    body = '{"action": "opened", "issue": {"id": 123}}'
    
    expected_sig = "sha256=" + hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {"X-Hub-Signature-256": expected_sig}
    valid, msg = verifier.verify(headers, body, secret)
    assert valid is True
    assert "Valid GitHub signature" in msg

def test_stripe_verifier():
    verifier = StripeVerifier()
    secret = "whsec_test123"
    body = '{"type": "payment_intent.succeeded"}'
    t = "1614000000"
    
    signed_payload = f"{t}.{body}".encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
    
    headers = {"Stripe-Signature": f"t={t},v1={sig}"}
    valid, msg = verifier.verify(headers, body, secret)
    assert valid is True
    assert "Valid Stripe signature" in msg

def test_exponential_backoff():
    next_1 = calculate_next_retry(1)
    next_2 = calculate_next_retry(2)
    next_3 = calculate_next_retry(3)

    assert next_1 < next_2 < next_3

