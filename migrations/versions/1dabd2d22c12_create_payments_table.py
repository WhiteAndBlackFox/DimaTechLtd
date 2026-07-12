"""create payments table

Revision ID: 1dabd2d22c12
Revises: f134523b2cf2
Create Date: 2026-07-12 18:17:56.345167

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1dabd2d22c12'
down_revision: str | Sequence[str] | None = 'f134523b2cf2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('payments')
