from sqlalchemy.orm import Session

from app.models import PricingConfig

DEFAULT_MONTHLY_PRICE = 10.0
DEFAULT_CURRENCY = "USD"
DEFAULT_EXCHANGE_RATE_USD_HTG = 132.0


def get_or_create_pricing_config(db: Session) -> PricingConfig:
    config = db.query(PricingConfig).first()
    if not config:
        config = PricingConfig(
            monthly_price=DEFAULT_MONTHLY_PRICE,
            currency=DEFAULT_CURRENCY,
            exchange_rate_usd_htg=DEFAULT_EXCHANGE_RATE_USD_HTG,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def calculer_montant(config: PricingConfig, months: int, provider: str) -> tuple[float, str]:
    """Renvoie (montant, devise) pour `months` mois au prix mensuel courant.
    Paiement par carte (Stripe) -> reste dans la devise de base (USD).
    Tout autre fournisseur (MonCash, NatCash, ...) -> converti en HTG au taux
    du jour saisi par l'admin."""
    base_amount = round(config.monthly_price * months, 2)
    if provider == "stripe":
        return base_amount, config.currency
    return round(base_amount * config.exchange_rate_usd_htg, 2), "HTG"
