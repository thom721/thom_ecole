"""create webhook_queue table

Revision ID: c9e4a7b1f3d6
Revises: a3c7f1e9b5d2
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e4a7b1f3d6'
down_revision: Union[str, Sequence[str], None] = 'a3c7f1e9b5d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'webhook_queue',
        sa.Column('id', sa.CHAR(36), primary_key=True, default=uuid.uuid4),
        sa.Column('path', sa.String(255), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_webhook_queue_status', 'webhook_queue', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_webhook_queue_status', table_name='webhook_queue')
    op.drop_table('webhook_queue')
