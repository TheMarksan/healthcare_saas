import { ref, watch, computed } from 'vue';

export type Theme = 'light' | 'dark';

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'light');
const isTransitioning = ref(false);
const transitionOrigin = ref({ x: 0, y: 0 });

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark');

  const applyTheme = (newTheme: Theme) => {
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const setTransitionOrigin = (x: number, y: number) => {
    transitionOrigin.value = { x, y };
    // Set CSS variables on root for View Transitions API
    document.documentElement.style.setProperty('--origin-x', `${x}px`);
    document.documentElement.style.setProperty('--origin-y', `${y}px`);
  };

  const toggleTheme = (event?: MouseEvent) => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light';

    // Get click position for transition origin
    if (event) {
      setTransitionOrigin(event.clientX, event.clientY);
    } else {
      setTransitionOrigin(window.innerWidth / 2, window.innerHeight / 2);
    }

    // Check if View Transitions API is supported
    if (document.startViewTransition) {
      isTransitioning.value = true;

      document.startViewTransition(() => {
        theme.value = newTheme;
        applyTheme(newTheme);
      }).finished.then(() => {
        isTransitioning.value = false;
      });
    } else {
      // Fallback for browsers without View Transitions API
      isTransitioning.value = true;
      theme.value = newTheme;
      applyTheme(newTheme);

      setTimeout(() => {
        isTransitioning.value = false;
      }, 800);
    }
  };

  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme;
    applyTheme(newTheme);
  };

  // Initialize theme on first use
  const initTheme = () => {
    // Check system preference
    if (!localStorage.getItem('theme')) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      theme.value = prefersDark ? 'dark' : 'light';
    }
    applyTheme(theme.value);
  };

  // Watch for system preference changes
  const watchSystemPreference = () => {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  };

  return {
    theme,
    isDark,
    isTransitioning,
    transitionOrigin,
    toggleTheme,
    setTheme,
    initTheme,
    watchSystemPreference,
  };
}
