<template>
  <div>
    <!-- Header -->
    <PageHeader
      title="Logs do Sistema"
      subtitle="Acompanhe operadoras com dados incompletos ou pendentes"
    >
      <template #mobile-toggle>
        <ThemeToggle />
      </template>
      <template #actions>
        <div class="hidden sm:block">
          <ThemeToggle />
        </div>
      </template>
    </PageHeader>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
      <Card
        class="cursor-pointer transition-all hover:shadow-lg"
        :class="activeTab === 'unmatched' ? 'ring-2 ring-primary' : ''"
        @click="activeTab = 'unmatched'"
      >
        <div class="flex items-center gap-4">
          <div class="p-3 rounded-xl bg-amber-100 dark:bg-amber-900/30">
            <AlertTriangle class="w-6 h-6 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Sem Match ANS</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ summary.unmatched }}</p>
          </div>
        </div>
      </Card>

      <Card
        class="cursor-pointer transition-all hover:shadow-lg"
        :class="activeTab === 'sem-despesas' ? 'ring-2 ring-primary' : ''"
        @click="activeTab = 'sem-despesas'"
      >
        <div class="flex items-center gap-4">
          <div class="p-3 rounded-xl bg-red-100 dark:bg-red-900/30">
            <FileX class="w-6 h-6 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Sem Despesas</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ summary.semDespesas }}</p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Tab Content -->
    <Card>
      <!-- Tab Header -->
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <component :is="tabConfig[activeTab].icon" class="w-5 h-5" :class="tabConfig[activeTab].iconClass" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ tabConfig[activeTab].title }}
          </h3>
        </div>
        <Badge :variant="tabConfig[activeTab].badgeVariant">
          {{ currentData.total }} registros
        </Badge>
      </div>

      <!-- Description -->
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {{ tabConfig[activeTab].description }}
      </p>

      <!-- Loading -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner :message="`Carregando ${tabConfig[activeTab].title.toLowerCase()}...`" />
      </div>

      <!-- Error State -->
      <ErrorState
        v-else-if="error"
        :type="errorType || 'generic'"
        :details="error"
        @retry="fetchTabData(activeTab)"
      />

      <!-- Data Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100 dark:bg-gray-800/50 dark:border-gray-700">
              <th class="py-3 px-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Registro ANS
              </th>
              <th class="py-3 px-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Razão Social
              </th>
              <th v-if="activeTab === 'unmatched'" class="py-3 px-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Qtd. Registros
              </th>
              <th v-if="activeTab !== 'unmatched'" class="py-3 px-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                UF
              </th>
              <th class="py-3 px-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Status
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr
              v-for="item in currentData.data"
              :key="item.registro_ans"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td class="py-3 px-4">
                <Badge variant="primary">{{ item.registro_ans }}</Badge>
              </td>
              <td class="py-3 px-4">
                <span class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ item.razao_social }}
                </span>
              </td>
              <td v-if="activeTab === 'unmatched'" class="py-3 px-4">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ item.quantidade_registros }}
                </span>
              </td>
              <td v-if="activeTab !== 'unmatched'" class="py-3 px-4">
                <Badge v-if="item.uf">{{ item.uf }}</Badge>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="py-3 px-4">
                <Badge :variant="tabConfig[activeTab].badgeVariant">
                  {{ item.descricao }}
                </Badge>
              </td>
            </tr>
            <tr v-if="currentData.data.length === 0">
              <td colspan="4" class="py-12 text-center text-gray-500 dark:text-gray-400">
                Nenhum registro encontrado
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="currentData.total > 0" class="mt-4 flex items-center justify-between border-t border-gray-100 dark:border-gray-700 pt-4">
        <span class="text-sm text-gray-500 dark:text-gray-400">
          Mostrando {{ currentData.data.length }} de {{ currentData.total }}
        </span>
        <div class="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            :disabled="!currentData.has_prev || loading"
            @click="loadPage(-1)"
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            :disabled="!currentData.has_next || loading"
            @click="loadPage(1)"
          >
            Próxima
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from 'vue';
import { Card, Badge, Button } from '@/components/ui';
import PageHeader from '@/components/PageHeader.vue';
import ThemeToggle from '@/components/ThemeToggle.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import ErrorState from '@/components/ErrorState.vue';
import { AlertTriangle, FileX } from 'lucide-vue-next';
import { API_BASE } from '@/lib/api';

