from abc import ABC, abstractmethod
from typing import Dict, Tuple

class BaseSignatureVerifier(ABC):
    @abstractmethod
    def verify(self, headers: Dict[str, str], raw_body: str, secret_key: str) -> Tuple[bool, str]:
        """
        Verifies the cryptographic signature of an inbound webhook.
        Returns a tuple: (is_valid: bool, reason_message: str)
        """
        pass

