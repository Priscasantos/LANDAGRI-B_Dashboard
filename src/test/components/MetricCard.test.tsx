import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricCard from '../../components/ui/MetricCard';

describe('MetricCard', () => {
  it('should render label and value', () => {
    render(<MetricCard icon="🎯" label="Accuracy" value="95%" help="Overall" />);
    expect(screen.getByText('Accuracy')).toBeDefined();
    expect(screen.getByText('95%')).toBeDefined();
    expect(screen.getByText('Overall')).toBeDefined();
  });

  it('should render with icon and default variant', () => {
    const { container } = render(<MetricCard icon="🎯" label="Test" value="50%" />);
    // Should use surface background with border
    expect(container.firstChild).toBeDefined();
  });

  it('should use canonical card tokens instead of saturated gradient backgrounds', () => {
    const { container } = render(
      <MetricCard icon="🎯" label="Accuracy" value="95%" help="Overall" variant="accuracy" />,
    );
    const card = container.firstChild as HTMLElement;
    // Canonical shadcn surface: no chapada, mesma língua do Card.
    expect(card).toHaveClass('bg-card');
    expect(card).toHaveClass('border-border');
    // Sem gradiente inline saturado (light ou dark).
    expect(card.style.background).toBe('');
    expect(card.style.backgroundImage).toBe('');
  });
});
