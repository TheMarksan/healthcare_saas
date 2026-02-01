"""
Testes unitários para os serviços de domínio.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from domain.services import AnalyticsService
from domain.schemas import EstatisticasResponse, TopOperadoraCrescimento


class TestAnalyticsService:
    """Testes para AnalyticsService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de AsyncSession."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_estatisticas_agregadas(self, mock_session):
        """Deve retornar estatísticas agregadas corretamente."""
        # Arrange
        # Mock para a query principal
        main_result = MagicMock()
        main_result.fetchone.return_value = MagicMock(
            total_operadoras=1250,
            total_despesas=Decimal("45000000000.00"),
            media_geral=Decimal("36000000.00")
        )
        
        # Mock para top UFs
        top_ufs_result = MagicMock()
        top_ufs_result.fetchall.return_value = [
            MagicMock(uf="SP", total=Decimal("18000000000.00")),
            MagicMock(uf="RJ", total=Decimal("8500000000.00")),
        ]
        
        # Mock para top operadoras
        top_operadoras_result = MagicMock()
        top_operadoras_result.fetchall.return_value = [
            MagicMock(razao_social="BRADESCO", cnpj="12345", total=Decimal("5200000000.00")),
        ]
        
        # Configura retornos sequenciais
        mock_session.execute.side_effect = [
            main_result,
            top_ufs_result,
            top_operadoras_result,
        ]
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_estatisticas_agregadas()
        
        # Assert
        assert isinstance(result, EstatisticasResponse)
        assert result.total_operadoras == 1250
        assert result.total_despesas == 45000000000.00
        assert result.media_geral == 36000000.00
        assert len(result.top_ufs) == 2
        assert result.top_ufs[0]["uf"] == "SP"

    @pytest.mark.asyncio
    async def test_get_estatisticas_agregadas_with_uf_filter(self, mock_session):
        """Deve aplicar filtro de UF nas estatísticas."""
        # Arrange
        main_result = MagicMock()
        main_result.fetchone.return_value = MagicMock(
            total_operadoras=450,
            total_despesas=Decimal("18000000000.00"),
            media_geral=Decimal("40000000.00")
        )
        
        top_ufs_result = MagicMock()
        top_ufs_result.fetchall.return_value = [
            MagicMock(uf="SP", total=Decimal("18000000000.00")),
        ]
        
        top_operadoras_result = MagicMock()
        top_operadoras_result.fetchall.return_value = []
        
        mock_session.execute.side_effect = [
            main_result,
            top_ufs_result,
            top_operadoras_result,
        ]
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_estatisticas_agregadas(uf="SP")
        
        # Assert
        assert result.total_operadoras == 450
        assert len(result.top_ufs) == 1
        assert result.top_ufs[0]["uf"] == "SP"

    @pytest.mark.asyncio
    async def test_get_estatisticas_empty_database(self, mock_session):
        """Deve tratar banco vazio graciosamente."""
        # Arrange
        main_result = MagicMock()
        main_result.fetchone.return_value = MagicMock(
            total_operadoras=0,
            total_despesas=None,
            media_geral=None
        )
        
        empty_result = MagicMock()
        empty_result.fetchall.return_value = []
        
        mock_session.execute.side_effect = [
            main_result,
            empty_result,
            empty_result,
        ]
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_estatisticas_agregadas()
        
        # Assert
        assert result.total_operadoras == 0
        assert result.total_despesas == 0
        assert result.media_geral == 0
        assert result.top_ufs == []

    @pytest.mark.asyncio
    async def test_get_top_crescimento(self, mock_session):
        """Deve retornar operadoras com maior crescimento."""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            MagicMock(
                registro_ans="412589",
                razao_social="OPERADORA A",
                uf="SP",
                periodo_inicial="2025T1",
                periodo_final="2025T3",
                valor_inicial=Decimal("5000000.00"),
                valor_final=Decimal("9275000.00"),
                crescimento_percentual=Decimal("85.50")
            ),
            MagicMock(
                registro_ans="325412",
                razao_social="OPERADORA B",
                uf="RJ",
                periodo_inicial="2025T1",
                periodo_final="2025T3",
                valor_inicial=Decimal("3200000.00"),
                valor_final=Decimal("5513600.00"),
                crescimento_percentual=Decimal("72.30")
            ),
        ]
        mock_session.execute.return_value = mock_result
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_top_crescimento(limit=5)
        
        # Assert
        assert len(result) == 2
        assert isinstance(result[0], TopOperadoraCrescimento)
        assert result[0].registro_ans == "412589"
        assert float(result[0].crescimento_percentual) == 85.50

    @pytest.mark.asyncio
    async def test_get_top_crescimento_with_uf_filter(self, mock_session):
        """Deve filtrar crescimento por UF."""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            MagicMock(
                registro_ans="412589",
                razao_social="OPERADORA SP",
                uf="SP",
                periodo_inicial="2025T1",
                periodo_final="2025T3",
                valor_inicial=Decimal("5000000.00"),
                valor_final=Decimal("9275000.00"),
                crescimento_percentual=Decimal("85.50")
            ),
        ]
        mock_session.execute.return_value = mock_result
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_top_crescimento(limit=5, uf="SP")
        
        # Assert
        assert len(result) == 1
        assert result[0].uf == "SP"

    @pytest.mark.asyncio
    async def test_get_despesas_por_uf(self, mock_session):
        """Deve retornar despesas agrupadas por UF."""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            MagicMock(
                uf="SP",
                total_despesas=Decimal("18000000000.00"),
                total_operadoras=450,
                media_despesas_por_operadora=Decimal("40000000.00"),
                percentual_total=Decimal("55.38")
            ),
            MagicMock(
                uf="RJ",
                total_despesas=Decimal("8500000000.00"),
                total_operadoras=180,
                media_despesas_por_operadora=Decimal("47222222.22"),
                percentual_total=Decimal("26.15")
            ),
            MagicMock(
                uf="MG",
                total_despesas=Decimal("5200000000.00"),
                total_operadoras=150,
                media_despesas_por_operadora=Decimal("34666666.67"),
                percentual_total=Decimal("16.00")
            ),
        ]
        mock_session.execute.return_value = mock_result
        
        service = AnalyticsService(mock_session)
        
        # Act
        result = await service.get_despesas_por_uf(limit=5)
        
        # Assert
        assert len(result) == 3
        assert result[0].uf == "SP"
        assert float(result[0].total_despesas) == 18000000000.00

    @pytest.mark.asyncio
    async def test_get_operadoras_acima_media(self, mock_session):
        """Deve retornar operadoras consistentemente acima da média."""
        # Arrange
        # Mock para operadoras (primeiro execute)
        operadoras_result = MagicMock()
        operadoras_result.fetchall.return_value = [
            MagicMock(
                registro_ans="326305",
                razao_social="BRADESCO SAUDE",
                uf="SP",
                trimestres_acima=3,
                periodos="2024T1, 2024T2, 2024T3"
            ),
        ]
        
        # Mock para count (segundo execute)
        count_result = MagicMock()
        count_result.scalar_one.return_value = 125
        
        mock_session.execute.side_effect = [
            operadoras_result,
            count_result,
        ]
        
        service = AnalyticsService(mock_session)
        
        # Act
        total, operadoras = await service.get_operadoras_acima_media(min_trimestres=2)
        
        # Assert
        assert total == 125
        assert len(operadoras) == 1
        assert operadoras[0].razao_social == "BRADESCO SAUDE"
