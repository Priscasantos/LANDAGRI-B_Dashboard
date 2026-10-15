import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LulcClasses from '../../components/overview/LulcClasses';

describe('LulcClasses (canonical muted badges)', () => {
  it('renders string legend classes as muted badges with clean wrap', () => {
    const { container } = render(
      <LulcClasses classification='["Forest", "Cropland", "Urban"]' />,
    );
    for (const name of ['Forest', 'Cropland', 'Urban']) {
      expect(screen.getByText(name)).toBeInTheDocument();
    }
    // Wrap limpo: container flex com wrap.
    const wrap = container.firstChild as HTMLElement;
    expect(wrap.className).toMatch(/flex-wrap/);
    // Badges canônicos: fundo muted, sem texto branco chapado.
    const badges = container.querySelectorAll('.bg-muted');
    expect(badges.length).toBe(3);
    expect(container.querySelector('.text-white')).toBeNull();
    badges.forEach((badge) => {
      expect((badge as HTMLElement).style.backgroundColor).toBe('');
    });
  });

  it('keeps the color cue as a decorative dot, not a saturated background', () => {
    const { container } = render(<LulcClasses classification='["Forest"]' />);
    expect(container.querySelector('.text-white')).toBeNull();
    const badge = screen.getByText('Forest').closest('.bg-muted') as HTMLElement;
    expect(badge).not.toBeNull();
    const dot = badge.querySelector('span[aria-hidden="true"]') as HTMLElement;
    expect(dot).not.toBeNull();
    // O dot preserva a cor da classe (legenda visual), o badge não.
    expect(dot.style.backgroundColor).not.toBe('');
  });

  it('renders empty state when there is no classification data', () => {
    render(<LulcClasses classification="" />);
    expect(screen.getByText(/no classification data/i)).toBeInTheDocument();
  });
});
