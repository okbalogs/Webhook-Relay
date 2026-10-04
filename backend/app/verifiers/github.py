import hmac
import hashlib
from typing import Dict, Tuple
from app.verifiers.base import BaseSignatureVerifier

class GitHubVerifier(BaseSignatureVerifier):
    """
    GitHub Signature Verifier.
    Expects header `X-Hub-Signature-256` in format: `sha256=...`
    HMAC algorithm: HMAC-SHA256 over raw request body
    """
    def verify(self, headers: Dict[str, str], raw_body: str, secret_key: str) -> Tuple[bool, str]:
        if not secret_key:
            return True, "No secret key configured; signature check skipped"

        sig_header = None
        for k, v in headers.items():
            if k.lower() == 'x-hub-signature-256':
                sig_header = v
                break

        if not sig_header:
            return False, "Missing 'X-Hub-Signature-256' header"

        if not sig_header.startswith("sha256="):
            return False, "Malformed GitHub signature header (must start with sha256=)"

        provided_sig = sig_header[7:]
        expected_sig = hmac.new(
            secret_key.encode('utf-8'),
            raw_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(expected_sig, provided_sig):
            return True, "Valid GitHub signature"

        return False, "GitHub signature verification failed"

