"""
Testes unitários para os repositórios.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from infra.repositories import OperadoraRepository, DespesaRepository
from domain.models import Operadora, DespesaTrimestral


class TestOperadoraRepository:
    """Testes para OperadoraRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_session, sample_operadora):
        """Deve retornar operadora quando encontrada por ID."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_operadora
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.get_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.registro_ans == "301337"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_session):
        """Deve retornar None quando operadora não encontrada."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.get_by_id(999)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_registro_ans(self, mock_session, sample_operadora):
        """Deve retornar operadora quando encontrada por registro ANS."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_operadora
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.get_by_registro_ans("301337")
        
        # Assert
        assert result is not None
        assert result.registro_ans == "301337"

    @pytest.mark.asyncio
    async def test_get_by_cnpj_cleans_formatting(self, mock_session, sample_operadora):
        """Deve limpar formatação do CNPJ antes de buscar."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_operadora
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act - CNPJ com formatação
        result = await repo.get_by_cnpj("44.988.925/0001-90")
        
        # Assert
        assert result is not None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count(self, mock_session):
        """Deve retornar contagem total de operadoras."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1250
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.count()
        
        # Assert
        assert result == 1250

    @pytest.mark.asyncio
    async def test_search_by_razao_social(self, mock_session, sample_operadoras):
        """Deve buscar operadoras por razão social."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_operadoras[0]]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.search(search="UNIMED")
        
        # Assert
        assert len(result) == 1
        assert result[0].razao_social == "UNIMED CAMPINAS"

    @pytest.mark.asyncio
    async def test_search_by_cnpj(self, mock_session, sample_operadoras):
        """Deve buscar operadoras por CNPJ."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_operadoras[0]]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act - CNPJ com formatação deve funcionar
        result = await repo.search(search="44.988.925/0001-90")
        
        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_with_uf_filter(self, mock_session, sample_operadoras):
        """Deve filtrar operadoras por UF."""
        # Arrange
        sp_operadoras = [op for op in sample_operadoras if op.uf == "SP"]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = sp_operadoras
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.search(uf="SP")
        
        # Assert
        assert len(result) == 2
        assert all(op.uf == "SP" for op in result)

    @pytest.mark.asyncio
    async def test_search_with_modalidade_filter(self, mock_session, sample_operadoras):
        """Deve filtrar operadoras por modalidade."""
        # Arrange
        seguradoras = [op for op in sample_operadoras if op.modalidade == "Seguradora Especializada em Saúde"]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = seguradoras
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.search(modalidade="Seguradora Especializada em Saúde")
        
        # Assert
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_with_cursor_pagination(self, mock_session, sample_operadoras):
        """Deve aplicar cursor para paginação keyset."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = sample_operadoras[1:]  # Após o cursor
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act - Cursor no formato "razao_social|registro_ans"
        result = await repo.search(cursor="BRADESCO SAUDE S.A.|326305")
        
        # Assert
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_filtered(self, mock_session):
        """Deve contar operadoras com filtros aplicados."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 35
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.count_filtered(search="UNIMED", uf="SP")
        
        # Assert
        assert result == 35

    @pytest.mark.asyncio
    async def test_get_modalidades(self, mock_session):
        """Deve retornar lista de modalidades distintas."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("Cooperativa Médica",),
            ("Medicina de Grupo",),
            ("Seguradora Especializada em Saúde",),
        ]
        mock_session.execute.return_value = mock_result
        
        repo = OperadoraRepository(mock_session)
        
        # Act
        result = await repo.get_modalidades()
        
        # Assert
        assert len(result) == 3
        assert "Cooperativa Médica" in result
        assert "Medicina de Grupo" in result


class TestDespesaRepository:
    """Testes para DespesaRepository."""

    @pytest.mark.asyncio
    async def test_get_by_operadora(self, mock_session, sample_despesas):
        """Deve retornar despesas de uma operadora."""
        # Arrange
        operadora_despesas = [d for d in sample_despesas if d.registro_ans == "301337"]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = operadora_despesas
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = DespesaRepository(mock_session)
        
        # Act
        result = await repo.get_by_operadora("301337")
        
        # Assert
        assert len(result) == 2
        assert all(d.registro_ans == "301337" for d in result)

    @pytest.mark.asyncio
    async def test_get_by_uf(self, mock_session, sample_despesas):
        """Deve retornar despesas por UF."""
        # Arrange
        sp_despesas = [d for d in sample_despesas if d.uf == "SP"]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = sp_despesas
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        repo = DespesaRepository(mock_session)
        
        # Act
        result = await repo.get_by_uf("SP")
        
        # Assert
        assert len(result) == 3
        assert all(d.uf == "SP" for d in result)

    @pytest.mark.asyncio
    async def test_get_total_by_uf(self, mock_session):
        """Deve retornar total de despesas agrupado por UF."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("SP", Decimal("18000000000.00"), 450),
            ("RJ", Decimal("8500000000.00"), 180),
        ]
        mock_session.execute.return_value = mock_result
        
        repo = DespesaRepository(mock_session)
        
        # Act
        result = await repo.get_total_by_uf()
        
        # Assert
        assert len(result) == 2
        assert result[0][0] == "SP"
        assert result[0][1] == Decimal("18000000000.00")
