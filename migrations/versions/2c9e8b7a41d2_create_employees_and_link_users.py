"""create employee records and link user accounts

Revision ID: 2c9e8b7a41d2
Revises: fedbbbb63701
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2c9e8b7a41d2"
down_revision: Union[str, Sequence[str], None] = "fedbbbb63701"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False, server_default="Unassigned"),
        sa.Column("salary", sa.Integer(), nullable=False),
        sa.Column("employment_type", sa.String(length=50), nullable=False, server_default="Full-time"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="Active"),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_employees_id", "employees", ["id"], unique=False)
    op.create_index("ix_employees_email", "employees", ["email"], unique=True)

    # Existing values are stored as the strings "true" and "false".
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.String(length=10),
        type_=sa.Boolean(),
        existing_nullable=False,
        postgresql_using="is_active::boolean",
    )
    op.add_column("users", sa.Column("employee_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_employee_id", "users", ["employee_id"], unique=True)
    op.create_foreign_key(
        "fk_users_employee_id_employees",
        "users",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_employee_id_employees", "users", type_="foreignkey")
    op.drop_index("ix_users_employee_id", table_name="users")
    op.drop_column("users", "employee_id")
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        type_=sa.String(length=10),
        existing_nullable=False,
        postgresql_using="CASE WHEN is_active THEN 'true' ELSE 'false' END",
    )
    op.drop_index("ix_employees_email", table_name="employees")
    op.drop_index("ix_employees_id", table_name="employees")
    op.drop_table("employees")
