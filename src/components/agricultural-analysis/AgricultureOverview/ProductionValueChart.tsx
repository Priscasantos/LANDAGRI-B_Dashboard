import { useMemo } from 'react';
import { Banknote } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import { useT } from '../../../i18n/LanguageContext';
import type { PamProduction } from '../../../lib/agriP2b';
import pamData from '../../../data/processed/brazilian_agricultural_data.json';

interface ValuePayload {
  totalBn: number | null;
  labels: string[];
  valuesMt: number[];
}

/**
 * P2b (2): valor da produção PAM — número R$ 927 bi (2025 definitiva) +
 * barra horizontal top por quantidade produzida. Sem valor por cultura no
 * JSON: barras usam quantidade (Mt), rotuladas como tal.
 */
export default function ProductionValueChart(): React.JSX.Element | null {
  const { t: tCharts } = useT('charts');
  const { t: tBody, locale } = useT('agricultural');

  const payload = useMemo<ValuePayload>(() => {
    try {
      const root = pamData as {
        data: { producao_agricola?: PamProduction; resumo_anual?: Record<string, { valor_total_producao_bilhoes_reais?: number }> };
      };
      const totalBn =
        root.data?.resumo_anual?.['2025']?.valor_total_producao_bilhoes_reais ?? null;
      const production = root.data?.producao_agricola;
      if (production === undefined) return { totalBn, labels: [], valuesMt: [] };
      const items = Object.values(production)
        .map((crop) => ({
          label: crop.nome,
          value: crop.quantidade_produzida_toneladas?.['2025'] ?? 0,
        }))
        .filter((i) => i.value > 0)
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);
      return {
        totalBn,
        labels: items.map((i) => i.label),
        valuesMt: items.map((i) => Math.round((i.value / 1_000_000) * 10) / 10),
      };
    } catch {
      return { totalBn: null, labels: [], valuesMt: [] };
    }
  }, []);

  if (payload.totalBn === null && payload.labels.length === 0) return null;

  const valueLabel =
    payload.totalBn === null
      ? '–'
      : locale === 'pt-BR'
        ? `R$ ${payload.totalBn} bi`
        : `R$ ${payload.totalBn}bn`;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={Banknote}
          label={tBody('productionValueKpi')}
          value={valueLabel}
          help={tBody('productionValueHelp')}
          variant="accuracy"
        />
      </div>
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-1">{tBody('hTopByProduction')}</h3>
        <p className="text-xs text-fg-muted mb-3">
          {tBody('productionValueNote')} {tCharts('productionTopCaption')}
        </p>
        {payload.labels.length > 0 ? (
          <EChartsHorizontalBar
            labels={payload.labels}
            values={payload.valuesMt}
            captionKey="productionTopCaption"
            height={Math.max(300, payload.labels.length * 35)}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
        )}
      </Card>
    </div>
  );
}
