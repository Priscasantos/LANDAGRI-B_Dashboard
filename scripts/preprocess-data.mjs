#!/usr/bin/env node

/**
 * LANDAGRI-B Data Preprocessor
 * Converts JSONC → JSON, CSV → JSON, XLSX → JSON for the React SPA
 *
 * Usage: node scripts/preprocess-data.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
// NOTE: `../data` (repo-local) is the source of truth. The legacy
// `../../landagri-dashboard/data` sibling-checkout path is kept as a
// read-only fallback so older clones keep working.
const LOCAL_DATA_DIR = path.resolve(__dirname, '../data');
const LEGACY_DATA_DIR = path.resolve(__dirname, '../../landagri-dashboard/data');
const DATA_SOURCE_DIR = fs.existsSync(LOCAL_DATA_DIR) ? LOCAL_DATA_DIR : LEGACY_DATA_DIR;
const DATA_OUTPUT_DIR = path.resolve(__dirname, '../src/data/processed');

// Ensure output directory exists
fs.mkdirSync(DATA_OUTPUT_DIR, { recursive: true });
fs.mkdirSync(path.join(DATA_OUTPUT_DIR, 'agricultural'), { recursive: true });

/**
 * Strip JSONC comments (both // and /* *!/) from a string
 */
function stripJsoncComments(text) {
  let result = '';
  let i = 0;
  let inString = false;
  let stringChar = null;

  while (i < text.length) {
    const ch = text[i];
    const next = text[i + 1] || '';

    // Handle strings (skip content inside them)
    if (!inString && (ch === '"' || ch === "'")) {
      inString = true;
      stringChar = ch;
      result += ch;
      i++;
      continue;
    }
    if (inString) {
      result += ch;
      if (ch === '\\' && i + 1 < text.length) {
        result += text[i + 1];
        i += 2;
        continue;
      }
      if (ch === stringChar) {
        inString = false;
      }
      i++;
      continue;
    }

    // Single-line comment //
    if (ch === '/' && next === '/') {
      while (i < text.length && text[i] !== '\n') {
        i++;
      }
      continue;
    }

    // Multi-line comment /* */
    if (ch === '/' && next === '*') {
      i += 2;
      while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) {
        i++;
      }
      i += 2; // skip */
      continue;
    }

    result += ch;
    i++;
  }

  return result;
}

/**
 * Load a JSONC file and strip comments
 */
function loadJsonc(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const clean = stripJsoncComments(content);
  return JSON.parse(clean);
}

/**
 * Copy file as-is to output (for logos, images, etc.)
 */
function copyFile(src, dest) {
  const destDir = path.dirname(dest);
  fs.mkdirSync(destDir, { recursive: true });
  fs.copyFileSync(src, dest);
  console.log(`  ✓ Copied ${path.basename(src)}`);
}

/**
 * Pre-process a JSONC file to JSON
 */
