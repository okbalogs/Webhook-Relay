import hmac
import hashlib
import time
from typing import Dict, Tuple
from app.verifiers.base import BaseSignatureVerifier

class StripeVerifier(BaseSignatureVerifier):
    """
    Stripe Signature Verifier.
    Expects header `Stripe-Signature` in format: `t=1614000000,v1=9f8a...`
    Signature payload: timestamp + '.' + raw_body
    HMAC algorithm: HMAC-SHA256
    """
    def verify(self, headers: Dict[str, str], raw_body: str, secret_key: str) -> Tuple[bool, str]:
        if not secret_key:
            return True, "No secret key configured; signature check skipped"

        # Case-insensitive header extraction
        sig_header = None
        for k, v in headers.items():
            if k.lower() == 'stripe-signature':
                sig_header = v
                break

        if not sig_header:
            return False, "Missing 'Stripe-Signature' header"

        items = {}
        for part in sig_header.split(','):
            kv = part.strip().split('=', 1)
            if len(kv) == 2:
                items[kv[0]] = kv[1]

        timestamp = items.get('t')
        signatures = [v for k, v in items.items() if k == 'v1']

        if not timestamp or not signatures:
            return False, "Malformed Stripe-Signature header"

        # Construct signed payload
        signed_payload = f"{timestamp}.{raw_body}".encode('utf-8')
        expected_sig = hmac.new(secret_key.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()

        for sig in signatures:
            if hmac.compare_digest(expected_sig, sig):
                return True, "Valid Stripe signature"

        return False, "Stripe signature verification failed"

