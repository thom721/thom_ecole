"""Intégration NatCash (Natcom) — PAS ENCORE IMPLÉMENTÉE.

Je n'ai pas de référence fiable de l'API marchand NatCash pour écrire un
client correct sans risquer de fabriquer des endpoints/champs incorrects.
Fournir la documentation officielle (ou les identifiants d'accès au portail
développeur NatCash) pour compléter cette intégration.
"""
from app.payments.base import PaymentInitResult, PaymentProvider


class NatCashProvider(PaymentProvider):
    async def create_payment(self, amount: float, currency: str, order_id: str) -> PaymentInitResult:
        raise NotImplementedError("Intégration NatCash non implémentée — documentation API requise.")

    async def verify_payment(self, provider_reference: str) -> bool:
        raise NotImplementedError("Intégration NatCash non implémentée — documentation API requise.")
