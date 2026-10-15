import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeCustomizer from '../../components/ThemeCustomizer';
import { ThemeProvider } from '../../components/theme-provider';

// jsdom aqui não expõe localStorage (falha pré-existente também no
// ThemeContext) — stub em memória só para este arquivo.
function installMemoryStorage(): Map<string, string> {
  const store = new Map<string, string>();
  vi.stubGlobal('localStorage', {
    getItem: (k: string) => (store.has(k) ? store.get(k) : null),
    setItem: (k: string, v: string) => void store.set(k, String(v)),
    removeItem: (k: string) => void store.delete(k),
    clear: () => store.clear(),
  } as Storage);
  return store;
}

function renderCustomizer() {
  return render(
    <ThemeProvider>
      <ThemeCustomizer />
    </ThemeProvider>,
  );
}

function openPanel() {
  fireEvent.click(screen.getByRole('button', { name: /personalizar tema/i }));
}

beforeEach(() => {
  installMemoryStorage();
});

describe('ThemeCustomizer (preset + layout)', () => {
  it('renders a labelled trigger button', () => {
    renderCustomizer();
    expect(
      screen.getByRole('button', { name: /personalizar tema/i }),
    ).toBeInTheDocument();
  });

  it('opens panel with preset, density, radius and font options', () => {
    renderCustomizer();
    openPanel();
    expect(screen.getByRole('dialog', { name: /personalizar tema/i })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /predefini/i })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /densidade/i })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /raio/i })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /fonte/i })).toBeInTheDocument();
  });

  it('lets the user pick density + radius with keyboard focus', () => {
    renderCustomizer();
    const trigger = screen.getByRole('button', { name: /personalizar tema/i });
    trigger.focus();
    expect(trigger).toHaveFocus();
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('radio', { name: /compacta/i }));
    expect(screen.getByRole('radio', { name: /compacta/i })).toBeChecked();
    fireEvent.click(screen.getByRole('radio', { name: /grande/i }));
    expect(screen.getByRole('radio', { name: /grande/i })).toBeChecked();
  });

  it('persists density + radius to localStorage and applies to root', () => {
    renderCustomizer();
    openPanel();
    fireEvent.click(screen.getByRole('radio', { name: /compacta/i }));
    expect(localStorage.getItem('landagri-density')).toBe('compact');
    expect(document.documentElement.dataset.density).toBe('compact');
    expect(localStorage.getItem('landagri-radius')).not.toBeNull();
  });

  it('applies a preset and persists its key', () => {
    renderCustomizer();
    openPanel();
    const preset = screen.getByRole('radio', { name: /^verde agro$/i });
    fireEvent.click(preset);
    expect(preset).toBeChecked();
    expect(localStorage.getItem('landagri-preset')).toBe('agro');
    // preset aplica o primary como CSS var na raiz
    expect(
      document.documentElement.style.getPropertyValue('--color-primary'),
    ).not.toBe('');
  });

  it('applies a font choice and persists it', () => {
    renderCustomizer();
    openPanel();
    const mono = screen.getByRole('radio', { name: /mono/i });
    fireEvent.click(mono);
    expect(mono).toBeChecked();
    expect(localStorage.getItem('landagri-font')).not.toBeNull();
  });

  it('restores defaults without new heavy deps', () => {
    renderCustomizer();
    openPanel();
    fireEvent.click(screen.getByRole('radio', { name: /compacta/i }));
    fireEvent.click(screen.getByRole('button', { name: /restaurar padrão/i }));
    expect(localStorage.getItem('landagri-density')).toBe('comfortable');
    expect(document.documentElement.dataset.density).toBe('comfortable');
  });
});
