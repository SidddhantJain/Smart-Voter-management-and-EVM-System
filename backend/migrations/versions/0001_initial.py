"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-22 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voters",
        sa.Column("voter_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("constituency", sa.String(length=120), nullable=True),
    )
    op.create_table(
        "constituencies",
        sa.Column("constituency_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
    )
    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.String(length=128), primary_key=True, nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("kind", sa.String(length=80), nullable=False),
    )
    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("target", sa.String(length=128), nullable=False),
        sa.Column("relation", sa.String(length=120), nullable=False),
    )
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("graph_edges")
    op.drop_table("graph_nodes")
    op.drop_table("constituencies")
    op.drop_table("voters")
