from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal

from domain.models import Operadora, DespesaTrimestral, MetricaOperadora


class OperadoraRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, operadora_id: int) -> Optional[Operadora]:
        result = await self.session.execute(
            select(Operadora).where(Operadora.id == operadora_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_registro_ans(self, registro_ans: str) -> Optional[Operadora]:
        result = await self.session.execute(
            select(Operadora).where(Operadora.registro_ans == registro_ans)
        )
        return result.scalar_one_or_none()
    
    async def get_by_cnpj(self, cnpj: str) -> Optional[Operadora]:
        clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        result = await self.session.execute(
            select(Operadora).where(Operadora.cnpj == clean_cnpj)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Operadora]:
        result = await self.session.execute(
            select(Operadora).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(Operadora.id)))
        return result.scalar_one()
    
    async def search(
        self, 
        search: Optional[str] = None,
        uf: Optional[str] = None,
        modalidade: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> list[Operadora]:
        query = select(Operadora)
        
        if search:
            # Busca por razão social ou CNPJ
            clean_search = search.replace(".", "").replace("/", "").replace("-", "")
            query = query.where(
                (Operadora.razao_social.ilike(f"%{search}%")) |
                (Operadora.cnpj.ilike(f"%{clean_search}%"))
            )
        if uf:
            query = query.where(Operadora.uf == uf)
        if modalidade:
            query = query.where(Operadora.modalidade == modalidade)
        if cursor:
            # Cursor format: "razao_social|registro_ans" for unique pagination
            parts = cursor.split('|')
            if len(parts) == 2:
                cursor_razao, cursor_reg = parts
                query = query.where(
                    (Operadora.razao_social > cursor_razao) |
                    ((Operadora.razao_social == cursor_razao) & (Operadora.registro_ans > cursor_reg))
                )
        
        # Ordenação com ID como tiebreaker para resultados determinísticos (importante para TiDB)
        query = query.order_by(Operadora.razao_social, Operadora.registro_ans, Operadora.id).limit(limit + 1)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def search_with_offset(
        self, 
        search: Optional[str] = None,
        uf: Optional[str] = None,
        modalidade: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> list[Operadora]:
        """Busca com paginação por offset (para saltos de página)"""
        query = select(Operadora)
        
        if search:
            clean_search = search.replace(".", "").replace("/", "").replace("-", "")
            query = query.where(
                (Operadora.razao_social.ilike(f"%{search}%")) |
                (Operadora.cnpj.ilike(f"%{clean_search}%"))
            )
        if uf:
            query = query.where(Operadora.uf == uf)
        if modalidade:
            query = query.where(Operadora.modalidade == modalidade)
        
        # Ordenação com ID como tiebreaker final para resultados determinísticos (importante para TiDB)
        query = query.order_by(Operadora.razao_social, Operadora.registro_ans, Operadora.id)
        query = query.offset(offset).limit(limit + 1)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_filtered(
        self,
        search: Optional[str] = None,
        uf: Optional[str] = None,
        modalidade: Optional[str] = None
    ) -> int:
        query = select(func.count(Operadora.id))
        
        if search:
            # Busca por razão social ou CNPJ
            clean_search = search.replace(".", "").replace("/", "").replace("-", "")
            query = query.where(
                (Operadora.razao_social.ilike(f"%{search}%")) |
                (Operadora.cnpj.ilike(f"%{clean_search}%"))
            )
        if uf:
            query = query.where(Operadora.uf == uf)
        if modalidade:
            query = query.where(Operadora.modalidade == modalidade)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def get_modalidades(self) -> list[str]:
        """Retorna lista de modalidades distintas"""
        result = await self.session.execute(
            select(Operadora.modalidade)
            .where(Operadora.modalidade.isnot(None))
            .where(Operadora.modalidade != '')
            .distinct()
            .order_by(Operadora.modalidade)
        )
        return [row[0] for row in result.all()]


class DespesaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_operadora(
        self, 
        registro_ans: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[DespesaTrimestral]:
        result = await self.session.execute(
            select(DespesaTrimestral)
            .where(DespesaTrimestral.registro_ans == registro_ans)
            .order_by(DespesaTrimestral.ano.desc(), DespesaTrimestral.trimestre.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_uf(
        self,
        uf: str,
        ano: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[DespesaTrimestral]:
        query = select(DespesaTrimestral).where(DespesaTrimestral.uf == uf)
        
        if ano:
            query = query.where(DespesaTrimestral.ano == ano)
        
        query = query.order_by(DespesaTrimestral.valor_despesas.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_total_by_uf(self) -> list[tuple[str, Decimal, int]]:
        result = await self.session.execute(
            select(
                DespesaTrimestral.uf,
                func.sum(DespesaTrimestral.valor_despesas).label('total'),
                func.count(func.distinct(DespesaTrimestral.razao_social)).label('operadoras')
            )
            .where(DespesaTrimestral.uf.isnot(None))
            .group_by(DespesaTrimestral.uf)
            .order_by(text('total DESC'))
        )
        return list(result.all())


class MetricaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_top_ranking(self, limit: int = 10) -> list[MetricaOperadora]:
        result = await self.session.execute(
            select(MetricaOperadora)
            .where(MetricaOperadora.ranking.isnot(None))
            .order_by(MetricaOperadora.ranking)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_uf(self, uf: str, limit: int = 100) -> list[MetricaOperadora]:
        result = await self.session.execute(
            select(MetricaOperadora)
            .where(MetricaOperadora.uf == uf)
            .order_by(MetricaOperadora.total_despesas.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_alta_variabilidade(self, limit: int = 50) -> list[MetricaOperadora]:
        result = await self.session.execute(
            select(MetricaOperadora)
            .where(MetricaOperadora.alta_variabilidade == True)
            .order_by(MetricaOperadora.total_despesas.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(MetricaOperadora.id)))
        return result.scalar_one()
