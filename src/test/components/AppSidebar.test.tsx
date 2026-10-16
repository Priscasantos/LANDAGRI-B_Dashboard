import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { SidebarProvider } from '../../components/ui/sidebar';
import { LanguageProvider } from '../../i18n/LanguageContext';
import AppSidebar from '../../components/layout/AppSidebar';

function renderSidebar(pathname = '/overview') {
  return render(
    <MemoryRouter initialEntries={[pathname]}>
      <LanguageProvider>
        <SidebarProvider>
          <AppSidebar />
        </SidebarProvider>
      </LanguageProvider>
    </MemoryRouter>,
  );
}

describe('AppSidebar collapsible groups (Fase 3)', () => {
  it('renders at most 4 group toggles with aria-expanded', () => {
    renderSidebar();
    const toggles = screen.getAllByRole('button', { expanded: true });
    expect(toggles.length).toBeLessThanOrEqual(4);
    expect(toggles.length).toBeGreaterThan(0);
  });

  it('collapses and re-expands a group on toggle', () => {
    renderSidebar();
    const toggle = screen.getByRole('button', { name: /Território|Territory/ });
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('link', { name: /Iniciativas|Initiatives/ })).toBeDefined();
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    expect(screen.queryByRole('link', { name: /Iniciativas|Initiatives/ })).toBeNull();
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
  });

  it('keeps the active group open and marks the active link', () => {
    renderSidebar('/predictive');
    expect(screen.getByRole('link', { name: /Simulador|Simulator/ })).toHaveAttribute(
      'aria-current',
      'page',
    );
  });

  it('keeps deep-link sub-items reachable (2-level rule)', () => {
    renderSidebar('/agricultural-analysis/overview');
    const sub = screen.getByRole('link', { name: /Panorama|Snapshot/ });
    expect(sub.getAttribute('href')).toBe('/agricultural-analysis/overview');
    expect(sub).toHaveAttribute('aria-current', 'page');
  });
});
