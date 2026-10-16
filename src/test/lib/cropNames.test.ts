import { describe, it, expect } from 'vitest';
import { formatCropName } from '../../lib/cropNames';

describe('formatCropName', () => {
  it('fixes the "3th harvest" ordinal typo for display', () => {
    expect(formatCropName('Beans (3th harvest)')).toBe('Beans (3rd harvest)');
  });

  it('fixes the same typo for other crops', () => {
    expect(formatCropName('Corn (3th harvest)')).toBe('Corn (3rd harvest)');
  });

  it('leaves correct names untouched', () => {
    expect(formatCropName('Soybean')).toBe('Soybean');
    expect(formatCropName('Beans (1st harvest)')).toBe('Beans (1st harvest)');
    expect(formatCropName('Beans (2nd harvest)')).toBe('Beans (2nd harvest)');
  });
});
