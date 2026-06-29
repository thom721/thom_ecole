"""add is_receive_arriere to profiles

Revision ID: b3e1f9a2c7d5
Revises: f4b6c1e8a3d2
Create Date: 2026-06-29 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b3e1f9a2c7d5'
down_revision: Union[str, None] = 'f4b6c1e8a3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'profiles',
        sa.Column(
            'is_receive_arriere',
            sa.Boolean(),
            nullable=False,
            server_default='0',
        ),
    )


def downgrade() -> None:
    op.drop_column('profiles', 'is_receive_arriere')
