import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsLine from '../../charts/echarts/EChartsLine';
import { useT } from '../../../i18n/LanguageContext';
import { buildPamYieldSeries, PAM_GRAIN_KEYS, PAM_YEARS, type PamUnified } from '../../../lib/agriP2b';
import pamData from '../../../data/processed/pam_unified.json';

/**
 * P2b (1): série de rendimento médio (kg/ha) por cultura PAM 2018–2025 —
 * linha multi-série. Só grãos em escala comparável; fonte viva
 * (Verde Agro via builders ECharts existentes).
 */
export default function ProductivitySeriesChart(): React.JSX.Element | null {
  const { t: tBody, locale } = useT('agricultural');

  const series = useMemo(() => {
    const production = (pamData as PamUnified).crops;
    return buildPamYieldSeries(production, PAM_GRAIN_KEYS, PAM_YEARS, locale);
  }, [locale]);

  if (series.length === 0) return null;

  return (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-1">{tBody('hYieldSeries')}</h3>
      <p className="text-xs text-fg-muted mb-3">{tBody('yieldGrainsNote')}</p>
      <EChartsLine series={series} captionKey="yieldSeriesCaption" height={400} />
    </Card>
  );
}