type TabType = 'unmatched' | 'sem-despesas';
type ErrorType = 'network' | 'server' | 'not-found' | 'generic';

interface LogItem {
  registro_ans: string;
  razao_social: string;
  quantidade_registros?: number;
  uf?: string;
  tipo: string;
  descricao: string;
}

interface LogResponse {
  data: LogItem[];
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

const activeTab = ref<TabType>('unmatched');
const loading = ref(false);
const error = ref<string | null>(null);
const errorType = ref<ErrorType | null>(null);
const offset = ref(0);
const limit = 50;

const summary = reactive({
  unmatched: 0,
  semDespesas: 0,
});

const dataCache = reactive<Record<TabType, LogResponse>>({
  unmatched: { data: [], total: 0, limit: 50, offset: 0, has_next: false, has_prev: false },
  'sem-despesas': { data: [], total: 0, limit: 50, offset: 0, has_next: false, has_prev: false },
});

const currentData = computed(() => dataCache[activeTab.value]);

const tabConfig = {
  unmatched: {
    title: 'Operadoras Sem Match',
    description: 'Operadoras que possuem registros de despesas mas não foram encontradas no cadastro oficial da ANS. Foram criadas como placeholder durante a importação.',
    icon: AlertTriangle,
    iconClass: 'text-amber-600 dark:text-amber-400',
    badgeVariant: 'warning' as const,
    endpoint: `${API_BASE}/logs/unmatched`,
  },
  'sem-despesas': {
    title: 'Operadoras Sem Despesas',
    description: 'Operadoras cadastradas no sistema mas que não possuem nenhum registro de despesa trimestral vinculado.',
    icon: FileX,
    iconClass: 'text-red-600 dark:text-red-400',
    badgeVariant: 'destructive' as const,
    endpoint: `${API_BASE}/logs/sem-despesas`,
  },
};

async function fetchSummary() {
  try {
    const response = await fetch(`${API_BASE}/logs`);
    if (!response.ok) throw new Error('Erro ao carregar resumo');
    const data = await response.json();
    summary.unmatched = data.unmatched_operadoras || 0;
    summary.semDespesas = data.sem_despesas || 0;
  } catch (err) {
    console.error('Erro ao carregar resumo:', err);
  }
}

async function fetchTabData(tab: TabType, newOffset = 0) {
  loading.value = true;
  error.value = null;
  errorType.value = null;
  try {
    const config = tabConfig[tab];
    const response = await fetch(`${config.endpoint}?limit=${limit}&offset=${newOffset}`);

    if (!response.ok) {
      if (response.status >= 500) {
        errorType.value = 'server';
      } else if (response.status === 404) {
        errorType.value = 'not-found';
      } else {
        errorType.value = 'generic';
      }
      throw new Error(`Erro ${response.status}`);
    }

    const data: LogResponse = await response.json();
    dataCache[tab] = data;
    offset.value = newOffset;

    // Update summary with actual totals
    if (tab === 'unmatched') summary.unmatched = data.total;
    if (tab === 'sem-despesas') summary.semDespesas = data.total;
  } catch (err) {
    if (!errorType.value) {
      errorType.value = 'network';
    }
    error.value = err instanceof Error ? err.message : 'Erro ao carregar dados';
    console.error(`Erro ao carregar ${tab}:`, err);
  } finally {
    loading.value = false;
  }
}

function loadPage(direction: number) {
  const newOffset = offset.value + (direction * limit);
  fetchTabData(activeTab.value, newOffset);
}

watch(activeTab, (newTab) => {
  offset.value = 0;
  if (dataCache[newTab].data.length === 0) {
    fetchTabData(newTab);
  }
});

onMounted(async () => {
  await fetchSummary();
  await fetchTabData('unmatched');
});
</script>
