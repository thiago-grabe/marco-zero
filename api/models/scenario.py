import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    aporte_mensal_extra: float = Field(ge=0, default=0)
    aporte_anual_extra: float = Field(ge=0, default=0)
    mes_aporte_anual: Optional[int] = Field(default=None, ge=1, le=12)


class ScenarioUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=80)
    aporte_mensal_extra: Optional[float] = Field(default=None, ge=0)
    aporte_anual_extra: Optional[float] = Field(default=None, ge=0)
    mes_aporte_anual: Optional[int] = Field(default=None, ge=1, le=12)
    status: Optional[str] = Field(
        default=None,
        pattern="^(planejado|em_execucao|concluido|abandonado)$",
    )


class ScenarioResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    nome: str
    status: str
    aporte_mensal_extra: float
    aporte_anual_extra: float
    mes_aporte_anual: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
