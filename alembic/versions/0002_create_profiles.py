"""create profiles table

Revision ID: 0002_create_profiles
Revises: 0001_create_users
Create Date: 2026-08-05
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_create_profiles"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


occupation = postgresql.ENUM(
    "private_sector",
    "government",
    "unemployed",
    "farmer",
    "student",
    "other",
    name="occupation",
    create_type=False,
)
salary_range = postgresql.ENUM(
    "below_10k",
    "10k_to_25k",
    "25k_to_50k",
    "50k_to_100k",
    "above_100k",
    name="salary_range",
    create_type=False,
)


def upgrade() -> None:
    occupation.create(op.get_bind(), checkfirst=True)
    salary_range.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("occupation", occupation, nullable=False),
        sa.Column("salary_range", salary_range, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_profiles_user_id"), "profiles", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_profiles_user_id"), table_name="profiles")
    op.drop_table("profiles")
    salary_range.drop(op.get_bind(), checkfirst=True)
    occupation.drop(op.get_bind(), checkfirst=True)
