import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from '../../components/ui/Card';

describe('Card', () => {
  it('should render children', () => {
    render(<Card><p>Test content</p></Card>);
    expect(screen.getByText('Test content')).toBeDefined();
  });

  it('should apply padding variants', () => {
    const { container } = render(<Card padding="sm"><p>Content</p></Card>);
    expect(container.firstChild).toHaveClass('p-4');
  });
});
