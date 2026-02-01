<template>
  <select
    :value="modelValue"
    @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    :disabled="disabled"
    :class="cn(
      'flex h-10 w-full rounded-lg border px-3 py-2 text-sm transition-colors appearance-none cursor-pointer',
      'bg-white border-gray-200',
      'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100',
      props.class
    )"
  >
    <slot />
  </select>
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Props {
  modelValue?: string;
  disabled?: boolean;
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

defineEmits(['update:modelValue']);
</script>
