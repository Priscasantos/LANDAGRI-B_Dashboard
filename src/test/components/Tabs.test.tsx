import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
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
    const button = screen.getByRole('button', { name: 'Timeline' });
    expect(button.querySelector('svg')).not.toBeNull();
  });

  it('keeps working for tabs without an icon (backward compatible)', () => {
    render(<Tabs tabs={[{ id: 'plain', label: 'Plain', content: <div>Body</div> }]} />);
    const button = screen.getByRole('button', { name: 'Plain' });
    expect(button.querySelector('svg')).toBeNull();
    expect(screen.getByText('Body')).toBeDefined();
  });
});