function processJsonc(srcFile, outputName) {
  const srcPath = path.join(DATA_SOURCE_DIR, srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: ${srcFile}`);
    return null;
  }
  try {
    const data = loadJsonc(srcPath);
    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    console.log(`  ✓ ${srcFile} → ${outputName}`);
    return data;
  } catch (err) {
    console.error(`  ✗ Error processing ${srcFile}: ${err.message}`);
    return null;
  }
}

/**
 * Typed calendar/availability row shapes (Fase 1: legacy `;`-joined keys
 * removed — consumers use `{crop, uf, months[12]}` /
 * `{crop, uf, anos_1s, anos_2s, is_long_aggregate}` directly).
 */
export const CALENDAR_MONTHS = [
  'October', 'November', 'December', 'January', 'February', 'March',
  'April', 'May', 'June', 'July', 'August', 'September',
];

/** National aggregate alias: source CSVs use "Brazil" as an Area value. */
export const AREA_ALIASES = { Brazil: 'BR' };

/**
 * Split raw CSV text into rows. Handles BOM, CRLF and auto-detects the
 * `;` (CONAB) vs `,` delimiter from the header line.
 */
export function splitTable(text) {
  const clean = text.replace(/^\uFEFF/, '').replace(/\r/g, '');
  const headerLine = clean.split('\n').find(l => l.trim() !== '') || '';
  const delimiter = (headerLine.match(/;/g) || []).length >= 2 ? ';' : ',';
  return clean
    .split('\n')
    .map(line => line.split(delimiter).map(cell => cell.trim()))
    .filter(cells => cells.some(c => c !== ''));
}

/**
 * Parse the CONAB crop-calendar table into typed rows.
 * `{ crop, uf, months[12] }` in October→September order.
 * All-empty filler rows (`;;;;;;;;;;;;;`) are dropped (consumers skip them).
 */
export function parseCalendarTable(rows) {
  const out = [];
  for (const cells of rows.slice(1)) {
    if (cells.length < 3) continue;
    const crop = (cells[0] || '').trim();
    const uf = (cells[1] || '').trim();
    const months = CALENDAR_MONTHS.map((_, i) => (cells[2 + i] || '').trim());
    if (!crop && !uf && months.every(m => m === '')) continue; // filler
    if (!crop || !uf) continue;
    out.push({ crop, uf, months });
  }
  return out;
}

/** Split a `Anos (1S/2S)` cell (`"2018-2019, 2019-2020"`) into year tokens. */
export function parseYearList(cell) {
  return (cell || '')
    .split(',')
    .map(s => s.trim())
    .filter(s => s !== '' && s !== ';');
}

/**
 * A token like "2000-2015" spans >2 harvest years: it is a multi-year
 * rollup, NOT a single agricultural year (biênio "2018-2019" → span 1).
 * Flagged so charts can keep aggregates out of per-year axes.
 */
export function isLongAggregate(token) {
  const m = token.match(/^(\d{4})\s*-\s*(\d{4}|\d{2})$/);
  if (!m) return false;
  let end = parseInt(m[2], 10);
  if (m[2].length === 2) end += 2000;
  return end - parseInt(m[0].slice(0, 4), 10) > 1;
}

/**
 * Parse the CONAB availability table into typed rows.
 * Empty "Crop Type" cells inherit the previous crop (forward-fill — the
 * source groups states under one crop label). `{ crop, uf, anos_1s,
 * anos_2s, is_long_aggregate }`.
 */
export function parseAvailabilityTable(rows) {
  const out = [];
  let lastCrop = '';
  for (const cells of rows.slice(1)) {
    if (cells.length < 2) continue;
    const rawCrop = (cells[0] || '').trim();
    if (rawCrop) lastCrop = rawCrop;
    const crop = lastCrop || 'Unknown';
    const uf = AREA_ALIASES[(cells[1] || '').trim()] || (cells[1] || '').trim();
    if (!uf) continue;
    const anos_1s = parseYearList(cells[2]);
    const anos_2s = parseYearList(cells[3]);
    const tokens = [...anos_1s, ...anos_2s];
    if (crop === 'Unknown' && tokens.length === 0) continue;
    out.push({
      crop,
      uf,
      anos_1s,
      anos_2s,
      is_long_aggregate: tokens.some(isLongAggregate),
    });
  }
  return out;
}

/**
 * ─── Area shares por cultura×UF (Gaia: ponderação honesta dos heatmaps) ───
 *
 * Os heatmaps de calendário ponderavam por nº de UFs (Roraima = MT) porque
 * faltava área por UF. O schema já prevê `mode: 'area'` via `areaSharePct`
 * (`src/lib/calendarShare.ts`); este bloco popula esse campo.
 *
 * Fonte: abas por UF de `data/conab_safra_2024_25.xlsx` (boletim CONAB safra
 * 2024/25 fechada — "Nota: Estimativa em julho/2025"), coluna de área da
 * safra 24/25. Método: participação da UF na área nacional da cultura
 * (soma das UFs; cruzada com a aba "Brasil - Total por Produto").
 *
 * Por que NÃO PAM: `data/brazilian_agricultural_data.json` (+ contraparte
 * EN) traz `territory_level: "Nacional (Brasil)"` — só agregados nacionais,
 * sem dimensão UF. Não há área PAM por UF em nenhuma fonte do repo, então
 * nada é derivado da PAM aqui (ver `gaps` em `buildAreaShares`).
 *
 * Regra de honestidade: cultura do calendário sem linha agregada
 * correspondente na safra NÃO recebe `areaSharePct` (campo ausente, nunca
 * zero inventado nem rateio) — `resolveShareMode` mantém `mode: 'uf'` e o
 * UI rotula o fallback. Exportado para testes unitários.
 */
export const AREA_SHARE_SEASON = '24/25';
export const AREA_SHARE_VINTAGE = 'conab_safra_2024_25.xlsx';

/** Coluna de área da safra fechada 24/25 (a coluna sem safra é a 23/24). */
export const AREA_SHARE_COLUMN_RE = /safra\s*24\/25/i;

/** Cultura do calendário → linha agregada de PRODUTO na safra por UF. */
export const CALENDAR_CROP_TO_SAFRA = {
  Cotton: 'ALGODÃO - CAROÇO (1)',
  Rice: 'ARROZ',
  'Beans (1st harvest)': 'FEIJÃO 1ª SAFRA',
  'Beans (2nd harvest)': 'FEIJÃO 2ª SAFRA',
  'Beans (3th harvest)': 'FEIJÃO 3ª SAFRA',
  'Corn (1st harvest)': 'Milho 1ª Safra',
  'Corn (2nd harvest)': 'Milho 2ª Safra',
  'Corn (3th harvest)': 'Milho 3ª Safra',
  Soybean: 'SOJA',
  Wheat: 'TRIGO',
};

/** Abas do workbook que são UFs (siglas de 2 letras). */
export function safraUfSheets(workbook) {
  return Object.keys(workbook || {}).filter((k) => /^[A-Z]{2}$/.test(k));
}

/** Localiza a coluna de área da safra-alvo; null quando ausente (sem adivinhar). */
export function findAreaColumn(sampleRow) {
  const keys = Object.keys(sampleRow || {});
  const areaKeys = keys.filter((k) => k.startsWith('ÁREA'));
  const hit = areaKeys.find((k) => AREA_SHARE_COLUMN_RE.test(k));
  return hit || null;
}

/**
 * Constrói `{ shares, coverage, gaps, metadata }` a partir do workbook da
 * safra 24/25 já parseado (`processXlsx`). `shares[crop][UF]` = % da área
 * nacional da cultura na UF (4 casas). `gaps` lista culturas sem linha na
 * safra e divergências UF-soma × total nacional (>0,5%) — nunca estimadas.
 */
export function buildAreaShares(safraWorkbook) {
  const gaps = [];
  const shares = {};
  const coverage = {};
  const ufSheets = safraUfSheets(safraWorkbook);
  if (ufSheets.length === 0) {
    gaps.push({ reason: 'no-uf-sheets', detail: `Workbook ${AREA_SHARE_VINTAGE} sem abas por UF` });
    return { metadata: areaSharesMetadata(null), shares, coverage, gaps };
  }
  const probe = (safraWorkbook[ufSheets[0]] || []).find((r) => r && typeof r.PRODUTO === 'string');
  const areaColumn = findAreaColumn(probe);
  if (!areaColumn) {
    gaps.push({ reason: 'no-area-column', detail: `Coluna de área ${AREA_SHARE_SEASON} ausente em ${AREA_SHARE_VINTAGE}` });
    return { metadata: areaSharesMetadata(null), shares, coverage, gaps };
  }
  const nationalRows = safraWorkbook['Brasil - Total por Produto'] || [];
  const nationalByProduto = new Map(nationalRows.map((r) => [r.PRODUTO, r[areaColumn]]));

  for (const [crop, produto] of Object.entries(CALENDAR_CROP_TO_SAFRA)) {
    const areas = {};
    for (const uf of ufSheets) {
      const row = (safraWorkbook[uf] || []).find((r) => r.PRODUTO === produto);
      const v = row ? row[areaColumn] : 0;
      areas[uf] = typeof v === 'number' && Number.isFinite(v) ? v : 0;
    }
    const total = Object.values(areas).reduce((s, v) => s + v, 0);
    if (total <= 0) {
      gaps.push({ crop, produto, reason: 'no-area', detail: `Sem área UF para ${produto} na safra ${AREA_SHARE_SEASON}` });
      continue;
    }
    const cropShares = {};
    for (const [uf, a] of Object.entries(areas)) cropShares[uf] = Math.round((a / total) * 100 * 1e4) / 1e4;
    shares[crop] = cropShares;
    const ufsWithArea = Object.values(areas).filter((a) => a > 0).length;
    coverage[crop] = {
      produto,
      ufs: ufSheets.length,
      ufsWithArea,
      nationalTotalThousandHa: Math.round(total * 10) / 10,
    };
    const national = nationalByProduto.get(produto);
    if (typeof national === 'number' && national > 0) {
      const diffPct = Math.abs(total - national) / national;
      coverage[crop].nationalCrossCheckDiffPct = Math.round(diffPct * 100 * 1e4) / 1e4;
      if (diffPct > 0.005) {
        gaps.push({ crop, produto, reason: 'cross-check', detail: `Soma UFs (${total}) diverge do total nacional (${national})` });
      }
    }
  }
  // Culturas do calendário fora do mapa (se o CSV ganhar culturas novas).
  return { metadata: areaSharesMetadata(areaColumn), shares, coverage, gaps };
}

function areaSharesMetadata(areaColumn) {
  return {
    source: 'CONAB',
    vintage: AREA_SHARE_VINTAGE,
    season: '2024/25',
    bulletinNote: 'Estimativa em julho/2025 (safra 2024/25 fechada)',
    areaColumn,
    method:
      'Participação da UF na área nacional da cultura (abas por UF / soma das UFs). PAM do repo é nacional-agregada e não fornece UF.',
  };
}

/**
 * Anexa `areaSharePct` às linhas tipadas do calendário a partir de
 * `buildAreaShares(...).shares`. Cultura sem share → linha inalterada
 * (campo ausente) e entrada em `gaps[].unmappedRows`. Pura (não muta).
 */
export function attachAreaShares(calendarRows, areaShares) {
  const shares = (areaShares && areaShares.shares) || {};
  const out = [];
  const missingCrops = new Set();
  for (const row of calendarRows) {
    const pct = shares[row.crop]?.[row.uf];
    if (typeof pct === 'number' && Number.isFinite(pct)) {
      out.push({ ...row, areaSharePct: pct });
    } else {
      out.push({ ...row });
      if (!shares[row.crop]) missingCrops.add(row.crop);
    }
  }
  return { rows: out, gaps: [...missingCrops].map((crop) => ({ crop, reason: 'unmapped-crop' })) };
}

/**
 * Read CSV file and output typed JSON. `parser` is parseCalendarTable |
 * parseAvailabilityTable. `postprocess` (opcional) transforma as linhas
 * antes da escrita (ex. `attachAreaShares` no calendário).
 */
function processCsv(srcFile, outputName, parser, postprocess) {
  const srcPath = path.join(DATA_SOURCE_DIR, 'csv', srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: csv/${srcFile}`);
    return;
  }
  try {
    const content = fs.readFileSync(srcPath, 'utf-8');
    const data = parser(splitTable(content));
    const finalData = typeof postprocess === 'function' ? postprocess(data) : data;

    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(finalData, null, 2));
    console.log(`  ✓ csv/${srcFile} → ${outputName} (${finalData.length} typed rows)`);
  } catch (err) {
    console.error(`  ✗ Error processing csv/${srcFile}: ${err.message}`);
  }
}

