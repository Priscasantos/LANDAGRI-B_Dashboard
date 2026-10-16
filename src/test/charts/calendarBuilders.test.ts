import { describe, it, expect } from 'vitest';
import {
  buildGanttOption,
  buildHeatmapOption,
  buildLineOption,
} from '../../components/charts/echarts/echarts-options';

type TooltipFormatter = (params: { data?: unknown; value?: unknown }) => string;

function heatmapFormatterOf(option: unknown): TooltipFormatter | null {
  if (typeof option !== 'object' || option === null) return null;
  const tooltip = (option as { tooltip?: { formatter?: unknown } }).tooltip;
  return typeof tooltip?.formatter === 'function' ? (tooltip.formatter as TooltipFormatter) : null;
}

describe('calendar builders (Fase 2: tips, sufixo %, mês atual)', () => {
  it('heatmap: tooltip usa tip da célula e fallback % localizado', () => {
    const option = buildHeatmapOption({
      theme: 'light',
      locale: 'pt-BR',
      x: ['Out', 'Nov'],
      y: ['Soja'],
      z: [[80, 0]],
      min: 0,
      max: 100,
      showValues: true,
      valueSuffix: '%',
      tips: [['<b>Soja · Out</b><br>UFs ativas: 80% (4/5)', null]],
    });
    const formatter = heatmapFormatterOf(option);
    expect(formatter).not.toBeNull();
    expect(formatter?.({ value: [0, 0, 80] })).toContain('Soja · Out');
    // Célula sem tip → fallback numérico com sufixo.
    expect(formatter?.({ value: [1, 0, 0] })).toContain('%');
  });

  it('line: markLineX marca o mês atual na primeira série', () => {
    const option = buildLineOption({
      theme: 'light',
      locale: 'pt-BR',
      series: [{ name: 'Plantio', x: ['Out', 'Nov'], y: [70, 60] }],
      yMin: 0,
      yMax: 100,
      markLineX: { x: 'Out', name: 'Mês atual' },
    });
    const series = (option as { series?: { markLine?: { data?: { xAxis?: unknown }[] } }[] }).series;
    expect(series?.[0]?.markLine?.data?.[0]?.xAxis).toBe('Out');
  });

  it('gantt: markLineX marca o mês atual no eixo de valor', () => {
    const option = buildGanttOption({
      theme: 'dark',
      locale: 'pt-BR',
      xLabels: ['Out', 'Nov'],
      bars: [{ y: 'Soja P (MT)', start: 0, duration: 1 }],
      markLineX: { position: 0.5, name: 'Mês atual' },
    });
    const series = (option as { series?: { markLine?: { data?: { xAxis?: unknown }[] } }[] }).series;
    const duration = series?.[series.length - 1];
    expect(duration?.markLine?.data?.[0]?.xAxis).toBe(0.5);
  });
});
