<template>
  <div>
    <!-- Back Button & Header -->
    <div class="mb-6">
      <router-link
        to="/operadoras"
        class="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600
               dark:text-gray-400 dark:hover:text-primary-400 transition-colors mb-4"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Voltar para lista
      </router-link>

      <PageHeader
        :title="operadora?.razao_social || 'Carregando...'"
        :subtitle="operadora ? `Registro ANS: ${operadora.registro_ans}` : ''"
      >
        <template #actions>
          <ThemeToggle />
        </template>
      </PageHeader>
    </div>

    <!-- Loading State -->
    <Card v-if="loading">
      <LoadingSpinner message="Carregando detalhes da operadora..." />
    </Card>

    <!-- Error State -->
    <Card v-else-if="error" class="text-center py-12">
      <div class="text-red-500 dark:text-red-400 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Erro ao carregar</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
      <Button @click="fetchData">Tentar novamente</Button>
    </Card>

    <!-- Content -->
    <template v-else-if="operadora">
      <!-- Info Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- CNPJ Card -->
        <Card class="relative overflow-hidden">
          <div class="absolute top-0 right-0 w-20 h-20 bg-primary-500/10 rounded-bl-full" />
          <div class="relative">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
              CNPJ
            </p>
            <p class="text-lg font-bold text-primary-600 dark:text-primary-400 font-mono">
              {{ formatCNPJ(operadora.cnpj) || 'Não informado' }}
            </p>
          </div>
        </Card>

        <!-- Registro ANS Card -->
        <Card class="relative overflow-hidden">
          <div class="absolute top-0 right-0 w-20 h-20 bg-emerald-500/10 rounded-bl-full" />
          <div class="relative">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
              Registro ANS
            </p>
            <Badge variant="primary" class="text-lg px-3 py-1">
              {{ operadora.registro_ans }}
            </Badge>
          </div>
        </Card>

        <!-- Modalidade Card -->
        <Card class="relative overflow-hidden">
          <div class="absolute top-0 right-0 w-20 h-20 bg-amber-500/10 rounded-bl-full" />
          <div class="relative">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
              Modalidade
            </p>
            <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ operadora.modalidade || 'Não informada' }}
            </p>
          </div>
        </Card>

        <!-- UF Card -->
        <Card class="relative overflow-hidden">
          <div class="absolute top-0 right-0 w-20 h-20 bg-violet-500/10 rounded-bl-full" />
          <div class="relative">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
              UF / Estado
            </p>
            <Badge class="text-lg px-3 py-1">
              {{ operadora.uf || 'N/A' }}
            </Badge>
          </div>
        </Card>
      </div>

      <!-- Despesas Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Card class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 border-emerald-200 dark:border-emerald-800">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-emerald-700 dark:text-emerald-300">Total de Despesas</p>
              <p class="text-2xl font-bold text-emerald-800 dark:text-emerald-200">
                {{ formatCurrency(totalDespesas) }}
              </p>
            </div>
          </div>
        </Card>

        <Card class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-blue-700 dark:text-blue-300">Média por Trimestre</p>
              <p class="text-2xl font-bold text-blue-800 dark:text-blue-200">
                {{ formatCurrency(mediaDespesas) }}
              </p>
            </div>
          </div>
        </Card>
      </div>

      <!-- Despesas Chart -->
      <Card>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Histórico de Despesas por Trimestre
        </h3>

        <div v-if="despesas.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>Nenhum registro de despesas encontrado</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="despesa in sortedDespesas"
            :key="`${despesa.trimestre}-${despesa.ano}`"
            class="group"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ despesa.trimestre }}/{{ despesa.ano }}
              </span>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {{ formatCurrency(despesa.valor_despesas) }}
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
              <div
                class="h-full rounded-full bg-gradient-to-r from-[#E0CAFB] to-[#9663C4]
                       transition-all duration-500 flex items-center justify-end pr-2"
                :style="{ width: `${getBarWidth(despesa.valor_despesas)}%` }"
              >
                <span
                  v-if="getBarWidth(despesa.valor_despesas) > 15"
                  class="text-xs font-medium text-white"
                >
                  {{ formatPercent(despesa.valor_despesas) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Card, Badge, Button } from '@/components/ui';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import PageHeader from '@/components/PageHeader.vue';
import ThemeToggle from '@/components/ThemeToggle.vue';

interface Operadora {
  id: number;
  registro_ans: string;
  cnpj: string;
  razao_social: string;
  modalidade: string;
  uf: string;
}

interface Despesa {
  id: number;
  registro_ans: string;
  trimestre: number;
  ano: number;
  valor_despesas: string | number;
}

const route = useRoute();

const operadora = ref<Operadora | null>(null);
const despesas = ref<Despesa[]>([]);
const totalDespesas = ref(0);
const mediaDespesas = ref(0);
const loading = ref(true);
const error = ref<string | null>(null);

const sortedDespesas = computed(() => {
  return [...despesas.value].sort((a, b) => {
    // Sort by year first, then by trimestre
    if (a.ano !== b.ano) return a.ano - b.ano;
    return a.trimestre - b.trimestre;
  });
});

const maxDespesa = computed(() => {
  if (despesas.value.length === 0) return 0;
  return Math.max(...despesas.value.map(d => Number(d.valor_despesas)));
});

function getBarWidth(valor: string | number): number {
  if (maxDespesa.value === 0) return 0;
  return (Number(valor) / maxDespesa.value) * 100;
}

function formatPercent(valor: string | number): string {
  if (totalDespesas.value === 0) return '0%';
  return ((Number(valor) / totalDespesas.value) * 100).toFixed(1) + '%';
}

function formatCurrency(value: string | number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(Number(value));
}

function formatCNPJ(cnpj: string | null): string {
  if (!cnpj) return '';
  const cleaned = cnpj.replace(/\D/g, '');
  if (cleaned.length !== 14) return cnpj;
  return cleaned.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    '$1.$2.$3/$4-$5'
  );
}

async function fetchData() {
  const registroAns = route.params.registroAns as string;

  loading.value = true;
  error.value = null;

  try {
    const response = await fetch(`/api/operadoras/registro/${registroAns}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Operadora não encontrada');
      }
      throw new Error('Erro ao carregar dados da operadora');
    }

    const data = await response.json();

    operadora.value = data.operadora;
    despesas.value = data.despesas;
    totalDespesas.value = data.total_despesas;
    mediaDespesas.value = data.media_despesas;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erro desconhecido';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>
