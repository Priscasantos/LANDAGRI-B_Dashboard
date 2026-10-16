import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHorizontalBarOption } from './echarts-options';
import type { EChartsPalette } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsHorizontalBarProps {
  labels: (string | number)[];
  values: (number | null)[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  color?: string;
  name?: string;
  height?: number;
  /**
   * `'divergent'`: cada barra codifica o sinal em torno de 0 (deltas;
   * âncora negativa vs. primária do preset ativo). Default `'theme'`.
   */
  palette?: EChartsPalette;
}

export default function EChartsHorizontalBar({
  labels,
  values,
  captionKey,
  color,
  name,
  height,
  palette,
}: EChartsHorizontalBarProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildHorizontalBarOption({
        labels,
        values,
        theme,
        colorway,
        preset: presetValue,
        locale,
        fontFamily,
        color,
        name,
        ...(palette !== undefined ? { palette } : {}),
      }),
    [labels, values, theme, colorway, presetValue, locale, fontFamily, color, name, palette],
  );

  const caption = captionKey !== undefined ? t(captionKey) : '';
  return (
    <EChartsBase
      option={option}
      ariaLabel={caption === '' ? t('interactiveChart') : caption}
      caption={caption}
      height={height}
    />
  );
}
