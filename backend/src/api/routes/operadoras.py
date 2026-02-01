from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from infra.database import get_db
from infra.repositories import OperadoraRepository, DespesaRepository
from domain.schemas import (
    OperadoraResponse,
    DespesaTrimestralResponse,
    OperadoraListResponse,
    DespesaListResponse
)

router = APIRouter()


@router.get("", response_model=OperadoraListResponse)
async def list_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="razao_social|registro_ans cursor para keyset pagination"),
    search: Optional[str] = None,
    uf: Optional[str] = None,
    modalidade: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    repo = OperadoraRepository(db)
    
    operadoras = await repo.search(
        razao_social=search,
        uf=uf,
        modalidade=modalidade,
        cursor=cursor,
        limit=limit
    )
    
    has_next = len(operadoras) > limit
    if has_next:
        operadoras = operadoras[:limit]
    
    total = await repo.count_filtered(razao_social=search, uf=uf, modalidade=modalidade)
    # Cursor composto: razao_social|registro_ans para ordenação única
    next_cursor = f"{operadoras[-1].razao_social}|{operadoras[-1].registro_ans}" if has_next and operadoras else None
    
    return OperadoraListResponse(
        data=[OperadoraResponse.model_validate(op) for op in operadoras],
        total=total,
        page=page,
        limit=limit,
        next_cursor=next_cursor,
        has_next=has_next,
        has_prev=cursor is not None
    )


@router.get("/registro/{registro_ans}")
async def get_operadora_by_registro(
    registro_ans: str,
    db: AsyncSession = Depends(get_db)
):
    """Busca operadora pelo registro ANS com histórico de despesas"""
    repo = OperadoraRepository(db)
    operadora = await repo.get_by_registro_ans(registro_ans)
    
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    
    # Buscar despesas da operadora
    despesa_repo = DespesaRepository(db)
    despesas = await despesa_repo.get_by_operadora(registro_ans, limit=20)
    
    # Calcular total e média
    total_despesas = sum(float(d.valor_despesas) for d in despesas)
    media_despesas = total_despesas / len(despesas) if despesas else 0
    
    return {
        "operadora": OperadoraResponse.model_validate(operadora),
        "despesas": [DespesaTrimestralResponse.model_validate(d) for d in despesas],
        "total_despesas": total_despesas,
        "media_despesas": media_despesas
    }


@router.get("/{cnpj}", response_model=OperadoraResponse)
async def get_operadora(
    cnpj: str,
    db: AsyncSession = Depends(get_db)
):
    repo = OperadoraRepository(db)
    operadora = await repo.get_by_cnpj(cnpj)
    
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    
    return OperadoraResponse.model_validate(operadora)


@router.get("/{cnpj}/despesas", response_model=DespesaListResponse)
async def get_despesas_operadora(
    cnpj: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = DespesaRepository(db)
    skip = (page - 1) * limit
    
    despesas = await repo.get_by_cnpj(cnpj, skip=skip, limit=limit)
    total = await repo.count_by_cnpj(cnpj)
    
    return DespesaListResponse(
        data=[DespesaTrimestralResponse.model_validate(d) for d in despesas],
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
        has_prev=page > 1
    )