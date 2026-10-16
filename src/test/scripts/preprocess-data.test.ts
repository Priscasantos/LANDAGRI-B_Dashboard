import { describe, it, expect } from 'vitest';
import {
  splitTable,
  parseCalendarTable,
  parseAvailabilityTable,
  detectHeaderRowIndex,
  normalizeBulletinRows,
  isLongAggregate,
  LEGACY_CALENDAR_KEY,
  LEGACY_AVAIL_KEY,
  CALENDAR_MONTHS,
} from '../../../scripts/preprocess-data.mjs';
import calendarJson from '../../data/processed/conab_calendar.json';
import availabilityJson from '../../data/processed/conab_availability.json';
import agriJson from '../../data/processed/conab_agricultural_data.json';
import detailedJson from '../../data/processed/conab_detailed_initiative.json';
import dictionaryJson from '../../data/processed/json_dictionary.json';
import dataNotes from '../../data/processed/conab_data_notes.json';

const CAL_FIXTURE = [
  'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September',
  'Cotton;RO;;;;P;P;;;;H;H;H;',
  'Cotton;TO;;;P;P;P;;;;H;H;H;',
  ';;;;;;;;;;;;;',
].join('\n');

const AVAIL_FIXTURE = [
  'Crop Type;Area;Anos (1S);Anos (2S)',
  'Cotton;GO;2018-2019, 2019-2020;',
  ';MS;2021-2022;',
  'Other winter crops;RS;2000-2015;',
  'Sugar cane mill;Brazil;2020-2021;',
].join('\n');

describe('preprocess-data.mjs typed parsers (P0)', () => {
  it('splitTable strips BOM/CRLF and detects the ; delimiter', () => {
    const rows = splitTable('﻿Crop type;Federation Unit;October\r\nCotton;RO;\r\n');
    expect(rows[0][0]).toBe('Crop type');
    expect(rows[1].slice(0, 2)).toEqual(['Cotton', 'RO']);
  });

  it('parseCalendarTable emits {crop, uf, months[12]} + legacy key, drops fillers', () => {
    const rows = parseCalendarTable(splitTable(CAL_FIXTURE));
    expect(rows).toHaveLength(2);
    expect(rows[0].crop).toBe('Cotton');
    expect(rows[0].uf).toBe('RO');
    expect(rows[0].months).toHaveLength(12);
    expect(rows[0].months[3]).toBe('P'); // January
    expect(rows[0][LEGACY_CALENDAR_KEY]).toBe('Cotton;RO;;;;P;P;;;;H;H;H;');
    expect(CALENDAR_MONTHS).toEqual([
      'October', 'November', 'December', 'January', 'February', 'March',
      'April', 'May', 'June', 'July', 'August', 'September',
    ]);
  });

  it('parseAvailabilityTable forward-fills crop, splits years, aliases BR', () => {
    const rows = parseAvailabilityTable(splitTable(AVAIL_FIXTURE));
    expect(rows).toHaveLength(4);
    expect(rows[0]).toMatchObject({ crop: 'Cotton', uf: 'GO', anos_1s: ['2018-2019', '2019-2020'], anos_2s: [] });
    expect(rows[1].crop).toBe('Cotton'); // forward-fill from ";MS;…"
    expect(rows[1].uf).toBe('MS');
    // Legacy key keeps the RAW line so old `split(';')` consumers behave identically.
    expect(rows[1][LEGACY_AVAIL_KEY]).toBe(';MS;2021-2022;');
    expect(rows[3].uf).toBe('BR');
  });

  it('flags long aggregates but not biennial pairs', () => {
    expect(isLongAggregate('2000-2015')).toBe(true);
    expect(isLongAggregate('2000-2014')).toBe(true);
    expect(isLongAggregate('2018-2019')).toBe(false);
    const rows = parseAvailabilityTable(splitTable(AVAIL_FIXTURE));
    expect(rows.find((r) => r.uf === 'RS')?.is_long_aggregate).toBe(true);
    expect(rows.find((r) => r.uf === 'GO')?.is_long_aggregate).toBe(false);
  });

  it('detectHeaderRowIndex skips bulletin title rows (no __EMPTY_* keys)', () => {
    const raw = [
      [null, null, '(em mil hectares)'],
      ['PRODUTO', 'SAFRAS', null, 'VARIAÇÃO'],
      [null, '23/24', '24/25', 'Percentual'],
      ['SOJA', 46149.6, 47614.9, 3.2],
    ];
    expect(detectHeaderRowIndex(raw)).toBe(1);
    expect(detectHeaderRowIndex([['a', 'b']])).toBe(0);
  });

  it('normalizeBulletinRows folds merged sub-headers, drops them, trims null cols', () => {
    const input = [
      { PRODUTO: null, SAFRAS: '23/24', __EMPTY: '24/25', VARIAÇÃO: 'Percentual', __EMPTY_1: null, __EMPTY_2: null },
      { PRODUTO: 'SOJA', SAFRAS: 46149.6, __EMPTY: 47614.9, VARIAÇÃO: 3.2, __EMPTY_1: null, __EMPTY_2: null },
    ];
    const rows = normalizeBulletinRows(input);
    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({ PRODUTO: 'SOJA', SAFRAS: 46149.6 });
    expect(Object.keys(rows[0]).some((k) => k.includes('__EMPTY'))).toBe(false);
    expect('SAFRAS 24/25' in rows[0]).toBe(true);
  });
});

