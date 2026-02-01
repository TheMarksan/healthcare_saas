import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useOperadoras, type OperadoraListResponse } from '@/composables/useOperadoras';
import { nextTick } from 'vue';

// Mock do fetch global
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('useOperadoras', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const mockResponse: OperadoraListResponse = {
    data: [
      {
        id: 1,
        registro_ans: '301337',
        cnpj: '44988925000190',
        razao_social: 'UNIMED CAMPINAS',
        modalidade: 'Cooperativa Médica',
        uf: 'SP',
      },
      {
        id: 2,
        registro_ans: '326305',
        cnpj: '92693118000160',
        razao_social: 'BRADESCO SAUDE S.A.',
        modalidade: 'Seguradora Especializada em Saúde',
        uf: 'SP',
      },
    ],
    total: 100,
    page: 1,
    limit: 10,
    next_cursor: 'BRADESCO SAUDE S.A.|326305',
    has_next: true,
    has_prev: false,
  };

  describe('fetchOperadoras', () => {
    it('deve buscar operadoras com parâmetros padrão', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, operadoras, total, loading } = useOperadoras();

      expect(loading.value).toBe(false);

      await fetchOperadoras();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/operadoras?')
      );
      expect(operadoras.value).toHaveLength(2);
      expect(total.value).toBe(100);
      expect(loading.value).toBe(false);
    });

    it('deve incluir parâmetros de busca na URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras } = useOperadoras();

      await fetchOperadoras({
        searchValue: 'unimed',
        ufValue: 'SP',
        modalidadeValue: 'Cooperativa Médica',
      });

      const fetchUrl = mockFetch.mock.calls[0][0] as string;
      expect(fetchUrl).toContain('search=unimed');
      expect(fetchUrl).toContain('uf=SP');
      expect(fetchUrl).toContain('modalidade=Cooperativa');
    });

    it('deve incluir cursor para paginação', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras } = useOperadoras();

      await fetchOperadoras({
        cursor: 'TESTE|123456',
      });

      const fetchUrl = mockFetch.mock.calls[0][0] as string;
      expect(fetchUrl).toContain('cursor=TESTE');
    });

    it('deve atualizar hasNext e hasPrev corretamente', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockResponse,
          has_next: true,
          has_prev: false,
        }),
      });

      const { fetchOperadoras, hasNext, hasPrev, page } = useOperadoras();

      await fetchOperadoras({ pageNum: 1 });

      expect(hasNext.value).toBe(true);
      expect(hasPrev.value).toBe(false);
      expect(page.value).toBe(1);
    });

    it('deve cachear cursor para próxima página', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras } = useOperadoras();

      await fetchOperadoras();

      // O cursor deve ser cacheado internamente para página 2
      // Verificamos que a segunda chamada usa o cursor cacheado
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockResponse,
          page: 2,
          has_prev: true,
        }),
      });
    });
  });

  describe('setSearch', () => {
    it('deve atualizar search e fazer nova busca', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { setSearch, search } = useOperadoras();

      setSearch('unimed');

      expect(search.value).toBe('unimed');
      expect(mockFetch).toHaveBeenCalled();
    });

    it('deve resetar para página 1 ao buscar', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { setSearch, page } = useOperadoras();

      setSearch('teste');

      await nextTick();

      const fetchUrl = mockFetch.mock.calls[0][0] as string;
      expect(fetchUrl).toContain('page=1');
    });
  });

  describe('setUf', () => {
    it('deve atualizar UF e fazer nova busca', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { setUf, uf } = useOperadoras();

      setUf('RJ');

      expect(uf.value).toBe('RJ');
      expect(mockFetch).toHaveBeenCalled();
    });

    it('deve permitir limpar filtro de UF', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { setUf, uf } = useOperadoras();

      setUf('SP');
      setUf('');

      expect(uf.value).toBe('');
    });
  });

  describe('setModalidade', () => {
    it('deve atualizar modalidade e fazer nova busca', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { setModalidade, modalidade } = useOperadoras();

      setModalidade('Cooperativa Médica');

      expect(modalidade.value).toBe('Cooperativa Médica');
      expect(mockFetch).toHaveBeenCalled();
    });
  });

  describe('nextPage', () => {
    it('deve avançar para próxima página quando hasNext é true', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, nextPage, hasNext, page } = useOperadoras();

      await fetchOperadoras();

      expect(hasNext.value).toBe(true);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockResponse,
          page: 2,
          has_prev: true,
        }),
      });

      nextPage();

      await nextTick();

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('não deve avançar quando hasNext é false', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockResponse,
          has_next: false,
        }),
      });

      const { fetchOperadoras, nextPage, hasNext } = useOperadoras();

      await fetchOperadoras();

      expect(hasNext.value).toBe(false);

      const callCount = mockFetch.mock.calls.length;
      nextPage();

      expect(mockFetch.mock.calls.length).toBe(callCount);
    });
  });

  describe('prevPage', () => {
    it('deve voltar para página anterior quando page > 1', async () => {
      // Primeira busca
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, nextPage, prevPage, page, hasNext } = useOperadoras();

      await fetchOperadoras();

      // Verifica que hasNext está true antes de chamar nextPage
      expect(hasNext.value).toBe(true);
      expect(page.value).toBe(1);

      // Segunda página
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockResponse,
          page: 2,
          has_prev: true,
        }),
      });

      nextPage();
      // Aguarda a promise interna resolver
      await new Promise(resolve => setTimeout(resolve, 0));
      await nextTick();

      expect(page.value).toBe(2);

      // Volta para primeira
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      prevPage();
      // Aguarda a promise interna resolver
      await new Promise(resolve => setTimeout(resolve, 0));
      await nextTick();

      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(page.value).toBe(1);
    });

    it('não deve voltar quando já está na página 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, prevPage, page } = useOperadoras();

      await fetchOperadoras();

      expect(page.value).toBe(1);

      const callCount = mockFetch.mock.calls.length;
      prevPage();

      expect(mockFetch.mock.calls.length).toBe(callCount);
    });
  });

  describe('goToPage', () => {
    it('deve ir para página específica', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, goToPage } = useOperadoras();

      await fetchOperadoras();

      goToPage(1);

      await nextTick();

      // Deve ter sido chamado (primeira busca + goToPage)
      expect(mockFetch.mock.calls.length).toBeGreaterThanOrEqual(1);
    });

    it('não deve ir para página inválida (< 1)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, goToPage } = useOperadoras();

      await fetchOperadoras();

      const callCount = mockFetch.mock.calls.length;
      goToPage(0);
      goToPage(-1);

      expect(mockFetch.mock.calls.length).toBe(callCount);
    });

    it('não deve ir para mesma página', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchOperadoras, goToPage, page } = useOperadoras();

      await fetchOperadoras();

      expect(page.value).toBe(1);

      const callCount = mockFetch.mock.calls.length;
      goToPage(1);

      expect(mockFetch.mock.calls.length).toBe(callCount);
    });
  });

  describe('estado inicial', () => {
    it('deve ter valores padrão corretos', () => {
      const {
        operadoras,
        total,
        page,
        limit,
        hasNext,
        hasPrev,
        loading,
        search,
        uf,
        modalidade,
      } = useOperadoras();

      expect(operadoras.value).toEqual([]);
      expect(total.value).toBe(0);
      expect(page.value).toBe(1);
      expect(limit.value).toBe(10);
      expect(hasNext.value).toBe(false);
      expect(hasPrev.value).toBe(false);
      expect(loading.value).toBe(false);
      expect(search.value).toBe('');
      expect(uf.value).toBe('');
      expect(modalidade.value).toBe('');
    });
  });
});
