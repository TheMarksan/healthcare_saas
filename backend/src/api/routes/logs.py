from fastapi import APIRouter, Query
from pathlib import Path
import csv
from typing import Optional

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data_pipeline" / "data"


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
    Operadoras sem match no cadastro ANS.
    Foram criadas como placeholder durante a importação.
    """
    csv_path = DATA_DIR / "trimestrais_contabeis" / "logs" / "unmatched_reg_ans.csv"
    
    if not csv_path.exists():
        return {"data": [], "total": 0, "message": "Arquivo de log não encontrado"}
    
    data = []
    total = 0
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total = len(rows)
        
        for row in rows[offset:offset + limit]:
            data.append({
                "registro_ans": row.get("RegistroANS", ""),
                "quantidade_registros": int(row.get("QuantidadeRegistros", 0)),
                "razao_social": row.get("RazaoSocialPlaceholder", ""),
                "tipo": "unmatched",
                "descricao": "Operadora não encontrada no cadastro ANS"
            })
    
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
    """Conta operadoras sem match"""
    csv_path = DATA_DIR / "trimestrais_contabeis" / "logs" / "unmatched_reg_ans.csv"
    if not csv_path.exists():
        return 0
    with open(csv_path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1  # -1 para o header


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
