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
const DATA_SOURCE_DIR = path.resolve(__dirname, '../../landagri-dashboard/data');
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
 * Read CSV file and output as JSON array
 */
function processCsv(srcFile, outputName) {
  const srcPath = path.join(DATA_SOURCE_DIR, 'csv', srcFile);
  if (!fs.existsSync(srcPath)) {
    console.log(`  ⚠ File not found: csv/${srcFile}`);
    return;
  }
  try {
    const content = fs.readFileSync(srcPath, 'utf-8');
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());

    const data = lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim());
      const obj = {};
      headers.forEach((header, idx) => {
        const val = values[idx] || '';
        const num = Number(val);
        obj[header] = isNaN(num) || val === '' ? val : num;
      });
      return obj;
    });

    const outputPath = path.join(DATA_OUTPUT_DIR, outputName);
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    console.log(`  ✓ csv/${srcFile} → ${outputName}`);
  } catch (err) {
    console.error(`  ✗ Error processing csv/${srcFile}: ${err.message}`);
  }
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
      const jsonData = XLSX.utils.sheet_to_json(sheet, { defval: null });
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
  processCsv('conab_crop_calendar.csv', 'conab_calendar.json');
  processCsv('conab_crop_avaliability.csv', 'conab_availability.json');

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

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
