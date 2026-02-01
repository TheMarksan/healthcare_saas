<template>
  <button
    ref="buttonRef"
    @click="handleToggle"
    :class="cn(
      'relative p-2.5 rounded-xl transition-all duration-300 overflow-visible',
      'hover:bg-gray-100 dark:hover:bg-gray-700',
      'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
      'dark:focus:ring-offset-gray-800'
    )"
    :aria-label="isDark ? 'Ativar modo claro' : 'Ativar modo escuro'"
  >
    <div class="relative w-6 h-6">
      <!-- Sun Icon -->
      <Sun
        ref="sunRef"
        :class="cn(
          'absolute inset-0 w-6 h-6 text-amber-500 transition-all duration-500',
          isDark ? 'opacity-0 rotate-90 scale-0' : 'opacity-100 rotate-0 scale-100'
        )"
      />
      <!-- Moon Icon -->
      <Moon
        ref="moonRef"
        :class="cn(
          'absolute inset-0 w-6 h-6 text-indigo-400 transition-all duration-500',
          isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'
        )"
      />
    </div>
  </button>

  <!-- Circular Transition Overlay with Fade Rings -->
  <Teleport to="body">
    <div
      v-if="showOverlay"
      class="fixed inset-0 pointer-events-none z-[9998]"
    >
      <!-- Multiple fade rings for softer effect -->
      <div
        v-for="ring in rings"
        :key="ring.id"
        class="absolute rounded-full"
        :style="{
          left: `${iconPosition.x}px`,
          top: `${iconPosition.y}px`,
          transform: 'translate(-50%, -50%)',
          width: `${ring.size}px`,
          height: `${ring.size}px`,
          background: ring.gradient,
          opacity: 0,
          animation: `${isExpanding ? 'ring-expand-fade' : 'ring-contract-fade'} ${ring.duration}s ${ring.easing} forwards`,
          animationDelay: `${ring.delay}s`,
        }"
      />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import { cn } from '@/lib/utils';
import { Sun, Moon } from 'lucide-vue-next';
import { useTheme } from '@/composables/useTheme';

const buttonRef = ref<HTMLButtonElement | null>(null);
const sunRef = ref<HTMLElement | null>(null);
const moonRef = ref<HTMLElement | null>(null);
const { isDark, isTransitioning, transitionOrigin, toggleTheme } = useTheme();

const showOverlay = ref(false);
const isExpanding = ref(true);
const iconPosition = reactive({ x: 0, y: 0 });

const handleToggle = (event: MouseEvent) => {
  // Get the active icon's center position
  if (buttonRef.value) {
    const rect = buttonRef.value.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    // Store icon position for rings
    iconPosition.x = centerX;
    iconPosition.y = centerY;

    // Create a synthetic event with icon center
    const syntheticEvent = {
      clientX: centerX,
      clientY: centerY,
    } as MouseEvent;

    isExpanding.value = isDark.value; // Expanding when going to light
    showOverlay.value = true;

    toggleTheme(syntheticEvent);

    // Hide overlay after animation completes
    setTimeout(() => {
      showOverlay.value = false;
    }, 1200);
  } else {
    toggleTheme(event);
  }
};

// Generate multiple rings with different properties - larger fade effect
const rings = computed(() => {
  const maxRadius = Math.hypot(
    Math.max(iconPosition.x || window.innerWidth / 2, window.innerWidth - (iconPosition.x || window.innerWidth / 2)),
    Math.max(iconPosition.y || window.innerHeight / 2, window.innerHeight - (iconPosition.y || window.innerHeight / 2))
  ) * 2.5;

  const baseColor = isExpanding.value
    ? 'rgba(255, 200, 50' // Warm golden light
    : 'rgba(99, 102, 241'; // Cool indigo

  return [
    // Core bright ring
    {
      id: 1,
      size: maxRadius,
      gradient: `radial-gradient(circle, ${baseColor}, 0.6) 0%, ${baseColor}, 0.3) 20%, ${baseColor}, 0.1) 50%, transparent 70%)`,
      duration: 1.0,
      delay: 0,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
    },
    // Secondary glow
    {
      id: 2,
      size: maxRadius * 0.85,
      gradient: `radial-gradient(circle, ${baseColor}, 0.7) 0%, ${baseColor}, 0.4) 25%, ${baseColor}, 0.1) 55%, transparent 75%)`,
      duration: 0.9,
      delay: 0.03,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
    },
    // Soft outer ring
    {
      id: 3,
      size: maxRadius * 1.15,
      gradient: `radial-gradient(circle, ${baseColor}, 0.35) 0%, ${baseColor}, 0.15) 40%, ${baseColor}, 0.05) 65%, transparent 85%)`,
      duration: 1.05,
      delay: 0.01,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
    },
    // Outermost fade halo
    {
      id: 4,
      size: maxRadius * 1.35,
      gradient: `radial-gradient(circle, ${baseColor}, 0.2) 0%, ${baseColor}, 0.08) 45%, transparent 75%)`,
      duration: 1.1,
      delay: 0,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
    },
    // Extra soft ambient ring
    {
      id: 5,
      size: maxRadius * 1.5,
      gradient: `radial-gradient(circle, ${baseColor}, 0.1) 0%, transparent 60%)`,
      duration: 1.15,
      delay: 0,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
    },
  ];
});
</script>

<style>
/* Ring animations with stronger fade in-out */
@keyframes ring-expand-fade {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
  75% {
    opacity: 0.4;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

@keyframes ring-contract-fade {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
  25% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.85;
  }
  85% {
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
}

/* View Transition API styles for the circular expanding effect */
::view-transition-old(root),
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}

::view-transition-old(root) {
  z-index: 1;
}

::view-transition-new(root) {
  z-index: 9999;
}

/* Dark mode: circle contracts (light shrinks to reveal dark) */
.dark::view-transition-old(root) {
  z-index: 9999;
}

.dark::view-transition-new(root) {
  z-index: 1;
}

/* Circular clip animation - smoother and longer */
@keyframes clip-circle-expand {
  0% {
    clip-path: circle(0% at var(--origin-x, 50%) var(--origin-y, 50%));
  }
  100% {
    clip-path: circle(150% at var(--origin-x, 50%) var(--origin-y, 50%));
  }
}

@keyframes clip-circle-contract {
  0% {
    clip-path: circle(150% at var(--origin-x, 50%) var(--origin-y, 50%));
  }
  100% {
    clip-path: circle(0% at var(--origin-x, 50%) var(--origin-y, 50%));
  }
}

/* Light mode transition: new view expands from icon */
::view-transition-new(root) {
  animation: clip-circle-expand 0.9s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Dark mode transition: old view contracts to icon */
.dark::view-transition-old(root) {
  animation: clip-circle-contract 0.9s cubic-bezier(0.22, 1, 0.36, 1);
}

.dark::view-transition-new(root) {
  animation: none;
}
</style>
