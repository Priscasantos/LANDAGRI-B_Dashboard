import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import calendarJson from '../../data/processed/conab_calendar.json';
import availabilityJson from '../../data/processed/conab_availability.json';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, '..', '..', '..');

/** Arquivos migrados do `split(';')` para arrays tipados (Fase 1, item 3). */
const MIGRATED_CONSUMERS = [
  'src/components/agricultural-analysis/CropCalendar/CropDistributionTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/ActivityIntensityTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/MonthlyIntensityTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/CalendarHeatmapsTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/SpatioTemporalTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/ActivitiesTimelineTab.tsx',
  'src/components/agricultural-analysis/CropCalendar/SeasonalOverviewTab.tsx',
  'src/components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityPage.tsx',
];

describe('anti-`;` regression (Fase 1, item 3)', () => {
  it('payloads processados não têm chaves `;`', () => {
    for (const row of calendarJson as Record<string, unknown>[]) {
      expect(Object.keys(row).some((k) => k.includes(';'))).toBe(false);
    }
    for (const row of availabilityJson as Record<string, unknown>[]) {
      expect(Object.keys(row).some((k) => k.includes(';'))).toBe(false);
    }
  });

  it('consumidores migrados não usam mais `split(";")` nem literais `;`', () => {
    expect(MIGRATED_CONSUMERS.length).toBeGreaterThanOrEqual(5);
    for (const rel of MIGRATED_CONSUMERS) {
      const text = readFileSync(join(repoRoot, rel), 'utf-8');
      expect(text, `${rel} ainda usa split(';')`).not.toMatch(/split\(\s*['"];/);
      expect(text, `${rel} ainda referencia a chave legada`).not.toContain('Crop type;Federation');
      expect(text, `${rel} ainda referencia a chave legada`).not.toContain('Crop Type;Area');
    }
  });

  it('nenhum outro componente referencia as chaves legadas', () => {
    const hits: string[] = [];
    const walk = (dir: string) => {
      for (const entry of readdirSync(join(repoRoot, dir), { withFileTypes: true })) {
        const rel = join(dir, entry.name);
        if (entry.isDirectory()) {
          if (entry.name !== 'test') walk(rel);
        } else if (/\.(tsx?|ts)$/.test(entry.name)) {
          const text = readFileSync(join(repoRoot, rel), 'utf-8');
          if (text.includes('Crop type;Federation') || text.includes('Crop Type;Area')) {
            hits.push(rel);
          }
        }
      }
    };
    walk('src/components');
    walk('src/lib');
    walk('src/pages');
    walk('src/hooks');
    expect(hits).toEqual([]);
  });
});
