import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserProfile(Base):
    """
    Extensão da identidade do Supabase Auth.
    Criada automaticamente no primeiro login via /auth/me.
    O `id` é o mesmo UUID do auth.users do Supabase (extraído do JWT).
    """

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    nome: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
