from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentInitResult:
    provider_reference: str
    redirect_url: str | None = None


class PaymentProvider(ABC):
    @abstractmethod
    async def create_payment(self, amount: float, currency: str, order_id: str) -> PaymentInitResult:
        """Démarre un paiement chez le fournisseur, renvoie une référence + une éventuelle URL de redirection."""

    @abstractmethod
    async def verify_payment(self, provider_reference: str) -> bool:
        """Confirme auprès du fournisseur que le paiement a bien été complété."""


def get_provider(name: str) -> "PaymentProvider":
    # Imports différés pour éviter un cycle d'import avec ce module.
    from app.payments.moncash import MonCashProvider
    from app.payments.natcash import NatCashProvider
    from app.payments.stripe_provider import StripeProvider

    providers = {
        "moncash": MonCashProvider,
        "natcash": NatCashProvider,
        "stripe": StripeProvider,
    }
    provider_cls = providers.get(name)
    if not provider_cls:
        raise ValueError(f"Fournisseur de paiement inconnu : {name!r}")
    return provider_cls()