/**
 * Flatten a CONAB bulletin's two-level header. `sheet_to_json` titles
 * merged sub-columns `__EMPTY*`; the rows right below the header (null
 * first cell) hold the sub-labels ("24/25", "VAR. %", "(c/b)"…). They are
 * folded into composite keys ("SAFRAS 24/25", "VARIAÇÃO (c/b)") and
 * dropped from the data. Rows are otherwise untouched. No __EMPTY keys
 * survive. Exported for unit tests.
 */
export function normalizeBulletinRows(jsonData) {
  if (!jsonData.length) return jsonData;
  const trimmed = trimNullColumns(jsonData);
  const keys = Object.keys(trimmed[0] || {});
  if (!keys.length) return trimmed;
  const firstKey = keys[0];
  let i = 0;
  while (
    i < jsonData.length &&
    (jsonData[i][firstKey] === null || jsonData[i][firstKey] === '')
  ) {
    i++;
  }
  const subRows = trimmed.slice(0, i);
  const dataRows = trimmed.slice(i);
  // No sub-header rows: leftover __EMPTY keys still fold onto their
  // forward-filled parent ("SAFRA" → "SAFRA (2)"); values untouched.
  // Parent header per column: merged cells forward-fill from the left.
  const parents = [];
  let lastParent = '';
  for (const k of keys) {
    if (!k.startsWith('__EMPTY')) lastParent = k;
    parents.push(lastParent);
  }
  const renamed = keys.map((k, col) => {
    if (!k.startsWith('__EMPTY')) return k;
    const subs = [];
    for (const r of subRows) {
      const v = r[keys[col]];
      if (v !== null && v !== '' && !subs.includes(String(v))) subs.push(String(v).trim());
    }
    const suffix = subs.join(' ').trim();
    return suffix ? `${parents[col]} ${suffix}`.trim() : parents[col] || k;
  });
  // De-dupe (merged "VAR. %" repeats) with numeric suffixes.
  const seen = new Map();
  const finalKeys = renamed.map(k => {
    const n = seen.get(k) || 0;
    seen.set(k, n + 1);
    return n === 0 ? k : `${k} (${n + 1})`;
  });
  const renamedRows = dataRows.map(row => {
    const obj = {};
    keys.forEach((k, col) => {
      obj[finalKeys[col]] = row[k];
    });
    return obj;
  });
  return trimNullColumns(renamedRows);
}

