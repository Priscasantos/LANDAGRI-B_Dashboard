"""
Accuracy Resolution Component - Comparison Analysis
==================================================

Componente para renderizar a aba de comparação precisão vs resolução.
Contém o gráfico plot_accuracy_resolution_scatter migrado do comparison_charts.py.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


def render_accuracy_resolution_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de comparação precisão vs resolução.
    
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 𝒂/𝓫 Pairwise Performance Analysis: Accuracy vs Spatial Resolution")
    
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para comparação.")
        return
    
    # Controles de visualização
    col1, col2 = st.columns(2)
    
    with col1:
        show_labels = st.checkbox(
            "Show initiative labels",
            value=True,
            help="Display initiative names on the chart"
        )
    
    with col2:
        color_by_type = st.checkbox(
            "Color by type",
            value=True,
            help="Use different colors for each initiative type"
        )
    
    # Informações estatísticas
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    with stats_col1:
        accuracy_data = pd.to_numeric(filtered_df.get("Accuracy (%)", []), errors="coerce")
        avg_accuracy = accuracy_data.mean() if not accuracy_data.isna().all() else 0
        st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
    
    with stats_col2:
        resolution_data = pd.to_numeric(filtered_df.get("Resolution", []), errors="coerce")
        avg_resolution = resolution_data.mean() if not resolution_data.isna().all() else 0
        st.metric("Average Resolution", f"{avg_resolution:.1f}m")
    
    with stats_col3:
        valid_data = len([
            1 for _, row in filtered_df.iterrows()
            if pd.notna(pd.to_numeric(row.get("Accuracy (%)", 0), errors="coerce")) and
               pd.notna(pd.to_numeric(row.get("Resolution", 0), errors="coerce"))
        ])
        st.metric("Valid Initiatives", valid_data)
    
    # Gerar gráfico
    fig_scatter = plot_accuracy_resolution_scatter(
        filtered_df, 
        show_labels=show_labels,
        color_by_type=color_by_type
    )
    
    if fig_scatter:
        st.plotly_chart(fig_scatter, use_container_width=True, key="accuracy_resolution_scatter")
        
    else:
        st.error("❌ Erro ao gerar gráfico de dispersão.")


@smart_cache_data(ttl=300)
def plot_accuracy_resolution_scatter(
    filtered_df: pd.DataFrame,
    show_labels: bool = True,
    color_by_type: bool = True
) -> go.Figure:
    """
    Gráfico de dispersão comparando precisão vs resolução.

    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
        show_labels: Se deve mostrar rótulos das iniciativas
        color_by_type: Se deve colorir por tipo

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
                    "Initiative": row.get("Display_Name", row.get("Name", "Unknown")),
                    "Accuracy": accuracy,
                    "Resolution": resolution,
                    "Type": row.get("Type", "Unknown"),
                    "Methodology": row.get("Methodology", "Unknown"),
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
    color_column = "Type" if color_by_type else None
    
    fig = px.scatter(
        plot_df,
        x="Resolution",
        y="Accuracy",
        color=color_column,
        text="Initiative" if show_labels else None,
        title="Accuracy vs Spatial Resolution",
        labels={
            "Resolution": "Spatial Resolution (m)",
            "Accuracy": "Accuracy (%)",
            "Type": "Initiative Type",
        },
        color_discrete_sequence=get_chart_colors(),
        hover_data=["Methodology"],
    )

    # Melhorar legibilidade
    if show_labels:
        fig.update_traces(
            textposition="top center",
            textfont_size=10,
        )
    
    fig.update_traces(
        marker={"size": 12, "line": {"width": 2, "color": "white"}},
    )

    apply_standard_layout(
        fig,
        title="Comparative Analysis: Accuracy vs Resolution",
        xaxis_title="Spatial Resolution (m)",
        yaxis_title="Accuracy (%)",
    )
    
    # Adicionar linhas de referência
    if plot_df["Accuracy"].max() > 0:
        avg_accuracy = plot_df["Accuracy"].mean()
        fig.add_hline(
            y=avg_accuracy,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Precisão Média: {avg_accuracy:.1f}%"
        )
    
    if plot_df["Resolution"].max() > 0:
        avg_resolution = plot_df["Resolution"].mean()
        fig.add_vline(
            x=avg_resolution,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Resolução Média: {avg_resolution:.1f}m"
        )

    return fig
