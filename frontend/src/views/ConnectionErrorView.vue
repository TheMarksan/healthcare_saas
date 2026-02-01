<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center px-4">
    <!-- Icon -->
    <div class="mb-8">
      <div class="p-6 bg-red-100 dark:bg-red-900/30 rounded-full">
        <WifiOff class="w-16 h-16 sm:w-20 sm:h-20 text-red-500 dark:text-red-400" />
      </div>
    </div>

    <!-- Content -->
    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3 text-center">
      Conexão não estabelecida
    </h1>
    <p class="text-gray-500 dark:text-gray-400 text-center max-w-md mb-8">
      Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente.
    </p>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-3">
      <Button @click="retry" :disabled="retrying">
        <RefreshCw v-if="!retrying" class="w-4 h-4 mr-2" />
        <svg
          v-else
          class="animate-spin w-4 h-4 mr-2"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        {{ retrying ? 'Conectando...' : 'Tentar Novamente' }}
      </Button>
      <Button variant="outline" @click="$router.push('/dashboard')">
        <Home class="w-4 h-4 mr-2" />
        Ir para Início
      </Button>
    </div>

    <!-- Help -->
    <div class="mt-12 text-center">
      <p class="text-sm text-gray-400 dark:text-gray-500 mb-2">
        Possíveis causas:
      </p>
      <ul class="text-sm text-gray-500 dark:text-gray-400 space-y-1">
        <li>• Sua conexão com a internet está instável</li>
        <li>• O servidor está temporariamente indisponível</li>
        <li>• Há um firewall bloqueando a conexão</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { WifiOff, RefreshCw, Home } from 'lucide-vue-next';
import { Button } from '@/components/ui';

const route = useRoute();
const router = useRouter();
const retrying = ref(false);

async function retry() {
  retrying.value = true;

  // Se há uma URL de retorno, tenta voltar para ela
  const returnUrl = route.query.returnUrl as string;

  // Aguarda um pouco para dar feedback visual
  await new Promise(resolve => setTimeout(resolve, 1000));

  if (returnUrl) {
    router.push(returnUrl);
  } else {
    // Recarrega a página
    window.location.reload();
  }
}
</script>
