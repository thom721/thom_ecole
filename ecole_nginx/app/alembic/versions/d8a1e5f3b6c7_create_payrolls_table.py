"""create_payrolls_table

Revision ID: d8a1e5f3b6c7
Revises: c2f8b4a6d9e1
Create Date: 2026-06-27 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd8a1e5f3b6c7'
down_revision: Union[str, Sequence[str], None] = 'c2f8b4a6d9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payrolls',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('montant', sa.Numeric(10, 2), nullable=False),
        sa.Column('mois', sa.String(20), nullable=False),
        sa.Column('annee', sa.String(4), nullable=False),
        sa.Column('statut', sa.String(20), nullable=False, server_default='En attente'),
        sa.Column('date_versement', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_foreign_key(
        'payrolls_user_id_foreign',
        'payrolls', 'users',
        ['user_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('payrolls_user_id_foreign', 'payrolls', type_='foreignkey')
    op.drop_table('payrolls')
