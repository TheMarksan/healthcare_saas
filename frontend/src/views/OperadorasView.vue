<template>
  <div>
    <!-- Header -->
    <PageHeader
      title="Operadoras de Saúde"
      subtitle="Gerencie e visualize as operadoras cadastradas"
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

    <!-- Filters Card -->
    <Card class="mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <SearchBar
          :model-value="search"
          @search="setSearch"
          class="flex-1 min-w-[250px]"
          placeholder="Buscar por razão social ou CNPJ..."
        />
        <ModalidadeSelect :model-value="modalidade" @update:modalidade="setModalidade" />
        <UFSelect :model-value="uf" @update:uf="setUf" />
      </div>
    </Card>

    <!-- Loading State -->
    <Card v-if="loading">
      <LoadingSpinner message="Carregando operadoras..." />
    </Card>

    <!-- Error State -->
    <Card v-else-if="error">
      <ErrorState
        :type="errorType || 'generic'"
        :details="error"
        @retry="fetchOperadoras()"
      />
    </Card>

    <!-- Data Table -->
    <Card v-else noPadding>
      <DataTable
        :columns="tableColumns"
        :data="operadoras"
        row-key="id"
      >
        <template #cell-id="{ value }">
          <span class="text-sm text-gray-600 dark:text-gray-400">{{ value }}</span>
        </template>
        <template #cell-registro_ans="{ value }">
          <Badge variant="primary">{{ value }}</Badge>
        </template>
        <template #cell-cnpj="{ value }">
          <span class="text-sm text-gray-600 dark:text-gray-400 font-mono">{{ formatCNPJ(value) }}</span>
        </template>
        <template #cell-razao_social="{ value }">
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ value }}</span>
        </template>
        <template #cell-modalidade="{ value }">
          <span class="text-sm text-gray-600 dark:text-gray-400">{{ value }}</span>
        </template>
        <template #cell-uf="{ value }">
          <Badge>{{ value }}</Badge>
        </template>
        <template #cell-acoes="{ row }">
          <router-link
            :to="`/operadoras/${row.registro_ans}`"
            class="inline-flex items-center justify-center w-8 h-8 rounded-lg
                   text-gray-500 hover:text-primary-600 hover:bg-primary-50
                   dark:text-gray-400 dark:hover:text-primary-400 dark:hover:bg-primary-900/30
                   transition-colors"
            title="Ver detalhes"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </router-link>
        </template>
      </DataTable>

      <!-- Pagination Footer -->
      <template #footer>
        <Pagination
          :page="page"
          :total="total"
          :limit="limit"
          :has-prev="hasPrev"
          :has-next="hasNext"
          :loading="loading"
          item-label="operadoras"
          @prev="prevPage"
          @next="nextPage"
          @go-to-page="goToPage"
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useOperadoras } from '@/composables/useOperadoras';
import { Card, Badge } from '@/components/ui';
import SearchBar from '@/components/SearchBar.vue';
import UFSelect from '@/components/UFSelect.vue';
import ModalidadeSelect from '@/components/ModalidadeSelect.vue';
import DataTable from '@/components/DataTable.vue';
import Pagination from '@/components/Pagination.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import ErrorState from '@/components/ErrorState.vue';
import PageHeader from '@/components/PageHeader.vue';
import ThemeToggle from '@/components/ThemeToggle.vue';

// Table columns configuration
const tableColumns = [
  { key: 'id', label: 'ID' },
  { key: 'registro_ans', label: 'Registro ANS' },
  { key: 'cnpj', label: 'CNPJ' },
  { key: 'razao_social', label: 'Razão Social' },
  { key: 'modalidade', label: 'Modalidade' },
  { key: 'uf', label: 'UF' },
  { key: 'acoes', label: 'Ações' },
];

const {
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
} = useOperadoras();

/**
 * Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX
 */
function formatCNPJ(cnpj: string | null): string {
  if (!cnpj) return '';
  const cleaned = cnpj.replace(/\D/g, '');
  if (cleaned.length !== 14) return cnpj;
  return cleaned.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    '$1.$2.$3/$4-$5'
  );
}

onMounted(() => {
  fetchOperadoras();
});
</script>
