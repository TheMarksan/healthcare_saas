<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <!-- Error Icon -->
    <div
      :class="[
        'w-20 h-20 rounded-full flex items-center justify-center mb-6',
        iconBgClass
      ]"
    >
      <component :is="iconComponent" :class="['w-10 h-10', iconColorClass]" />
    </div>

    <!-- Title -->
    <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2 text-center">
      {{ title }}
    </h3>

    <!-- Message -->
    <p class="text-gray-500 dark:text-gray-400 text-center max-w-md mb-6">
      {{ message }}
    </p>

    <!-- Details (optional) -->
    <div
      v-if="details"
      class="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2 mb-6 max-w-md"
    >
      <code class="text-sm text-gray-600 dark:text-gray-400 break-all">
        {{ details }}
      </code>
    </div>

    <!-- Actions -->
    <div class="flex gap-3">
      <Button
        v-if="showRetry"
        @click="$emit('retry')"
        :disabled="retrying"
        class="min-w-[120px]"
      >
        <RefreshCw v-if="!retrying" class="w-4 h-4 mr-2" />
        <svg
          v-else
          class="animate-spin w-4 h-4 mr-2"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        {{ retrying ? 'Tentando...' : 'Tentar Novamente' }}
      </Button>
      <Button
        v-if="showHome"
        variant="outline"
        @click="$router.push('/')"
      >
        <Home class="w-4 h-4 mr-2" />
        Ir para Início
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import {
  WifiOff,
  ServerCrash,
  AlertTriangle,
  FileQuestion,
  RefreshCw,
  Home,
  ShieldAlert
} from 'lucide-vue-next';
import { Button } from '@/components/ui';

type ErrorType = 'network' | 'server' | 'not-found' | 'forbidden' | 'generic';

interface Props {
  type?: ErrorType;
  title?: string;
  message?: string;
  details?: string;
  showRetry?: boolean;
  showHome?: boolean;
  retrying?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'generic',
  showRetry: true,
  showHome: false,
  retrying: false,
});

defineEmits<{
  (e: 'retry'): void;
}>();

const errorConfig = computed(() => {
  const configs: Record<ErrorType, {
    icon: typeof WifiOff;
    title: string;
    message: string;
    bgClass: string;
    colorClass: string;
  }> = {
    network: {
      icon: WifiOff,
      title: 'Erro de Conexão',
      message: 'Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente.',
      bgClass: 'bg-red-100 dark:bg-red-900/30',
      colorClass: 'text-red-500 dark:text-red-400',
    },
    server: {
      icon: ServerCrash,
      title: 'Erro no Servidor',
      message: 'O servidor encontrou um problema ao processar sua solicitação. Por favor, tente novamente em alguns instantes.',
      bgClass: 'bg-orange-100 dark:bg-orange-900/30',
      colorClass: 'text-orange-500 dark:text-orange-400',
    },
    'not-found': {
      icon: FileQuestion,
      title: 'Não Encontrado',
      message: 'O recurso solicitado não foi encontrado. Verifique se o endereço está correto.',
      bgClass: 'bg-blue-100 dark:bg-blue-900/30',
      colorClass: 'text-blue-500 dark:text-blue-400',
    },
    forbidden: {
      icon: ShieldAlert,
      title: 'Acesso Negado',
      message: 'Você não tem permissão para acessar este recurso.',
      bgClass: 'bg-yellow-100 dark:bg-yellow-900/30',
      colorClass: 'text-yellow-600 dark:text-yellow-400',
    },
    generic: {
      icon: AlertTriangle,
      title: 'Algo deu errado',
      message: 'Ocorreu um erro inesperado. Por favor, tente novamente.',
      bgClass: 'bg-gray-100 dark:bg-gray-800',
      colorClass: 'text-gray-500 dark:text-gray-400',
    },
  };

  return configs[props.type];
});

const iconComponent = computed(() => errorConfig.value.icon);
const iconBgClass = computed(() => errorConfig.value.bgClass);
const iconColorClass = computed(() => errorConfig.value.colorClass);
const title = computed(() => props.title || errorConfig.value.title);
const message = computed(() => props.message || errorConfig.value.message);
</script>
