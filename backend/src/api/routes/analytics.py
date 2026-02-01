from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from infra.database import get_db
from infra.repositories import MetricaRepository
from domain.services import AnalyticsService
from domain.schemas import (
    MetricaOperadoraResponse,
    TopOperadoraCrescimento,
    DespesaPorUF,
    OperadoraAcimaMedia,
    EstatisticasResponse
)
from core.cache import cache

router = APIRouter()

CACHE_KEY_ESTATISTICAS = "estatisticas_agregadas"


@router.get("", response_model=EstatisticasResponse)
async def get_estatisticas(
    uf: str = Query(None, description="Filtrar por UF"),
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"{CACHE_KEY_ESTATISTICAS}_{uf or 'all'}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    service = AnalyticsService(db)
    result = await service.get_estatisticas_agregadas(uf=uf)
    cache.set(cache_key, result, ttl=300)
    return result


@router.get("/top-ranking", response_model=list[MetricaOperadoraResponse])
async def get_top_ranking(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = MetricaRepository(db)
    metricas = await repo.get_top_ranking(limit=limit)
    return [MetricaOperadoraResponse.model_validate(m) for m in metricas]


@router.get("/alta-variabilidade", response_model=list[MetricaOperadoraResponse])
async def get_alta_variabilidade(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    repo = MetricaRepository(db)
    metricas = await repo.get_alta_variabilidade(limit=limit)
    return [MetricaOperadoraResponse.model_validate(m) for m in metricas]


@router.get("/crescimento", response_model=list[TopOperadoraCrescimento])
async def get_top_crescimento(
    limit: int = Query(5, ge=1, le=20),
    uf: str = Query(None, description="Filtrar por UF"),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_top_crescimento(limit=limit, uf=uf)


@router.get("/despesas-por-uf", response_model=list[DespesaPorUF])
async def get_despesas_por_uf(
    limit: int = Query(5, ge=1, le=27),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_despesas_por_uf(limit=limit)


@router.get("/acima-media")
async def get_operadoras_acima_media(
    min_trimestres: int = Query(2, ge=1, le=4),
    uf: str = Query(None, description="Filtrar por UF"),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    total, operadoras = await service.get_operadoras_acima_media(min_trimestres=min_trimestres, uf=uf)
    
    return {
        "total_operadoras": total,
        "operadoras": [op.model_dump() for op in operadoras]
    }
