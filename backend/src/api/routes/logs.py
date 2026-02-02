from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("")
async def get_logs_summary():
    """Retorna resumo de todos os logs disponíveis"""
    logs = {
        "unmatched_operadoras": await get_unmatched_count(),
        "sem_despesas": await get_sem_despesas_count(),
    }
    return logs


@router.get("/unmatched")
async def get_unmatched_operadoras(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Operadoras sem match no cadastro ANS (placeholder).
    Busca do banco de dados operadoras com cadastro_incompleto=true ou CNPJ nulo.
    """
    from sqlalchemy import text
    from infra.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Conta total - operadoras placeholder (CNPJ nulo ou cadastro incompleto)
        count_query = text("""
            SELECT COUNT(DISTINCT o.registro_ans) 
            FROM operadoras o
            WHERE o.cnpj IS NULL OR o.cnpj = ''
        """)
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()
        
        # Busca dados paginados com agregação de despesas
        query = text("""
            SELECT 
                o.registro_ans,
                o.razao_social,
                o.uf,
                o.modalidade,
                COUNT(d.id) as quantidade_registros
            FROM operadoras o
            LEFT JOIN despesas_trimestrais d ON o.registro_ans = d.registro_ans
            WHERE o.cnpj IS NULL OR o.cnpj = ''
            GROUP BY o.registro_ans, o.razao_social, o.uf, o.modalidade
            ORDER BY o.razao_social
            LIMIT :limit OFFSET :offset
        """)
        result = await session.execute(query, {"limit": limit, "offset": offset})
        rows = result.fetchall()
        
        data = [
            {
                "registro_ans": row.registro_ans,
                "quantidade_registros": row.quantidade_registros or 0,
                "razao_social": row.razao_social,
                "uf": row.uf,
                "modalidade": row.modalidade,
                "tipo": "unmatched",
                "descricao": "Operadora não encontrada no cadastro ANS (placeholder)"
            }
            for row in rows
        ]
    
    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total,
        "has_prev": offset > 0
    }


@router.get("/sem-despesas")
async def get_operadoras_sem_despesas(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Operadoras cadastradas mas sem nenhum registro de despesa.
    """
    from sqlalchemy import text
    from infra.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Conta total - usando operadora_id que é a FK real
        count_query = text("""
            SELECT COUNT(*) FROM operadoras o
            LEFT JOIN despesas_trimestrais d ON o.id = d.operadora_id
            WHERE d.id IS NULL
        """)
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()
        
        # Busca dados paginados
        query = text("""
            SELECT o.id, o.registro_ans, o.razao_social, o.cnpj, o.uf, o.modalidade
            FROM operadoras o
            LEFT JOIN despesas_trimestrais d ON o.id = d.operadora_id
            WHERE d.id IS NULL
            ORDER BY o.razao_social
            LIMIT :limit OFFSET :offset
        """)
        result = await session.execute(query, {"limit": limit, "offset": offset})
        rows = result.fetchall()
        
        data = [
            {
                "id": row.id,
                "registro_ans": row.registro_ans,
                "razao_social": row.razao_social,
                "cnpj": row.cnpj,
                "uf": row.uf,
                "modalidade": row.modalidade,
                "tipo": "sem_despesas",
                "descricao": "Nenhum registro de despesa encontrado"
            }
            for row in rows
        ]
    
    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total,
        "has_prev": offset > 0
    }


async def get_unmatched_count() -> int:
    """Conta operadoras sem match (placeholder - CNPJ nulo)"""
    from sqlalchemy import text
    from infra.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        query = text("""
            SELECT COUNT(*) FROM operadoras 
            WHERE cnpj IS NULL OR cnpj = ''
        """)
        result = await session.execute(query)
        return result.scalar_one()


async def get_sem_despesas_count() -> int:
    """Conta operadoras sem despesas"""
    from sqlalchemy import text
    from infra.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        query = text("""
            SELECT COUNT(*) FROM operadoras o
            LEFT JOIN despesas_trimestrais d ON o.id = d.operadora_id
            WHERE d.id IS NULL
        """)
        result = await session.execute(query)
        return result.scalar_one()
