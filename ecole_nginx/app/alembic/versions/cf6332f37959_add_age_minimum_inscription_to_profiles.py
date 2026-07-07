"""add age_minimum_inscription to profiles

Revision ID: cf6332f37959
Revises: b3e1f9a2c7d5
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'cf6332f37959'
down_revision: Union[str, None] = 'b3e1f9a2c7d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'profiles',
        sa.Column(
            'age_minimum_inscription',
            sa.Integer(),
            nullable=False,
            server_default='1',
        ),
    )


def downgrade() -> None:
    op.drop_column('profiles', 'age_minimum_inscription')
