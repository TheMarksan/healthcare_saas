<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center px-4">
    <!-- Error Icon -->
    <div class="relative mb-8">
      <div class="text-[120px] sm:text-[150px] font-bold text-gray-100 dark:text-gray-800 select-none">
        {{ errorCode }}
      </div>
      <div class="absolute inset-0 flex items-center justify-center">
        <div :class="['p-6 rounded-full', iconBgClass]">
          <component :is="iconComponent" :class="['w-16 h-16 sm:w-20 sm:h-20', iconColorClass]" />
        </div>
      </div>
    </div>

    <!-- Content -->
    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3 text-center">
      {{ title }}
    </h1>
    <p class="text-gray-500 dark:text-gray-400 text-center max-w-md mb-4">
      {{ message }}
    </p>

    <!-- Technical Details -->
    <div
      v-if="showDetails && details"
      class="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3 mb-6 max-w-lg w-full"
    >
      <div class="flex items-center gap-2 mb-2">
        <AlertCircle class="w-4 h-4 text-gray-500" />
        <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
          Detalhes técnicos
        </span>
      </div>
      <code class="text-sm text-gray-600 dark:text-gray-400 break-all block">
        {{ details }}
      </code>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-3 mb-8">
      <Button v-if="canRetry" @click="handleRetry" :disabled="retrying">
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
        {{ retrying ? 'Tentando...' : 'Tentar Novamente' }}
      </Button>
      <Button variant="outline" @click="$router.push('/dashboard')">
        <Home class="w-4 h-4 mr-2" />
        Ir para Início
      </Button>
    </div>

    <!-- Help Text -->
    <p class="text-sm text-gray-400 dark:text-gray-500 text-center">
      Se o problema persistir, entre em contato com o suporte técnico.
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import {
  WifiOff,
  ServerCrash,
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  Home,
} from 'lucide-vue-next';
import { Button } from '@/components/ui';

type ErrorType = 'network' | 'server' | '403' | '500' | 'generic';

const route = useRoute();
const retrying = ref(false);

// Props from route query or defaults
const errorType = computed<ErrorType>(() => {
  const type = route.query.type as string;
  if (['network', 'server', '403', '500', 'generic'].includes(type)) {
    return type as ErrorType;
  }
  return 'generic';
});

const errorCode = computed(() => route.query.code || getDefaultCode(errorType.value));
const details = computed(() => route.query.details as string | undefined);
const showDetails = computed(() => route.query.showDetails !== 'false');
const canRetry = computed(() => route.query.canRetry !== 'false');

function getDefaultCode(type: ErrorType): string {
  const codes: Record<ErrorType, string> = {
    network: 'OFFLINE',
    server: '500',
    '403': '403',
    '500': '500',
    generic: 'ERRO',
  };
  return codes[type];
}

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
      title: 'Sem Conexão',
      message: 'Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente.',
      bgClass: 'bg-red-100 dark:bg-red-900/30',
      colorClass: 'text-red-500 dark:text-red-400',
    },
    server: {
      icon: ServerCrash,
      title: 'Erro no Servidor',
      message: 'O servidor encontrou um problema ao processar sua solicitação. Nossa equipe foi notificada.',
      bgClass: 'bg-orange-100 dark:bg-orange-900/30',
      colorClass: 'text-orange-500 dark:text-orange-400',
    },
    '403': {
      icon: ShieldAlert,
      title: 'Acesso Negado',
      message: 'Você não tem permissão para acessar este recurso. Verifique suas credenciais ou entre em contato com o administrador.',
      bgClass: 'bg-yellow-100 dark:bg-yellow-900/30',
      colorClass: 'text-yellow-600 dark:text-yellow-400',
    },
    '500': {
      icon: ServerCrash,
      title: 'Erro Interno',
      message: 'Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde.',
      bgClass: 'bg-red-100 dark:bg-red-900/30',
      colorClass: 'text-red-500 dark:text-red-400',
    },
    generic: {
      icon: AlertTriangle,
      title: 'Algo deu errado',
      message: 'Ocorreu um erro inesperado. Por favor, tente novamente ou retorne à página inicial.',
      bgClass: 'bg-gray-100 dark:bg-gray-800',
      colorClass: 'text-gray-500 dark:text-gray-400',
    },
  };

  return configs[errorType.value];
});

const iconComponent = computed(() => errorConfig.value.icon);
const iconBgClass = computed(() => errorConfig.value.bgClass);
const iconColorClass = computed(() => errorConfig.value.colorClass);
const title = computed(() => (route.query.title as string) || errorConfig.value.title);
const message = computed(() => (route.query.message as string) || errorConfig.value.message);

async function handleRetry() {
  retrying.value = true;

  // If there's a return URL, go back to it
  const returnUrl = route.query.returnUrl as string;
  if (returnUrl) {
    window.location.href = returnUrl;
  } else {
    // Otherwise, go back or reload
    window.location.reload();
  }
}
</script>
