"""
Distributions Component - Comparison Analysis
=============================================

Componente para renderizar análise de distribuições de métricas.
Combina gráficos de metodologia, resolução espacial e cobertura temporal.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import uuid

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


def render_distributions_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de distribuições com múltiplos gráficos de análise.
    
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📉 Distributions Analysis")
    st.markdown("*Analysis of initiative distributions across different dimensions.*")

    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para análise de distribuições.")
        return
    
    # Sub-abas para diferentes tipos de distribuições
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "🔧 Methodologies",
        "📉 Distributions Analysis",
        "⏱️ Temporal Coverage",
    ])
    
    with sub_tab1:
        st.markdown("#### 🔧 Methodologies")
        render_methodology_distribution(filtered_df)
    
    with sub_tab2:
        st.markdown("#### 📉 Distributions Analysis")
        render_resolution_distribution(filtered_df)
    
    with sub_tab3:
        st.markdown("#### ⏱️ Temporal Coverage")
        render_temporal_coverage_distribution(filtered_df)


def render_methodology_distribution(filtered_df: pd.DataFrame) -> None:
    """Renderizar distribuição de metodologias por tipo."""
    
    fig_methodology = plot_methodology_comparison(filtered_df)
    if fig_methodology:
        # Use a short uuid suffix to ensure the chart key is unique across multiple renders
        unique_key = f"methodology_distribution_chart_{uuid.uuid4().hex[:8]}"
        st.plotly_chart(fig_methodology, use_container_width=True, key=unique_key)
    else:
        st.info("ℹ️ Dados insuficientes para análise de metodologias.")


def render_resolution_distribution(filtered_df: pd.DataFrame) -> None:
    """Renderizar distribuição de resoluções espaciais."""
    
    fig_resolution = plot_spatial_resolution_comparison(filtered_df)
    if fig_resolution:
        st.plotly_chart(fig_resolution, use_container_width=True, key="resolution_distribution_chart")
    else:
        st.info("ℹ️ Dados insuficientes para análise de resolução.")


def render_temporal_coverage_distribution(filtered_df: pd.DataFrame) -> None:
    """Renderizar distribuição de cobertura temporal."""
    
    fig_temporal = plot_temporal_coverage_comparison(filtered_df)
    if fig_temporal:
        st.plotly_chart(fig_temporal, use_container_width=True, key="temporal_coverage_distribution_chart")
    else:
        st.info("ℹ️ Dados insuficientes para análise temporal.")


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
        return None

    # Verificar se temos as colunas necessárias
    if "Type" not in filtered_df.columns or "Methodology" not in filtered_df.columns:
        return None

    # Contar metodologias por tipo
    methodology_counts = (
        filtered_df.groupby(["Type", "Methodology"]).size().reset_index(name="Count")
    )

    if methodology_counts.empty:
        return None

    # Criar gráfico de barras agrupadas
    fig = go.Figure()

    colors = get_chart_colors()
    methodologies = methodology_counts["Methodology"].unique()

    for i, methodology in enumerate(methodologies):
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
        title="Distribution of Methodologies by Type",
        xaxis_title="Initiative Type",
        yaxis_title="Number of Initiatives",
    )

    # Set legend title
    fig.update_layout(legend=dict(title=dict(text="Methodology")))

    fig.update_layout(barmode="group")
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
    if filtered_df.empty or "Resolution" not in filtered_df.columns:
        return None

    # Extrair dados de resolução
    resolution_data = []
    for _, row in filtered_df.iterrows():
        resolution = pd.to_numeric(row.get("Resolution", 0), errors="coerce")
        if pd.notna(resolution) and resolution > 0:
            resolution_data.append({
                "Initiative": row.get("Display_Name", row.get("Name", "Unknown")),
                "Resolution": resolution,
                "Type": row.get("Type", "Unknown")
            })

    if not resolution_data:
        return None

    res_df = pd.DataFrame(resolution_data)

    # Criar gráfico de barras
    fig = px.bar(
        res_df,
        x="Initiative",
        y="Resolution",
        color="Type",
        title="Spatial Resolution Comparison",
        labels={
            "Resolution": "Resolution (m)",
            "Initiative": "Initiatives",
            "Type": "Type"
        },
        color_discrete_sequence=get_chart_colors()
    )

    apply_standard_layout(
        fig,
        title="Spatial Resolution Comparison",
        xaxis_title="Initiatives",
        yaxis_title="Resolution (m)"
    )

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
        return None

    # Calcular duração de cada iniciativa
    temporal_data = []
    for _, row in filtered_df.iterrows():
        start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
        end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")

        if pd.notna(start_year) and pd.notna(end_year):
            duration = int(end_year) - int(start_year) + 1
            temporal_data.append(
                {
                    "Initiative": row.get("Display_Name", row.get("Name", "Unknown")),
                    "Duration": duration,
                    "Start_Year": int(start_year),
                    "End_Year": int(end_year),
                    "Type": row.get("Type", "Unknown"),
                }
            )

    if not temporal_data:
        return None

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
        title="Temporal Duration of Initiatives",
        xaxis_title="Duration (years)",
        yaxis_title="Initiatives",
    )

    # Set legend title
    fig.update_layout(legend=dict(title=dict(text="Level")))

    fig.update_layout(
        height=max(400, len(temporal_data) * 25), 
        yaxis={"autorange": "reversed"}
    )

    return fig
