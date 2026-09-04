"""numbering_sequences

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "numbering_sequences",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("date", sa.String(10), primary_key=True),
        sa.Column("last_no", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_table("numbering_sequences")
