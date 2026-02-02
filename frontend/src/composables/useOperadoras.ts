import { ref, computed } from 'vue';
import { API_BASE } from '@/lib/api';

export interface Operadora {
  id: number;
  registro_ans: string;
  cnpj?: string;
  razao_social: string;
  modalidade?: string;
  uf?: string;
  created_at?: string;
  updated_at?: string;
}

export interface OperadoraListResponse {
  data: Operadora[];
  total: number;
  page: number;
  limit: number;
  next_cursor?: string;
  has_next: boolean;
  has_prev: boolean;
}

export function useOperadoras() {
  const operadoras = ref<Operadora[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(10);
  const hasNext = ref(false);
  const hasPrev = ref(false);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const errorType = ref<'network' | 'server' | 'not-found' | 'generic' | null>(null);
  const search = ref('');
  const uf = ref('');
  const modalidade = ref('');
  const nextCursor = ref<string | null>(null);
  const cursorCache = ref<Map<number, string>>(new Map()); // Cache cursors by page number

  async function fetchOperadoras({
    pageNum = 1,
    pageSize = 10,
    searchValue = search.value,
    ufValue = uf.value,
    modalidadeValue = modalidade.value,
    cursor = null,
    reset = false,
  }: {
    pageNum?: number;
    pageSize?: number;
    searchValue?: string;
    ufValue?: string;
    modalidadeValue?: string;
    cursor?: string | null;
    reset?: boolean;
  } = {}) {
    loading.value = true;
    error.value = null;
    errorType.value = null;
    try {
      const params = new URLSearchParams({
        page: String(pageNum),
        limit: String(pageSize),
      });
      if (searchValue) params.append('search', searchValue);
      if (ufValue) params.append('uf', ufValue);
      if (modalidadeValue) params.append('modalidade', modalidadeValue);
      if (cursor) params.append('cursor', cursor);

      const res = await fetch(`${API_BASE}/operadoras?${params.toString()}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
        },
      });

      if (!res.ok) {
        if (res.status === 404) {
          errorType.value = 'not-found';
          throw new Error('Recurso não encontrado');
        } else if (res.status >= 500) {
          errorType.value = 'server';
          throw new Error('Erro no servidor');
        } else {
          errorType.value = 'generic';
          throw new Error(`Erro ${res.status}`);
        }
      }

      const data: OperadoraListResponse = await res.json();

      operadoras.value = data.data;
      total.value = data.total;
      page.value = pageNum;
      limit.value = data.limit;
      hasNext.value = data.has_next;
      hasPrev.value = pageNum > 1;
      nextCursor.value = data.next_cursor || null;

      // Cache the cursor for next page
      if (data.next_cursor) {
        cursorCache.value.set(pageNum + 1, data.next_cursor);
      }

      if (reset) {
        cursorCache.value = new Map();
        if (data.next_cursor) {
          cursorCache.value.set(2, data.next_cursor);
        }
      }
    } catch (e) {
      if (!errorType.value) {
        errorType.value = 'network';
      }
      error.value = e instanceof Error ? e.message : 'Erro ao carregar operadoras';
      console.error('Erro ao buscar operadoras:', e);
    } finally {
      loading.value = false;
    }
  }

  function setSearch(val: string) {
    search.value = val;
    fetchOperadoras({ pageNum: 1, pageSize: limit.value, searchValue: val, ufValue: uf.value, modalidadeValue: modalidade.value, reset: true });
  }

  function setUf(val: string) {
    uf.value = val;
    fetchOperadoras({ pageNum: 1, pageSize: limit.value, searchValue: search.value, ufValue: val || '', modalidadeValue: modalidade.value, reset: true });
  }

  function setModalidade(val: string) {
    modalidade.value = val;
    fetchOperadoras({ pageNum: 1, pageSize: limit.value, searchValue: search.value, ufValue: uf.value, modalidadeValue: val || '', reset: true });
  }

  function nextPage() {
    if (hasNext.value) {
      const cursor = cursorCache.value.get(page.value + 1) || nextCursor.value;
      fetchOperadoras({
        pageNum: page.value + 1,
        pageSize: limit.value,
        searchValue: search.value,
        ufValue: uf.value,
        modalidadeValue: modalidade.value,
        cursor: cursor,
      });
    }
  }

  function prevPage() {
    if (page.value > 1) {
      goToPage(page.value - 1);
    }
  }

  function goToPage(targetPage: number) {
    if (targetPage < 1 || targetPage === page.value) return;

    const totalPages = Math.ceil(total.value / limit.value);
    if (targetPage > totalPages) return;

    if (targetPage === 1) {
      // First page - no cursor needed
      fetchOperadoras({
        pageNum: 1,
        pageSize: limit.value,
        searchValue: search.value,
        ufValue: uf.value,
        modalidadeValue: modalidade.value,
        cursor: null,
      });
    } else {
      // Check if we have a cached cursor for this page
      const cachedCursor = cursorCache.value.get(targetPage);
      if (cachedCursor) {
        fetchOperadoras({
          pageNum: targetPage,
          pageSize: limit.value,
          searchValue: search.value,
          ufValue: uf.value,
          modalidadeValue: modalidade.value,
          cursor: cachedCursor,
        });
      } else {
        // Use offset-based pagination for distant pages (faster than sequential fetch)
        fetchWithOffset(targetPage);
      }
    }
  }

  async function fetchWithOffset(targetPage: number) {
    // Evita chamadas duplicadas
    if (loading.value) return;
    
    loading.value = true;
    error.value = null;
    errorType.value = null;

    try {
      const offset = (targetPage - 1) * limit.value;
      const params = new URLSearchParams({
        page: String(targetPage),
        limit: String(limit.value),
        offset: String(offset),
      });
      if (search.value) params.append('search', search.value);
      if (uf.value) params.append('uf', uf.value);
      if (modalidade.value) params.append('modalidade', modalidade.value);

      const res = await fetch(`${API_BASE}/operadoras?${params.toString()}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
        },
      });

      if (!res.ok) {
        throw new Error(`Erro ${res.status}`);
      }

      const data: OperadoraListResponse = await res.json();

      operadoras.value = data.data;
      total.value = data.total;
      page.value = targetPage;
      limit.value = data.limit; // Sincroniza limit com a API
      hasNext.value = data.has_next;
      hasPrev.value = targetPage > 1;
      nextCursor.value = data.next_cursor || null;

      // Cache cursor for next page
      if (data.next_cursor) {
        cursorCache.value.set(targetPage + 1, data.next_cursor);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao carregar operadoras';
      errorType.value = 'generic';
    } finally {
      loading.value = false;
    }
  }

  return {
    operadoras,
    total,
    page,
    limit,
    hasNext,
    hasPrev,
    loading,
    error,
    errorType,
    search,
    uf,
    modalidade,
    fetchOperadoras,
    setSearch,
    setUf,
    setModalidade,
    nextPage,
    prevPage,
    goToPage,
  };
}
