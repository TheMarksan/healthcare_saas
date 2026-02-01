<template>
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr class="bg-gray-50 border-b border-gray-100 dark:bg-gray-800/50 dark:border-gray-700">
          <th
            v-for="column in columns"
            :key="column.key"
            :class="cn(
              'py-4 px-6 text-left text-xs font-semibold uppercase tracking-wider',
              'text-gray-500 dark:text-gray-400',
              column.class
            )"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
        <tr
          v-for="(row, index) in data"
          :key="getRowKey(row, index)"
          :class="cn(
            'transition-colors cursor-pointer',
            'hover:bg-secondary/30 dark:hover:bg-primary/10'
          )"
          @click="$emit('row-click', row)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            :class="cn('py-4 px-6', column.cellClass)"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="data.length === 0">
          <td :colspan="columns.length" class="py-12 text-center text-gray-500 dark:text-gray-400">
            <slot name="empty">
              Nenhum registro encontrado
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Column {
  key: string;
  label: string;
  class?: string;
  cellClass?: string;
}

interface Props {
  columns: Column[];
  data: Record<string, any>[];
  rowKey?: string;
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
});

defineEmits(['row-click']);

const getRowKey = (row: Record<string, any>, index: number) => {
  return row[props.rowKey] ?? index;
};
</script>
