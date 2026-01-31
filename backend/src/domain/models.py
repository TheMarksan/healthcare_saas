from sqlalchemy import (
    Column, BigInteger, Integer, SmallInteger, String, Boolean, 
    DECIMAL, DateTime, Text, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from infra.database import Base


class ImportType(str, Enum):
    OPERADORAS = 'operadoras'
    DESPESAS = 'despesas'
    METRICAS = 'metricas'


class ImportStatus(str, Enum):
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    registro_ans = Column(String(10), unique=True, nullable=False, index=True)
    cnpj = Column(String(18), index=True)
    razao_social = Column(String(255), nullable=False)
    modalidade = Column(String(100))
    uf = Column(String(2), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    despesas = relationship("DespesaTrimestral", back_populates="operadora")
    metricas = relationship("MetricaOperadora", back_populates="operadora")
    
    __table_args__ = (
        Index('idx_uf_modalidade', 'uf', 'modalidade'),
    )


class DespesaTrimestral(Base):
    __tablename__ = "despesas_trimestrais"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    operadora_id = Column(BigInteger, ForeignKey('operadoras.id', ondelete='SET NULL'))
    registro_ans = Column(String(10), nullable=False, index=True)
    cnpj = Column(String(18))
    razao_social = Column(String(255), nullable=False)
    uf = Column(String(2))
    modalidade = Column(String(100))
    ano = Column(SmallInteger, nullable=False)
    trimestre = Column(SmallInteger, nullable=False)
    valor_despesas = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    cadastro_incompleto = Column(Boolean, default=False)
    cnpj_conflict = Column(Boolean, default=False)
    cnpj_invalido = Column(Boolean, default=False)
    razao_social_ausente = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    operadora = relationship("Operadora", back_populates="despesas")
    
    __table_args__ = (
        Index('idx_operadora_periodo', 'operadora_id', 'ano', 'trimestre'),
        Index('idx_ano_trimestre', 'ano', 'trimestre'),
        Index('idx_uf_ano_trimestre', 'uf', 'ano', 'trimestre'),
    )


class MetricaOperadora(Base):
    __tablename__ = "metricas_operadoras"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    operadora_id = Column(BigInteger, ForeignKey('operadoras.id', ondelete='SET NULL'))
    registro_ans = Column(String(10))
    cnpj = Column(String(18))
    razao_social = Column(String(255), nullable=False)
    uf = Column(String(2))
    modalidade = Column(String(100))
    ranking = Column(Integer)
    total_despesas = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    media_trimestral = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    desvio_padrao = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    coeficiente_variacao = Column(DECIMAL(10, 6), nullable=False, default=0.00)
    alta_variabilidade = Column(Boolean, default=False)
    quantidade_trimestres = Column(Integer, nullable=False, default=0)
    cadastro_incompleto = Column(Boolean, default=False)
    cnpj_conflict = Column(Boolean, default=False)
    razao_social_ausente = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    operadora = relationship("Operadora", back_populates="metricas")
    
    __table_args__ = (
        Index('idx_ranking', 'ranking'),
        Index('idx_total_despesas_metricas', 'total_despesas'),
        Index('idx_uf_metricas', 'uf'),
    )


class ImportReject(Base):
    __tablename__ = "import_rejects"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    import_type = Column(SQLEnum(ImportType), nullable=False)
    line_number = Column(Integer)
    raw_data = Column(Text)
    error_type = Column(String(100))
    error_message = Column(Text)
    field_name = Column(String(100))
    field_value = Column(Text)
    rejected_at = Column(DateTime, server_default=func.now())


class ImportLog(Base):
    __tablename__ = "import_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    import_type = Column(String(50), nullable=False)
    file_name = Column(String(255))
    total_lines = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    reject_count = Column(Integer, default=0)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)
    status = Column(SQLEnum(ImportStatus), default=ImportStatus.RUNNING)
    error_summary = Column(Text)