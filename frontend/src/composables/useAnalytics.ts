import { ref, computed } from 'vue';
import { API_BASE } from '@/lib/api';

export interface Estatisticas {
  total_operadoras: number;
  total_despesas: number;
  media_geral: number;
  top_ufs: { uf: string; total: number }[];
  top_operadoras: { razao_social: string; cnpj: string; total: number }[];
  updated_at: string;
}

export interface TopCrescimento {
  registro_ans: string;
  razao_social: string;
  uf: string | null;
  periodo_inicial: string;
  periodo_final: string;
  valor_inicial: number;
  valor_final: number;
  crescimento_percentual: number;
}

export interface DespesaPorUF {
  uf: string;
  total_despesas: number;
  total_operadoras: number;
  media_despesas_por_operadora: number;
  percentual_total: number;
}

export interface OperadoraAcimaMedia {
  registro_ans: string;
  razao_social: string;
  uf: string | null;
  trimestres_acima_media: number;
  periodos: string;
}

export function useAnalytics() {
  const estatisticas = ref<Estatisticas | null>(null);
  const topCrescimento = ref<TopCrescimento[]>([]);
  const despesasPorUF = ref<DespesaPorUF[]>([]);
  const operadorasAcimaMedia = ref<{ total_operadoras: number; operadoras: OperadoraAcimaMedia[] } | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const errorType = ref<'network' | 'server' | 'not-found' | 'generic' | null>(null);
  const selectedUF = ref<string>('');

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const formatPercent = (value: number): string => {
    return `${value.toFixed(2)}%`;
  };

  const fetchEstatisticas = async (uf?: string) => {
    try {
      loading.value = true;
      error.value = null;
      errorType.value = null;
      const params = uf ? `?uf=${encodeURIComponent(uf)}` : '';
      const response = await fetch(`${API_BASE}/estatisticas${params}`);
      if (!response.ok) {
        if (response.status >= 500) {
          errorType.value = 'server';
        } else if (response.status === 404) {
          errorType.value = 'not-found';
        } else {
          errorType.value = 'generic';
        }
        throw new Error('Erro ao buscar estatísticas');
      }
      estatisticas.value = await response.json();
    } catch (e) {
      if (!errorType.value) {
        errorType.value = 'network';
      }
      error.value = e instanceof Error ? e.message : 'Erro desconhecido';
      console.error('Erro ao buscar estatísticas:', e);
    } finally {
      loading.value = false;
    }
  };

  const fetchTopCrescimento = async (limit: number = 5, uf?: string) => {
    try {
      let params = `limit=${limit}`;
      if (uf) params += `&uf=${encodeURIComponent(uf)}`;
      const response = await fetch(`${API_BASE}/estatisticas/crescimento?${params}`);
      if (!response.ok) throw new Error('Erro ao buscar top crescimento');
      topCrescimento.value = await response.json();
    } catch (e) {
      console.error('Erro ao buscar top crescimento:', e);
    }
  };

  const fetchDespesasPorUF = async (limit: number = 27) => {
    try {
      const response = await fetch(`${API_BASE}/estatisticas/despesas-por-uf?limit=${limit}`);
      if (!response.ok) throw new Error('Erro ao buscar despesas por UF');
      despesasPorUF.value = await response.json();
    } catch (e) {
      console.error('Erro ao buscar despesas por UF:', e);
    }
  };

  const fetchOperadorasAcimaMedia = async (minTrimestres: number = 2, uf?: string) => {
    try {
      let params = `min_trimestres=${minTrimestres}`;
      if (uf) params += `&uf=${encodeURIComponent(uf)}`;
      const response = await fetch(`${API_BASE}/estatisticas/acima-media?${params}`);
      if (!response.ok) throw new Error('Erro ao buscar operadoras acima da média');
      operadorasAcimaMedia.value = await response.json();
    } catch (e) {
      console.error('Erro ao buscar operadoras acima da média:', e);
    }
  };

  const fetchAll = async (uf?: string) => {
    loading.value = true;
    await Promise.all([
      fetchEstatisticas(uf),
      fetchTopCrescimento(5, uf),
      fetchDespesasPorUF(),
      fetchOperadorasAcimaMedia(2, uf),
    ]);
    loading.value = false;
  };

  // Computed filtered data based on selectedUF
  const filteredTopCrescimento = computed(() => {
    if (!selectedUF.value) return topCrescimento.value;
    return topCrescimento.value.filter(item => item.uf === selectedUF.value);
  });

  const filteredOperadorasAcimaMedia = computed(() => {
    if (!operadorasAcimaMedia.value) return null;
    if (!selectedUF.value) return operadorasAcimaMedia.value;
    const filtered = operadorasAcimaMedia.value.operadoras.filter(item => item.uf === selectedUF.value);
    return {
      total_operadoras: filtered.length,
      operadoras: filtered,
    };
  });

  const filteredEstatisticas = computed(() => {
    if (!estatisticas.value || !selectedUF.value) return estatisticas.value;

    // Filter top_operadoras by UF (if possible - need backend support for full filtering)
    return estatisticas.value;
  });

  const setUF = async (uf: string) => {
    selectedUF.value = uf;
    // Refetch data with the new UF filter
    await fetchAll(uf || undefined);
  };

  // Get unique UFs from despesas data
  const availableUFs = computed(() => {
    return despesasPorUF.value.map(d => d.uf).sort();
  });

  return {
    estatisticas,
    topCrescimento,
    despesasPorUF,
    operadorasAcimaMedia,
    loading,
    error,
    errorType,
    selectedUF,
    availableUFs,
    filteredTopCrescimento,
    filteredOperadorasAcimaMedia,
    filteredEstatisticas,
    formatCurrency,
    formatNumber,
    formatPercent,
    fetchEstatisticas,
    fetchTopCrescimento,
    fetchDespesasPorUF,
    fetchOperadorasAcimaMedia,
    fetchAll,
    setUF,
  };
}
