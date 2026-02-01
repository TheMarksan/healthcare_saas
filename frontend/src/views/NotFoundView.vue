<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center px-4">
    <!-- 404 -->
    <div class="mb-8">
      <div class="text-[150px] sm:text-[200px] font-bold text-gray-200 dark:text-gray-700 select-none">
        404
      </div>
    </div>

    <!-- Content -->
    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3 text-center">
      Página não encontrada
    </h1>
    <p class="text-gray-500 dark:text-gray-400 text-center max-w-md mb-8">
      A página que você está procurando não existe ou foi movida para outro endereço.
    </p>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-3">
      <Button @click="$router.back()" variant="outline">
        <ArrowLeft class="w-4 h-4 mr-2" />
        Voltar
      </Button>
      <Button @click="$router.push('/dashboard')">
        <Home class="w-4 h-4 mr-2" />
        Ir para Início
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, Home } from 'lucide-vue-next';
import { Button } from '@/components/ui';
</script>
