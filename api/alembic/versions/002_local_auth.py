"""Add local auth fields (email + password_hash) to user_profiles

Revision ID: 002
Revises: 001
Create Date: 2026-05-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("email", sa.String, nullable=True, unique=True))
    op.add_column("user_profiles", sa.Column("password_hash", sa.String, nullable=True))
    op.create_index("ix_user_profiles_email", "user_profiles", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_profiles_email", "user_profiles")
    op.drop_column("user_profiles", "password_hash")
    op.drop_column("user_profiles", "email")
