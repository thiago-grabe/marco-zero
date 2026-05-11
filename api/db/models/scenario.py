import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Scenario(Base):
    """
    Parâmetros de um cenário de amortização.
    Resultados NÃO são persistidos — calculados em runtime pelo motor.
    """

    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    contract_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    nome: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="'planejado'")

    # Parâmetros de aporte
    aporte_mensal_extra: Mapped[float] = mapped_column(
        Numeric(14, 2), nullable=False, server_default="0"
    )
    aporte_anual_extra: Mapped[float] = mapped_column(
        Numeric(14, 2), nullable=False, server_default="0"
    )
    mes_aporte_anual: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=datetime.now
    )
