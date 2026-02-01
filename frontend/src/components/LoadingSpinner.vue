<template>
  <div class="flex flex-col items-center justify-center gap-4 py-12">
    <div class="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
    <span class="text-gray-500 dark:text-gray-400">{{ message }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message?: string;
}

withDefaults(defineProps<Props>(), {
  message: 'Carregando...',
});
</script>