/**
 * Drop all-null columns (bulletin sheets are wider than the real table;
 * those columns only carry nulls). Rows otherwise untouched.
 * Exported for unit tests.
 */
export function trimNullColumns(rows) {
  const live = new Set();
  for (const row of rows) {
    for (const [k, v] of Object.entries(row)) {
      if (v !== null && v !== '') live.add(k);
    }
  }
  if (live.size === 0) return rows;
  return rows.map(row => {
    const obj = {};
    for (const k of Object.keys(row)) {
      if (live.has(k)) obj[k] = row[k];
    }
    return obj;
  });
}

/**
 * Find the real header row of a CONAB bulletin sheet: first row (within
 * the top 12) whose cells mention PRODUTO or REGIÃO/UF. Falls back to 0.
 * Exported for unit tests.
 */
export function detectHeaderRowIndex(rawRows) {
  const limit = Math.min(rawRows.length, 12);
  for (let i = 0; i < limit; i++) {
    const joined = (rawRows[i] || [])
      .filter(v => v !== null && v !== '')
      .map(String)
      .join(' ')
      .toUpperCase();
    if (/PRODUTO|REGI[ÃA]O\/UF/.test(joined)) return i;
  }
  return 0;
}

/**
 * Process XLSX file to JSON (if xlsx module available).
 * Returns the parsed workbook object (sheets map) so follow-up steps
 * (e.g. `buildAreaShares`) can reuse it without re-reading the file;
 * null when skipped/failed.
 */
