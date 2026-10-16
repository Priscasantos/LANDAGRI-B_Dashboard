import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  slugifyChartPart,
  buildChartFileStem,
  buildChartFileName,
  rowsToCsv,
  downloadRowsAsCsv,
  useChartExport,
} from '../../hooks/use-chart-export';

function stubDownload(): { clicks: string[] } {
  const clicks: string[] = [];
  const createObjectURL = vi.fn(() => 'blob:mock');
  const revokeObjectURL = vi.fn(() => undefined);
  vi.stubGlobal('URL', { createObjectURL, revokeObjectURL });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
    this: HTMLAnchorElement,
  ): void {
    clicks.push(this.download);
  });
  return { clicks };
}

describe('use-chart-export (Expansão #2)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('slugifyChartPart normaliza acentos/espaços e cai para "chart" no vazio', () => {
    expect(slugifyChartPart('Análise Temporal')).toBe('analise-temporal');
    expect(slugifyChartPart('MapBiomas  v2!!')).toBe('mapbiomas-v2');
    expect(slugifyChartPart('')).toBe('chart');
    expect(slugifyChartPart('---')).toBe('chart');
  });

  it('buildChartFileStem inclui rota + iniciativa + locale + chart', () => {
    const stem = buildChartFileStem({
      route: 'temporal',
      initiative: 'MapBiomas',
      locale: 'pt-BR',
      chartId: 'evolucao',
    });
    expect(stem).toBe('landagri-temporal-mapbiomas-pt-br-evolucao');
  });

  it('buildChartFileStem omite iniciativa ausente sem hífens duplos', () => {
    const stem = buildChartFileStem({ route: '/', locale: 'en', chartId: 'x' });
    expect(stem).toBe('landagri-chart-en-x');
    expect(buildChartFileStem({ route: 'temporal', locale: 'pt-BR', chartId: 'x' })).toBe(
      'landagri-temporal-pt-br-x',
    );
  });

  it('buildChartFileName acrescenta a extensão csv por padrão', () => {
    expect(
      buildChartFileName({ route: 'overview', locale: 'pt-BR', chartId: 'tabela' }),
    ).toBe('landagri-overview-pt-br-tabela.csv');
  });

  it('rowsToCsv usa papaparse com cabeçalho e escaping', () => {
    const csv = rowsToCsv([
      { iniciativa: 'A, B', valor: 1 },
      { iniciativa: 'C', valor: 2 },
    ]);
    expect(csv).toContain('iniciativa,valor');
    expect(csv).toContain('"A, B"');
  });

  it('rowsToCsv vazio retorna string vazia', () => {
    expect(rowsToCsv([])).toBe('');
  });

  it('downloadRowsAsCsv dispara download com o filename e não faz nada sem linhas', () => {
    const { clicks } = stubDownload();
    downloadRowsAsCsv([{ a: 1 }], 'landagri-x.csv');
    expect(clicks).toEqual(['landagri-x.csv']);
    downloadRowsAsCsv([], 'landagri-x.csv');
    expect(clicks).toHaveLength(1);
  });

  it('useChartExport monta filename com rota/locale e exporta o dataset visível', () => {
    stubDownload();
    const createSpy = vi.spyOn(document, 'createElement');
    const { result } = renderHook(() =>
      useChartExport({ chartId: 'evolucao', route: 'temporal' }),
    );
    // Default fora do provider = PT.
    expect(result.current.exportLabel).toBe('Exportar CSV');
    expect(result.current.fileName).toBe('landagri-temporal-pt-br-evolucao.csv');
    act(() => {
      result.current.exportCsv([{ ano: 2020, valor: 3 }]);
    });
    const anchor = createSpy.mock.results
      .map((r) => r.value)
      .find((el): el is HTMLAnchorElement => el instanceof HTMLAnchorElement);
    expect(anchor?.download).toBe('landagri-temporal-pt-br-evolucao.csv');
  });
});
