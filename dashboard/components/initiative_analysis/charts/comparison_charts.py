"""
Comparison Analysis Charts
=========================

Gráficos específicos para análise comparativa de iniciativas LULC.
Organização modular dos charts de comparação.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


@smart_cache_data(ttl=300)
def plot_accuracy_resolution_scatter(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de dispersão comparando precisão vs resolução.

    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas

    Returns:
        Figura Plotly com scatter plot
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para comparação",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Extrair dados de precisão e resolução
    plot_data = []
    for _, row in filtered_df.iterrows():
        accuracy = pd.to_numeric(row.get("Accuracy (%)", 0), errors="coerce")
        resolution = pd.to_numeric(row.get("Resolution", 0), errors="coerce")

        if (
            pd.notna(accuracy)
            and pd.notna(resolution)
            and accuracy > 0
            and resolution > 0
        ):
            plot_data.append(
                {
                    "Initiative": row.get("Display_Name", "Unknown"),
                    "Accuracy": accuracy,
                    "Resolution": resolution,
                    "Type": row.get("Type", "Unknown"),
                }
            )

    if not plot_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para análise de precisão vs resolução",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    plot_df = pd.DataFrame(plot_data)

    # Criar scatter plot
    fig = px.scatter(
        plot_df,
        x="Resolution",
        y="Accuracy",
        color="Type",
        text="Initiative",
        title="Precisão vs Resolução Espacial",
        labels={
            "Resolution": "Resolução Espacial (m)",
            "Accuracy": "Precisão (%)",
            "Type": "Tipo de Iniciativa",
        },
        color_discrete_sequence=get_chart_colors(),
    )

    # Melhorar legibilidade
    fig.update_traces(
        textposition="top center",
        marker=dict(size=12, line=dict(width=2, color="white")),
    )

    apply_standard_layout(
        fig,
        title="Análise Comparativa: Precisão vs Resolução",
        xaxis_title="Resolução Espacial (m)",
        yaxis_title="Precisão (%)",
    )

    return fig


@smart_cache_data(ttl=300)
def plot_methodology_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Comparação de metodologias por tipo de iniciativa.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com análise de metodologias
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para análise de metodologias",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Contar metodologias por tipo
    methodology_counts = (
        filtered_df.groupby(["Type", "Methodology"]).size().reset_index(name="Count")
    )

    if methodology_counts.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados de metodologia insuficientes",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Criar gráfico de barras agrupadas
    fig = go.Figure()

    colors = get_chart_colors()
    types = methodology_counts["Type"].unique()

    for i, methodology in enumerate(methodology_counts["Methodology"].unique()):
        method_data = methodology_counts[
            methodology_counts["Methodology"] == methodology
        ]

        fig.add_trace(
            go.Bar(
                name=methodology,
                x=method_data["Type"],
                y=method_data["Count"],
                marker_color=colors[i % len(colors)],
            )
        )

    apply_standard_layout(
        fig,
        title="Distribuição de Metodologias por Tipo",
        xaxis_title="Tipo de Iniciativa",
        yaxis_title="Número de Iniciativas",
    )

    fig.update_layout(barmode="group")

    return fig


@smart_cache_data(ttl=300)
def plot_temporal_coverage_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Comparação da cobertura temporal entre iniciativas.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com análise temporal comparativa
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

    # Calcular duração de cada iniciativa
    temporal_data = []
    for _, row in filtered_df.iterrows():
        start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
        end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")

        if pd.notna(start_year) and pd.notna(end_year):
            duration = int(end_year) - int(start_year) + 1
            temporal_data.append(
                {
                    "Initiative": row.get("Display_Name", "Unknown"),
                    "Duration": duration,
                    "Start_Year": int(start_year),
                    "End_Year": int(end_year),
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

    # Criar gráfico de barras horizontais
    fig = go.Figure()

    colors = get_chart_colors()
    types = temp_df["Type"].unique()

    for i, initiative_type in enumerate(types):
        type_data = temp_df[temp_df["Type"] == initiative_type]

        fig.add_trace(
            go.Bar(
                name=initiative_type,
                y=type_data["Initiative"],
                x=type_data["Duration"],
                orientation="h",
                marker_color=colors[i % len(colors)],
                hovertemplate="<b>%{y}</b><br>"
                + "Duração: %{x} anos<br>"
                + f"Tipo: {initiative_type}<extra></extra>",
            )
        )

    apply_standard_layout(
        fig,
        title="Duração Temporal das Iniciativas",
        xaxis_title="Duração (anos)",
        yaxis_title="Iniciativas",
    )

    fig.update_layout(
        height=max(400, len(temporal_data) * 25), yaxis=dict(autorange="reversed")
    )

    return fig


@smart_cache_data(ttl=300)
def plot_performance_radar(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Gráfico radar para comparação multidimensional.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com radar chart
    """
    if filtered_df.empty or len(filtered_df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para análise radar",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Selecionar as primeiras 5 iniciativas para comparação
    sample_df = filtered_df.head(5).copy()

    # Normalizar métricas para escala 0-1
    metrics = ["Accuracy (%)", "Resolution"]
    radar_data = []

    for _, row in sample_df.iterrows():
        values = []
        for metric in metrics:
            value = pd.to_numeric(row.get(metric, 0), errors="coerce")
            if pd.isna(value):
                value = 0
            values.append(float(value))

        # Normalizar resolução (inverter para que menor seja melhor)
        if len(values) >= 2 and values[1] > 0:
            values[1] = 1 / (values[1] / 100)  # Normalizar resolução

        # Normalizar precisão para escala 0-1
        if len(values) >= 1:
            values[0] = values[0] / 100

        radar_data.append(
            {"Initiative": row.get("Display_Name", "Unknown")[:20], "Values": values}
        )

    if not radar_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para radar",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Criar radar chart
    fig = go.Figure()

    categories = ["Precisão", "Resolução (Normalizada)"]
    colors = get_chart_colors()

    for i, data in enumerate(radar_data):
        values = data["Values"] + [data["Values"][0]]  # Fechar o polígono
        categories_closed = categories + [categories[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories_closed,
                fill="toself",
                name=data["Initiative"],
                line_color=colors[i % len(colors)],
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Comparação Multidimensional - Radar",
        showlegend=True,
    )

    return fig


@smart_cache_data(ttl=300)
def plot_spatial_resolution_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras comparando resoluções espaciais.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com comparação de resoluções
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para comparação de resolução",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Comparação de Resolução Espacial")

    # Extrair dados de resolução
    resolution_data = []
    for _, row in filtered_df.iterrows():
        resolution = pd.to_numeric(row.get("Resolution", 0), errors="coerce")
        if pd.notna(resolution) and resolution > 0:
            resolution_data.append(
                {
                    "Initiative": row.get("Display_Name", "Unknown")[:20],
                    "Resolution": resolution,
                    "Type": row.get("Type", "Unknown"),
                }
            )

    if not resolution_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados de resolução insuficientes",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Comparação de Resolução Espacial")

    resolution_df = pd.DataFrame(resolution_data)
    resolution_df = resolution_df.sort_values("Resolution")

    # Criar gráfico de barras
    fig = px.bar(
        resolution_df,
        x="Initiative",
        y="Resolution",
        color="Type",
        title="Comparação de Resolução Espacial",
        labels={
            "Resolution": "Resolução (m)",
            "Initiative": "Iniciativas",
            "Type": "Tipo",
        },
        color_discrete_sequence=get_chart_colors(),
    )

    apply_standard_layout(
        fig,
        title="Comparação de Resolução Espacial",
        xaxis_title="Iniciativas",
        yaxis_title="Resolução (m)",
    )

    fig.update_layout(xaxis_tickangle=-45)

    return fig


