"""add user role

Revision ID: e7b0b013f9db
Revises: 108b44256ce2
Create Date: 2025-07-02 20:11:49.212660

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = "e7b0b013f9db"
down_revision: Union[str, None] = "108b44256ce2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    user_role_enum = sa.Enum("maintainer", "member", name="user_role_enum")
    user_role_enum.create(op.get_bind())

    # 2. Neue Spalte mit Enum-Typ hinzufügen
    op.add_column(
        "users",
        sa.Column(
            "role", user_role_enum, nullable=False, server_default="member"
        ),
    )


def downgrade():
    # 1. Spalte löschen
    op.drop_column("users", "role")

    # 2. Enum-Typ aus PostgreSQL löschen
    user_role_enum = sa.Enum("maintainer", "member", name="user_role_enum")
    user_role_enum.drop(op.get_bind())
