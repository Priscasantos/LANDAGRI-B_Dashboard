import { useMemo, useState, type ReactElement } from 'react';
import { Pause, Play } from 'lucide-react';
import EChartsBase from './EChartsBase';
import {
  buildTimelineOption,
  TIMELINE_ANIMATION_PLAY_INTERVAL,
  TIMELINE_ANIMATION_START,
  type TimelineItemInput,
} from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { usePrefersReducedMotion } from '../../../hooks/use-prefers-reduced-motion';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsTimelineProps {
  /** One entry per initiative (years + color + tooltip). */
  items: TimelineItemInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  /**
   * Expansão #4 (reversível): animated playback 1985→present via the
   * native `timeline` component (year labels, autoplay, Verde Agro
   * checkpoint). Omitted/false → static chart (fatia 2c output).
   */
  animated?: boolean;
  /** First frame year (default 1985). */
  animationFrom?: number;
  /** Last frame year (default: current year). */
  animationTo?: number;
  /** ms per frame (default 1500). */
  playInterval?: number;
}

export default function EChartsTimeline({
  items,
  captionKey,
  height = 520,
  animated = false,
  animationFrom = TIMELINE_ANIMATION_START,
  animationTo,
  playInterval = TIMELINE_ANIMATION_PLAY_INTERVAL,
}: EChartsTimelineProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');
  const reduceMotion = usePrefersReducedMotion();
  // Explicit user intent; `null` follows the default (autoplay unless the
  // OS prefers reduced motion). No autoplay in that case, manual play stays.
  const [manual, setManual] = useState<boolean | null>(null);
  const playing = animated && (manual ?? !reduceMotion);

  const option = useMemo(
    () =>
      buildTimelineOption({
        items,
        theme,
        locale,
        fontFamily,
        ...(animated
          ? {
              animation: {
                from: animationFrom,
                to: animationTo,
                playInterval,
                autoPlay: playing,
              },
            }
          : {}),
      }),
    [items, theme, locale, fontFamily, animated, animationFrom, animationTo, playInterval, playing],
  );

  const caption = captionKey !== undefined ? t(captionKey) : '';
  const toggleLabel = playing ? t('timelinePause') : t('timelinePlay');
  return (
    <div className="w-full min-w-0 space-y-2">
      {animated ? (
        <div className="flex justify-start">
          <button
            type="button"
            aria-pressed={playing}
            onClick={() => setManual(!playing)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface-alt px-2.5 py-1.5 text-xs font-medium text-fg-secondary transition-colors hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            {playing ? (
              <Pause size={14} aria-hidden="true" />
            ) : (
              <Play size={14} aria-hidden="true" />
            )}
            {toggleLabel}
          </button>
        </div>
      ) : null}
      <EChartsBase
        option={option}
        ariaLabel={caption === '' ? t('interactiveChart') : caption}
        caption={caption}
        height={height}
      />
    </div>
  );
}
