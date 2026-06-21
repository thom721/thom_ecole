"""Intégration MonCash (Digicel Haïti).

Implémente le flux REST documenté par MonCash : token OAuth2
(client_credentials) -> CreatePayment -> redirection du client vers la page
de paiement MonCash -> au retour, RetrieveTransactionPayment pour confirmer.

IMPORTANT : à vérifier contre la documentation officielle MonCash Business
avant mise en production (les noms de champs/endpoints peuvent évoluer selon
la version de l'API) — non testé ici faute d'identifiants marchand réels.
Remplir MONCASH_CLIENT_ID / MONCASH_CLIENT_SECRET dans .env avant d'utiliser.
"""
import os

import httpx

from app.payments.base import PaymentInitResult, PaymentProvider

MONCASH_BASE_URL = os.environ.get("MONCASH_BASE_URL", "https://sandbox.moncashbutton.digicelgroup.com")
MONCASH_GATEWAY_URL = os.environ.get(
    "MONCASH_GATEWAY_URL", "https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware"
)
MONCASH_CLIENT_ID = os.environ.get("MONCASH_CLIENT_ID", "")
MONCASH_CLIENT_SECRET = os.environ.get("MONCASH_CLIENT_SECRET", "")


class MonCashProvider(PaymentProvider):
    async def _get_access_token(self) -> str:
        if not MONCASH_CLIENT_ID or not MONCASH_CLIENT_SECRET:
            raise RuntimeError(
                "MONCASH_CLIENT_ID / MONCASH_CLIENT_SECRET manquants dans l'environnement."
            )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MONCASH_BASE_URL}/Api/oauth/token",
                data={"grant_type": "client_credentials", "scope": "read,write"},
                auth=(MONCASH_CLIENT_ID, MONCASH_CLIENT_SECRET),
                timeout=20,
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def create_payment(self, amount: float, currency: str, order_id: str) -> PaymentInitResult:
        token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MONCASH_BASE_URL}/Api/v1/CreatePayment",
                json={"amount": amount, "orderId": order_id},
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
            )
            response.raise_for_status()
            payment_token = response.json()["payment_token"]["token"]

        redirect_url = f"{MONCASH_GATEWAY_URL}/Payment/Redirect?token={payment_token}"
        return PaymentInitResult(provider_reference=order_id, redirect_url=redirect_url)

    async def verify_payment(self, provider_reference: str) -> bool:
        token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MONCASH_BASE_URL}/Api/v1/RetrieveTransactionPayment",
                json={"orderId": provider_reference},
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("status") == 0 or data.get("transaction", {}).get("message") == "successful"
