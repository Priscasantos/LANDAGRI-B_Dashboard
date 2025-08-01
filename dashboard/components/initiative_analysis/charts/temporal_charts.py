"""
Temporal Analysis Charts
=======================

Gráficos específicos para análise temporal de iniciativas LULC.
Separado da estrutura monolítica para organização modular.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

import pandas as pd
import plotly.graph_objects as go

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


@smart_cache_data(ttl=300)
def plot_temporal_evolution_frequency(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de evolução temporal da frequência de iniciativas.

    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas

    Returns:
        Figura Plotly com evolução temporal
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para análise temporal",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Extrair dados temporais
    temporal_data = []
    for _, row in filtered_df.iterrows():
        if "Start_Year" in row and "End_Year" in row:
            start_year = pd.to_numeric(row["Start_Year"], errors="coerce")
            end_year = pd.to_numeric(row["End_Year"], errors="coerce")

            if pd.notna(start_year) and pd.notna(end_year):
                for year in range(int(start_year), int(end_year) + 1):
                    temporal_data.append(
                        {
                            "Year": year,
                            "Initiative": row.get("Display_Name", "Unknown"),
                            "Type": row.get("Type", "Unknown"),
                        }
                    )

    if not temporal_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados temporais insuficientes",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    temp_df = pd.DataFrame(temporal_data)
    yearly_counts = temp_df.groupby("Year").size().reset_index(name="Count")

    # Criar gráfico de linha
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly_counts["Year"],
            y=yearly_counts["Count"],
            mode="lines+markers",
            name="Iniciativas Ativas",
            line={"color": get_chart_colors()[0], "width": 3},
            marker={"size": 8},
        )
    )

    apply_standard_layout(
        fig,
        title="Evolução Temporal de Iniciativas LULC",
        xaxis_title="Ano",
        yaxis_title="Número de Iniciativas Ativas",
    )

    return fig


@smart_cache_data(ttl=300)
def plot_timeline_chart(
    metadata: dict,
    filtered_df: pd.DataFrame,
    chart_height: int | None = None,
    chart_width: int | None = None,
    item_spacing: int = 25,
    line_width: int = 15,
    margin_config: dict | None = None,
) -> go.Figure:
    """
    Plot an improved timeline using anos_disponiveis from metadata, with acronyms from DataFrame.
    Args:
        metadata: Initiative metadata
        filtered_df: Filtered DataFrame
        chart_height: Custom chart height (None for auto)
        chart_width: Custom chart width (None for auto)
        item_spacing: Vertical spacing between items (pixels)
        line_width: Width of timeline bars
        margin_config: Custom margins dict
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (Insufficient data)"
        )

    plot_df = filtered_df.copy()
    if "Name" not in plot_df.columns and "Nome" in plot_df.columns:
        plot_df.rename(columns={"Nome": "Name"}, inplace=True)
    from dashboard.components.shared.chart_core import add_display_names_to_df

    if "Display_Name" not in plot_df.columns:
        plot_df = add_display_names_to_df(plot_df)

    timeline_data = []
    all_years = set()

    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]
        if initiative_row_series.empty:
            continue
        initiative_row = initiative_row_series.iloc[0]
        display_name = initiative_row["Display_Name"]
        metodologia = initiative_row.get("Methodology", "N/A")
        coverage = meta_content.get("coverage", "N/A")
        years_key = (
            "available_years"
            if "available_years" in meta_content
            else "anos_disponiveis"
        )
        if years_key in meta_content and meta_content[years_key]:
            valid_years_for_initiative = [
                int(y)
                for y in meta_content[years_key]
                if pd.notna(y) and str(y).strip().isdigit()
            ]
            if not valid_years_for_initiative:
                continue
            for ano in valid_years_for_initiative:
                timeline_data.append(
                    {
                        "produto": nome_original_metadata,
                        "produto_display_name": display_name,
                        "ano": int(ano),
                        "disponivel": 1,
                        "metodologia": metodologia,
                        "coverage": coverage,
                    }
                )
                all_years.add(int(ano))

    if not timeline_data:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No temporal data for selected initiatives)"
        )
    timeline_df = pd.DataFrame(timeline_data)

    min_year_data = int(timeline_df["ano"].min()) if not timeline_df.empty else 1985
    max_year_data = int(timeline_df["ano"].max()) if not timeline_df.empty else 2024
    chart_min_year, chart_max_year = min_year_data, max_year_data + 1
    all_years_range = list(range(min_year_data, max_year_data + 1))
    coverage_order = ["Global", "Continental", "National", "Regional", "N/A"]

    unique_items = []
    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]
        if not initiative_row_series.empty:
            initiative_row = initiative_row_series.iloc[0]
            acronym = meta_content.get("acronym", initiative_row["Display_Name"])
            coverage = meta_content.get("coverage", "N/A")
            unique_items.append(
                (nome_original_metadata, {"coverage": coverage, "acronym": acronym})
            )

    try:
        sorted_items = sorted(
            unique_items,
            key=lambda x: (
                (
                    coverage_order.index(x[1]["coverage"])
                    if x[1]["coverage"] in coverage_order
                    else len(coverage_order)
                ),
                x[1]["acronym"],
            ),
            reverse=True,
        )
    except (ValueError, KeyError):
        sorted_items = sorted(unique_items, key=lambda x: x[1]["acronym"])

    display_acronyms_sorted = [item[1]["acronym"] for item in sorted_items]
    if not display_acronyms_sorted:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No unique initiatives to display)"
        )

    matrix_data = []
    for item in sorted_items:
        nome_original_metadata = item[0]
        acronym = item[1]["acronym"]
        produto_data_for_matrix_rows = timeline_df[
            timeline_df["produto"] == nome_original_metadata
        ]
        if produto_data_for_matrix_rows.empty:
            continue
        produto_anos = produto_data_for_matrix_rows["ano"].tolist()
        produto_metodologia = produto_data_for_matrix_rows["metodologia"].iloc[0]
        for ano_iter in all_years_range:
            matrix_data.append(
                {
                    "produto": nome_original_metadata,
                    "produto_acronym": acronym,
                    "ano": ano_iter,
                    "disponivel": 1 if ano_iter in produto_anos else 0,
                    "metodologia": produto_metodologia,
                }
            )

    if not matrix_data:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No data for matrix generation)"
        )
    matrix_df = pd.DataFrame(matrix_data)

    fig_timeline = go.Figure()
    import plotly.express as px

    from scripts.utilities.config import get_initiative_color_map

    unique_original_names_for_colors = [item[0] for item in sorted_items]
    color_map = get_initiative_color_map(unique_original_names_for_colors)

    for acronym in display_acronyms_sorted:
        produto_data_plot = matrix_df[matrix_df["produto_acronym"] == acronym]
        if produto_data_plot.empty:
            continue
        anos_disponiveis = sorted(
            produto_data_plot[produto_data_plot["disponivel"] == 1]["ano"].tolist()
        )
        metodologia = produto_data_plot["metodologia"].iloc[0]
        original_name_for_color_key = produto_data_plot["produto"].iloc[0]
        cor = color_map.get(
            original_name_for_color_key,
            px.colors.qualitative.Set1[
                display_acronyms_sorted.index(acronym) % len(px.colors.qualitative.Set1)
            ],
        )

        if anos_disponiveis:
            segments = []
            start_year_segment = anos_disponiveis[0]
            end_year_segment = anos_disponiveis[0]
            for j in range(1, len(anos_disponiveis)):
                if anos_disponiveis[j] == end_year_segment + 1:
                    end_year_segment = anos_disponiveis[j]
                else:
                    segments.append((start_year_segment, end_year_segment))
                    start_year_segment = anos_disponiveis[j]
                    end_year_segment = anos_disponiveis[j]
            segments.append((start_year_segment, end_year_segment))

            for seg_start, seg_end in segments:
                fig_timeline.add_trace(
                    go.Scatter(
                        x=[seg_start, seg_end + 1],
                        y=[acronym, acronym],
                        mode="lines",
                        line={"color": cor, "width": line_width},
                        name=acronym,
                        showlegend=False,
                        legendgroup=acronym,
                        hovertemplate=f"<b>{acronym}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>",
                    )
                )

    from scripts.plotting.chart_core import CHART_CONFIG

    default_margins = {
        "l": CHART_CONFIG["margins"]["left"],
        "r": CHART_CONFIG["margins"]["right"],
        "t": CHART_CONFIG["margins"]["top"],
        "b": CHART_CONFIG["margins"]["bottom"],
    }
    margins = margin_config if margin_config else default_margins

    if chart_height is None:
        calculated_height = max(300, len(display_acronyms_sorted) * item_spacing)
    else:
        calculated_height = chart_height

    tick_width_standard = 0.8

    fig_timeline.update_layout(
        height=calculated_height,
        margin=margins,
        yaxis={
            "tickmode": "array",
            "tickvals": display_acronyms_sorted,
            "ticktext": display_acronyms_sorted,
            "type": "category",
            "categoryorder": "array",
            "categoryarray": display_acronyms_sorted,
            "showgrid": False,
            "ticks": "outside",
            "ticklen": 8,
            "tickwidth": tick_width_standard,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
        },
        xaxis={
            "range": [chart_min_year - 0.5, chart_max_year + 0.5],
            "tickmode": "array",
            "tickvals": list(range(chart_min_year, chart_max_year + 2)),
            "ticktext": [
                str(year) for year in range(chart_min_year, chart_max_year + 2)
            ],
            "tickformat": "d",
            "tickangle": -45,
            "ticks": "outside",
            "ticklen": 8,
            "tickwidth": tick_width_standard,
            "tickcolor": "black",
            "showgrid": True,
            "zeroline": False,
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
            "type": "linear",
            "dtick": 1,
            "autorange": False,
            "fixedrange": False,
        },
        showlegend=True,
        legend={"traceorder": "normal"},
    )
    return fig_timeline


