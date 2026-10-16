import { describe, it, expect } from 'vitest';
import {
  splitTable,
  parseCalendarTable,
  parseAvailabilityTable,
  detectHeaderRowIndex,
  normalizeBulletinRows,
  isLongAggregate,
  buildAreaShares,
  attachAreaShares,
  safraUfSheets,
  findAreaColumn,
  CALENDAR_MONTHS,
} from '../../../scripts/preprocess-data.mjs';
import calendarJson from '../../data/processed/conab_calendar.json';
import availabilityJson from '../../data/processed/conab_availability.json';
import agriJson from '../../data/processed/conab_agricultural_data.json';
import detailedJson from '../../data/processed/conab_detailed_initiative.json';
import dictionaryJson from '../../data/processed/json_dictionary.json';
import dataNotes from '../../data/processed/conab_data_notes.json';
import areaSharesJson from '../../data/processed/conab_area_shares.json';

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

  it('parseCalendarTable emits {crop, uf, months[12]} with NO `;`-joined legacy keys', () => {
    const rows = parseCalendarTable(splitTable(CAL_FIXTURE));
    expect(rows).toHaveLength(2);
    expect(rows[0].crop).toBe('Cotton');
    expect(rows[0].uf).toBe('RO');
    expect(rows[0].months).toHaveLength(12);
    expect(rows[0].months[3]).toBe('P'); // January
    for (const r of rows) {
      expect(Object.keys(r).some((k) => k.includes(';'))).toBe(false);
    }
    expect(CALENDAR_MONTHS).toEqual([
      'October', 'November', 'December', 'January', 'February', 'March',
      'April', 'May', 'June', 'July', 'August', 'September',
    ]);
  });

  it('parseAvailabilityTable forward-fills crop, splits years, aliases BR, no legacy keys', () => {
    const rows = parseAvailabilityTable(splitTable(AVAIL_FIXTURE));
    expect(rows).toHaveLength(4);
    expect(rows[0]).toMatchObject({ crop: 'Cotton', uf: 'GO', anos_1s: ['2018-2019', '2019-2020'], anos_2s: [] });
    expect(rows[1].crop).toBe('Cotton'); // forward-fill from ";MS;…"
    expect(rows[1].uf).toBe('MS');
    expect(rows[3].uf).toBe('BR');
    for (const r of rows) {
      expect(Object.keys(r).some((k) => k.includes(';'))).toBe(false);
    }
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
  it('calendar rows are typed with NO `;`-joined legacy keys', () => {
    const rows = calendarJson as Record<string, unknown>[];
    expect(rows.length).toBeGreaterThan(100);
    for (const r of rows) {
      expect(typeof r['crop']).toBe('string');
      expect(typeof r['uf']).toBe('string');
      expect(r['months']).toHaveLength(12);
      expect(Object.keys(r).some((k) => k.includes(';'))).toBe(false);
    }
  });

  it('availability rows are typed, forward-filled, aggregates flagged, no legacy keys', () => {
    const rows = availabilityJson as Record<string, unknown>[];
    expect(rows.length).toBeGreaterThan(10);
    for (const r of rows) {
      expect(typeof r['crop']).toBe('string');
      expect((r['crop'] as string).length).toBeGreaterThan(0);
      expect(Array.isArray(r['anos_1s'])).toBe(true);
      expect(Array.isArray(r['anos_2s'])).toBe(true);
      expect(typeof r['is_long_aggregate']).toBe('boolean');
      expect(Object.keys(r).some((k) => k.includes(';'))).toBe(false);
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

const SAFRA_FIXTURE = {
  MT: [
    { PRODUTO: 'SOJA', 'ÁREA (Em mil ha)': 100, 'ÁREA (Em mil ha) Safra 24/25 (b)': 300 },
    { PRODUTO: 'ARROZ', 'ÁREA (Em mil ha)': 50, 'ÁREA (Em mil ha) Safra 24/25 (b)': 100 },
  ],
  RO: [
    { PRODUTO: 'SOJA', 'ÁREA (Em mil ha)': 10, 'ÁREA (Em mil ha) Safra 24/25 (b)': 100 },
    { PRODUTO: 'ARROZ', 'ÁREA (Em mil ha)': 0, 'ÁREA (Em mil ha) Safra 24/25 (b)': 0 },
  ],
  'Brasil - Total por Produto': [
    { PRODUTO: 'SOJA', 'ÁREA (Em mil ha)': 110, 'ÁREA (Em mil ha) Safra 24/25 (b)': 400 },
    { PRODUTO: 'ARROZ', 'ÁREA (Em mil ha)': 50, 'ÁREA (Em mil ha) Safra 24/25 (b)': 100 },
  ],
};

describe('area shares cultura×UF (Gaia: ponderação por área)', () => {
  it('detecta abas UF e coluna da safra fechada (ignora coluna da safra anterior)', () => {
    expect(safraUfSheets(SAFRA_FIXTURE).sort()).toEqual(['MT', 'RO']);
    expect(findAreaColumn(SAFRA_FIXTURE.MT[0])).toBe('ÁREA (Em mil ha) Safra 24/25 (b)');
    expect(findAreaColumn({ PRODUTO: 'X', 'ÁREA (Em mil ha)': 1 })).toBeNull();
  });

  it('participação soma ~100 por cultura; UF zerada recebe 0 explícito', () => {
    const { shares, coverage, gaps } = buildAreaShares(SAFRA_FIXTURE);
    expect(shares['Soybean']).toMatchObject({ MT: 75, RO: 25 });
    const sum = Object.values(shares['Soybean'] as Record<string, number>).reduce((s, v) => s + v, 0);
    expect(sum).toBeCloseTo(100, 5);
    expect(shares['Rice']).toMatchObject({ MT: 100, RO: 0 });
    expect(coverage['Soybean']).toMatchObject({ ufs: 2, ufsWithArea: 2 });
    // O fixture só traz SOJA/ARROZ: as outras 8 culturas mapeadas viram gap
    // 'no-area' (sem área UF no fixture) — e nenhum 'cross-check' dispara.
    expect(gaps).toHaveLength(8);
    expect(gaps.every((g: { reason: string }) => g.reason === 'no-area')).toBe(true);
  });

  it('divergência soma-UFs × nacional vira gap (nunca estimativa silenciosa)', () => {
    const bad = {
      ...SAFRA_FIXTURE,
      'Brasil - Total por Produto': [
        { PRODUTO: 'SOJA', 'ÁREA (Em mil ha) Safra 24/25 (b)': 800 },
      ],
    };
    const { gaps } = buildAreaShares(bad);
    expect(gaps.some((g: { reason: string }) => g.reason === 'cross-check')).toBe(true);
  });

  it('attachAreaShares pesa só culturas mapeadas; resto fica sem campo (fallback uf)', () => {
    const { shares } = buildAreaShares(SAFRA_FIXTURE);
    const rows = [
      { crop: 'Soybean', uf: 'MT', months: Array(12).fill('') },
      { crop: 'Soybean', uf: 'RO', months: Array(12).fill('') },
      { crop: 'Coffee', uf: 'MG', months: Array(12).fill('') },
    ];
    const { rows: out, gaps } = attachAreaShares(rows, { shares });
    expect(out[0]).toMatchObject({ areaSharePct: 75 });
    expect(out[1]).toMatchObject({ areaSharePct: 25 });
    expect('areaSharePct' in (out[2] as object)).toBe(false);
    expect(gaps).toEqual([{ crop: 'Coffee', reason: 'unmapped-crop' }]);
  });

  it('processed: conab_area_shares.json cobre as 10 culturas do calendário', () => {
    const area = areaSharesJson as {
      metadata: { vintage: string; season: string };
      shares: Record<string, Record<string, number>>;
      gaps: unknown[];
    };
    expect(area.metadata.vintage).toBe('conab_safra_2024_25.xlsx');
    expect(area.metadata.season).toBe('2024/25');
    const calendarCrops = [...new Set((calendarJson as { crop: string }[]).map((r) => r.crop))];
    expect(calendarCrops).toHaveLength(10);
    for (const crop of calendarCrops) {
      expect(area.shares[crop], `sem share UF: ${crop}`).toBeDefined();
      const sum = Object.values(area.shares[crop]).reduce((s, v) => s + v, 0);
      expect(sum).toBeCloseTo(100, 1);
    }
    // Concentração real que o modo 'uf' escondia: MT domina algodão e soja.
    expect(area.shares['Cotton']['MT']).toBeGreaterThan(60);
    expect(area.shares['Cotton']['MT']).toBeGreaterThan(area.shares['Cotton']['BA']);
    expect(area.shares['Soybean']['MT']).toBeGreaterThan(20);
  });

  it('processed: linhas do calendário carregam areaSharePct (modo area ativa)', () => {
    const rows = calendarJson as { crop: string; uf: string; areaSharePct?: unknown }[];
    expect(rows.length).toBeGreaterThan(100);
    for (const r of rows) {
      expect(typeof r.areaSharePct, `${r.crop}/${r.uf}`).toBe('number');
    }
    const cotton = rows.filter((r) => r.crop === 'Cotton');
    const mt = cotton.find((r) => r.uf === 'MT')?.areaSharePct as number;
    const ro = cotton.find((r) => r.uf === 'RO')?.areaSharePct as number;
    expect(mt).toBeGreaterThan(ro); // Roraima/MT não empatam mais
  });

  it('processed: notes documentam fonte/ano e a lacuna PAM (nacional, sem UF)', () => {
    const notes = dataNotes as Record<string, unknown>;
    expect(typeof notes['area_shares']).toBe('string');
    expect(JSON.stringify(notes)).toContain('2024/25');
  });
});