async function processXlsx(srcFile, outputName) {
  const srcPath = path.join(DATA_SOURCE_DIR, srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: ${srcFile}`);
    return null;
  }

  try {
    let XLSX;
    try {
      XLSX = (await import('xlsx')).default;
    } catch {
      console.log(`  ⚠ xlsx module not available, skipping ${srcFile}`);
      return null;
    }

    const workbook = XLSX.readFile(srcPath);
    const result = {};

    workbook.SheetNames.forEach(sheetName => {
      const sheet = workbook.Sheets[sheetName];
      // CONAB bulletins keep 4-7 title rows above the real header
      // (default `sheet_to_json` would mistitle them as `__EMPTY_*`).
      const rawRows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: null });
      const headerIdx = detectHeaderRowIndex(rawRows);
      const rawJson = XLSX.utils.sheet_to_json(sheet, { defval: null, range: headerIdx });
      const jsonData = normalizeBulletinRows(rawJson);
      if (jsonData.length > 0) {
        result[sheetName] = jsonData;
        return;
      }
      // Sheet has no data rows: distinguish a truly empty sheet from a
      // failed-download placeholder (e.g. a single {"error_type":"NotFound"}
      // cell, whose text is swallowed as the header row above).
      const raw = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: null });
      const cells = raw.flat().filter(v => v !== null && v !== '');
      if (cells.length === 0) {
        result[sheetName] = [];
        return;
      }
      result[sheetName] = {
        _unavailable: true,
        reason: `Sheet "${sheetName}" in ${srcFile} has no data rows; the source spreadsheet looks like a failed-download placeholder. Re-download it and re-run \`npm run preprocess\`.`,
        raw_preview: cells.slice(0, 3),
      };
    });

    if (Object.keys(result).length === 0) {
      console.log(`  ⚠ No data found in ${srcFile}`);
      return null;
    }

    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`  ✓ ${srcFile} → ${outputName} (${JSON.stringify(result).length} bytes)`);
    return result;
  } catch (err) {
    console.log(`  ⚠ Could not process ${srcFile}: ${err.message}`);
    return null;
  }
}

