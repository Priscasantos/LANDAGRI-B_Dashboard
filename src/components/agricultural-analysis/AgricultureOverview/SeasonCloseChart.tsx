import { useMemo } from 'react';
import Card from '../../ui/Card';
import DataTable from '../../ui/DataTable';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName } from '../../../data/glossary';
import {
  buildSeasonClose,
  formatDeltaPct,
  type ConabCrops,
} from '../../../lib/agriP2b';
import conabData from '../../../data/processed/conab_agricultural_data.json';

const PREV_SEASON = '2024/25';
const NEXT_SEASON = '2025/26';
const TOP_N = 6;

/**
 * P2b (3): fechamento safra 24/25 × 25/26 — barra agrupada de produção
 * (mil t) + tabela área×produção com Δ %. 25/26 é previsão CONAB.
 */
export default function SeasonCloseChart(): React.JSX.Element | null {
  const { t: tCharts, locale } = useT('charts');
  const { t: tBody, locale: bodyLocale } = useT('agricultural');

  const rows = useMemo(() => {
    const crops = (conabData as { crops?: ConabCrops }).crops;
    return buildSeasonClose(crops, PREV_SEASON, NEXT_SEASON, TOP_N);
  }, []);

  const tableData = useMemo(
    () =>
      rows.map((r) => ({
        name: translateCropName(r.name, bodyLocale),
        areaPrev: r.areaPrev.toLocaleString(locale),
        areaNext: r.areaNext.toLocaleString(locale),
        deltaArea: formatDeltaPct(r.deltaArea, bodyLocale),
        prodPrev: r.prodPrev.toLocaleString(locale),
        prodNext: r.prodNext.toLocaleString(locale),
        deltaProd: formatDeltaPct(r.deltaProd, bodyLocale),
      })),
    [rows, bodyLocale, locale],
  );

  if (rows.length === 0) return null;

  const categories = rows.map((r) => translateCropName(r.name, bodyLocale));

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-1">{tBody('hSeasonClose')}</h3>
        <p className="text-xs text-fg-muted mb-3">{tBody('seasonForecastNote')}</p>
        <EChartsGroupedBar
          categories={categories}
          series={[
            { name: `${tBody('seasonCloseProd')} ${PREV_SEASON}`, values: rows.map((r) => r.prodPrev) },
            { name: `${tBody('seasonCloseProd')} ${NEXT_SEASON}`, values: rows.map((r) => r.prodNext) },
          ]}
          captionKey="seasonCloseCaption"
          height={400}
        />
      </Card>
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSeasonCloseTable')}</h3>
        <DataTable
          columns={[
            { key: 'name', label: tCharts('crop') },
            { key: 'areaPrev', label: `${tBody('seasonCloseArea')} ${PREV_SEASON}` },
            { key: 'areaNext', label: `${tBody('seasonCloseArea')} ${NEXT_SEASON}` },
            { key: 'deltaArea', label: `${tBody('deltaPctShort')} ${tBody('seasonCloseArea')}` },
            { key: 'prodPrev', label: `${tBody('seasonCloseProd')} ${PREV_SEASON}` },
            { key: 'prodNext', label: `${tBody('seasonCloseProd')} ${NEXT_SEASON}` },
            { key: 'deltaProd', label: `${tBody('deltaPctShort')} ${tBody('seasonCloseProd')}` },
          ]}
          data={tableData as unknown as Record<string, unknown>[]}
        />
      </Card>
    </div>
  );
}
