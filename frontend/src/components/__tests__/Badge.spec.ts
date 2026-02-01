import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { Badge } from '@/components/ui';

describe('Badge', () => {
  describe('renderização', () => {
    it('deve renderizar com conteúdo via slot', () => {
      const wrapper = mount(Badge, {
        slots: {
          default: 'SP',
        },
      });

      expect(wrapper.text()).toBe('SP');
    });

    it('deve aplicar classes base', () => {
      const wrapper = mount(Badge, {
        slots: {
          default: 'Teste',
        },
      });

      expect(wrapper.classes()).toContain('inline-flex');
    });
  });

  describe('variants', () => {
    it('deve aplicar variant default', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'default',
        },
        slots: {
          default: 'Default',
        },
      });

      expect(wrapper.html()).toContain('Default');
    });

    it('deve aplicar variant primary', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'primary',
        },
        slots: {
          default: '301337',
        },
      });

      expect(wrapper.html()).toContain('301337');
    });

    it('deve aplicar variant secondary', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'secondary',
        },
        slots: {
          default: 'Secondary',
        },
      });

      expect(wrapper.html()).toContain('Secondary');
    });

    it('deve aplicar variant destructive', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'destructive',
        },
        slots: {
          default: 'Erro',
        },
      });

      expect(wrapper.html()).toContain('Erro');
    });

    it('deve aplicar variant warning', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'warning',
        },
        slots: {
          default: 'Alerta',
        },
      });

      expect(wrapper.html()).toContain('Alerta');
    });

    it('deve aplicar variant success', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'success',
        },
        slots: {
          default: 'OK',
        },
      });

      expect(wrapper.html()).toContain('OK');
    });

    it('deve aplicar variant outline', () => {
      const wrapper = mount(Badge, {
        props: {
          variant: 'outline',
        },
        slots: {
          default: 'Outline',
        },
      });

      expect(wrapper.html()).toContain('Outline');
    });
  });

  describe('acessibilidade', () => {
    it('deve usar elemento span por padrão', () => {
      const wrapper = mount(Badge, {
        slots: {
          default: 'Teste',
        },
      });

      expect(wrapper.element.tagName.toLowerCase()).toBe('span');
    });
  });
});
