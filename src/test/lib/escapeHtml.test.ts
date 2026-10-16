import { describe, expect, it } from 'vitest';
import { escapeHtml } from '../../lib/escapeHtml';

describe('escapeHtml', () => {
  it('escapa os 5 caracteres especiais sem tocar em texto simples', () => {
    expect(escapeHtml('Soja')).toBe('Soja');
    expect(escapeHtml('<b>Milho</b>')).toBe('&lt;b&gt;Milho&lt;/b&gt;');
    expect(escapeHtml('A & B')).toBe('A &amp; B');
    expect(escapeHtml('"UF"')).toBe('&quot;UF&quot;');
    expect(escapeHtml("l'ane")).toBe('l&#39;ane');
  });

  it('escapa & primeiro (sem double-escape de entidades)', () => {
    expect(escapeHtml('&lt;')).toBe('&amp;lt;');
  });
});
