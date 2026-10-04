import hmac
import hashlib
import base64
from typing import Dict, Tuple
from app.verifiers.base import BaseSignatureVerifier

class ShopifyVerifier(BaseSignatureVerifier):
    """
    Shopify Signature Verifier.
    Expects header `X-Shopify-Hmac-SHA256` containing Base64-encoded HMAC SHA256 hash.
    """
    def verify(self, headers: Dict[str, str], raw_body: str, secret_key: str) -> Tuple[bool, str]:
        if not secret_key:
            return True, "No secret key configured; signature check skipped"

        sig_header = None
        for k, v in headers.items():
            if k.lower() == 'x-shopify-hmac-sha256':
                sig_header = v
                break

        if not sig_header:
            return False, "Missing 'X-Shopify-Hmac-SHA256' header"

        digest = hmac.new(
            secret_key.encode('utf-8'),
            raw_body.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_sig = base64.b64encode(digest).decode('utf-8')

        if hmac.compare_digest(expected_sig, sig_header):
            return True, "Valid Shopify signature"

        return False, "Shopify signature verification failed"

