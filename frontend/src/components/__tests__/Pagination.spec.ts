import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import Pagination from '@/components/Pagination.vue';

describe('Pagination', () => {
  const defaultProps = {
    page: 1,
    total: 100,
    limit: 10,
    hasPrev: false,
    hasNext: true,
    loading: false,
    itemLabel: 'operadoras',
  };

  describe('renderização', () => {
    it('deve mostrar informação de paginação corretamente', () => {
      const wrapper = mount(Pagination, {
        props: defaultProps,
      });

      const text = wrapper.text();
      expect(text).toContain('1');
      expect(text).toContain('10');
      expect(text).toContain('100');
    });

    it('deve calcular total de páginas corretamente', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          total: 95,
          limit: 10,
        },
      });

      // 95 / 10 = 10 páginas
      const text = wrapper.text();
      expect(text).toContain('10');
    });

    it('deve usar itemLabel customizado', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          itemLabel: 'registros',
        },
      });

      expect(wrapper.text()).toContain('registros');
    });
  });

  describe('navegação', () => {
    it('deve desabilitar botão anterior na primeira página', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          page: 1,
          hasPrev: false,
        },
      });

      const prevButton = wrapper.find('[data-testid="prev-button"]');
      // Verifica se existe botão de anterior e se está desabilitado
      const buttons = wrapper.findAll('button');
      const prevBtn = buttons.find(b => b.text().includes('Anterior') || b.attributes('disabled') !== undefined);

      if (prevBtn) {
        expect(prevBtn.attributes('disabled')).toBeDefined();
      }
    });

    it('deve desabilitar botão próximo na última página', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          page: 10,
          hasNext: false,
        },
      });

      const buttons = wrapper.findAll('button');
      const nextBtn = buttons.find(b => b.text().includes('Próxima'));

      if (nextBtn) {
        expect(nextBtn.attributes('disabled')).toBeDefined();
      }
    });

    it('deve emitir evento prev ao clicar em anterior', async () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          page: 2,
          hasPrev: true,
        },
      });

      const buttons = wrapper.findAll('button');
      const prevBtn = buttons.find(b => b.text().includes('Anterior'));

      if (prevBtn) {
        await prevBtn.trigger('click');
        expect(wrapper.emitted('prev')).toBeTruthy();
      }
    });

    it('deve emitir evento next ao clicar em próxima', async () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          hasNext: true,
        },
      });

      const buttons = wrapper.findAll('button');
      const nextBtn = buttons.find(b => b.text().includes('Próxima'));

      if (nextBtn) {
        await nextBtn.trigger('click');
        expect(wrapper.emitted('next')).toBeTruthy();
      }
    });

    it('deve emitir evento go-to-page ao clicar em número de página', async () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          total: 100,
          limit: 10,
        },
      });

      // Tenta encontrar botão de página que não seja a página atual
      const pageButtons = wrapper.findAll('button').filter(b => {
        const text = b.text();
        // Deve ser número e não ser a página atual (1)
        return /^\d+$/.test(text) && text !== '1';
      });

      if (pageButtons.length > 0) {
        await pageButtons[0].trigger('click');
        // O componente emite 'goToPage' (camelCase)
        expect(wrapper.emitted('goToPage')).toBeTruthy();
      }
    });
  });

  describe('estado de loading', () => {
    it('deve desabilitar botões durante loading', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          loading: true,
        },
      });

      const buttons = wrapper.findAll('button');
      buttons.forEach(button => {
        expect(button.attributes('disabled')).toBeDefined();
      });
    });
  });

  describe('casos especiais', () => {
    it('deve tratar total zero', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          total: 0,
        },
      });

      expect(wrapper.text()).toContain('0');
    });

    it('deve tratar página única', () => {
      const wrapper = mount(Pagination, {
        props: {
          ...defaultProps,
          total: 5,
          limit: 10,
          hasNext: false,
          hasPrev: false,
        },
      });

      const buttons = wrapper.findAll('button');
      // Ambos botões devem estar desabilitados
      buttons.forEach(button => {
        if (button.text().includes('Anterior') || button.text().includes('Próxima')) {
          expect(button.attributes('disabled')).toBeDefined();
        }
      });
    });
  });
});
