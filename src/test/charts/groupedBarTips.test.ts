import { describe, it, expect } from 'vitest';
import { buildGroupedBarOption } from '../../components/charts/echarts/echarts-options';

describe('grouped bar tips (tooltip com UFs, aditivo)', () => {
  it('sem tips mantém tooltip padrão do eixo (legado)', () => {
    const option = buildGroupedBarOption({
      categories: ['Cotton'],
      series: [{ name: 'Plantio', values: [42] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const tooltip = option.tooltip as Record<string, unknown>;
    expect(tooltip.trigger).toBe('axis');
    expect(tooltip.formatter).toBeUndefined();
  });

  it('com tips usa HTML pré-formatado por [série][categoria]', () => {
    const option = buildGroupedBarOption({
      categories: ['Cotton'],
      series: [
        { name: 'Plantio', values: [42] },
        { name: 'Colheita', values: [17] },
      ],
      tips: [
        ['<b>Cotton</b><br>Plantio: 42% (MT, GO)'],
        ['<b>Cotton</b><br>Colheita: 17% (MT)'],
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const formatter = (option.tooltip as { formatter: (p: unknown) => string }).formatter;
    expect(typeof formatter).toBe('function');
    const html = formatter([
      { seriesIndex: 0, dataIndex: 0, seriesName: 'Plantio', value: 42, marker: '●' },
      { seriesIndex: 1, dataIndex: 0, seriesName: 'Colheita', value: 17, marker: '●' },
    ]);
    expect(html).toContain('Plantio: 42% (MT, GO)');
    expect(html).toContain('Colheita: 17% (MT)');
  });

  it('tip ausente/null cai no padrão série: valor localizado', () => {
    const option = buildGroupedBarOption({
      categories: ['Cotton'],
      series: [{ name: 'Plantio', values: [42] }],
      tips: [[null]],
      theme: 'light',
      locale: 'pt-BR',
    });
    const formatter = (option.tooltip as { formatter: (p: unknown) => string }).formatter;
    const html = formatter([{ seriesIndex: 0, dataIndex: 0, seriesName: 'Plantio', value: 42, marker: '●' }]);
    expect(html).toContain('Cotton');
    expect(html).toContain('Plantio');
  });
});
