"""standards + standard_items + equipment

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "standards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("std_no", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_standards_std_no", "standards", ["std_no"], unique=True)
    op.create_index("ix_standards_status", "standards", ["status"])

    op.create_table(
        "standard_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("standard_id", sa.Integer(), sa.ForeignKey("standards.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(8), nullable=False, server_default="EMI"),
        sa.Column("method", sa.String(256), nullable=True),
        sa.Column("criteria", sa.String(512), nullable=True),
    )
    op.create_index("ix_standard_items_standard_id", "standard_items", ["standard_id"])
    op.create_index("ix_standard_items_category", "standard_items", ["category"])

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(16), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("model", sa.String(64), nullable=True),
        sa.Column("location", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_equipment_code", "equipment", ["code"], unique=True)


def downgrade():
    op.drop_index("ix_equipment_code", table_name="equipment")
    op.drop_table("equipment")
    op.drop_index("ix_standard_items_category", table_name="standard_items")
    op.drop_index("ix_standard_items_standard_id", table_name="standard_items")
    op.drop_table("standard_items")
    op.drop_index("ix_standards_status", table_name="standards")
    op.drop_index("ix_standards_std_no", table_name="standards")
    op.drop_table("standards")
