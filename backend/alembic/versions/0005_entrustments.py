"""entrustments

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "entrustments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(24), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("source_quote_id", sa.Integer(), sa.ForeignKey("quotations.id"), nullable=True),
        sa.Column("requirement", sa.Text(), nullable=True),
        sa.Column("external_no", sa.String(64), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("created_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("terminated_at", sa.DateTime(), nullable=True),
        sa.Column("terminated_by", sa.String(64), nullable=True),
        sa.Column("terminated_reason", sa.String(256), nullable=True),
    )
    op.create_index("ix_entrustments_code", "entrustments", ["code"], unique=True)
    op.create_index("ix_entrustments_customer_id", "entrustments", ["customer_id"])
    op.create_index("ix_entrustments_source_quote_id", "entrustments", ["source_quote_id"])
    op.create_index("ix_entrustments_status", "entrustments", ["status"])


def downgrade():
    op.drop_index("ix_entrustments_status", table_name="entrustments")
    op.drop_index("ix_entrustments_source_quote_id", table_name="entrustments")
    op.drop_index("ix_entrustments_customer_id", table_name="entrustments")
    op.drop_index("ix_entrustments_code", table_name="entrustments")
    op.drop_table("entrustments")
