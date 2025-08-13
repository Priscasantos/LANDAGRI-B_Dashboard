"""
Scatter Chart Component - Comparison Analysis
============================================

Componente para renderizar a aba de scatter chart na análise comparativa.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_scatter_chart_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de scatter chart para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🟢 Scatter Chart - Relação entre Métricas")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para scatter chart.")
        return
    fig = create_scatter_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="comparison_scatter_chart")
    else:
        st.error("❌ Erro ao gerar scatter chart.")

@smart_cache_data(ttl=300)
def create_scatter_chart(filtered_df: pd.DataFrame) -> px.scatter:
    """
    Criar scatter chart comparativo para múltiplas iniciativas.
    Args:
        filtered_df: DataFrame filtrado
    Returns:
        Figura Plotly Express com scatter chart
    """
    if filtered_df.empty or "Accuracy (%)" not in filtered_df.columns or "Resolution" not in filtered_df.columns:
        return px.scatter()
    fig = px.scatter(
        filtered_df,
        x="Resolution",
        y="Accuracy (%)",
        color="Display_Name" if "Display_Name" in filtered_df.columns else None,
        title="Relação entre Resolução e Acurácia",
    )
    apply_standard_layout(fig, xaxis_title="Resolução", yaxis_title="Acurácia (%)")
    return fig
