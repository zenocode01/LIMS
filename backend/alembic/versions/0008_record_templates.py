"""record_templates + template_fields

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "record_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tpl_no", sa.String(8), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("form_level", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("category", sa.String(8), nullable=False, server_default="EMI"),
        sa.Column("controlled", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_record_templates_tpl_no", "record_templates", ["tpl_no"], unique=True)
    op.create_index("ix_record_templates_category", "record_templates", ["category"])
    op.create_index("ix_record_templates_controlled", "record_templates", ["controlled"])

    op.create_table(
        "template_fields",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("record_templates.id"), nullable=False),
        sa.Column("field_no", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("field_name", sa.String(64), nullable=False),
        sa.Column("field_type", sa.String(16), nullable=False, server_default="text"),
        sa.Column("unit", sa.String(16), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("criteria_expr", sa.String(256), nullable=True),
    )
    op.create_index("ix_template_fields_template_id", "template_fields", ["template_id"])


def downgrade():
    op.drop_index("ix_template_fields_template_id", table_name="template_fields")
    op.drop_table("template_fields")
    op.drop_index("ix_record_templates_controlled", table_name="record_templates")
    op.drop_index("ix_record_templates_category", table_name="record_templates")
    op.drop_index("ix_record_templates_tpl_no", table_name="record_templates")
    op.drop_table("record_templates")
