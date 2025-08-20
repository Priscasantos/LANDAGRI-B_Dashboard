"""
Heatmap Component - Comparison Analysis
======================================

Componente para renderizar a aba de heatmap na análise comparativa.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_heatmap_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de heatmap para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🔥 Heatmap Comparativo das Iniciativas")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para heatmap.")
        return
    fig = create_heatmap_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="comparison_heatmap_chart")
    else:
        st.error("❌ Erro ao gerar heatmap.")

@smart_cache_data(ttl=300)
def create_heatmap_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Criar heatmap comparativo para múltiplas iniciativas.
    Args:
        filtered_df: DataFrame filtrado
    Returns:
        Figura Plotly com heatmap
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para heatmap",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig
    # Exemplo: heatmap de correlação entre métricas
    if filtered_df.shape[1] < 2:
        return go.Figure()
    corr = filtered_df.select_dtypes(include=[float, int]).corr()
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale="Viridis"))
    apply_standard_layout(fig, title="Correlation Heatmap of Metrics", xaxis_title="Metric", yaxis_title="Metric")
    return fig
