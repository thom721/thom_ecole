"""add microsecond precision to salaire_historiques.created_at

Revision ID: bd9b7a813621
Revises: 39b129c52dff
Create Date: 2026-07-06 00:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME as MySQLDateTime

revision: str = 'bd9b7a813621'
down_revision: Union[str, None] = '39b129c52dff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sans précision fractionnaire, deux changements de salaire faits dans la
    # même seconde (ex. deux appels rapprochés) ne peuvent pas être triés de
    # façon fiable par created_at — le rapport pourrait alors afficher
    # ancien/nouveau montant dans le mauvais ordre.
    op.alter_column(
        'salaire_historiques', 'created_at',
        existing_type=sa.DateTime(),
        type_=MySQLDateTime(fsp=6),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'salaire_historiques', 'created_at',
        existing_type=MySQLDateTime(fsp=6),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
