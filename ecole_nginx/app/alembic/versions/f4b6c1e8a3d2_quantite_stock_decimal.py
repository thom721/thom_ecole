"""quantite_stock_decimal

Revision ID: f4b6c1e8a3d2
Revises: e9c4f7a2b1d8
Create Date: 2026-06-27 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f4b6c1e8a3d2'
down_revision: Union[str, Sequence[str], None] = 'e9c4f7a2b1d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Certains produits se vendent par fraction (mètre de tissu, kg...) :
    # le stock doit accepter une quantité décimale, pas seulement entière.
    op.alter_column(
        'produits', 'quantite_stock',
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
        existing_server_default='0',
    )


def downgrade() -> None:
    op.alter_column(
        'produits', 'quantite_stock',
        existing_type=sa.Numeric(10, 2),
        type_=sa.Integer(),
        existing_nullable=False,
        existing_server_default='0',
    )
