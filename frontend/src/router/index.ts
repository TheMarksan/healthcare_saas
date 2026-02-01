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
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/LogsView.vue'),
    meta: { title: 'Logs do Sistema' },
  },
  {
    path: '/sobre',
    name: 'Sobre',
    component: () => import('@/views/SobreView.vue'),
    meta: { title: 'Sobre' },
  },
  {
    path: '/erro',
    name: 'Error',
    component: () => import('@/views/ErrorView.vue'),
    meta: { title: 'Erro' },
  },
  {
    path: '/sem-conexao',
    name: 'ConnectionError',
    component: () => import('@/views/ConnectionErrorView.vue'),
    meta: { title: 'Sem Conexão' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Página não encontrada' },
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
