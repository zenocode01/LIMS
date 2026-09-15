"""samples + sample_events

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "samples",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("biz_line", sa.String(16), nullable=False, server_default="EMC"),
        sa.Column("entrustment_id", sa.Integer(), sa.ForeignKey("entrustments.id"), nullable=False),
        sa.Column("name_model", sa.String(128), nullable=False),
        sa.Column("appearance", sa.String(256), nullable=True),
        sa.Column("external_no", sa.String(64), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="registered"),
        sa.Column("created_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_samples_code", "samples", ["code"], unique=True)
    op.create_index("ix_samples_entrustment_id", "samples", ["entrustment_id"])
    op.create_index("ix_samples_status", "samples", ["status"])

    op.create_table(
        "sample_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sample_id", sa.Integer(), sa.ForeignKey("samples.id"), nullable=False),
        sa.Column("from_status", sa.String(16), nullable=True),
        sa.Column("to_status", sa.String(16), nullable=False),
        sa.Column("operator", sa.String(64), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_sample_events_sample_id", "sample_events", ["sample_id"])


def downgrade():
    op.drop_index("ix_sample_events_sample_id", table_name="sample_events")
    op.drop_table("sample_events")
    op.drop_index("ix_samples_status", table_name="samples")
    op.drop_index("ix_samples_entrustment_id", table_name="samples")
    op.drop_index("ix_samples_code", table_name="samples")
    op.drop_table("samples")
