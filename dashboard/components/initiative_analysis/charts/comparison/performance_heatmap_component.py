"""
Performance Heatmap Component - Comparison Analysis
==================================================

Componente para renderizar a aba de heatmap de performance na análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_performance_heatmap_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de heatmap de performance para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🔥 Heatmap de Performance Normalizada")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para heatmap de performance.")
        return
    fig = create_performance_heatmap(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            label="📥 Download Heatmap",
            data=fig.to_html(),
            file_name="performance_heatmap.html",
            mime="text/html"
        )
    else:
        st.error("❌ Erro ao gerar heatmap de performance.")

@smart_cache_data(ttl=300)
def create_performance_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Criar heatmap de performance normalizada entre iniciativas.
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
    # Exemplo: heatmap de normalização de acurácia e resolução
    metrics = ["Accuracy (%)", "Resolution"]
    data = []
    initiatives = []
    for _, row in filtered_df.iterrows():
        row_data = []
        for metric in metrics:
            val = pd.to_numeric(row.get(metric, 0), errors="coerce")
            row_data.append(val if pd.notna(val) else 0)
        data.append(row_data)
        initiatives.append(row.get("Display_Name", row.get("Name", "Unknown")))
    if not data:
        return go.Figure()
    z = data
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=metrics,
        y=initiatives,
        colorscale="Viridis"
    ))
    apply_standard_layout(fig, title="Heatmap de Performance Normalizada", xaxis_title="Métrica", yaxis_title="Iniciativa")
    return fig
