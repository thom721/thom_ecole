"""create pointages

Revision ID: 6af9d208f564
Revises: 37c980e6705d
Create Date: 2026-07-03 00:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = '6af9d208f564'
down_revision: Union[str, None] = '37c980e6705d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pointages',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('heure_arrivee', sa.DateTime(), nullable=True),
        sa.Column('heure_depart', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'date', name='uq_pointage_user_date'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('pointages')
