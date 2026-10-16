import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Select from '../../components/ui/Select';

const OPTIONS = [
  { value: 'a', label: 'Alpha' },
  { value: 'b', label: 'Beta' },
];

describe('Select (unified shadcn-style dropdown)', () => {
  it('associates the visible label with the native select', () => {
    render(<Select label="Cultura" options={OPTIONS} value="a" onChange={() => undefined} />);
    const select = screen.getByRole('combobox', { name: 'Cultura' });
    expect(select.getAttribute('id')).not.toBeNull();
    expect(screen.getByText('Cultura').getAttribute('for')).toBe(select.getAttribute('id'));
  });

  it('renders the translated placeholder as a disabled option', () => {
    render(
      <Select
        label="Cultura"
        options={OPTIONS}
        value=""
        onChange={() => undefined}
        placeholder="Selecione..."
      />,
    );
    const placeholder = screen.getByRole('option', { name: 'Selecione...' });
    expect(placeholder).toHaveProperty('disabled', true);
  });

  it('notifies onChange with the selected value', () => {
    const onChange = vi.fn();
    render(<Select label="Cultura" options={OPTIONS} value="a" onChange={onChange} />);
    fireEvent.change(screen.getByRole('combobox', { name: 'Cultura' }), {
      target: { value: 'b' },
    });
    expect(onChange).toHaveBeenCalledWith('b');
  });

  it('meets the 44px touch target with a visible focus style', () => {
    render(<Select label="Cultura" options={OPTIONS} value="a" onChange={() => undefined} />);
    const cls = (screen.getByRole('combobox', { name: 'Cultura' }) as HTMLSelectElement).className;
    expect(cls).toContain('min-h-[44px]');
    expect(cls).toContain('focus-visible:outline-primary');
  });
});
