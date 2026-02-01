// Configuração centralizada da API
// Em desenvolvimento: usa proxy do Vite (/api)
// Em produção: usa VITE_API_URL do .env

export const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api';
