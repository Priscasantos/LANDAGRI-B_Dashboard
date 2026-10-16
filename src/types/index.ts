export * from './initiative';
export * from './sensor';
export * from './agricultural';
export * from './calendar';
export * from './theme';
// Nota: `plotly.d.ts` é declaração ambiente (tipos globais Plotly) e por isso
// fica fora do barrel — não é módulo re-exportável.
// Direção de imports: `src/lib/` importa tipos daqui; `src/types/` nunca
// importa de `src/lib/` (validado por grep na revisão do council).
