"""init

Revision ID: e024590c1b5a
Revises: 
Create Date: 2026-01-08 15:58:27.800696
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e024590c1b5a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("subscription_plan", sa.String(), nullable=True, server_default=sa.text("'free'")),
        sa.Column("subscription_status", sa.String(), nullable=True, server_default=sa.text("'active'")),
        sa.Column("subscription_expires_at", sa.DateTime(), nullable=True),
        sa.Column("api_key", sa.String(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_api_key", "users", ["api_key"], unique=True)

    op.create_table(
        "threats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("threat_type", sa.String(), nullable=True),
        sa.Column("severity", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True, server_default=sa.text("'detected'")),
        sa.Column("source_ip", sa.String(), nullable=True),
        sa.Column("destination_ip", sa.String(), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("process_name", sa.String(), nullable=True),
        sa.Column("hash_value", sa.String(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_threats_threat_type", "threats", ["threat_type"], unique=False)
    op.create_index("ix_threats_severity", "threats", ["severity"], unique=False)
    op.create_index("ix_threats_detected_at", "threats", ["detected_at"], unique=False)

    op.create_table(
        "licenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("license_key", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("max_devices", sa.Integer(), nullable=True, server_default=sa.text("1")),
        sa.Column("devices_used", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_licenses_license_key", "licenses", ["license_key"], unique=True)

    op.create_table(
        "system_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("cpu_usage", sa.Float(), nullable=True),
        sa.Column("memory_usage", sa.Float(), nullable=True),
        sa.Column("disk_usage", sa.Float(), nullable=True),
        sa.Column("network_traffic", sa.Float(), nullable=True),
        sa.Column("active_threats", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("blocked_threats", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("recorded_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_system_metrics_recorded_at", "system_metrics", ["recorded_at"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(), nullable=True),
        sa.Column("event_description", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_system_metrics_recorded_at", table_name="system_metrics")
    op.drop_table("system_metrics")

    op.drop_index("ix_licenses_license_key", table_name="licenses")
    op.drop_table("licenses")

    op.drop_index("ix_threats_detected_at", table_name="threats")
    op.drop_index("ix_threats_severity", table_name="threats")
    op.drop_index("ix_threats_threat_type", table_name="threats")
    op.drop_table("threats")

    op.drop_index("ix_users_api_key", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