@smart_cache_data(ttl=300)
def plot_correlation_matrix(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Matriz de correlação entre métricas numéricas.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com matriz de correlação
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para matriz de correlação",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Matriz de Correlação")

    # Selecionar apenas colunas numéricas relevantes
    numeric_cols = []
    for col in [
        "Accuracy (%)",
        "Resolution",
        "Total_Classes",
        "Start_Year",
        "End_Year",
    ]:
        if col in filtered_df.columns:
            numeric_data = pd.to_numeric(filtered_df[col], errors="coerce")
            if not numeric_data.isna().all():
                numeric_cols.append(col)

    if len(numeric_cols) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados numéricos insuficientes para correlação",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return apply_standard_layout(fig, title="Matriz de Correlação")

    # Calcular matriz de correlação
    numeric_df = filtered_df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    correlation_matrix = numeric_df.corr()

    # Criar heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale="RdBu",
            zmid=0,
            hoverongaps=False,
            hovertemplate="<b>%{x} vs %{y}</b><br>Correlação: %{z:.3f}<extra></extra>",
            showscale=True,
            colorbar=dict(title="Correlação"),
        )
    )

    fig.update_layout(
        title={
            "text": "🔗 Matriz de Correlação entre Métricas",
            "x": 0.5,
            "font": {"size": 18, "color": "#2E3440"},
        },
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif"},
    )

    return fig
