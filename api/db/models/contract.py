import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Property(Base):
    """Imóvel — agrupa um ou mais contratos."""

    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    apelido: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class Contract(Base):
    """
    Financiamento imobiliário.
    Contém os campos necessários para o motor SAC/PRICE/Itaú.
    No MVP: preenchido manualmente pelo usuário (sem DDC parser).
    """

    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    apelido: Mapped[str | None] = mapped_column(String, nullable=True)
    banco: Mapped[str] = mapped_column(String, nullable=False)
    sistema_amortizacao: Mapped[str] = mapped_column(String, nullable=False)  # SAC | PRICE

    # Campos do motor
    taxa_mensal: Mapped[float] = mapped_column(Numeric(12, 10), nullable=False)
    saldo_devedor: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    amortizacao_mensal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    mip_mensal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")
    dfi_mensal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")
    data_proxima_parcela: Mapped[date] = mapped_column(Date, nullable=False)
    prazo_remanescente: Mapped[int] = mapped_column(Integer, nullable=False)

    # Campos opcionais (contexto histórico)
    valor_original: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    data_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=datetime.now
    )
