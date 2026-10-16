import { useCallback, useMemo } from 'react';
import Papa from 'papaparse';
import { useT } from '../i18n/LanguageContext';
import { getBasename } from '../config/routes';

/** Linha genérica de dataset visível (gráfico ou tabela). */
export type ChartRow = Record<string, unknown>;

export interface ChartFileParts {
  /** Slug da rota (ex. `overview`, `temporal`). Derivado do pathname quando omitido. */
  route?: string;
  /** Iniciativa destacada (ex. `MapBiomas`). Omitida quando ausente. */
  initiative?: string;
  /** Locale ativo (`pt-BR` | `en`) — sempre parte do nome. */
  locale: string;
  /** Identificador do gráfico/tabela. Default `chart`. */
  chartId?: string;
}

/**
 * Normaliza um trecho do nome do arquivo: minúsculas, sem acentos,
 * separadores viram `-`. Vazio → `chart`.
 */
export function slugifyChartPart(raw: string): string {
  const slug = raw
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug === '' ? 'chart' : slug;
}

/** Basename (gh-pages) não entra no nome do arquivo. */
function stripBasename(pathname: string): string {
  const base = getBasename();
  if (base !== '/' && pathname.startsWith(base)) {
    const rest = pathname.slice(base.length);
    return rest === '' ? '/' : rest;
  }
  return pathname;
}

/** `/initiative-analysis/x` → `initiative-analysis-x`; `/` → `overview`. */
export function pathToRoute(pathname: string): string {
  const clean = stripBasename(pathname);
  const parts = clean.split('/').filter((p) => p !== '');
  if (parts.length === 0) return 'overview';
  return slugifyChartPart(parts.join('-'));
}

function activePathname(): string {
  if (typeof window === 'undefined') return '/';
  return window.location.pathname;
}

/**
 * `landagri-{rota}-{iniciativa?}-{locale}-{chart}` — iniciativa/rota/locale
 * sempre presentes (rota cai para o pathname, locale vem do i18n).
 */
export function buildChartFileStem(parts: ChartFileParts): string {
  const route = slugifyChartPart(parts.route ?? pathToRoute(activePathname()));
  const localeSlug = slugifyChartPart(parts.locale);
  const chart = slugifyChartPart(parts.chartId ?? 'chart');
  const initiative =
    parts.initiative === undefined || parts.initiative === ''
      ? ''
      : `-${slugifyChartPart(parts.initiative)}`;
  return `landagri-${route}${initiative}-${localeSlug}-${chart}`;
}

/** Mesmo stem + extensão (`csv` por padrão). */
export function buildChartFileName(parts: ChartFileParts, ext = 'csv'): string {
  return `${buildChartFileStem(parts)}.${slugifyChartPart(ext)}`;
}

/** Serializa linhas via papaparse (cabeçalho + escaping). Vazio → `''`. */
export function rowsToCsv(rows: ChartRow[]): string {
  if (rows.length === 0) return '';
  return Papa.unparse(rows);
}

function downloadTextFile(content: string, filename: string, mimeType: string): void {
  if (typeof document === 'undefined') return;
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** Baixa o dataset visível como CSV (BOM p/ Excel PT). Sem linhas → nada. */
export function downloadRowsAsCsv(rows: ChartRow[], filename: string): void {
  if (rows.length === 0) return;
  downloadTextFile(`\ufeff${rowsToCsv(rows)}`, filename, 'text/csv;charset=utf-8;');
}

export interface UseChartExportInput {
  chartId?: string;
  route?: string;
  initiative?: string;
}

export interface UseChartExportResult {
  fileStem: string;
  fileName: string;
  exportLabel: string;
  exportCsv: (rows: ChartRow[]) => void;
}

/**
 * Nome de arquivo com iniciativa/rota/locale + ação de export CSV do
 * dataset visível (papaparse). Rótulo traduzido via namespace `charts`.
 */
export function useChartExport(input: UseChartExportInput = {}): UseChartExportResult {
  const { t, locale } = useT('charts');
  const fileStem = useMemo<string>(
    () =>
      buildChartFileStem({
        route: input.route ?? pathToRoute(activePathname()),
        initiative: input.initiative,
        locale,
        chartId: input.chartId,
      }),
    [input.route, input.initiative, input.chartId, locale],
  );
  const fileName = useMemo<string>(() => `${fileStem}.csv`, [fileStem]);
  const exportCsv = useCallback(
    (rows: ChartRow[]): void => {
      downloadRowsAsCsv(rows, fileName);
    },
    [fileName],
  );
  return { fileStem, fileName, exportLabel: t('exportCsv'), exportCsv };
}
