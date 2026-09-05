"""ajouter_inscription_a_profiles

Revision ID: d7f3a1c5e9b2
Revises: c4d9e2f6a8b1
Create Date: 2026-08-29 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f3a1c5e9b2'
down_revision: Union[str, Sequence[str], None] = 'c4d9e2f6a8b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('inscription', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('profiles', 'inscription')
