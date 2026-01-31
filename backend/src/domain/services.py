from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal
from datetime import datetime

from domain.schemas import TopOperadoraCrescimento, DespesaPorUF, OperadoraAcimaMedia, EstatisticasResponse


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_estatisticas_agregadas(self) -> EstatisticasResponse:
        query = text("""
            SELECT 
                (SELECT COUNT(DISTINCT registro_ans) FROM operadoras) AS total_operadoras,
                (SELECT COALESCE(SUM(valor_despesas), 0) FROM despesas_trimestrais) AS total_despesas,
                (SELECT COALESCE(AVG(valor_despesas), 0) FROM despesas_trimestrais WHERE valor_despesas > 0) AS media_geral
        """)
        result = await self.session.execute(query)
        row = result.fetchone()
        
        top_ufs_query = text("""
            SELECT uf, SUM(valor_despesas) AS total
            FROM despesas_trimestrais
            WHERE uf IS NOT NULL AND uf != ''
            GROUP BY uf
            ORDER BY total DESC
            LIMIT 5
        """)
        top_ufs_result = await self.session.execute(top_ufs_query)
        top_ufs = [{"uf": r.uf, "total": float(r.total)} for r in top_ufs_result.fetchall()]
        
        top_operadoras_query = text("""
            SELECT razao_social, cnpj, SUM(valor_despesas) AS total
            FROM despesas_trimestrais
            WHERE valor_despesas > 0
            GROUP BY razao_social, cnpj
            ORDER BY total DESC
            LIMIT 5
        """)
        top_operadoras_result = await self.session.execute(top_operadoras_query)
        top_operadoras = [
            {"razao_social": r.razao_social, "cnpj": r.cnpj, "total": float(r.total)} 
            for r in top_operadoras_result.fetchall()
        ]
        
        return EstatisticasResponse(
            total_operadoras=row.total_operadoras or 0,
            total_despesas=float(row.total_despesas or 0),
            media_geral=float(row.media_geral or 0),
            top_ufs=top_ufs,
            top_operadoras=top_operadoras,
            updated_at=datetime.utcnow()
        )
    
    async def get_top_crescimento(self, limit: int = 5) -> list[TopOperadoraCrescimento]:
        query = text("""
            WITH periodo_range AS (
                SELECT 
                    MIN(CONCAT(ano, LPAD(trimestre, 2, '0'))) AS primeiro_periodo,
                    MAX(CONCAT(ano, LPAD(trimestre, 2, '0'))) AS ultimo_periodo
                FROM despesas_trimestrais
            ),
            despesas_primeira AS (
                SELECT registro_ans, razao_social, uf, ano, trimestre, valor_despesas AS valor_inicial
                FROM despesas_trimestrais d
                INNER JOIN periodo_range p ON CONCAT(d.ano, LPAD(d.trimestre, 2, '0')) = p.primeiro_periodo
                WHERE valor_despesas > 0
            ),
            despesas_ultima AS (
                SELECT registro_ans, razao_social, uf, ano, trimestre, valor_despesas AS valor_final
                FROM despesas_trimestrais d
                INNER JOIN periodo_range p ON CONCAT(d.ano, LPAD(d.trimestre, 2, '0')) = p.ultimo_periodo
                WHERE valor_despesas > 0
            )
            SELECT 
                dp.registro_ans,
                dp.razao_social,
                dp.uf,
                CONCAT(dp.ano, 'T', dp.trimestre) AS periodo_inicial,
                CONCAT(du.ano, 'T', du.trimestre) AS periodo_final,
                dp.valor_inicial,
                du.valor_final,
                ROUND(((du.valor_final - dp.valor_inicial) / dp.valor_inicial) * 100, 2) AS crescimento_percentual
            FROM despesas_primeira dp
            INNER JOIN despesas_ultima du ON dp.registro_ans = du.registro_ans AND dp.uf = du.uf
            WHERE dp.valor_inicial > 0 AND du.valor_final > 0
            ORDER BY crescimento_percentual DESC
            LIMIT :limit
        """)
        
        result = await self.session.execute(query, {"limit": limit})
        rows = result.fetchall()
        
        return [
            TopOperadoraCrescimento(
                registro_ans=row.registro_ans,
                razao_social=row.razao_social,
                uf=row.uf,
                periodo_inicial=row.periodo_inicial,
                periodo_final=row.periodo_final,
                valor_inicial=Decimal(str(row.valor_inicial)),
                valor_final=Decimal(str(row.valor_final)),
                crescimento_percentual=Decimal(str(row.crescimento_percentual))
            )
            for row in rows
        ]
    
    async def get_despesas_por_uf(self, limit: int = 5) -> list[DespesaPorUF]:
        query = text("""
            WITH despesas_uf AS (
                SELECT 
                    uf,
                    SUM(valor_despesas) AS total_despesas,
                    COUNT(DISTINCT razao_social) AS total_operadoras
                FROM despesas_trimestrais
                WHERE uf IS NOT NULL AND valor_despesas > 0
                GROUP BY uf
            ),
            total_geral AS (
                SELECT SUM(total_despesas) AS total FROM despesas_uf
            )
            SELECT 
                d.uf,
                d.total_despesas,
                d.total_operadoras,
                ROUND(d.total_despesas / d.total_operadoras, 2) AS media_despesas_por_operadora,
                ROUND((d.total_despesas / t.total) * 100, 2) AS percentual_total
            FROM despesas_uf d, total_geral t
            ORDER BY d.total_despesas DESC
            LIMIT :limit
        """)
        
        result = await self.session.execute(query, {"limit": limit})
        rows = result.fetchall()
        
        return [
            DespesaPorUF(
                uf=row.uf,
                total_despesas=Decimal(str(row.total_despesas)),
                total_operadoras=row.total_operadoras,
                media_despesas_por_operadora=Decimal(str(row.media_despesas_por_operadora)),
                percentual_total=Decimal(str(row.percentual_total))
            )
            for row in rows
        ]
    
    async def get_operadoras_acima_media(self, min_trimestres: int = 2) -> tuple[int, list[OperadoraAcimaMedia]]:
        query = text("""
            WITH media_por_trimestre AS (
                SELECT ano, trimestre, AVG(valor_despesas) AS media_geral
                FROM despesas_trimestrais
                WHERE valor_despesas > 0
                GROUP BY ano, trimestre
            ),
            operadoras_acima AS (
                SELECT 
                    d.registro_ans,
                    d.razao_social,
                    d.uf,
                    SUM(CASE WHEN d.valor_despesas > m.media_geral THEN 1 ELSE 0 END) AS trimestres_acima,
                    GROUP_CONCAT(
                        DISTINCT CONCAT(d.ano, 'T', d.trimestre) 
                        ORDER BY d.ano, d.trimestre 
                        SEPARATOR ', '
                    ) AS periodos
                FROM despesas_trimestrais d
                INNER JOIN media_por_trimestre m ON d.ano = m.ano AND d.trimestre = m.trimestre
                WHERE d.valor_despesas > 0
                GROUP BY d.registro_ans, d.razao_social, d.uf
                HAVING trimestres_acima >= :min_trimestres
            )
            SELECT * FROM operadoras_acima
            ORDER BY trimestres_acima DESC, razao_social
            LIMIT 50
        """)
        
        result = await self.session.execute(query, {"min_trimestres": min_trimestres})
        rows = result.fetchall()
        
        count_query = text("""
            SELECT COUNT(*) FROM (
                SELECT d.registro_ans
                FROM despesas_trimestrais d
                INNER JOIN (
                    SELECT ano, trimestre, AVG(valor_despesas) AS media_geral
                    FROM despesas_trimestrais WHERE valor_despesas > 0
                    GROUP BY ano, trimestre
                ) m ON d.ano = m.ano AND d.trimestre = m.trimestre
                WHERE d.valor_despesas > 0
                GROUP BY d.registro_ans, d.uf
                HAVING SUM(CASE WHEN d.valor_despesas > m.media_geral THEN 1 ELSE 0 END) >= :min_trimestres
            ) AS subquery
        """)
        
        count_result = await self.session.execute(count_query, {"min_trimestres": min_trimestres})
        total = count_result.scalar_one()
        
        operadoras = [
            OperadoraAcimaMedia(
                registro_ans=row.registro_ans,
                razao_social=row.razao_social,
                uf=row.uf,
                trimestres_acima_media=row.trimestres_acima,
                periodos=row.periodos
            )
            for row in rows
        ]
        
        return total, operadoras
