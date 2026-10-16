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
 * Legacy single-key row shapes (kept so existing consumers keep working).
 * Typed fields are ADDED alongside — never replace — the legacy key.
 */
export const LEGACY_CALENDAR_KEY = 'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September';
export const LEGACY_AVAIL_KEY = 'Crop Type;Area;Anos (1S);Anos (2S)';

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
 * `{ crop, uf, months[12] }` in October→September order + legacy key.
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
    out.push({
      crop,
      uf,
      months,
      [LEGACY_CALENDAR_KEY]: [crop, uf, ...months].join(';'),
    });
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
 * anos_2s, is_long_aggregate }` + legacy key.
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
      [LEGACY_AVAIL_KEY]: [rawCrop, cells[1] || '', cells[2] || '', cells[3] || ''].join(';'),
    });
  }
  return out;
}

/**
 * Read CSV file and output typed JSON (with legacy keys preserved).
 * `parser` is parseCalendarTable | parseAvailabilityTable.
 */
function processCsv(srcFile, outputName, parser) {
  const srcPath = path.join(DATA_SOURCE_DIR, 'csv', srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: csv/${srcFile}`);
    return;
  }
  try {
    const content = fs.readFileSync(srcPath, 'utf-8');
    const data = parser(splitTable(content));

    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    console.log(`  ✓ csv/${srcFile} → ${outputName} (${data.length} typed rows)`);
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
 * Process XLSX file to JSON (if xlsx module available)
 */
async function processXlsx(srcFile, outputName) {
  const srcPath = path.join(DATA_SOURCE_DIR, srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: ${srcFile}`);
    return;
  }

  try {
    let XLSX;
    try {
      XLSX = (await import('xlsx')).default;
    } catch {
      console.log(`  ⚠ xlsx module not available, skipping ${srcFile}`);
      return;
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
      return;
    }

    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`  ✓ ${srcFile} → ${outputName} (${JSON.stringify(result).length} bytes)`);
  } catch (err) {
    console.log(`  ⚠ Could not process ${srcFile}: ${err.message}`);
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
function writeDataNotes() {
  const notes = {
    anos_1s: 'Crop years with mapping coverage in the first-semester (1S) campaign.',
    anos_2s: 'Crop years with mapping coverage in the second-semester (2S) campaign.',
    year_format: 'Agricultural years as "YYYY-YYYY" pairs, comma-separated per cell.',
    long_aggregates:
      'Tokens spanning more than one harvest year (e.g. "2000-2014", "2000-2015") are multi-year rollups, not single agricultural years; rows carrying them are flagged is_long_aggregate.',
    area_aliases: AREA_ALIASES,
    calendar_months:
      'Calendar `months` arrays run October→September (CONAB bulletin order), one code per month (P/H/PH/"").',
  };
  fs.writeFileSync(
    path.join(DATA_OUTPUT_DIR, 'conab_data_notes.json'),
    JSON.stringify(notes, null, 2),
  );
  console.log('  ✓ conab_data_notes.json (methodology notes)');
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
  processJsonc('json/initiatives_metadata_backup.jsonc', 'initiatives_backup.json');
  processJsonc('json/sensors_metadata.jsonc', 'sensors.json');
  processJsonc('json/sensors_metadata_original.jsonc', 'sensors_original.json');
  processJsonc('json/agricultural_conab_mapping_data_complete.jsonc', 'conab_mapping.json');
  processJsonc('json/conab_detailed_initiative.jsonc', 'conab_detailed_initiative.json');

  console.log('\n📄 Processing top-level JSON files...');
  const topJsonFiles = [
    'brazilian_agricultural_data.json',
    'brazilian_ibge_agricultural_data.json',
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

  console.log('\n📄 Processing CSV files...');
  processCsv('conab_crop_calendar.csv', 'conab_calendar.json', parseCalendarTable);
  processCsv('conab_crop_avaliability.csv', 'conab_availability.json', parseAvailabilityTable);
  writeDataNotes();

  console.log('\n📄 Processing XLSX files...');
  await processXlsx('conab_safra_2023_24.xlsx', 'conab_safra_2324.json');
  await processXlsx('conab_safra_2024_25.xlsx', 'conab_safra_2425.json');
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
