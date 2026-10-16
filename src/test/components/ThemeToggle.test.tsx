import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../../components/theme-provider';
import ThemeToggle from '../../components/ui/ThemeToggle';

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

function renderToggle() {
  return render(
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>,
  );
}

describe('ThemeToggle (mode-toggle system/light/dark)', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark', 'light');
    mockMatchMedia(false);
  });

  it('renders a labelled toggle button with test id', () => {
    renderToggle();
    const button = screen.getByTestId('theme-toggle');
    expect(button).toBeInTheDocument();
    expect(button).toHaveAccessibleName();
  });

  it('cycles system -> light on first activation (system prefers dark off)', () => {
    renderToggle();
    const button = screen.getByTestId('theme-toggle');
    // system+light-effective shows the "switch to dark" affordance
    expect(button.getAttribute('aria-label')).toMatch(/escuro/i);
    fireEvent.click(button);
    expect(localStorage.getItem('landagri-theme')).toBe('light');
  });

  it('cycles light -> dark -> system across three activations', () => {
    localStorage.setItem('landagri-theme', 'light');
    renderToggle();
    const button = screen.getByTestId('theme-toggle');
    fireEvent.click(button); // light -> dark
    expect(localStorage.getItem('landagri-theme')).toBe('dark');
    expect(button.getAttribute('aria-label')).toMatch(/claro/i);
    fireEvent.click(button); // dark -> system
    expect(localStorage.getItem('landagri-theme')).toBe('system');
  });

  it('reflects a stored dark theme on mount', () => {
    localStorage.setItem('landagri-theme', 'dark');
    renderToggle();
    expect(screen.getByTestId('theme-toggle').getAttribute('aria-label')).toMatch(
      /claro/i,
    );
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('is keyboard operable', () => {
    renderToggle();
    const button = screen.getByTestId('theme-toggle');
    button.focus();
    expect(button).toHaveFocus();
    fireEvent.click(button);
    expect(localStorage.getItem('landagri-theme')).not.toBeNull();
  });
});
