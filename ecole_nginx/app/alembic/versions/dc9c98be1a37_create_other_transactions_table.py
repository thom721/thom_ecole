"""create_other_transactions_table

Revision ID: dc9c98be1a37
Revises: 
Create Date: 2026-01-29 15:56:21.899586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'dc9c98be1a37'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'other_transactions',
        sa.Column('id', sa.String(36), primary_key=True, default=uuid.uuid4),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('montant', sa.Numeric(10, 2), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('delete_by', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('delete_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB'
    )  
def downgrade() -> None:
    op.drop_table('other_transactions')
