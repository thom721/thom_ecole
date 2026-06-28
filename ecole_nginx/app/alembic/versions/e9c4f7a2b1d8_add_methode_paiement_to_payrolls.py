"""add_methode_paiement_to_payrolls

Revision ID: e9c4f7a2b1d8
Revises: d8a1e5f3b6c7
Create Date: 2026-06-27 04:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e9c4f7a2b1d8'
down_revision: Union[str, Sequence[str], None] = 'd8a1e5f3b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'payrolls',
        sa.Column('methode_paiement', sa.String(20), nullable=False, server_default='Espèce'),
    )


def downgrade() -> None:
    op.drop_column('payrolls', 'methode_paiement')
