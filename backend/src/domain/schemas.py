from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OperadoraBase(BaseModel):
    registro_ans: str = Field(..., max_length=10)
    cnpj: Optional[str] = Field(None, max_length=18)
    razao_social: str = Field(..., max_length=255)
    modalidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)


class OperadoraCreate(OperadoraBase):
    pass


class OperadoraResponse(OperadoraBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DespesaTrimestralBase(BaseModel):
    registro_ans: str
    razao_social: str
    uf: Optional[str] = None
    ano: int = Field(..., ge=2020, le=2030)
    trimestre: int = Field(..., ge=1, le=4)
    valor_despesas: Decimal = Field(default=Decimal("0.00"))


class DespesaTrimestralCreate(DespesaTrimestralBase):
    cnpj: Optional[str] = None
    modalidade: Optional[str] = None


class DespesaTrimestralResponse(DespesaTrimestralBase):
    id: int
    operadora_id: Optional[int] = None
    cnpj: Optional[str] = None
    modalidade: Optional[str] = None
    cadastro_incompleto: bool = False
    cnpj_conflict: bool = False
    cnpj_invalido: bool = False
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MetricaOperadoraBase(BaseModel):
    razao_social: str
    uf: Optional[str] = None
    total_despesas: Decimal
    media_trimestral: Decimal
    quantidade_trimestres: int


class MetricaOperadoraResponse(MetricaOperadoraBase):
    id: int
    operadora_id: Optional[int] = None
    registro_ans: Optional[str] = None
    cnpj: Optional[str] = None
    modalidade: Optional[str] = None
    ranking: Optional[int] = None
    desvio_padrao: Decimal
    coeficiente_variacao: Decimal
    alta_variabilidade: bool = False
    cadastro_incompleto: bool = False
    cnpj_conflict: bool = False
    razao_social_ausente: bool = False
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TopOperadoraCrescimento(BaseModel):
    registro_ans: str
    razao_social: str
    uf: Optional[str] = None
    periodo_inicial: str
    periodo_final: str
    valor_inicial: Decimal
    valor_final: Decimal
    crescimento_percentual: Decimal


class DespesaPorUF(BaseModel):
    uf: str
    total_despesas: Decimal
    total_operadoras: int
    media_despesas_por_operadora: Decimal
    percentual_total: Decimal


class OperadoraAcimaMedia(BaseModel):
    registro_ans: str
    razao_social: str
    uf: Optional[str] = None
    trimestres_acima_media: int
    periodos: str


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int


class OperadoraListResponse(BaseModel):
    data: List[OperadoraResponse]
    total: int
    page: int
    limit: int
    next_cursor: Optional[str] = None
    has_next: bool
    has_prev: bool


class EstatisticasResponse(BaseModel):
    total_operadoras: int
    total_despesas: float
    media_geral: float
    top_ufs: List[dict]
    top_operadoras: List[dict]
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OperadoraFilter(BaseModel):
    search: Optional[str] = None
    uf: Optional[str] = None
    min_despesas: Optional[float] = None
    max_despesas: Optional[float] = None
    has_cadastro: Optional[bool] = None