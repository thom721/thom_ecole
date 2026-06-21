"""add_niveau_id_faculte_id_to_formations

Revision ID: 92c34921c4ae
Revises: b1f448c43b72
Create Date: 2026-05-16 16:06:51.034716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92c34921c4ae'
down_revision: Union[str, Sequence[str], None] = 'b1f448c43b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('formations', sa.Column('niveau_id',  sa.String(36), nullable=True))
    op.add_column('formations', sa.Column('faculte_id', sa.String(36), nullable=True))


def downgrade() -> None:
    op.drop_column('formations', 'faculte_id')
    op.drop_column('formations', 'niveau_id')
