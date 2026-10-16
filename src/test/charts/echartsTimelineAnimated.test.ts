import { describe, expect, it } from 'vitest';
import {
  buildTimelineOption,
  TIMELINE_ANIMATION_PLAY_INTERVAL,
  TIMELINE_ANIMATION_START,
} from '../../components/charts/echarts/echarts-options';
import {
  LANDAGRI_COLORWAY_DARK,
  LANDAGRI_COLORWAY_LIGHT,
} from '../../lib/echarts-theme';

const ITEMS = [
  { label: 'MapBiomas', years: [2000, 2001, 2003], color: '#2E7D32' },
  { label: 'TerraClass', years: [2004, 2008], color: '#43A047' },
];

interface TimelineLike {
  axisType: string;
  data: string[];
  autoPlay: boolean;
  playInterval: number;
  checkpointStyle: { color: string };
}

interface AnimatedOption {
  timeline: TimelineLike;
  options: { series: { type: string; data: unknown[] }[] }[];
}

function animated(extra: Record<string, unknown> = {}): AnimatedOption {
  const option = buildTimelineOption({
    items: ITEMS,
    theme: 'light',
    locale: 'pt-BR',
    animation: { ...extra },
  });
  return option as unknown as AnimatedOption;
}

describe('timeline animada (Expansão #4)', () => {
  it('estática por padrão: sem chave `timeline` (reversível)', () => {
    const option = buildTimelineOption({
      items: ITEMS,
      theme: 'light',
      locale: 'pt-BR',
    });
    expect('timeline' in (option as Record<string, unknown>)).toBe(false);
    expect('options' in (option as Record<string, unknown>)).toBe(false);
  });

  it('emite `timeline` 1985→ano atual com autoplay e intervalo padrão', () => {
    const currentYear = new Date().getFullYear();
    const { timeline } = animated();
    expect(timeline.axisType).toBe('category');
    expect(timeline.data[0]).toBe(String(TIMELINE_ANIMATION_START));
    expect(TIMELINE_ANIMATION_START).toBe(1985);
    expect(timeline.data[timeline.data.length - 1]).toBe(String(currentYear));
    expect(timeline.data).toHaveLength(currentYear - 1985 + 1);
    expect(timeline.autoPlay).toBe(true);
    expect(timeline.playInterval).toBe(TIMELINE_ANIMATION_PLAY_INTERVAL);
  });

  it('checkpoint usa o Verde Agro do tema ativo', () => {
    expect(animated().timeline.checkpointStyle.color).toBe(LANDAGRI_COLORWAY_LIGHT[0]);
    const dark = buildTimelineOption({
      items: ITEMS,
      theme: 'dark',
      locale: 'pt-BR',
      animation: {},
    }) as unknown as AnimatedOption;
    expect(dark.timeline.checkpointStyle.color).toBe(LANDAGRI_COLORWAY_DARK[0]);
  });

  it('respeita from/to/playInterval/autoPlay explícitos', () => {
    const { timeline, options } = animated({
      from: 2000,
      to: 2002,
      playInterval: 800,
      autoPlay: false,
    });
    expect(timeline.data).toEqual(['2000', '2001', '2002']);
    expect(timeline.playInterval).toBe(800);
    expect(timeline.autoPlay).toBe(false);
    expect(options).toHaveLength(3);
  });

  it('frames reutilizam as séries: primeiro vazio, último igual ao estático', () => {
    const { options, timeline } = animated();
    expect(timeline.data[0]).toBe('1985');
    const first = options[0].series.filter((s) => s.type === 'scatter');
    expect(first.every((s) => s.data.length === 0)).toBe(true);
    const staticOption = buildTimelineOption({
      items: ITEMS,
      theme: 'light',
      locale: 'pt-BR',
    });
    const staticSeries = staticOption.series as { type: string; data: unknown[] }[];
    const last = options[options.length - 1].series;
    expect(last).toEqual(staticSeries);
  });
});
