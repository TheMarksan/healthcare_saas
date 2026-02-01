<template>
  <div>
    <!-- Header -->
    <PageHeader title="Estatísticas" subtitle="Visão geral das despesas das operadoras de saúde">
      <template #mobile-toggle>
        <ThemeToggle />
      </template>
      <template #actions>
        <Select v-model="selectedUF" class="w-full sm:w-40" @update:modelValue="setUF">
          <option value="">Todos os estados</option>
          <option v-for="uf in availableUFs" :key="uf" :value="uf">{{ uf }}</option>
        </Select>
        <div class="hidden sm:block">
          <ThemeToggle />
        </div>
      </template>
    </PageHeader>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Carregando estatísticas..." />

    <div v-else class="space-y-6">
      <!-- Highlight Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Total Despesas -->
        <Card class="relative overflow-hidden">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total de Despesas</p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ formatCurrency(estatisticas?.total_despesas || 0) }}
              </p>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ estatisticas?.total_operadoras || 0 }} operadoras
              </p>
            </div>
            <div class="p-3 bg-primary/10 rounded-xl">
              <DollarSign class="w-6 h-6 text-primary" />
            </div>
          </div>
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-secondary" />
        </Card>

        <!-- Média Geral -->
        <Card class="relative overflow-hidden">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Média por Trimestre</p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ formatCurrency(estatisticas?.media_geral || 0) }}
              </p>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                média geral
              </p>
            </div>
            <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
              <TrendingUp class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-green-400 to-emerald-500" />
        </Card>

        <!-- Operadoras Acima da Média -->
        <Card class="relative overflow-hidden">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Acima da Média</p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ operadorasAcimaMedia?.total_operadoras || 0 }}
              </p>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                em 2+ trimestres
              </p>
            </div>
            <div class="p-3 bg-amber-100 dark:bg-amber-900/30 rounded-xl">
              <AlertTriangle class="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-400 to-orange-500" />
        </Card>
      </div>

      <!-- Charts Row -->
      <div :class="['grid grid-cols-1 gap-6', !selectedUF ? 'lg:grid-cols-2' : '']">
        <!-- Top 5 Operadoras -->
        <Card>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Top 5 Operadoras por Despesas</h3>
              <Badge variant="primary">Ranking</Badge>
            </div>
          </template>
          <div class="space-y-4">
            <div
              v-for="(op, index) in estatisticas?.top_operadoras || []"
              :key="index"
              class="flex items-center gap-4"
            >
              <div class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-primary/10 text-primary font-bold">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ op.razao_social }}
                </p>
                <div class="mt-1 w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                  <div
                    class="h-2 rounded-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
                    :style="{ width: `${(op.total / (estatisticas?.top_operadoras[0]?.total || 1)) * 100}%` }"
                  />
                </div>
              </div>
              <div class="flex-shrink-0 text-right">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatCurrency(op.total) }}
                </p>
              </div>
            </div>
          </div>
        </Card>

        <!-- Distribuição por UF - Pie Chart (hidden when UF is selected) -->
        <Card v-if="!selectedUF">
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Distribuição por UF</h3>
              <Badge variant="secondary">Pizza</Badge>
            </div>
          </template>
          <div class="h-[300px] flex items-center justify-center">
            <Pie v-if="pieChartData" :data="pieChartData" :options="pieChartOptions" />
            <p v-else class="text-gray-500 dark:text-gray-400">Sem dados disponíveis</p>
          </div>
        </Card>
      </div>

      <!-- Second Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Crescimento - Bar Chart -->
        <Card>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Top 5 Maior Crescimento</h3>
              <Badge variant="success">1º → 3º Trim</Badge>
            </div>
          </template>
          <div class="h-[300px]">
            <Bar v-if="barChartData" :data="barChartData" :options="barChartOptions" />
            <p v-else class="text-gray-500 dark:text-gray-400 flex items-center justify-center h-full">
              Sem dados disponíveis
            </p>
          </div>
        </Card>

        <!-- Operadoras Acima da Média -->
        <Card>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Operadoras Acima da Média</h3>
              <Badge variant="warning">2+ Trimestres</Badge>
            </div>
          </template>
          <div class="h-[300px] overflow-y-auto">
            <div class="space-y-3">
              <div
                v-for="(op, index) in (operadorasAcimaMedia?.operadoras || []).slice(0, 10)"
                :key="index"
                class="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {{ op.razao_social }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ op.periodos }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <Badge v-if="op.uf" variant="default">{{ op.uf }}</Badge>
                  <Badge variant="warning">{{ op.trimestres_acima_media }} trim</Badge>
                </div>
              </div>
              <p v-if="!operadorasAcimaMedia?.operadoras?.length" class="text-center text-gray-500 dark:text-gray-400 py-8">
                Nenhuma operadora encontrada
              </p>
            </div>
          </div>
        </Card>
      </div>

      <!-- Doughnut Chart - All UFs (hidden when UF is selected) -->
      <Card v-if="!selectedUF">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Média de Despesas por UF</h3>
            <Badge variant="primary">Detalhado</Badge>
          </div>
        </template>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="h-[300px] flex items-center justify-center">
            <Doughnut v-if="doughnutChartData" :data="doughnutChartData" :options="doughnutChartOptions" />
          </div>
          <div class="overflow-y-auto max-h-[300px]">
            <div class="space-y-2">
              <div
                v-for="(uf, index) in despesasPorUF"
                :key="uf.uf"
                class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-3 h-3 rounded-full"
                    :style="{ backgroundColor: getChartColor(index) }"
                  />
                  <span class="font-medium text-gray-900 dark:text-white">{{ uf.uf }}</span>
                </div>
                <div class="text-right">
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">
                    {{ formatCurrency(uf.media_despesas_por_operadora) }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ uf.total_operadoras }} operadoras
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar, Doughnut } from 'vue-chartjs';
import { DollarSign, TrendingUp, AlertTriangle } from 'lucide-vue-next';
import { useAnalytics } from '@/composables/useAnalytics';
import { useTheme } from '@/composables/useTheme';
import { Card, Badge, Select } from '@/components/ui';
import PageHeader from '@/components/PageHeader.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import ThemeToggle from '@/components/ThemeToggle.vue';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const { isDark } = useTheme();

