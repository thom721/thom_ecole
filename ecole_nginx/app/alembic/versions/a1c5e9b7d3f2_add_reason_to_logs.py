"""add_reason_to_logs

Revision ID: a1c5e9b7d3f2
Revises: f4b6c1e8a3d2
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1c5e9b7d3f2'
down_revision: Union[str, Sequence[str], None] = 'f4b6c1e8a3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Raison saisie par l'utilisateur pour un retour de paiement ou une
    # suppression de vente/dépense/transaction — alimentée par ReasonContext
    # (app/Helper/context.py) via global_observer.py.
    op.add_column('logs', sa.Column('reason', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('logs', 'reason')
