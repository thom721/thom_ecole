"""create messages table

Revision ID: f1a6c3e8d2b5
Revises: e8c4f2a9b1d6
Create Date: 2026-10-17 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a6c3e8d2b5'
down_revision: Union[str, Sequence[str], None] = 'e8c4f2a9b1d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Idempotent : une exécution interrompue (CREATE TABLE validé tout de
    # suite par MySQL, alembic_version non mis à jour) ne doit pas bloquer
    # toutes les migrations suivantes — cas déjà vécu avec webhook_queue.
    if sa.inspect(op.get_bind()).has_table('messages'):
        return
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('sender_id', sa.CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('recipient_id', sa.CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_messages_recipient_read', 'messages', ['recipient_id', 'read_at'])
    op.create_index('ix_messages_pair', 'messages', ['sender_id', 'recipient_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_messages_pair', table_name='messages')
    op.drop_index('ix_messages_recipient_read', table_name='messages')
    op.drop_table('messages')
