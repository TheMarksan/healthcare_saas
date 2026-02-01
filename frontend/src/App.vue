
<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <main class="transition-all duration-300 ml-16 p-6">
      <div class="max-w-7xl mx-auto">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme';
import Sidebar from '@/components/Sidebar.vue';

// Initialize theme
const { initTheme, watchSystemPreference } = useTheme();
initTheme();
watchSystemPreference();
</script>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

