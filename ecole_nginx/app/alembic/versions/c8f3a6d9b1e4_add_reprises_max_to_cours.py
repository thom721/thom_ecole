"""add reprises_max to cours

Revision ID: c8f3a6d9b1e4
Revises: e7d3a9c1f6b4
Create Date: 2026-09-10 00:00:05.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f3a6d9b1e4'
down_revision: Union[str, Sequence[str], None] = 'e7d3a9c1f6b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cours', sa.Column('reprises_max', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('cours', 'reprises_max')
