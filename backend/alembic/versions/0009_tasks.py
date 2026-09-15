"""tasks + quotations.standard_item_id

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite 不支持 ALTER ADD COLUMN 带外键: PG 加外键, SQLite 只加列（SQLite 默认不强制 FK）
    if op.get_bind().dialect.name == "postgresql":
        op.add_column(
            "quotation_items",
            sa.Column("standard_item_id", sa.Integer(), sa.ForeignKey("standard_items.id"), nullable=True),
        )
    else:
        op.add_column(
            "quotation_items",
            sa.Column("standard_item_id", sa.Integer(), nullable=True),
        )
    op.create_index("ix_quotation_items_standard_item_id", "quotation_items", ["standard_item_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(24), nullable=False),
        sa.Column("entrustment_id", sa.Integer(), sa.ForeignKey("entrustments.id"), nullable=False),
        sa.Column("sample_id", sa.Integer(), sa.ForeignKey("samples.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("standard_items.id"), nullable=False),
        sa.Column("category", sa.String(8), nullable=False, server_default="EMI"),
        sa.Column("status", sa.String(16), nullable=False, server_default="unscheduled"),
        sa.Column("retest_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tasks_code", "tasks", ["code"], unique=True)
    op.create_index("ix_tasks_entrustment_id", "tasks", ["entrustment_id"])
    op.create_index("ix_tasks_sample_id", "tasks", ["sample_id"])
    op.create_index("ix_tasks_item_id", "tasks", ["item_id"])
    op.create_index("ix_tasks_category", "tasks", ["category"])
    op.create_index("ix_tasks_status", "tasks", ["status"])


def downgrade():
    for idx in ("ix_tasks_status", "ix_tasks_category", "ix_tasks_item_id", "ix_tasks_sample_id", "ix_tasks_entrustment_id", "ix_tasks_code"):
        op.drop_index(idx, table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_quotation_items_standard_item_id", table_name="quotation_items")
    op.drop_column("quotation_items", "standard_item_id")
