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
  # Relatório de melhorias nos gráficos

  Objetivo: inventariar valores e strings hardcoded em gráficos, priorizar o que deve ser centralizado e propor um plano de ação com foco em facilidade de manutenção e consistência visual.

  Escopo inicial: análise focal em `dashboard/components/agricultural_analysis/charts/availability/crop_diversity.py` (estado + região) — os achados podem ser replicados a outros módulos.

  ## Sumário Executivo

  - Itens de alta prioridade: valores user-facing e layout que afetam a interface (títulos, hovertemplates, legendas, margens e paletas de cores). Priorizar centralização.
  - Itens de média prioridade: docstrings, region mapping duplicado, valores numéricos (tamanhos, alturas) que afetam legibilidade.
  - Itens de baixa prioridade: comentários e nomes internos.

  ---

  ## Progresso recente (hoje)

  - Inspeção detalhada do módulo `crop_diversity.py` e identificação de hardcodings (palette, hovertemplates, layout, region mapping).
  - Adicionados helpers centralizados em `dashboard/components/shared/chart_core.py`:
    - `HOVER_TEMPLATE_CROP`, `HOVER_TEMPLATE_REGION` (com Plotly placeholders escapados);
    - `calc_height(n_rows, min_height=400, per_row=25)`;
    - `build_standard_layout(title, title_x, **overrides)`.
  - Refatorado `dashboard/components/agricultural_analysis/charts/availability/crop_diversity.py` para consumir os helpers e correção de import relativo.
  - Corrigido bug em hovertemplates (KeyError causado por `str.format`) e validado via `py_compile`.

  ## Inventário — o que precisa ser padronizado (detalhado)

  1) Paleta de cores (hardcoded)
  - Local: `enhanced_palette` dentro de `crop_diversity.py`.
  - Impacto: duplicação e dificuldade para alterar esquema globalmente.
  - Ação: mover para `dashboard.components.shared.color_palettes` ou `scripts/utilities/color_palettes.py` e expor `DEFAULT_QUALITATIVE_20`.

  2) Política de resolução de cor por cultura
  - Local: lógica inline que chama `get_crop_color` e aplica fallback para paleta.
  - Impacto: lógica espalhada por módulos.
  - Ação: criar `resolve_crop_color(crop, index=None, region=None)` em `color_palettes` ou `chart_core`.

  3) Hovertemplates (user-facing formatting)
  - Local: cada trace constrói seu próprio hovertemplate.
  - Impacto: variações acidentais e dificuldade para adicionar units/localização.
  - Ação: usar `HOVER_TEMPLATE_*` + small formatter function para produzir strings finais.

  4) Layout e tema (font, margins, legend)
  - Local: `fig.update_layout(...)` com muitos hardcoded em cada arquivo.
  - Impacto: inconsistências e custo para alterar visual global.
  - Ação: consolidar em `build_standard_layout` (já criado) e aplicar em charts prioritários.

  5) Region mapping duplicado
  - Local: `region_mapping` repetido em múltiplas funções.
  - Ação: extrair `REGION_MAPPING` para `constants/regions.py`.

  6) Magic numbers (font sizes, margins, line widths)
  - Ação: expor constantes em `chart_core` como `BASE_FONT_SIZE`, `LEGEND_FONT_SIZE`, `MARGIN_DEFAULT`.

  7) Typing / linting issues
  - Exemplos: use built-in `dict` type annotation (PEP585), trailing whitespace, unused imports.
  - Ação: quick lint pass on files modified.

  ## Priorização (curto prazo)

  - Alta (urgente):
    1. Centralizar paleta + fallback de cores.
    2. Consolidar layout/theme via `build_standard_layout` e aplicar a `crop_diversity.py` (feito) e 2–3 módulos prioritários.
    3. Centralizar hover templates e garantir escaping seguro.
  - Média:
    1. Extrair `REGION_MAPPING` para módulo de constantes.
    2. Padronizar `calc_height` para charts com linhas variáveis.
  - Baixa:
    1. Lint/PEP fixes e remoção de imports não usados.

  ## Plano de ação — próximos passos (sprint)

  1. Curto prazo (hoje/amanhã)
     - Rodar validação visual local: `streamlit run dashboard/overview_preview.py` e corrigir regressões (eu posso executar e reportar).
     - Aplicar lint rápido nas alterações feitas (`chart_core.py`, `crop_diversity.py`, e outros arquivos que você editou).

  2. Próximas 3–5 tarefas (esta sprint)
     - Propagar `build_standard_layout` + `HOVER_TEMPLATE_*` + `calc_height` para módulos prioritários: sugeridos:
       - `monthly_activity_charts.py`
       - `conab_availability_analysis.py`
       - `regional_calendar_charts.py`
       - `modern_timeline_chart.py`
       - `conab_specific_charts.py`
     - Implementar `resolve_crop_color` e mover DEFAULT palette para `color_palettes`.

  3. Longo prazo
     - Adicionar smoke tests para importar/render charts (headless) no CI.
     - Centralizar user-facing labels em `ui_text.py` com suporte a i18n.

  ## Riscos e notas de validação

  - Fazer grandes mudanças na API de `color_palettes` pode exigir atualizações em múltiplos módulos; prefira adicionar novas funções mantendo as antigas compatíveis.
  - Alterações visuais (margins/legend) exigem verificação manual no UI.

  ---

  ## Quick wins eu posso executar agora

  - Rodar Streamlit e validar visualmente (reportarei erros/runtime stack traces).
  - Aplicar correções de lint nos arquivos alterados.
  - Propagar `build_standard_layout` para 1–2 módulos e abrir patches separados.

  Diga qual ação prefere que eu faça primeiro: `rodar Streamlit` ou `corrigir lint`.
