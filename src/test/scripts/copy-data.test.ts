/// <reference types="node" />
import { describe, it, expect } from 'vitest';
import { execFileSync } from 'node:child_process';
import { readFileSync, statSync, writeFileSync, existsSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const script = join(root, 'scripts', 'copy-data.mjs');
const pubInitiatives = join(root, 'public', 'data', 'processed', 'initiatives.json');
const pubSensors = join(root, 'public', 'data', 'processed', 'sensors.json');
const srcInitiatives = join(root, 'src', 'data', 'processed', 'initiatives.json');
const srcSensors = join(root, 'src', 'data', 'processed', 'sensors.json');

function runCopyData(): string {
  return execFileSync('node', [script], { encoding: 'utf-8' });
}

describe('copy-data.mjs (Fase 3: idempotent src → public sync)', () => {
  it('exits 0 and keeps public/ in sync with src/ source of truth', () => {
    const out = runCopyData();
    expect(out).toContain('Data sync complete');
    expect(readFileSync(pubInitiatives, 'utf-8')).toBe(readFileSync(srcInitiatives, 'utf-8'));
    expect(readFileSync(pubSensors, 'utf-8')).toBe(readFileSync(srcSensors, 'utf-8'));
  });

  it('is idempotent: second run copies nothing and preserves mtimes', () => {
    runCopyData(); // ensure synced
    const mtimeA = statSync(pubInitiatives).mtimeMs;
    const mtimeB = statSync(pubSensors).mtimeMs;

    const out = runCopyData(); // second run must be a no-op

    expect(out).toContain('up-to-date');
    expect(out).toContain('0 copied');
    expect(statSync(pubInitiatives).mtimeMs).toBe(mtimeA);
    expect(statSync(pubSensors).mtimeMs).toBe(mtimeB);
  });

  it('--check passes when public/ mirrors src/ and writes nothing', () => {
    runCopyData(); // ensure synced
    const mtimeA = statSync(pubInitiatives).mtimeMs;
    const out = execFileSync('node', [script, '--check'], { encoding: 'utf-8' });
    expect(out).toContain('--check, no writes');
    expect(statSync(pubInitiatives).mtimeMs).toBe(mtimeA);
  });

  it('--check fails on drift and resync recovers (CI gate)', () => {
    runCopyData(); // ensure synced
    const original = readFileSync(pubInitiatives, 'utf-8');
    try {
      writeFileSync(pubInitiatives, original + ' '); // simulate hand-edit drift
      expect(() => execFileSync('node', [script, '--verify'], { encoding: 'utf-8' })).toThrow();
    } finally {
      runCopyData(); // restore canonical copy
    }
    expect(readFileSync(pubInitiatives, 'utf-8')).toBe(readFileSync(srcInitiatives, 'utf-8'));
  });

  it('never creates a dist/public orphan (strips the public/ prefix)', () => {
    const orphan = join(root, 'dist', 'public');
    rmSync(orphan, { recursive: true, force: true });
    runCopyData();
    expect(existsSync(orphan)).toBe(false);
  });
});
