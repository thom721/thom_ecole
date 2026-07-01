from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    """Une installation ecole_nginx enregistrée (un client = un MAC address)."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mac = Column(String, unique=True, index=True, nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    licence_keys = relationship("LicenceKey", back_populates="client", order_by="desc(LicenceKey.created_at)")
    payments = relationship("Payment", back_populates="client", order_by="desc(Payment.created_at)")


class LicenceKey(Base):
    """Historique des clés d'activation générées pour un client."""
    __tablename__ = "licence_keys"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    key = Column(String, nullable=False)
    expiration_date = Column(String, nullable=False)  # format YYYY-MM-DD
    days_valid = Column(Integer, nullable=False)  # valeur "sémantique" (ce que le client a payé cette fois-ci), pour l'affichage historique
    days_valid_key = Column(Integer, nullable=True)  # valeur RÉELLEMENT utilisée dans le HMAC de `key` (cumul des jours restants inclus) — voir _valider_paiement
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="licence_keys")


class Payment(Base):
    """Paiement de renouvellement de licence (MonCash / NatCash / Stripe)."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    provider = Column(String, nullable=False)  # "moncash" | "natcash" | "stripe"
    amount = Column(Float, nullable=False)
    currency = Column(String, default="HTG", nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending | success | failed
    days_valid = Column(Integer, nullable=False)  # durée choisie au moment du paiement
    provider_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="payments")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PricingConfig(Base):
    """Configuration unique (une seule ligne) du prix mensuel et du taux de
    change du jour, gérée par l'admin. Le prix de base est toujours en
    `currency` (USD) — pour les paiements autres que carte (Stripe), le
    montant est converti en HTG via `exchange_rate_usd_htg` au moment du
    paiement."""
    __tablename__ = "pricing_config"

    id = Column(Integer, primary_key=True, index=True)
    monthly_price = Column(Float, nullable=False, default=10.0)
    currency = Column(String, nullable=False, default="USD")
    exchange_rate_usd_htg = Column(Float, nullable=False, default=132.0)
    # Si True, la clé est générée et affichée dès que le fournisseur de paiement confirme.
    # Si False, le paiement passe en statut "paid" et un admin doit cliquer "Activer" pour générer la clé.
    auto_release = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
