# Relatório de Melhorias nos Gráficos

Objetivo: inventariar valores e strings hardcoded em gráficos, priorizar o que deve ser centralizado e propor um plano de ação com foco em facilidade de manutenção e consistência visual.

Escopo inicial: análise focal em `dashboard/components/agricultural_analysis/charts/availability/crop_diversity.py` (estado + região) — os achados podem ser replicados a outros módulos.

## Sumário Executivo
- Itens de alta prioridade: valores user-facing e layout que afetam a interface (títulos, hovertemplates, legendas, margens e paletas de cores). Priorizar centralização.
- Itens de média prioridade: docstrings, region mapping duplicado, valores numéricos (tamanhos, alturas) que afetam legibilidade.
- Itens de baixa prioridade: comentários e nomes internos.

---

## Inventário — `crop_diversity.py` (principais hardcodings)

1) Paleta de cores (hardcoded)
- Local: `enhanced_palette` (lista de hex) — linhas cerca de 40-55 do arquivo.
- Exemplos:
  - '#1f77b4', '#ff7f0e', '#2ca02c', ...
- Impacto: Duplicação de paletas e dificuldade para alterar esquema de cores globalmente.
- Ação sugerida: mover para `scripts/utilities/modern_color_palettes.py` (ou usar o módulo `color_palettes` já existente). Exportar como `DEFAULT_QUALITATIVE_20` ou similar.

2) Lógica de resolução de cor por cultura
- Local: iteração `for i, crop in enumerate(crop_series.keys()): explicit_color = get_crop_color(crop) ...` (logo após a paleta)
- Impacto: mistura de lógica de cores e construção do gráfico.
- Ação: criar utilitário `resolve_crop_color(crop, index)` em `color_palettes` que encapsule fallback e regras de cor.

3) Hovertemplate hardcoded
- Local: em cada trace: `hovertemplate=f"<b>{crop}</b><br>State: %{{y}}<br>Intensity: %{{x}}<extra></extra>"`
- Impacto: formatação repetida, difícil alteração global (por exemplo incluir unidades ou localizações diferentes).
- Ação: centralizar templates em `ui_text.py` ou `chart_helpers.py` como `HOVER_TEMPLATE_CROP` e fornecer função `format_hover(crop)`.

4) Layout e tema hardcoded
- Local: `fig.update_layout(...)` — inclui `title`, `xaxis_title`, `yaxis_title`, `height`, `barmode`, `plot_bgcolor`, `paper_bgcolor`, `font`, `legend`, `margin`, `yaxis`.
- Exemplos: `height=max(400, len(states) * 25)`, `margin=dict(l=100, r=260, t=80, b=60)`, `legend` placement `x=1.02`.
- Impacto: inconsistência entre gráficos; alteração do visual exige editar muitos arquivos.
- Ação: criar `chart_theme.py` (ou similar) com `BASE_LAYOUT`, `LEGEND_STYLE`, `TITLE_STYLE`, `AXIS_STYLE` e usar `fig.update_layout(**BASE_LAYOUT, title=..., height=calc_height(len(states)))`.

5) Region mapping duplicado
- Local: `region_mapping` aparece tanto na versão state quanto na region (duplicação de  map).
- Impacto: manutenção dolorosa se regras mudarem.
- Ação: extrair `REGION_MAPPING` para `constants/regions.py` ou `color_palettes` se apropriado.

6) Valores numéricos magic numbers
- Exemplos: font sizes (11, 12, 14, 15), line widths, borderwidths, margin numeric values.
- Ação: mover para `chart_theme` constants (BASE_FONT_SIZE, LEGEND_FONT_SIZE, MARGIN_DEFAULT).

---

## Priorização (curto prazo)
- Alta (implementar primeiro):
  1. Centralizar paleta de cores e resolver fallback (`color_palettes`).
  2. Centralizar layout/tema base (`chart_theme`), mover `fig.update_layout` properties para lá.
  3. Centralizar hovertemplates e strings user-facing (títulos/axis labels) em `ui_text.py`.
- Média:
  1. Extrair `REGION_MAPPING` para um módulo de constantes.
  2. Parametrizar altura `height` com função utilitária `calc_height(n, min_h=400, per_row=25)`.
- Baixa:
  1. Renomear/comments, limpar duplicação menor.

---

## Exemplo mínimo de implementação (não aplicado automaticamente)
- Novo arquivo sugerido: `scripts/utilities/chart_theme.py`
```py
BASE_LAYOUT = {
  'plot_bgcolor': 'rgba(0,0,0,0)',
  'paper_bgcolor': 'rgba(0,0,0,0)',
  'font': {'family': 'Arial, sans-serif', 'size': 12, 'color': '#2C3E50'},
  'barmode': 'stack'
}
LEGEND_STYLE = {'orientation': 'v', 'x': 1.02, 'y': 1, 'bordercolor': 'rgba(44,62,80,0.1)', 'borderwidth': 1}

# helper
def calc_height(n_rows, min_height=400, per_row=25):
  return max(min_height, n_rows * per_row)
```
- Em `crop_diversity.py` substituir:
  - `ten_color_palette` por `from scripts.utilities.color_palettes import DEFAULT_QUALITATIVE_...`
  - `fig.update_layout(...)` por `fig.update_layout(**BASE_LAYOUT, title=..., height=calc_height(len(states)), legend=LEGEND_STYLE)`

---

## Riscos e notas de validação
- Alterar nomes públicos em `color_palettes` pode exigir atualizar múltiplos módulos; ao invés disso, adicionar novas constantes/funcões mantendo compatibilidade com as existentes reduz risco.
- Ajustes de legenda/margens exigem verificação visual (executar `streamlit run` e inspecionar). Recomendo pequenos commits e revisão manual.

---

## Próximo passo sugerido
- Implementar passo-a-passo: 1) mover paleta e funções de cor, 2) adicionar `chart_theme`, 3) substituir `fig.update_layout` em `crop_diversity.py` e 4) testar localmente.

Se quiser, aplico a primeira mudança (criar `chart_theme.py` e substituir chamadas em `crop_diversity.py`) agora e executo uma checagem de erros.
