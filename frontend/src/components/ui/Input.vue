<template>
  <input
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="cn(
      'flex h-10 w-full rounded-lg border px-3 py-2 text-sm transition-colors',
      'bg-white border-gray-200 placeholder:text-gray-400',
      'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 dark:placeholder:text-gray-500',
      props.class
    )"
  />
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Props {
  modelValue?: string;
  type?: string;
  placeholder?: string;
  disabled?: boolean;
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
});

defineEmits(['update:modelValue']);
</script>
