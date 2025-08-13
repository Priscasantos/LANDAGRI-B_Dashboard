"""
Heatmap Component - Detailed Analysis
=====================================

Componente para renderizar a aba de heatmap na análise detalhada.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)

def render_heatmap_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render heatmap tab for detailed analysis.
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    if filtered_df.empty:
        st.warning("⚠️ No data available for heatmap.")
        return
    fig = create_heatmap_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="detailed_heatmap_chart")
    else:
        st.error("❌ Error generating heatmap.")

@smart_cache_data(ttl=300)
def create_heatmap_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Criar heatmap detalhado para múltiplas iniciativas.
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
    apply_standard_layout(fig, title="Heatmap de Correlação de Métricas", xaxis_title="Métrica", yaxis_title="Métrica")
    return fig
