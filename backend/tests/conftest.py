"""
Configuração de fixtures para testes do backend.
"""
import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Importa primeiro o Base do database (sem trigger __init__)
from infra.database import Base

# Depois importa os models
from domain.models import Operadora, DespesaTrimestral, MetricaOperadora


# Fixture para event loop
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Fixture para banco de dados em memória
@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão de banco de dados SQLite em memória para testes."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# Fixture para mock de sessão
@pytest.fixture
def mock_session() -> AsyncMock:
    """Cria um mock de AsyncSession para testes unitários."""
    session = AsyncMock(spec=AsyncSession)
    return session


# Fixtures de dados de exemplo
@pytest.fixture
def sample_operadora() -> Operadora:
    """Operadora de exemplo para testes."""
    return Operadora(
        id=1,
        registro_ans="301337",
        cnpj="44988925000190",
        razao_social="UNIMED CAMPINAS COOPERATIVA DE TRABALHO MEDICO",
        modalidade="Cooperativa Médica",
        uf="SP",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_operadoras() -> list[Operadora]:
    """Lista de operadoras de exemplo para testes."""
    return [
        Operadora(
            id=1,
            registro_ans="301337",
            cnpj="44988925000190",
            razao_social="UNIMED CAMPINAS",
            modalidade="Cooperativa Médica",
            uf="SP",
        ),
        Operadora(
            id=2,
            registro_ans="326305",
            cnpj="92693118000160",
            razao_social="BRADESCO SAUDE S.A.",
            modalidade="Seguradora Especializada em Saúde",
            uf="SP",
        ),
        Operadora(
            id=3,
            registro_ans="005711",
            cnpj="86878469000120",
            razao_social="SUL AMERICA CIA DE SEGURO SAUDE",
            modalidade="Seguradora Especializada em Saúde",
            uf="RJ",
        ),
    ]


@pytest.fixture
def sample_despesas() -> list[DespesaTrimestral]:
    """Lista de despesas de exemplo para testes."""
    return [
        DespesaTrimestral(
            id=1,
            operadora_id=1,
            registro_ans="301337",
            razao_social="UNIMED CAMPINAS",
            uf="SP",
            ano=2025,
            trimestre=1,
            valor_despesas=Decimal("15000000.50"),
        ),
        DespesaTrimestral(
            id=2,
            operadora_id=1,
            registro_ans="301337",
            razao_social="UNIMED CAMPINAS",
            uf="SP",
            ano=2025,
            trimestre=2,
            valor_despesas=Decimal("16500000.75"),
        ),
        DespesaTrimestral(
            id=3,
            operadora_id=2,
            registro_ans="326305",
            razao_social="BRADESCO SAUDE",
            uf="SP",
            ano=2025,
            trimestre=1,
            valor_despesas=Decimal("5200000000.00"),
        ),
    ]
