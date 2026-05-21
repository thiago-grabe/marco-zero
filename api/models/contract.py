import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class CustoExtra(BaseModel):
    """Custo extra não mapeado — cadastrado pelo usuário."""
    nome: str = Field(min_length=1, max_length=100)
    valor: float = Field(gt=0)


class PropertyCreate(BaseModel):
    apelido: str = "Meu Imóvel"


class ContractCreate(BaseModel):
    """Payload do onboarding — cria imóvel + contrato num único request."""

    property_apelido: str = Field(default="Apartamento")
    apelido: Optional[str] = None

    banco: str = Field(min_length=1)
    sistema_amortizacao: str = Field(pattern="^(SAC|PRICE)$")

    taxa_mensal: float = Field(gt=0.002, lt=0.02,
                                description="Ex: 0.009631 (0,9631% a.m.)")
    saldo_devedor: float = Field(gt=0)
    amortizacao_mensal: float = Field(gt=0)
    mip_mensal: float = Field(ge=0, default=0)
    dfi_mensal: float = Field(ge=0, default=0)
    data_proxima_parcela: date
    prazo_remanescente: int = Field(gt=0, lt=600)

    custos_extras: list[CustoExtra] = Field(default_factory=list)

    valor_original: Optional[float] = Field(default=None, gt=0)
    data_inicio: Optional[date] = None

    @model_validator(mode="after")
    def amort_menor_que_saldo(self) -> "ContractCreate":
        if self.amortizacao_mensal >= self.saldo_devedor:
            raise ValueError("amortizacao_mensal deve ser menor que saldo_devedor")
        return self


class ContractUpdate(BaseModel):
    apelido: Optional[str] = None
    saldo_devedor: Optional[float] = Field(default=None, gt=0)
    amortizacao_mensal: Optional[float] = Field(default=None, gt=0)
    mip_mensal: Optional[float] = Field(default=None, ge=0)
    dfi_mensal: Optional[float] = Field(default=None, ge=0)
    data_proxima_parcela: Optional[date] = None
    prazo_remanescente: Optional[int] = Field(default=None, gt=0)
    custos_extras: Optional[list[CustoExtra]] = None


class ContractResponse(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    apelido: Optional[str]
    banco: str
    sistema_amortizacao: str

    taxa_mensal: float
    taxa_anual_efetiva: float
    saldo_devedor: float
    amortizacao_mensal: float
    mip_mensal: float
    dfi_mensal: float
    seguros_mensal: float
    custos_extras: list[CustoExtra]
    custos_extras_total: float
    parcela_total: float
    juros_proxima: float

    data_proxima_parcela: date
    prazo_remanescente: int
    data_quitacao: date

    valor_original: Optional[float]
    data_inicio: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}


class QuickContractCreate(BaseModel):
    """Caminho de massa: 3 campos obrigatórios + taxa opcional."""
    parcela_mensal: float = Field(gt=0)
    banco: str = Field(min_length=1)
    saldo_devedor: float = Field(gt=0)
    taxa_mensal: Optional[float] = Field(default=None, gt=0.001, lt=0.03,
                                          description="Taxa mensal em decimal (ex: 0.009631). Se não informada, é estimada.")


class QuickContractResponse(ContractResponse):
    """Resposta do quick com lista de campos estimados."""
    campos_estimados: list[str] = []


class OperationCreate(BaseModel):
    tipo: str = Field(pattern="^(amortizacao_prazo|amortizacao_parcela)$")
    data_operacao: date
    valor_principal: float = Field(gt=0)
    notas: Optional[str] = None


class OperationResponse(BaseModel):
    id: uuid.UUID
    tipo: str
    data_operacao: date
    valor_principal: float
    notas: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
