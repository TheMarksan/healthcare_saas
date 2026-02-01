<template>
  <aside
    :class="cn(
      'fixed left-0 top-0 z-50 h-screen backdrop-blur-md border-r shadow-xl transition-all duration-300 ease-in-out',
      'bg-white/95 border-gray-200 dark:bg-gray-900/95 dark:border-gray-700',
      isOpen ? 'w-64' : 'w-16'
    )"
    @mouseenter="!isPinned && (isOpen = true)"
    @mouseleave="!isPinned && (isOpen = false)"
  >
    <!-- Header -->
    <div class="flex items-center justify-between h-16 px-4 border-b border-gray-100 dark:border-gray-800">
      <transition name="fade">
        <router-link v-if="isOpen" to="/dashboard" class="text-xl font-bold text-primary truncate hover:opacity-80 transition-opacity">
          Healthcare
        </router-link>
      </transition>
      <button
        @click="isPinned = !isPinned"
        :class="cn(
          'p-2 rounded-lg transition-all duration-200',
          'hover:bg-secondary dark:hover:bg-gray-800',
          isPinned ? 'text-primary bg-secondary dark:bg-gray-800' : 'text-gray-400 dark:text-gray-500'
        )"
      >
        <Pin v-if="isPinned" class="w-5 h-5" />
        <PinOff v-else class="w-5 h-5" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
      <template v-for="item in menuItems" :key="item.name">
        <router-link
          :to="item.route"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            :class="cn(
              'w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200',
              isActive
                ? 'bg-primary text-white shadow-lg shadow-primary/30'
                : 'text-gray-600 dark:text-gray-400 hover:bg-secondary dark:hover:bg-gray-800 hover:text-primary dark:hover:text-primary'
            )"
          >
            <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
            <transition name="slide-fade">
              <span v-if="isOpen" class="truncate font-medium">{{ item.name }}</span>
            </transition>
          </button>
        </router-link>
      </template>
    </nav>

    <!-- Footer -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100 dark:border-gray-800">
      <button
        :class="cn(
          'w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200',
          'text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500'
        )"
      >
        <LogOut class="w-5 h-5 flex-shrink-0" />
        <transition name="slide-fade">
          <span v-if="isOpen" class="truncate font-medium">Sair</span>
        </transition>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Building2,
  LogOut,
  Pin,
  PinOff,
} from 'lucide-vue-next';

const isOpen = ref(false);
const isPinned = ref(false);

const menuItems = [
  { name: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { name: 'Operadoras', icon: Building2, route: '/operadoras' },
];
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
