"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-04

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
    )
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("location_text", sa.String(255), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "MANAGER", "WORKER", name="userrole"), nullable=False, server_default="WORKER"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "cages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("size_x", sa.Float(), nullable=True),
        sa.Column("size_y", sa.Float(), nullable=True),
        sa.Column("depth", sa.Float(), nullable=True),
        sa.Column("qr_token", sa.String(64), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cages_code", "cages", ["code"])
    op.create_index("ix_cages_qr_token", "cages", ["qr_token"])

    op.create_table(
        "lots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("species", sa.Enum("BURI", "KAMPACHI", name="species"), nullable=False),
        sa.Column("stage", sa.Enum("MOJAKO", "HAMACHI", "BURI", name="stage"), nullable=False),
        sa.Column("item_label", sa.String(50), nullable=False),
        sa.Column("origin_type", sa.Enum("WILD", "HATCHERY", "TRANSFER", name="origintype"), nullable=False, server_default="WILD"),
        sa.Column("received_date", sa.Date(), nullable=False),
        sa.Column("initial_count", sa.Integer(), nullable=False),
        sa.Column("initial_avg_weight_g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_table(
        "cage_lots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cage_id", sa.Integer(), sa.ForeignKey("cages.id"), nullable=False),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("start_count_est", sa.Integer(), nullable=False),
        sa.Column("end_count_est", sa.Integer(), nullable=True),
        sa.Column("start_avg_weight_g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("end_avg_weight_g", sa.Float(), nullable=True),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.Enum(
            "FEEDING", "MORTALITY", "SAMPLING", "TREATMENT", "ENVIRONMENT",
            "MOVE", "SPLIT", "MERGE", "HARVEST", "NOTE", name="eventtype"
        ), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cage_id", sa.Integer(), sa.ForeignKey("cages.id"), nullable=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_events_cage_id", "events", ["cage_id"])
    op.create_index("ix_events_lot_id", "events", ["lot_id"])

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "feed_rate_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("species", sa.Enum("BURI", "KAMPACHI", name="species"), nullable=False),
        sa.Column("stage", sa.Enum("MOJAKO", "HAMACHI", "BURI", name="stage"), nullable=False),
        sa.Column("temp_min", sa.Float(), nullable=False),
        sa.Column("temp_max", sa.Float(), nullable=False),
        sa.Column("feed_rate_pct_per_day", sa.Float(), nullable=False),
        sa.Column("note", sa.String(255), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cage_id", sa.Integer(), sa.ForeignKey("cages.id"), nullable=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("severity", sa.Enum("INFO", "WARNING", "CRITICAL", name="alertseverity"), nullable=False, server_default="WARNING"),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("status", sa.Enum("OPEN", "CLOSED", name="alertstatus"), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("feed_rate_rules")
    op.drop_table("attachments")
    op.drop_table("events")
    op.drop_table("cage_lots")
    op.drop_table("lots")
    op.drop_table("cages")
    op.drop_table("users")
    op.drop_table("sites")
    op.drop_table("farms")
    op.execute("DROP TYPE IF EXISTS alertstatus")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS origintype")
    op.execute("DROP TYPE IF EXISTS stage")
    op.execute("DROP TYPE IF EXISTS species")
    op.execute("DROP TYPE IF EXISTS userrole")