/**
 * Methodology notes for the typed calendar/availability JSONs.
 * `Anos (1S)` = crop years with mapping in the 1st-semester campaign,
 * `Anos (2S)` = 2nd-semester campaign ("YYYY-YYYY" agricultural years).
 * Tokens spanning >1 year ("2000-2014") are multi-year rollups flagged
 * `is_long_aggregate` — keep them out of per-year axes. Area "Brazil"
 * is normalized to "BR" (national aggregate, cf. json_dictionary).
 */
function writeDataNotes(areaSummary) {
  const notes = {
    anos_1s: 'Crop years with mapping coverage in the first-semester (1S) campaign.',
    anos_2s: 'Crop years with mapping coverage in the second-semester (2S) campaign.',
    year_format: 'Agricultural years as "YYYY-YYYY" pairs, comma-separated per cell.',
    long_aggregates:
      'Tokens spanning more than one harvest year (e.g. "2000-2014", "2000-2015") are multi-year rollups, not single agricultural years; rows carrying them are flagged is_long_aggregate.',
    area_aliases: AREA_ALIASES,
    calendar_months:
      'Calendar `months` arrays run October→September (CONAB bulletin order), one code per month (P/H/PH/"").',
    area_shares:
      'Calendar rows carry `areaSharePct` = UF share (%) of the crop national area from CONAB safra 2024/25 closed bulletin per-UF sheets (conab_safra_2024_25.xlsx, Jul/2025; full matrix in conab_area_shares.json). Repo PAM is national-only and cannot supply UF splits — unmapped crops carry NO areaSharePct (honest `mode: uf` fallback).',
  };
  if (areaSummary) notes.area_shares_coverage = areaSummary;
  fs.writeFileSync(
    path.join(DATA_OUTPUT_DIR, 'conab_data_notes.json'),
    JSON.stringify(notes, null, 2),
  );
  console.log('  ✓ conab_data_notes.json (methodology notes)');
}

/**
 * Build the unified PAM payload (Fase 1 i18n): PT + EN IBGE files carry
 * IDENTICAL numeric series under different slugs/keys, so the bundle keeps
 * the numbers ONCE under stable EN slugs plus a `{pt, en}` name dictionary.
 * Any numeric mismatch between the two sources throws — never silently
 * ships a half-merged payload. Exported for unit tests.
 */
