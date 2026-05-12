"""Add custos_extras JSON field to contracts

Revision ID: 003
Revises: 002
Create Date: 2026-05-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # custos_extras: JSON array of {nome: string, valor: number}
    # Ex: [{"nome": "Taxa de administração", "valor": 50.00}]
    op.add_column(
        "contracts",
        sa.Column("custos_extras", sa.JSON, nullable=True, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("contracts", "custos_extras")
