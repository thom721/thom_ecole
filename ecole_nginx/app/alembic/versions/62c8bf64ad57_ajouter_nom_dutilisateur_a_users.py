"""ajouter_nom_dutilisateur_a_users

Revision ID: 62c8bf64ad57
Revises: d4b730647604
Create Date: 2026-02-17 17:30:31.302850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62c8bf64ad57'
down_revision: Union[str, Sequence[str], None] = 'd4b730647604'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', 
        sa.Column('username', sa.String(length=255), nullable=True, unique=True, index=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'username')
