<template>
  <div class="min-h-[calc(100vh-4rem)] flex flex-col">
    <!-- Header -->
    <PageHeader
      title="Sobre o Sistema"
      subtitle="Healthcare SaaS - Análise de dados de operadoras de saúde"
    >
      <template #mobile-toggle>
        <ThemeToggle />
      </template>
      <template #actions>
        <div class="hidden sm:block">
          <ThemeToggle />
        </div>
      </template>
    </PageHeader>

    <!-- Content -->
    <div class="flex-1 space-y-6">
      <!-- Main Description -->
      <Card>
        <div class="flex items-start gap-4">
          <div class="p-3 rounded-xl bg-primary/10">
            <HeartPulse class="w-8 h-8 text-primary" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Healthcare SaaS
            </h2>
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed">
              Projeto de SaaS vertical focado em healthcare, com ênfase em tradeoffs técnicos de
              processamento de dados, técnicas de normalização, consumo de APIs, queries otimizadas
              e paginação eficiente no frontend. O sistema proporciona dashboards e estatísticas
              sobre despesas de eventos/sinistros em operadoras de healthcare, com dados dos últimos
              trimestres disponíveis.
            </p>
          </div>
        </div>
      </Card>

      <!-- Dados Disponíveis -->
      <Card>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Calendar class="w-5 h-5 text-primary" />
          Dados Disponíveis
        </h3>
        <div class="space-y-4">
          <p class="text-gray-600 dark:text-gray-300 leading-relaxed">
            O sistema contém dados de despesas com eventos/sinistros dos seguintes trimestres:
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <span class="font-semibold text-gray-900 dark:text-white">1º Trimestre 2025</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Data base: 01/01/2025</p>
            </div>
            <div class="p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <span class="font-semibold text-gray-900 dark:text-white">2º Trimestre 2025</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Data base: 01/04/2025</p>
            </div>
            <div class="p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <span class="font-semibold text-gray-900 dark:text-white">3º Trimestre 2025</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Data base: 01/07/2025</p>
            </div>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 italic">
            Os dados são atualizados conforme disponibilização pela ANS no Portal de Dados Abertos.
          </p>
        </div>
      </Card>

      <!-- ANS Section -->
      <Card>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Building class="w-5 h-5 text-primary" />
          Fonte de Dados - ANS
        </h3>
        <div class="space-y-4">
          <p class="text-gray-600 dark:text-gray-300 leading-relaxed">
            Os dados utilizados neste sistema são obtidos da
            <strong>Agência Nacional de Saúde Suplementar (ANS)</strong>, uma autarquia federal
            vinculada ao Ministério da Saúde. A ANS é responsável por regular, normatizar, controlar
            e fiscalizar as atividades que garantem a assistência suplementar à saúde no Brasil.
          </p>
          <p class="text-gray-600 dark:text-gray-300 leading-relaxed">
            A agência disponibiliza dados abertos sobre operadoras de planos de saúde, incluindo
            informações cadastrais, demonstrações contábeis e dados de despesas assistenciais,
            promovendo transparência e permitindo análises do setor de saúde suplementar.
          </p>
          <div class="flex flex-wrap gap-3 pt-2">
            <a
              href="https://dadosabertos.ans.gov.br/"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
            >
              <ExternalLink class="w-4 h-4" />
              Portal de Dados Abertos ANS
            </a>
            <a
              href="https://www.gov.br/ans/pt-br"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <ExternalLink class="w-4 h-4" />
              Site Oficial ANS
            </a>
          </div>
        </div>
      </Card>
    </div>

    <!-- Footer -->
    <footer class="mt-8 py-6 border-t border-gray-200 dark:border-gray-700">
      <div class="text-center text-sm text-gray-500 dark:text-gray-400">
        <p>
          Feito por <span class="font-semibold text-gray-700 dark:text-gray-300">Marcos Melo</span>
          <span class="mx-2">|</span>
          Projeto de Avaliação de SaaS Vertical
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { Card } from '@/components/ui';
import PageHeader from '@/components/PageHeader.vue';
import ThemeToggle from '@/components/ThemeToggle.vue';
import {
  HeartPulse,
  Building,
  ExternalLink,
  Calendar,
} from 'lucide-vue-next';
</script>
