<template>
  <div :class="cn(cardVariants({ variant }), props.class)">
    <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
      <slot name="header" />
    </div>
    <div :class="cn('p-6', noPadding && 'p-0')">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cardVariants = cva(
  'rounded-xl shadow-sm border overflow-hidden transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-white border-gray-100 dark:bg-gray-800 dark:border-gray-700',
        elevated: 'bg-white border-gray-100 shadow-lg dark:bg-gray-800 dark:border-gray-700',
        ghost: 'bg-transparent border-transparent shadow-none',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

type CardVariants = VariantProps<typeof cardVariants>;

interface Props {
  variant?: CardVariants['variant'];
  noPadding?: boolean;
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  noPadding: false,
});
</script>