export function buildPamUnified(pt, en) {
  const ptCrops = pt?.data?.producao_agricola || {};
  const enCrops = en?.data?.agricultural_production || {};
  const ptByCode = {};
  for (const [slug, entry] of Object.entries(ptCrops)) ptByCode[entry.codigo] = { slug, entry };
  const enByCode = {};
  for (const [slug, entry] of Object.entries(enCrops)) enByCode[entry.code] = { slug, entry };

  const ptCodes = Object.keys(ptByCode).sort();
  const enCodes = Object.keys(enByCode).sort();
  if (JSON.stringify(ptCodes) !== JSON.stringify(enCodes)) {
    throw new Error(
      `PAM code sets diverged: PT [${ptCodes}] vs EN [${enCodes}]`,
    );
  }

  const crops = {};
  for (const code of ptCodes) {
    const { slug: ptSlug, entry: p } = ptByCode[code];
    const { slug: enSlug, entry: e } = enByCode[code];
    for (const year of Object.keys(p.quantidade_produzida_toneladas || {})) {
      const pairs = [
        [p.quantidade_produzida_toneladas?.[year], e.production_quantity_tonnes?.[year], 'quantity', year],
        [p.area_colhida_hectares?.[year], e.harvested_area_hectares?.[year], 'area', year],
        [p.rendimento_medio_kg_por_ha?.[year], e.average_yield_kg_per_ha?.[year], 'yield', year],
      ];
      for (const [pv, ev, kind, y] of pairs) {
        if (pv !== ev) {
          throw new Error(`PAM numeric mismatch code=${code} (${ptSlug}/${enSlug}) ${kind} ${y}: ${pv} !== ${ev}`);
        }
      }
    }
    crops[enSlug] = {
      code,
      name: e.name,
      nome: p.nome,
      production_quantity_tonnes: e.production_quantity_tonnes,
      harvested_area_hectares: e.harvested_area_hectares,
      average_yield_kg_per_ha: e.average_yield_kg_per_ha,
    };
  }

  const ptSlugToEn = {};
  for (const code of ptCodes) ptSlugToEn[ptByCode[code].slug] = enByCode[code].slug;

  const summaryAnnual = {};
  for (const [year, s] of Object.entries(en?.data?.summary_annual || {})) {
    const ps = pt?.data?.resumo_anual?.[year] || {};
    summaryAnnual[year] = {
      total_harvested_area_hectares: s.total_harvested_area_hectares,
      main_crops: (s.main_crops || []).map(sl => sl),
      total_production_value_billion_reais: s.total_production_value_billion_reais,
      production_value_source: {
        pt: ps.fonte_valor_producao || null,
        en: s.production_value_source || null,
      },
    };
  }

  const lang = (ptVal, enVal) => ({ pt: ptVal ?? null, en: enVal ?? null });
  const variables = {};
  for (const code of Object.keys(en?.metadata?.variables || {})) {
    variables[code] = lang(pt?.metadata?.variables?.[code], en?.metadata?.variables?.[code]);
  }

  return {
    metadata: {
      source: lang(pt?.metadata?.source, en?.metadata?.source),
      source_url: en?.metadata?.source_url || pt?.metadata?.source_url || null,
      survey: lang(pt?.metadata?.survey, en?.metadata?.survey),
      survey_code: en?.metadata?.survey_code || pt?.metadata?.survey_code || null,
      territory_level: lang(pt?.metadata?.territory_level, en?.metadata?.territory_level),
      periodicity: lang(pt?.metadata?.periodicity, en?.metadata?.periodicity),
      period_range: en?.metadata?.period_range || pt?.metadata?.period_range || null,
      last_updated: en?.metadata?.last_updated || pt?.metadata?.last_updated || null,
      description: lang(pt?.metadata?.description, en?.metadata?.description),
      variables,
      pam_2025_status: lang(pt?.metadata?.pam_2025_status, en?.metadata?.pam_2025_status),
    },
    crops,
    summary_annual: summaryAnnual,
  };
}

/**
 * Read the PT + EN PAM sources, unify, and write `pam_unified.json`.
 * The per-language copies are NOT emitted (single payload in the bundle).
 */
function processPamUnified() {
  const ptPath = path.join(DATA_SOURCE_DIR, 'brazilian_agricultural_data.json');
  const enPath = path.join(DATA_SOURCE_DIR, 'brazilian_ibge_agricultural_data.json');
  if (!fs.existsSync(ptPath) || !fs.existsSync(enPath)) {
    console.log('  ⚠ PAM sources missing (brazilian_agricultural_data.json + brazilian_ibge_agricultural_data.json)');
    return;
  }
  try {
    const pt = JSON.parse(fs.readFileSync(ptPath, 'utf-8'));
    const en = JSON.parse(fs.readFileSync(enPath, 'utf-8'));
    const unified = buildPamUnified(pt, en);
    fs.writeFileSync(path.join(DATA_OUTPUT_DIR, 'pam_unified.json'), JSON.stringify(unified, null, 2));
    console.log(`  ✓ PAM PT+EN → pam_unified.json (${Object.keys(unified.crops).length} crops, single numeric payload)`);
  } catch (err) {
    console.error(`  ✗ Error building pam_unified.json: ${err.message}`);
    throw err;
  }
}

/**
 * Copy partner logos to public directory
 */
function copyLogos() {
  const logosDir = path.join(DATA_SOURCE_DIR, 'Logos_partners');
  if (!fs.existsSync(logosDir)) {
    console.log('  ⚠ Logos_partners directory not found');
    return;
  }

  const publicLogosDir = path.resolve(__dirname, '../public/logos');
  fs.mkdirSync(publicLogosDir, { recursive: true });

  const logoFiles = fs.readdirSync(logosDir);
  logoFiles.forEach(file => {
    const src = path.join(logosDir, file);
    const dest = path.join(publicLogosDir, file);
    copyFile(src, dest);
  });
}

// ─── Main ───────────────────────────────────────────────────────

