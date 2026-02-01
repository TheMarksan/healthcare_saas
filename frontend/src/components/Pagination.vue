<template>
  <div class="flex items-center justify-between flex-wrap gap-4">
    <span class="text-sm text-gray-500 dark:text-gray-400">
      Mostrando <span class="font-semibold text-gray-700 dark:text-gray-200">{{ startItem }}-{{ endItem }}</span>
      de <span class="font-semibold text-gray-700 dark:text-gray-200">{{ total }}</span> {{ itemLabel }}
    </span>
    <div class="flex items-center gap-2">
      <Button
        variant="outline"
        size="sm"
        :disabled="!hasPrev || loading"
        @click="$emit('prev')"
        class="px-3"
      >
        <ChevronLeft class="w-4 h-4" />
      </Button>

      <!-- Page Numbers -->
      <div class="flex items-center gap-1">
        <button
          v-for="pageNum in visiblePages"
          :key="pageNum"
          @click="pageNum !== '...' && $emit('goToPage', pageNum)"
          :disabled="pageNum === '...' || pageNum === page || loading"
          :class="[
            'min-w-[36px] h-9 px-3 text-sm font-medium rounded-lg transition-colors',
            pageNum === page
              ? 'bg-primary text-white'
              : pageNum === '...'
              ? 'text-gray-400 cursor-default'
              : 'text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
          ]"
        >
          {{ pageNum }}
        </button>
      </div>

      <Button
        size="sm"
        :disabled="!hasNext || loading"
        @click="$emit('next')"
        class="px-3"
      >
        <ChevronRight class="w-4 h-4" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';
import { Button } from '@/components/ui';

interface Props {
  page: number;
  total: number;
  limit: number;
  hasPrev: boolean;
  hasNext: boolean;
  loading?: boolean;
  itemLabel?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  itemLabel: 'registros',
  limit: 10,
});

defineEmits(['prev', 'next', 'goToPage']);

const totalPages = computed(() => Math.ceil(props.total / props.limit));

const startItem = computed(() => {
  if (props.total === 0) return 0;
  return (props.page - 1) * props.limit + 1;
});

const endItem = computed(() => {
  return Math.min(props.page * props.limit, props.total);
});

const visiblePages = computed(() => {
  const pages: (number | string)[] = [];
  const total = totalPages.value;
  const current = props.page;

  if (total <= 7) {
    // Show all pages if 7 or fewer
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    // Always show first page
    pages.push(1);

    if (current > 3) {
      pages.push('...');
    }

    // Show pages around current
    const start = Math.max(2, current - 1);
    const end = Math.min(total - 1, current + 1);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    if (current < total - 2) {
      pages.push('...');
    }

    // Always show last page
    if (total > 1) {
      pages.push(total);
    }
  }

  return pages;
});
</script>
