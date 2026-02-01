<template>
  <div>
    <select
      v-model="selectedModalidade"
      @change="$emit('update:modalidade', selectedModalidade)"
      class="w-56 px-3 py-2 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary transition-colors cursor-pointer"
    >
      <option value="" class="dark:bg-gray-800">Todas as modalidades</option>
      <option v-for="mod in modalidades" :key="mod" :value="mod" class="dark:bg-gray-800">{{ mod }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect, onMounted } from 'vue';

const props = defineProps<{ modelValue?: string }>();
const emit = defineEmits(['update:modalidade']);

const modalidades = ref<string[]>([]);
const selectedModalidade = ref(props.modelValue || '');

watchEffect(() => {
  if (props.modelValue !== undefined) selectedModalidade.value = props.modelValue;
});

onMounted(async () => {
  try {
    const res = await fetch('/api/operadoras/modalidades');
    if (res.ok) {
      modalidades.value = await res.json();
    }
  } catch (error) {
    console.error('Erro ao carregar modalidades:', error);
  }
});
</script>
