import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Clock } from 'lucide-react';
import Tabs from '../../components/ui/Tabs';

describe('Tabs', () => {
  it('renders a Lucide icon next to the label when provided', () => {
    render(
      <Tabs
        tabs={[{ id: 'timeline', label: 'Timeline', icon: Clock, content: <div>Body</div> }]}
      />,
    );
    expect(screen.getByText('Timeline')).toBeDefined();
    const button = screen.getByRole('tab', { name: 'Timeline' });
    expect(button.querySelector('svg')).not.toBeNull();
  });

  it('keeps working for tabs without an icon (backward compatible)', () => {
    render(<Tabs tabs={[{ id: 'plain', label: 'Plain', content: <div>Body</div> }]} />);
    const button = screen.getByRole('tab', { name: 'Plain' });
    expect(button.querySelector('svg')).toBeNull();
    expect(screen.getByText('Body')).toBeDefined();
  });

  it('exposes a tablist with aria-selected synced to the active tab', () => {
    render(
      <Tabs
        tabs={[
          { id: 'a', label: 'Alpha', content: <div>Body A</div> },
          { id: 'b', label: 'Beta', content: <div>Body B</div> },
        ]}
      />,
    );
    expect(screen.getByRole('tablist', { name: 'Seções' })).toBeDefined();
    expect(screen.getByRole('tab', { name: 'Alpha' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: 'Beta' })).toHaveAttribute('aria-selected', 'false');
    fireEvent.click(screen.getByRole('tab', { name: 'Beta' }));
    expect(screen.getByRole('tab', { name: 'Beta' })).toHaveAttribute('aria-selected', 'true');
  });

  it('meets the 44px touch target on tab buttons', () => {
    render(<Tabs tabs={[{ id: 'plain', label: 'Plain', content: <div>Body</div> }]} />);
    expect(screen.getByRole('tab', { name: 'Plain' }).className).toContain('min-h-[44px]');
  });
});
