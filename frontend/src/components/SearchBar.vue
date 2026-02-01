<template>
  <div class="flex gap-2 w-full">
    <div class="relative flex-1">
      <input
        v-model="search"
        @input="onInput"
        @keyup.enter="emitSearch"
        type="text"
        :placeholder="placeholder"
        class="w-full px-3 py-2 pr-10 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary transition-colors"
      />
      <div v-if="isSearching" class="absolute right-3 top-1/2 -translate-y-1/2">
        <svg class="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <button
        v-else-if="search"
        @click="clearSearch"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

const props = withDefaults(defineProps<{
  modelValue?: string;
  placeholder?: string;
}>(), {
  placeholder: 'Buscar...'
});
const emit = defineEmits(['update:modelValue', 'search']);

const search = ref(props.modelValue || '');
const isSearching = ref(false);
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

watch(() => props.modelValue, (val) => {
  if (val !== undefined && val !== search.value) {
    search.value = val;
  }
});

function onInput() {
  emit('update:modelValue', search.value);

  // Debounce live search
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }

  isSearching.value = true;
  debounceTimer = setTimeout(() => {
    emitSearch();
    isSearching.value = false;
  }, 400);
}

function emitSearch() {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }
  isSearching.value = false;
  emit('search', search.value);
}

function clearSearch() {
  search.value = '';
  emit('update:modelValue', '');
  emit('search', '');
}

onUnmounted(() => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
});
</script>
