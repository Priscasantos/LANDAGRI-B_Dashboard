import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Target } from 'lucide-react';
import SectionCards from '../../components/ui/SectionCards';

const items = [
  { key: 'a', label: 'Iniciativas', value: '12' },
  { key: 'b', label: 'Cobertura', value: 'Global' },
];

const itemsWithIcon = [
  { key: 'a', label: 'Iniciativas', value: '12', Icon: Target },
];

describe('SectionCards (Fase 2: SummaryCards successor)', () => {
  it('renders Overview variant with list semantics', () => {
    render(<SectionCards variant="overview" title="Resumo" items={items} />);
    expect(screen.getByRole('list', { name: /resumo/i })).toBeInTheDocument();
    expect(screen.getByText('Iniciativas')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('renders Initiative variant with list semantics', () => {
    render(<SectionCards variant="initiative" title="Detalhes" items={items} />);
    expect(screen.getByRole('list', { name: /detalhes/i })).toBeInTheDocument();
    expect(screen.getByText('Cobertura')).toBeInTheDocument();
  });

  it('supports icons with aria-hidden decoration', () => {
    const { container } = render(
      <SectionCards variant="overview" title="Com ícone" items={itemsWithIcon} iconAriaHidden />,
    );
    expect(container.querySelector('[aria-hidden="true"]')).not.toBeNull();
  });

  it('renders empty state instead of crashing on no items', () => {
    render(<SectionCards variant="overview" title="Vazio" items={[]} />);
    expect(screen.getByText(/nenhum dado/i)).toBeInTheDocument();
  });
});
