<template>
  <div>
    <select
      v-model="selectedUf"
      @change="$emit('update:uf', selectedUf)"
      class="w-56 px-3 py-2 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary transition-colors cursor-pointer"
    >
      <option value="" class="dark:bg-gray-800">Todos os estados</option>
      <option v-for="uf in ufs" :key="uf" :value="uf" class="dark:bg-gray-800">{{ uf }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue';
const props = defineProps<{ modelValue?: string }>();
const emit = defineEmits(['update:uf']);
const ufs = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
];
const selectedUf = ref(props.modelValue || '');

watchEffect(() => {
  if (props.modelValue !== undefined) selectedUf.value = props.modelValue;
});
</script>

<!-- Removido CSS customizado, agora tudo é Tailwind -->
