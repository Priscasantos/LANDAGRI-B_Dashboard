import { describe, expect, it } from 'vitest';
import { formatCompactK, formatKpiArea, formatKpiProduction, formatProductivity } from '../../lib/format';

describe('format lib — KPI compacto locale-aware (1×, sem unidade duplicada)', () => {
  it('formata milhares compactos 1× em PT ("94,9 mil")', () => {
    expect(formatCompactK(94928, 'pt-BR')).toBe('94,9 mil');
  });

  it('formata milhares compactos 1× em EN ("94.9k")', () => {
    expect(formatCompactK(94928, 'en')).toBe('94.9k');
  });

  it('não duplica a palavra da unidade (sem "thousand"/"mil" extra)', () => {
    expect(formatKpiProduction(94928, 'pt-BR')).not.toMatch(/thousand/i);
    expect(formatKpiProduction(94928, 'pt-BR')).not.toMatch(/mil.*mil/i);
    expect(formatKpiProduction(94928, 'en')).not.toMatch(/thousand/i);
  });

  it('produção total usa separador decimal do locale', () => {
    expect(formatKpiProduction(294928, 'pt-BR')).toBe('294,9 mil\u00a0t');
    expect(formatKpiProduction(294928, 'en')).toBe('294.9k\u00a0t');
  });

  it('área plantada usa separador decimal do locale', () => {
    expect(formatKpiArea(75232, 'pt-BR')).toBe('75,2 mil\u00a0ha');
    expect(formatKpiArea(75232, 'en')).toBe('75.2k\u00a0ha');
  });

  it('produtividade usa kg/ha com agrupamento do locale e espaço inseparável', () => {
    expect(formatProductivity(4310, 'pt-BR')).toBe('4.310\u00A0kg/ha');
    expect(formatProductivity(4310, 'en')).toBe('4,310\u00A0kg/ha');
  });

  it('valores pequenos (<1000) não usam sufixo compacto', () => {
    expect(formatCompactK(9, 'pt-BR')).toBe('9');
    expect(formatCompactK(9, 'en')).toBe('9');
  });
});
