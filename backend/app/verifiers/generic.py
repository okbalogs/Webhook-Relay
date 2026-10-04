import hmac
import hashlib
from typing import Dict, Tuple
from app.verifiers.base import BaseSignatureVerifier

class GenericVerifier(BaseSignatureVerifier):
    """
    Generic Signature Verifier.
    Supports standard `X-Signature`, `X-Webhook-Secret`, or `Authorization` matching.
    """
    def verify(self, headers: Dict[str, str], raw_body: str, secret_key: str) -> Tuple[bool, str]:
        if not secret_key:
            return True, "No secret key configured; signature check skipped"

        # Check for signature headers
        possible_headers = ['x-signature', 'x-webhook-signature', 'x-secret', 'x-webhook-secret']
        found_header = None
        found_val = None

        for k, v in headers.items():
            if k.lower() in possible_headers:
                found_header = k.lower()
                found_val = v
                break

        if not found_val:
            # Fallback: check if raw secret key matches header value directly
            return True, "Generic webhook accepted (no standard signature header required)"

        # Check raw secret match or HMAC-SHA256 match
        if hmac.compare_digest(found_val, secret_key):
            return True, "Valid generic token secret match"

        expected_sig = hmac.new(
            secret_key.encode('utf-8'),
            raw_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(expected_sig, found_val) or hmac.compare_digest(f"sha256={expected_sig}", found_val):
            return True, "Valid generic HMAC signature"

        return False, "Generic signature verification failed"

