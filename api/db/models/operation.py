import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserOperation(Base):
    """
    Amortizações e outros eventos declarados pelo usuário.
    Entidade de primeira classe — não derivada do DDC.
    """

    __tablename__ = "user_operations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    contract_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    tipo: Mapped[str] = mapped_column(String, nullable=False)  # amortizacao_prazo | amortizacao_parcela
    data_operacao: Mapped[date] = mapped_column(Date, nullable=False)
    valor_principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    notas: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
