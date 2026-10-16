# Gráficos × tema: colorway do preset + paleta divergente

> Reversível: tudo aqui é aditivo. Sem `preset`/`colorway` explícitos, os
> builders caem nas constantes Verde Agro legadas; `palette` default é
> `'theme'`; `data-palette` default é `theme` (sidebar inalterada).

## Por que os gráficos ignoravam o tema

O preset (Azul, Verde Agro, Verde Agro v2, Terra, Âmbar) grava
`--color-chart-1..10` + sidebar + headers na raiz (`use-theme-manager` →
`applyToRoot`). Mas os builders ECharts liam SÓ `theme: 'light'|'dark'` e
resolviam constantes Verde Agro fixas (`LANDAGRI_COLORWAY_*`,
`heatmapVisualColors` sem preset, `getChartLayout().colorway`). Resultado:
só a sidebar mudava de preset; os gráficos, não.

## Como seguem o preset agora

| Camada                                                                           | Antes                              | Depois                                                                                                                         |
| -------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Séries categóricas (barra, linha, pizza, scatter, radar, polar, gantt, timeline) | `LANDAGRI_COLORWAY_*` fixo         | `colorway` injetado via `useChartColorway()` (lê `--color-chart-1..10` vivas, fallback `presetCharts`)                         |
| Heatmap/visualMap sequencial                                                     | rampa Verde Agro fixa              | `heatmapVisualColors(theme, 'theme', preset)` → `sequentialRampForPreset` (neutro → primária do preset)                        |
| Heatmap correlação −1…1                                                          | divergente verde↔terra fixa        | `heatmapVisualColors(theme, 'divergent', preset)` → `divergentRampForPreset` (primária do preset + âncora negativa por preset) |
| Barras de delta em torno de 0                                                    | —                                  | `buildHorizontalBarOption({palette:'divergent', preset})` → `divergingColorForValue` por barra                                 |
| Plotly legado                                                                    | colorway Verde Agro fixa           | `getChartLayout(theme, font, colorway?)`                                                                                       |
| Recharts Predictive (linhas)                                                     | já via `themeDataColor` (tokens) ✓ | deltas via `var(--color-success/error)` (antes hex `#10b981/#ef4444`)                                                          |
| Sidebar                                                                          | tinta sutil do preset              | + variante alto contraste por preset com `palette: 'divergent'` (`sidebarDivergentVars`, `data-palette`)                       |

Grid, tooltip (Berry), legend e markArea/markLine continuam neutros por
desenho — já variavam light/dark e NÃO variam por preset (cromo, não dado).
Exceções semânticas intencionais (identidade visual, nunca preset):
`LULC_CLASS_COLORS`, `phenoColors` (fase fenológica), bordas `#fff`.

## Regra analítica `palette: 'theme' | 'divergent'`

- `'theme'` (default em tudo): categorias e magnitudes.
- `'divergent'`: SÓ onde o sinal importa — heatmap de correlação e barras
  de delta em torno de 0. O global `data-palette` da raiz NÃO re-tinge
  gráficos automaticamente (evita codificar sinal onde só há magnitude);
  ele só densifica a sidebar.
- Âncoras negativas por preset (`DIVERGENT_NEGATIVE` em
  `src/lib/chart-preset.ts`): Azul/Verde\* → vermelho-terra; Terra → teal;
  Âmbar → índigo. Rótulos de célula mantêm contraste AA automático
  (`autoCellLabelColor`).

## Onde mexer

- `src/lib/chart-preset.ts` — `presetCharts`, `sequentialRampForPreset`,
  `divergentRampForPreset`, `divergingColorForValue`, `sidebarDivergentVars`, `mixHex`.
- `src/hooks/use-chart-colorway.ts` — `useChartColorway()` /
  `readChartColorway()` (wrappers → builders).
- `src/hooks/use-theme-manager.ts` — `palette`, `PALETTE_KEY`, `data-palette`.
- `src/components/ThemeCustomizer.tsx` — grupo Paleta (Tema/Divergente).
- Testes: `src/test/charts/chartPreset.test.ts` (16 casos).