const {
  estatisticas,
  topCrescimento,
  despesasPorUF,
  operadorasAcimaMedia,
  loading,
  selectedUF,
  availableUFs,
  formatCurrency,
  fetchAll,
  setUF,
} = useAnalytics();

// Chart colors
const chartColors = [
  '#9663C4', '#E0CAFB', '#6366F1', '#8B5CF6', '#A855F7',
  '#D946EF', '#EC4899', '#F43F5E', '#F97316', '#FBBF24',
  '#84CC16', '#22C55E', '#14B8A6', '#06B6D4', '#0EA5E9',
  '#3B82F6', '#6366F1', '#8B5CF6', '#A855F7', '#C084FC',
  '#E879F9', '#F472B6', '#FB7185', '#FDA4AF', '#FECACA',
  '#FED7AA', '#FEF08A',
];

const getChartColor = (index: number) => chartColors[index % chartColors.length];

// Pie Chart Data - Distribution by UF
const pieChartData = computed(() => {
  if (!despesasPorUF.value.length) return null;

  const data = despesasPorUF.value.slice(0, 10);

  return {
    labels: data.map(d => d.uf),
    datasets: [{
      data: data.map(d => d.total_despesas),
      backgroundColor: data.map((_, i) => getChartColor(i)),
      borderColor: isDark.value ? '#1f2937' : '#ffffff',
      borderWidth: 2,
    }],
  };
});

const pieChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const,
      labels: {
        color: isDark.value ? '#e5e7eb' : '#374151',
        padding: 15,
        usePointStyle: true,
      },
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const value = context.raw;
          return ` ${formatCurrency(value)}`;
        },
      },
    },
  },
}));

// Bar Chart Data - Top Growth
const barChartData = computed(() => {
  if (!topCrescimento.value.length) return null;

  const data = topCrescimento.value.slice(0, 5);

  return {
    labels: data.map(d => d.razao_social.substring(0, 20) + '...'),
    datasets: [{
      label: 'Crescimento %',
      data: data.map(d => d.crescimento_percentual),
      backgroundColor: chartColors.slice(0, 5),
      borderColor: chartColors.slice(0, 5),
      borderWidth: 1,
      borderRadius: 8,
    }],
  };
});

const barChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          return ` ${context.raw.toFixed(2)}%`;
        },
      },
    },
  },
  scales: {
    x: {
      grid: {
        color: isDark.value ? '#374151' : '#e5e7eb',
      },
      ticks: {
        color: isDark.value ? '#9ca3af' : '#6b7280',
        callback: (value: any) => `${value}%`,
      },
    },
    y: {
      grid: {
        display: false,
      },
      ticks: {
        color: isDark.value ? '#e5e7eb' : '#374151',
      },
    },
  },
}));

// Doughnut Chart Data - Average by UF
const doughnutChartData = computed(() => {
  if (!despesasPorUF.value.length) return null;

  return {
    labels: despesasPorUF.value.map(d => d.uf),
    datasets: [{
      data: despesasPorUF.value.map(d => d.media_despesas_por_operadora),
      backgroundColor: despesasPorUF.value.map((_, i) => getChartColor(i)),
      borderColor: isDark.value ? '#1f2937' : '#ffffff',
      borderWidth: 2,
    }],
  };
});

const doughnutChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '60%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const value = context.raw;
          return ` Média: ${formatCurrency(value)}`;
        },
      },
    },
  },
}));

onMounted(() => {
  fetchAll();
});
</script>
