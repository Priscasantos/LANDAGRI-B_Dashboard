import { describe, it, expect } from 'vitest';
import {
  minMaxNormalize,
  scaleValue,
  roundTo,
  formatNumber,
  formatPercent,
} from '../../lib/normalize';

describe('normalize (Fase 2: unit coverage)', () => {
  it('minMaxNormalize maps to [0, 1]', () => {
    expect(minMaxNormalize([0, 50, 100])).toEqual([0, 0.5, 1]);
  });

  it('minMaxNormalize returns 0.5 for constant input', () => {
    expect(minMaxNormalize([7, 7, 7])).toEqual([0.5, 0.5, 0.5]);
  });

  it('minMaxNormalize returns [] for empty input', () => {
    expect(minMaxNormalize([])).toEqual([]);
  });

  it('scaleValue maps across ranges', () => {
    expect(scaleValue(50, 0, 100, 0, 1)).toBeCloseTo(0.5);
    expect(scaleValue(0, 0, 100, 10, 20)).toBeCloseTo(10);
    expect(scaleValue(100, 0, 100, 10, 20)).toBeCloseTo(20);
  });

  it('roundTo rounds to N decimals', () => {
    expect(roundTo(3.14159, 2)).toBe(3.14);
    expect(roundTo(2.5, 0)).toBe(3);
  });

  it('formatNumber uses thousands separator', () => {
    expect(formatNumber(1234567)).toBe('1,234,567');
  });

  it('formatPercent appends % with default 1 decimal', () => {
    expect(formatPercent(92.55)).toBe('92.6%');
    expect(formatPercent(90, 0)).toBe('90%');
  });
});
