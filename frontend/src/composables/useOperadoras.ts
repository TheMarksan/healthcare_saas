import { ref, computed } from 'vue';

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
  const search = ref('');
  const uf = ref('');
  const nextCursor = ref<string | null>(null);
  const cursorCache = ref<Map<number, string>>(new Map()); // Cache cursors by page number

  async function fetchOperadoras({
    pageNum = 1,
    pageSize = 10,
    searchValue = search.value,
    ufValue = uf.value,
    cursor = null,
    reset = false,
  }: {
    pageNum?: number;
    pageSize?: number;
    searchValue?: string;
    ufValue?: string;
    cursor?: string | null;
    reset?: boolean;
  } = {}) {
    loading.value = true;
    try {
      const params = new URLSearchParams({
        page: String(pageNum),
        limit: String(pageSize),
      });
      if (searchValue) params.append('search', searchValue);
      if (ufValue) params.append('uf', ufValue);
      if (cursor) params.append('cursor', cursor);

      const res = await fetch(`/api/operadoras?${params.toString()}`);
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
    } finally {
      loading.value = false;
    }
  }

  function setSearch(val: string) {
    search.value = val;
    fetchOperadoras({ pageNum: 1, pageSize: limit.value, searchValue: val, ufValue: uf.value, reset: true });
  }

  function setUf(val: string) {
    uf.value = val;
    fetchOperadoras({ pageNum: 1, pageSize: limit.value, searchValue: search.value, ufValue: val || '', reset: true });
  }

  function nextPage() {
    if (hasNext.value) {
      const cursor = cursorCache.value.get(page.value + 1) || nextCursor.value;
      fetchOperadoras({
        pageNum: page.value + 1,
        pageSize: limit.value,
        searchValue: search.value,
        ufValue: uf.value,
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
          cursor: cachedCursor,
        });
      } else {
        // For keyset pagination without cache, we need to fetch sequentially
        // This is a limitation, so we fetch from the beginning up to target page
        fetchSequentialPages(targetPage);
      }
    }
  }

  async function fetchSequentialPages(targetPage: number) {
    loading.value = true;
    try {
      let cursor: string | null = null;

      for (let p = 1; p <= targetPage; p++) {
        const params = new URLSearchParams({
          page: String(p),
          limit: String(limit.value),
        });
        if (search.value) params.append('search', search.value);
        if (uf.value) params.append('uf', uf.value);
        if (cursor) params.append('cursor', cursor);

        const res = await fetch(`/api/operadoras?${params.toString()}`);
        const data: OperadoraListResponse = await res.json();

        if (p === targetPage) {
          operadoras.value = data.data;
          total.value = data.total;
          page.value = p;
          hasNext.value = data.has_next;
          hasPrev.value = p > 1;
          nextCursor.value = data.next_cursor || null;
        }

        if (data.next_cursor) {
          cursorCache.value.set(p + 1, data.next_cursor);
          cursor = data.next_cursor;
        } else {
          break;
        }
      }
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
    search,
    uf,
    fetchOperadoras,
    setSearch,
    setUf,
    nextPage,
    prevPage,
    goToPage,
  };
}
