from app.db.models import ProviderType
from app.verifiers.stripe import StripeVerifier
from app.verifiers.github import GitHubVerifier
from app.verifiers.shopify import ShopifyVerifier
from app.verifiers.generic import GenericVerifier

def get_verifier(provider: ProviderType):
    if provider == ProviderType.STRIPE:
        return StripeVerifier()
    elif provider == ProviderType.GITHUB:
        return GitHubVerifier()
    elif provider == ProviderType.SHOPIFY:
        return ShopifyVerifier()
    else:
        return GenericVerifier()

