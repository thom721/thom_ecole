"""Intégration Stripe — EN ATTENTE (demandé explicitement par l'utilisateur).

Squelette prêt à compléter : installer le SDK `stripe`, fournir
STRIPE_SECRET_KEY dans .env, puis implémenter via
stripe.checkout.Session.create(...) / Session.retrieve(...).
"""
from app.payments.base import PaymentInitResult, PaymentProvider


class StripeProvider(PaymentProvider):
    async def create_payment(self, amount: float, currency: str, order_id: str) -> PaymentInitResult:
        raise NotImplementedError("Intégration Stripe en attente.")

    async def verify_payment(self, provider_reference: str) -> bool:
        raise NotImplementedError("Intégration Stripe en attente.")
