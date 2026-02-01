import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Estatísticas' },
  },
  {
    path: '/operadoras',
    name: 'Operadoras',
    component: () => import('@/views/OperadorasView.vue'),
    meta: { title: 'Operadoras' },
  },
  {
    path: '/operadoras/:registroAns',
    name: 'OperadoraDetail',
    component: () => import('@/views/OperadoraDetailView.vue'),
    meta: { title: 'Detalhes da Operadora' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Update page title on navigation
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'Healthcare'} - Healthcare SaaS`;
  next();
});

export default router;
