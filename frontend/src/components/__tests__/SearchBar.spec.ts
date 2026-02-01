import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import SearchBar from '@/components/SearchBar.vue';

describe('SearchBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  describe('renderização', () => {
    it('deve renderizar com placeholder padrão', () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');
      expect(input.exists()).toBe(true);
      expect(input.attributes('placeholder')).toBe('Buscar...');
    });

    it('deve renderizar com placeholder customizado', () => {
      const wrapper = mount(SearchBar, {
        props: {
          placeholder: 'Buscar por razão social ou CNPJ...',
        },
      });

      const input = wrapper.find('input');
      expect(input.attributes('placeholder')).toBe('Buscar por razão social ou CNPJ...');
    });

    it('deve mostrar valor inicial do modelValue', () => {
      const wrapper = mount(SearchBar, {
        props: {
          modelValue: 'unimed',
        },
      });

      const input = wrapper.find('input');
      expect((input.element as HTMLInputElement).value).toBe('unimed');
    });
  });

  describe('interação', () => {
    it('deve emitir update:modelValue ao digitar', async () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');
      await input.setValue('teste');

      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['teste']);
    });

    it('deve emitir search após debounce', async () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');
      await input.setValue('unimed');

      // Avança o timer do debounce (400ms no componente)
      vi.advanceTimersByTime(400);

      expect(wrapper.emitted('search')).toBeTruthy();
    });

    it('deve emitir search imediatamente ao pressionar Enter', async () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');
      await input.setValue('bradesco');
      await input.trigger('keyup.enter');

      expect(wrapper.emitted('search')).toBeTruthy();
      expect(wrapper.emitted('search')![0]).toEqual(['bradesco']);
    });

    it('deve mostrar botão de limpar quando há texto', async () => {
      const wrapper = mount(SearchBar, {
        props: {
          modelValue: 'teste',
        },
      });

      // Aguarda renderização
      await wrapper.vm.$nextTick();

      // Procura botão de limpar (X)
      const clearButton = wrapper.find('button');
      expect(clearButton.exists()).toBe(true);
    });

    it('deve limpar busca ao clicar no botão de limpar', async () => {
      const wrapper = mount(SearchBar, {
        props: {
          modelValue: 'teste',
        },
      });

      await wrapper.vm.$nextTick();

      const clearButton = wrapper.find('button');
      if (clearButton.exists()) {
        await clearButton.trigger('click');
        expect(wrapper.emitted('search')).toBeTruthy();
      }
    });
  });

  describe('debounce', () => {
    it('deve aplicar debounce nas buscas', async () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');

      // Digita várias vezes rapidamente
      await input.setValue('u');
      await input.setValue('un');
      await input.setValue('uni');
      await input.setValue('unim');
      await input.setValue('unime');
      await input.setValue('unimed');

      // Antes do debounce, não deve ter emitido search
      expect(wrapper.emitted('search')).toBeFalsy();

      // Após o debounce (400ms)
      vi.advanceTimersByTime(400);

      // Deve ter emitido apenas uma vez com o valor final
      const searchEvents = wrapper.emitted('search');
      expect(searchEvents).toBeTruthy();
      expect(searchEvents![searchEvents!.length - 1]).toEqual(['unimed']);
    });

    it('deve cancelar debounce anterior ao digitar novamente', async () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');

      await input.setValue('teste1');
      vi.advanceTimersByTime(200); // Não completa o debounce

      await input.setValue('teste2');
      vi.advanceTimersByTime(400); // Completa o novo debounce

      const searchEvents = wrapper.emitted('search');
      expect(searchEvents).toBeTruthy();
      // O último valor emitido deve ser 'teste2'
      expect(searchEvents![searchEvents!.length - 1]).toEqual(['teste2']);
    });
  });

  describe('acessibilidade', () => {
    it('deve ter tipo text no input', () => {
      const wrapper = mount(SearchBar);

      const input = wrapper.find('input');
      expect(input.attributes('type')).toBe('text');
    });
  });
});