@smart_cache_data(ttl=300)
def plot_coverage_gaps_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Análise de lacunas temporais na cobertura.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com análise de gaps
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para análise de gaps",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Calcular gaps por ano
    all_years = set()
    initiative_years = {}

    for _, row in filtered_df.iterrows():
        start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
        end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")

        if pd.notna(start_year) and pd.notna(end_year):
            years = set(range(int(start_year), int(end_year) + 1))
            all_years.update(years)
            initiative_years[row.get("Display_Name", "Unknown")] = years

    if not all_years:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para análise de gaps",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Calcular cobertura por ano
    year_coverage = {}
    for year in sorted(all_years):
        coverage_count = sum(1 for years in initiative_years.values() if year in years)
        year_coverage[year] = coverage_count

    # Criar gráfico de barras
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(year_coverage.keys()),
            y=list(year_coverage.values()),
            name="Cobertura por Ano",
            marker_color=get_chart_colors()[0],
        )
    )

    apply_standard_layout(
        fig,
        title="Cobertura Temporal - Análise de Gaps",
        xaxis_title="Ano",
        yaxis_title="Número de Iniciativas",
    )

    return fig


@smart_cache_data(ttl=300)
def plot_temporal_availability_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Cria heatmap de disponibilidade temporal das iniciativas.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com heatmap de disponibilidade
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para heatmap temporal",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Heatmap de Disponibilidade Temporal")

    # Construir matriz de disponibilidade
    availability_matrix = []
    initiative_names = []
    all_years = set()

    for _, row in filtered_df.iterrows():
        start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
        end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")

        if pd.notna(start_year) and pd.notna(end_year):
            years = list(range(int(start_year), int(end_year) + 1))
            all_years.update(years)
            initiative_names.append(row.get("Display_Name", "Unknown")[:25])

    if not all_years:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados temporais insuficientes para heatmap",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Heatmap de Disponibilidade Temporal")

    sorted_years = sorted(all_years)

    # Construir matriz
    for _, row in filtered_df.iterrows():
        start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
        end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")

        if pd.notna(start_year) and pd.notna(end_year):
            initiative_years = set(range(int(start_year), int(end_year) + 1))
            row_data = [1 if year in initiative_years else 0 for year in sorted_years]
            availability_matrix.append(row_data)

    if not availability_matrix:
        fig = go.Figure()
        fig.add_annotation(
            text="Matriz de disponibilidade vazia",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Heatmap de Disponibilidade Temporal")

    # Criar heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=availability_matrix,
            x=sorted_years,
            y=initiative_names,
            colorscale=[
                [0, "#ECEFF4"],  # Não disponível
                [1, "#5E81AC"],  # Disponível
            ],
            hoverongaps=False,
            hovertemplate="<b>%{y}</b><br>Ano: %{x}<br>Disponível: %{z}<extra></extra>",
            showscale=True,
            colorbar={
                "title": "Disponibilidade",
                "tickvals": [0, 1],
                "ticktext": ["Não", "Sim"],
            },
        )
    )

    fig.update_layout(
        title={
            "text": "🔥 Heatmap de Disponibilidade Temporal",
            "x": 0.5,
            "font": {"size": 18, "color": "#2E3440"},
        },
        xaxis={"title": "Ano", "title_font": {"size": 14, "color": "#4C566A"}},
        yaxis={"title": "Iniciativas", "title_font": {"size": 14, "color": "#4C566A"}},
        height=max(400, len(initiative_names) * 25 + 100),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif"},
    )

    return fig
