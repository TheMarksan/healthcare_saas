<template>
  <header class="mt-6 mb-8">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <!-- Title row with theme toggle on mobile -->
      <div class="flex items-center justify-between sm:justify-start">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-primary dark:text-primary">
            <slot name="title">{{ title }}</slot>
          </h1>
          <p v-if="subtitle || $slots.subtitle" class="text-gray-500 dark:text-gray-400 mt-1 text-sm sm:text-base">
            <slot name="subtitle">{{ subtitle }}</slot>
          </p>
        </div>
        <!-- Theme toggle visible only on mobile, same row as title -->
        <div class="sm:hidden">
          <slot name="mobile-toggle" />
        </div>
      </div>
      <!-- Actions: on mobile shows only select, on desktop shows all -->
      <div v-if="$slots.actions" class="flex items-center gap-4">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
interface Props {
  title?: string;
  subtitle?: string;
}

defineProps<Props>();
</script>
