import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeCustomizer from '../../components/ThemeCustomizer';

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

beforeEach(() => {
  installMemoryStorage();
});

describe('ThemeCustomizer (density/radius only)', () => {
  it('renders a labelled trigger button', () => {
    render(<ThemeCustomizer />);
    expect(
      screen.getByRole('button', { name: /personalizar densidade/i }),
    ).toBeInTheDocument();
  });

  it('opens panel with keyboard and lets user pick density + radius', () => {
    render(<ThemeCustomizer />);
    const trigger = screen.getByRole('button', { name: /personalizar densidade/i });
    trigger.focus();
    expect(trigger).toHaveFocus();
    fireEvent.click(trigger);
    expect(screen.getByRole('group', { name: /densidade/i })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /raio/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('radio', { name: /compacta/i }));
    expect(screen.getByRole('radio', { name: /compacta/i })).toBeChecked();
    fireEvent.click(screen.getByRole('radio', { name: /grande/i }));
    expect(screen.getByRole('radio', { name: /grande/i })).toBeChecked();
  });

  it('persists choices without new heavy deps', () => {
    render(<ThemeCustomizer />);
    fireEvent.click(screen.getByRole('button', { name: /personalizar densidade/i }));
    fireEvent.click(screen.getByRole('radio', { name: /compacta/i }));
    expect(localStorage.getItem('landagri-density')).toBe('compact');
    expect(document.documentElement.dataset.density).toBe('compact');
  });
});
