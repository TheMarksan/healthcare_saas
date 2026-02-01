import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAnalytics } from '@/composables/useAnalytics';

// Mock do fetch global
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('useAnalytics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const mockEstatisticas = {
    total_operadoras: 1250,
    total_despesas: 45000000000.0,
    media_geral: 36000000.0,
    top_ufs: [
      { uf: 'SP', total: 18000000000.0 },
      { uf: 'RJ', total: 8500000000.0 },
    ],
    top_operadoras: [
      { razao_social: 'BRADESCO SAUDE', cnpj: '12345', total: 5200000000.0 },
    ],
    updated_at: '2026-02-01T12:00:00',
  };

  describe('fetchEstatisticas', () => {
    it('deve buscar estatísticas com sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockEstatisticas),
      });

      const { fetchEstatisticas, estatisticas, loading } = useAnalytics();

      expect(loading.value).toBe(false);

      await fetchEstatisticas();

      expect(mockFetch).toHaveBeenCalledWith('/api/estatisticas');
      expect(estatisticas.value).not.toBeNull();
      expect(estatisticas.value?.total_operadoras).toBe(1250);
      expect(loading.value).toBe(false);
    });

    it('deve buscar estatísticas filtradas por UF', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockEstatisticas,
          total_operadoras: 450,
        }),
      });

      const { fetchEstatisticas } = useAnalytics();

      await fetchEstatisticas('SP');

      expect(mockFetch).toHaveBeenCalledWith('/api/estatisticas?uf=SP');
    });

    it('deve tratar erro na requisição', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { fetchEstatisticas, error } = useAnalytics();

      await fetchEstatisticas();

      expect(error.value).not.toBeNull();
    });

    it('deve tratar resposta não ok', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const { fetchEstatisticas, error } = useAnalytics();

      await fetchEstatisticas();

      expect(error.value).not.toBeNull();
    });
  });

  describe('fetchTopCrescimento', () => {
    const mockCrescimento = [
      {
        registro_ans: '412589',
        razao_social: 'OPERADORA A',
        uf: 'SP',
        crescimento_percentual: 85.5,
      },
      {
        registro_ans: '325412',
        razao_social: 'OPERADORA B',
        uf: 'RJ',
        crescimento_percentual: 72.3,
      },
    ];

    it('deve buscar top crescimento com sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCrescimento),
      });

      const { fetchTopCrescimento, topCrescimento } = useAnalytics();

      await fetchTopCrescimento();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/estatisticas/crescimento')
      );
      expect(topCrescimento.value).toHaveLength(2);
    });

    it('deve aceitar parâmetro de limite', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCrescimento),
      });

      const { fetchTopCrescimento } = useAnalytics();

      await fetchTopCrescimento(10);

      expect(mockFetch).toHaveBeenCalledWith('/api/estatisticas/crescimento?limit=10');
    });
  });

  describe('fetchDespesasPorUF', () => {
    const mockDespesasUf = [
      { uf: 'SP', total_despesas: 18000000000.0, quantidade_operadoras: 450 },
      { uf: 'RJ', total_despesas: 8500000000.0, quantidade_operadoras: 180 },
    ];

    it('deve buscar despesas por UF com sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockDespesasUf),
      });

      const { fetchDespesasPorUF, despesasPorUF } = useAnalytics();

      await fetchDespesasPorUF();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/estatisticas/despesas-por-uf')
      );
      expect(despesasPorUF.value).toHaveLength(2);
    });
  });

  describe('formatCurrency', () => {
    it('deve formatar valores em reais', () => {
      const { formatCurrency } = useAnalytics();

      const result = formatCurrency(1500000.5);

      expect(result).toContain('1.500.000');
      expect(result).toContain('R$');
    });

    it('deve formatar valores zerados', () => {
      const { formatCurrency } = useAnalytics();

      const result = formatCurrency(0);

      expect(result).toContain('R$');
      expect(result).toContain('0,00');
    });

    it('deve formatar valores negativos', () => {
      const { formatCurrency } = useAnalytics();

      const result = formatCurrency(-1000.5);

      expect(result).toContain('1.000,50');
    });
  });

  describe('formatNumber', () => {
    it('deve formatar números com separador de milhares', () => {
      const { formatNumber } = useAnalytics();

      const result = formatNumber(1250000);

      expect(result).toBe('1.250.000');
    });

    it('deve formatar valores zerados', () => {
      const { formatNumber } = useAnalytics();

      const result = formatNumber(0);

      expect(result).toBe('0');
    });
  });

  describe('estado inicial', () => {
    it('deve ter valores padrão corretos', () => {
      const {
        estatisticas,
        topCrescimento,
        despesasPorUF,
        loading,
        error,
      } = useAnalytics();

      expect(estatisticas.value).toBeNull();
      expect(topCrescimento.value).toEqual([]);
      expect(despesasPorUF.value).toEqual([]);
      expect(loading.value).toBe(false);
      expect(error.value).toBeNull();
    });
  });
});
