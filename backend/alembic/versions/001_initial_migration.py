"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "instagram_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instagram_user_id", sa.String(100), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("profile_picture_url", sa.String(500)),
        sa.Column("access_token", sa.String(1000), nullable=False),
        sa.Column("token_expires_at", sa.DateTime),
        sa.Column("page_id", sa.String(100)),
        sa.Column("page_name", sa.String(255)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_instagram_accounts_user_id", "instagram_accounts", ["user_id"])
    op.create_index("ix_instagram_accounts_instagram_user_id", "instagram_accounts", ["instagram_user_id"])

    op.create_table(
        "automations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instagram_account_id", UUID(as_uuid=True), sa.ForeignKey("instagram_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("trigger_type", sa.String(50), nullable=False),
        sa.Column("trigger_keyword", sa.String(255), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("response_message", sa.Text, nullable=False),
        sa.Column("response_link", sa.String(1000)),
        sa.Column("require_follow", sa.Boolean, default=False),
        sa.Column("follow_required_message", sa.Text),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_index("ix_automations_user_id", "automations", ["user_id"])

    op.create_table(
        "automation_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("automation_id", UUID(as_uuid=True), sa.ForeignKey("automations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trigger_type", sa.String(50)),
        sa.Column("trigger_keyword", sa.String(255)),
        sa.Column("sender_instagram_id", sa.String(100)),
        sa.Column("sender_username", sa.String(100)),
        sa.Column("action_taken", sa.String(100)),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_automation_logs_user_id", "automation_logs", ["user_id"])
    op.create_index("ix_automation_logs_created_at", "automation_logs", ["created_at"])

    op.create_table(
        "webhook_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("raw_payload", JSONB, nullable=False),
        sa.Column("processed", sa.Boolean, default=False),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "uploaded_files",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_url", sa.String(1000), nullable=False),
        sa.Column("file_size", sa.Integer),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("bucket_path", sa.String(1000)),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("uploaded_files")
    op.drop_table("webhook_events")
    op.drop_table("automation_logs")
    op.drop_table("automations")
    op.drop_table("instagram_accounts")
    op.drop_table("users")
