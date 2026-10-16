import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../../components/theme-provider';
import { useTheme, useEffectiveTheme } from '../../hooks/use-theme';

/** Test consumer exposing provider state + resolved effective theme. */
function TestConsumer() {
  const { theme, setTheme } = useTheme();
  const effective = useEffectiveTheme();
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <span data-testid="effective-value">{effective}</span>
      <button data-testid="set-light" onClick={() => setTheme('light')}>
        Light
      </button>
      <button data-testid="set-dark" onClick={() => setTheme('dark')}>
        Dark
      </button>
      <button data-testid="set-system" onClick={() => setTheme('system')}>
        System
      </button>
    </div>
  );
}

function mockMatchMedia(darkMatches: boolean): void {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)' ? darkMatches : false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
    })),
  });
}

describe('ThemeProvider (system/light/dark)', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark', 'light');
    mockMatchMedia(false);
  });

  it('defaults to system theme when nothing is stored', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId('theme-value').textContent).toBe('system');
  });

  it('resolves effective theme to light when system prefers light', () => {
    mockMatchMedia(false);
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId('effective-value').textContent).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('resolves effective theme to dark when system prefers dark', () => {
    mockMatchMedia(true);
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId('effective-value').textContent).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('sets explicit light theme and persists it', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    fireEvent.click(screen.getByTestId('set-light'));
    expect(screen.getByTestId('theme-value').textContent).toBe('light');
    expect(localStorage.getItem('landagri-theme')).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('sets explicit dark theme, applies .dark and persists it', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    fireEvent.click(screen.getByTestId('set-dark'));
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
    expect(screen.getByTestId('effective-value').textContent).toBe('dark');
    expect(localStorage.getItem('landagri-theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('reads a stored theme on mount', () => {
    localStorage.setItem('landagri-theme', 'dark');
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('falls back to system for an unknown stored value', () => {
    localStorage.setItem('landagri-theme', 'midnight-neon');
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId('theme-value').textContent).toBe('system');
  });

  it('throws when useTheme is used outside ThemeProvider', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow(
      'useTheme must be used within a ThemeProvider',
    );
    spy.mockRestore();
  });
});