async function main() {
  console.log('\n🔧 LANDAGRI-B Data Preprocessor\n');
  console.log(`Source: ${DATA_SOURCE_DIR}`);
  console.log(`Output: ${DATA_OUTPUT_DIR}\n`);

  console.log('📄 Processing JSONC files...');
  processJsonc('json/initiatives_metadata.jsonc', 'initiatives.json');
  processJsonc('json/sensors_metadata.jsonc', 'sensors.json');
  processJsonc('json/agricultural_conab_mapping_data_complete.jsonc', 'conab_mapping.json');
  processJsonc('json/conab_detailed_initiative.jsonc', 'conab_detailed_initiative.json');

  console.log('\n📄 Processing top-level JSON files...');
  const topJsonFiles = [
    'conab_agricultural_data.json',
    'conab_mapping_data.json',
    'json_dictionary.json',
  ];

  topJsonFiles.forEach(file => {
    const srcPath = path.join(DATA_SOURCE_DIR, file);
    if (fs.existsSync(srcPath)) {
      try {
        const content = fs.readFileSync(srcPath, 'utf-8');
        const data = JSON.parse(content);
        fs.writeFileSync(path.join(DATA_OUTPUT_DIR, file), JSON.stringify(data, null, 2));
        console.log(`  ✓ ${file}`);
      } catch (err) {
        console.error(`  ✗ Error processing ${file}: ${err.message}`);
      }
    } else {
      console.log(`  ⚠ File not found: ${file}`);
    }
  });

  console.log('\n📄 Processing PAM files (PT+EN → unified i18n payload)...');
  processPamUnified();

  console.log('\n📄 Processing CONAB safra 2024/25 (closed) → area shares cultura×UF...');
  const safra2425 = await processXlsx('conab_safra_2024_25.xlsx', 'conab_safra_2425.json');
  let areaShares = { metadata: null, shares: {}, coverage: {}, gaps: [] };
  if (safra2425) {
    try {
      areaShares = buildAreaShares(safra2425);
      fs.writeFileSync(
        path.join(DATA_OUTPUT_DIR, 'conab_area_shares.json'),
        JSON.stringify(areaShares, null, 2),
      );
      const nCrops = Object.keys(areaShares.shares).length;
      console.log(`  ✓ conab_area_shares.json (${nCrops} crops, ${areaShares.gaps.length} gaps)`);
      for (const g of areaShares.gaps) console.log(`    ⚠ gap: ${JSON.stringify(g)}`);
    } catch (err) {
      console.error(`  ✗ Error building conab_area_shares.json: ${err.message}`);
    }
  } else {
    console.log('  ⚠ Safra 2024/25 unavailable — calendar keeps `mode: uf` fallback (no invented shares)');
  }

  console.log('\n📄 Processing CSV files...');
  processCsv('conab_crop_calendar.csv', 'conab_calendar.json', parseCalendarTable, (rows) => {
    const { rows: withArea, gaps } = attachAreaShares(rows, areaShares);
    for (const g of gaps) console.log(`    ⚠ gap: calendar crop "${g.crop}" sem área UF (${g.reason})`);
    return withArea;
  });
  processCsv('conab_crop_avaliability.csv', 'conab_availability.json', parseAvailabilityTable);
  writeDataNotes({
    crops: Object.keys(areaShares.shares).length,
    gaps: areaShares.gaps.length,
    ufsPerCrop: Object.values(areaShares.coverage)[0]?.ufs ?? 0,
  });

  console.log('\n📄 Processing XLSX files...');
  await processXlsx('conab_safra_2023_24.xlsx', 'conab_safra_2324.json');
  await processXlsx('conab_safra_2025_26.xlsx', 'conab_safra_2526.json');

  console.log('\n🖼️ Copying partner logos...');
  copyLogos();

  console.log('\n✅ Pre-processing complete!\n');
  console.log(`Output files in ${DATA_OUTPUT_DIR}:`);
  const files = fs.readdirSync(DATA_OUTPUT_DIR, { recursive: true });
  files.forEach(f => {
    const fullPath = path.join(DATA_OUTPUT_DIR, f);
    if (fs.statSync(fullPath).isFile()) {
      const stats = fs.statSync(fullPath);
      console.log(`  ${f} (${(stats.size / 1024).toFixed(1)} KB)`);
    }
  });
  console.log('');
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}
