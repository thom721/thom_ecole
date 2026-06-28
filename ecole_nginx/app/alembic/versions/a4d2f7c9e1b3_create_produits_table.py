"""create_produits_table

Revision ID: a4d2f7c9e1b3
Revises: 0427cf969b31
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a4d2f7c9e1b3'
down_revision: Union[str, Sequence[str], None] = '0427cf969b31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'produits',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('nom', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('prix', sa.Numeric(8, 2), nullable=False),
        sa.Column('quantite_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.add_column('order_items', sa.Column('produit_id', sa.CHAR(36), nullable=True))
    op.create_foreign_key(
        'order_items_produit_id_foreign',
        'order_items', 'produits',
        ['produit_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('order_items_produit_id_foreign', 'order_items', type_='foreignkey')
    op.drop_column('order_items', 'produit_id')
    op.drop_table('produits')
