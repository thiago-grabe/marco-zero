"""MVP initial schema — 5 tables + RLS

Revision ID: 001
Revises:
Create Date: 2026-05-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_profiles ────────────────────────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── properties ───────────────────────────────────────────────────────────
    op.create_table(
        "properties",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("apelido", sa.String, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_properties_user_id", "properties", ["user_id"])

    # ── contracts ────────────────────────────────────────────────────────────
    op.create_table(
        "contracts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("apelido", sa.String, nullable=True),
        sa.Column("banco", sa.String, nullable=False),
        sa.Column("sistema_amortizacao", sa.String, nullable=False),
        sa.Column("taxa_mensal", sa.Numeric(12, 10), nullable=False),
        sa.Column("saldo_devedor", sa.Numeric(14, 2), nullable=False),
        sa.Column("amortizacao_mensal", sa.Numeric(14, 2), nullable=False),
        sa.Column("mip_mensal", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("dfi_mensal", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("data_proxima_parcela", sa.Date, nullable=False),
        sa.Column("prazo_remanescente", sa.Integer, nullable=False),
        sa.Column("valor_original", sa.Numeric(14, 2), nullable=True),
        sa.Column("data_inicio", sa.Date, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_contracts_user_id", "contracts", ["user_id"])

    # ── scenarios ────────────────────────────────────────────────────────────
    op.create_table(
        "scenarios",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="'planejado'"),
        sa.Column("aporte_mensal_extra", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("aporte_anual_extra", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("mes_aporte_anual", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_scenarios_user_id", "scenarios", ["user_id"])
    op.create_index("ix_scenarios_contract_id", "scenarios", ["contract_id"])

    # ── user_operations ──────────────────────────────────────────────────────
    op.create_table(
        "user_operations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.String, nullable=False),
        sa.Column("data_operacao", sa.Date, nullable=False),
        sa.Column("valor_principal", sa.Numeric(14, 2), nullable=False),
        sa.Column("notas", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_user_operations_user_id", "user_operations", ["user_id"])
    op.create_index("ix_user_operations_contract_id", "user_operations", ["contract_id"])

    # ── RLS — Row-Level Security ─────────────────────────────────────────────
    # Habilitar RLS em todas as tabelas de dados do usuário
    for table in ("user_profiles", "properties", "contracts", "scenarios", "user_operations"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # Políticas: usuário vê e modifica apenas seus próprios dados.
    # O user_id é injetado pelo middleware FastAPI via:
    #   SET LOCAL app.current_user_id = '<uuid>'
    # A função current_setting('app.current_user_id', true) retorna NULL
    # se não estiver definido — o que nega acesso, que é o comportamento correto.

    rls_tables = {
        "user_profiles": "id",        # a PK é o user_id
        "properties": "user_id",
        "contracts": "user_id",
        "scenarios": "user_id",
        "user_operations": "user_id",
    }

    for table, col in rls_tables.items():
        op.execute(f"""
            CREATE POLICY "{table}_user_isolation"
            ON {table}
            FOR ALL
            USING (
                {col} = current_setting('app.current_user_id', true)::uuid
            )
            WITH CHECK (
                {col} = current_setting('app.current_user_id', true)::uuid
            )
        """)


def downgrade() -> None:
    for table in ("user_operations", "scenarios", "contracts", "properties", "user_profiles"):
        op.execute(f'DROP POLICY IF EXISTS "{table}_user_isolation" ON {table}')
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.drop_table("user_operations")
    op.drop_table("scenarios")
    op.drop_table("contracts")
    op.drop_table("properties")
    op.drop_table("user_profiles")
