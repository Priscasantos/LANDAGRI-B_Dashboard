/**
 * Escapa texto para interpolação segura em tooltip HTML do ECharts
 * (`<b>…</b><br>…`). Cobre crop/UF/lane vindos de dados (CONAB/PAM) ou
 * rótulos traduzidos — evita quebra de markup / injeção via `<`, `>`, `&`,
 * aspas. Números/booleanos passam como string sem alteração.
 */
export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
