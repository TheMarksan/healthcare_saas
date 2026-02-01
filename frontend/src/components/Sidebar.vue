<template>
  <!-- Mobile Header (< 600px) -->
  <header
    class="mobile-header fixed top-0 left-0 right-0 z-50 h-14 px-4 flex items-center justify-between bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-sm"
  >
    <router-link to="/dashboard" class="text-xl font-bold text-primary hover:opacity-80 transition-opacity">
      Healthcare
    </router-link>
    <button
      @click="mobileMenuOpen = !mobileMenuOpen"
      class="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-secondary dark:hover:bg-gray-800 transition-colors"
      aria-label="Menu"
    >
      <X v-if="mobileMenuOpen" class="w-6 h-6" />
      <Menu v-else class="w-6 h-6" />
    </button>
  </header>

  <!-- Mobile Dropdown Menu -->
  <transition name="dropdown">
    <div
      v-if="mobileMenuOpen"
      class="mobile-header fixed top-14 left-0 right-0 z-40 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-lg"
    >
      <nav class="px-4 py-3 space-y-1">
        <template v-for="item in menuItems" :key="item.name">
          <router-link
            :to="item.route"
            custom
            v-slot="{ isActive, navigate }"
          >
            <button
              @click="navigate(); mobileMenuOpen = false"
              :class="cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                isActive
                  ? 'bg-primary text-white shadow-lg shadow-primary/30'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-secondary dark:hover:bg-gray-800 hover:text-primary dark:hover:text-primary'
              )"
            >
              <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
              <span class="font-medium">{{ item.name }}</span>
            </button>
          </router-link>
        </template>
      </nav>
    </div>
  </transition>

  <!-- Mobile backdrop -->
  <transition name="fade">
    <div
      v-if="mobileMenuOpen"
      class="mobile-header fixed inset-0 top-14 z-30 bg-black/20 backdrop-blur-sm"
      @click="mobileMenuOpen = false"
    />
  </transition>

  <!-- Desktop Sidebar (>= 600px) -->
  <aside
    :class="cn(
      'desktop-sidebar fixed left-0 top-0 z-50 h-screen backdrop-blur-md border-r shadow-xl transition-all duration-300 ease-in-out',
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
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Building2,
  Pin,
  PinOff,
  Menu,
  X,
  FileWarning,
  Info,
} from 'lucide-vue-next';

const isOpen = ref(false);
const isPinned = ref(false);
const mobileMenuOpen = ref(false);

const menuItems = [
  { name: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { name: 'Operadoras', icon: Building2, route: '/operadoras' },
  { name: 'Logs', icon: FileWarning, route: '/logs' },
  { name: 'Sobre', icon: Info, route: '/sobre' },
];
</script>

<style scoped>
/* Hide mobile header on desktop, show on mobile */
.mobile-header {
  display: none;
}

/* Hide desktop sidebar on mobile, show on desktop */
.desktop-sidebar {
  display: flex;
  flex-direction: column;
}

@media (max-width: 599px) {
  .mobile-header {
    display: flex;
  }

  .desktop-sidebar {
    display: none;
  }
}

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

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
