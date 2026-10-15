import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChartFontFamily } from '../../hooks/use-chart-font';
import { getFontOption } from '../../lib/fonts';

describe('useChartFontFamily (Fase 2 qualidade)', () => {
  it('resolves the active data-font option', () => {
    document.documentElement.dataset.font = 'default';
    const { result } = renderHook(() => useChartFontFamily());
    expect(result.current).toBe(getFontOption('default').sans);
  });

  it('reacts to data-font changes without remount', async () => {
    document.documentElement.dataset.font = 'default';
    const { result } = renderHook(() => useChartFontFamily());
    await act(async () => {
      document.documentElement.dataset.font = 'mono';
    });
    expect(result.current).toBe(getFontOption('mono').sans);
    document.documentElement.dataset.font = 'default';
  });
});
