"""create payroll_versements

Revision ID: 37c980e6705d
Revises: 7e23faa1c08d
Create Date: 2026-07-03 00:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = '37c980e6705d'
down_revision: Union[str, None] = '7e23faa1c08d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payroll_versements',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('payroll_id', CHAR(36), sa.ForeignKey('payrolls.id'), nullable=False),
        sa.Column('montant', sa.Numeric(10, 2), nullable=False),
        sa.Column('date_versement', sa.Date(), nullable=False),
        sa.Column('methode_paiement', sa.String(255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('collected_by', CHAR(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('payroll_versements')