describe('processed CONAB JSONs (run `npm run preprocess` if stale)', () => {
  it('calendar rows are typed and keep the legacy key', () => {
    const rows = calendarJson as Record<string, unknown>[];
    expect(rows.length).toBeGreaterThan(100);
    for (const r of rows) {
      expect(typeof r['crop']).toBe('string');
      expect(typeof r['uf']).toBe('string');
      expect(r['months']).toHaveLength(12);
      expect(typeof r[LEGACY_CALENDAR_KEY]).toBe('string');
    }
  });

  it('availability rows are typed, forward-filled, aggregates flagged', () => {
    const rows = availabilityJson as Record<string, unknown>[];
    expect(rows.length).toBeGreaterThan(10);
    for (const r of rows) {
      expect(typeof r['crop']).toBe('string');
      expect((r['crop'] as string).length).toBeGreaterThan(0);
      expect(Array.isArray(r['anos_1s'])).toBe(true);
      expect(Array.isArray(r['anos_2s'])).toBe(true);
      expect(typeof r['is_long_aggregate']).toBe('boolean');
      expect(typeof r[LEGACY_AVAIL_KEY]).toBe('string');
    }
    // No empty-crop rows survive; aggregates exist and are flagged.
    expect(rows.some((r) => r['crop'] === '')).toBe(false);
    expect(rows.some((r) => r['is_long_aggregate'] === true)).toBe(true);
    // National aggregate uses the BR sigla, never a "Brazil" area value.
    expect(rows.some((r) => r['uf'] === 'Brazil')).toBe(false);
  });

  it('agricultural data carries 2024/25 (closed) + 2025/26 (forecast)', () => {
    const crops = (agriJson as { crops: Record<string, { production_data: Record<string, { production: number }> }> }).crops;
    for (const [, crop] of Object.entries(crops)) {
      expect(Object.keys(crop.production_data)).toContain('2024/25');
      expect(Object.keys(crop.production_data)).toContain('2025/26');
      expect(crop.production_data['2025/26'].production).toBeGreaterThan(0);
    }
    expect(crops['soybean'].production_data['2025/26'].production).toBe(180407);
  });

  it('detailed initiative coverage + dictionary use National, not Brazil', () => {
    const initiative = (detailedJson as Record<string, { coverage: string }>)['CONAB Crop Monitoring Initiative'];
    expect(initiative.coverage).toBe('National');
    const raw = JSON.stringify(detailedJson);
    expect(raw).not.toContain('"Brazil"');
    const country = (dictionaryJson as { mesoregions: { Country: { name_pt: string; states: { nome: string }[] } } }).mesoregions.Country;
    expect(country.name_pt).toBe('Nacional');
    expect(country.states[0].nome).toBe('National');
  });

  it('methodology notes document Anos (1S)/(2S) and aggregates', () => {
    const notes = dataNotes as Record<string, unknown>;
    expect(typeof notes['anos_1s']).toBe('string');
    expect(typeof notes['anos_2s']).toBe('string');
    expect(typeof notes['long_aggregates']).toBe('string');
  });
});
