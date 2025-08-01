"""
Bar Chart Component - Comparison Analysis
========================================

Componente para renderizar a aba de bar chart na análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_bar_chart_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de bar chart para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📊 Bar Chart - Comparação de Iniciativas")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para bar chart.")
        return
    fig = create_bar_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            label="📥 Download Bar Chart",
            data=fig.to_html(),
            file_name="comparison_bar_chart.html",
            mime="text/html"
        )
    else:
        st.error("❌ Erro ao gerar bar chart.")

@smart_cache_data(ttl=300)
def create_bar_chart(filtered_df: pd.DataFrame) -> px.bar:
    """
    Criar bar chart comparativo para múltiplas iniciativas.
    Args:
        filtered_df: DataFrame filtrado
    Returns:
        Figura Plotly Express com bar chart
    """
    if filtered_df.empty or "Display_Name" not in filtered_df.columns:
        return px.bar()
    # Exemplo: comparar acurácia entre iniciativas
    if "Accuracy (%)" in filtered_df.columns:
        fig = px.bar(
            filtered_df,
            x="Display_Name",
            y="Accuracy (%)",
            color="Display_Name",
            title="Acurácia por Iniciativa",
        )
        apply_standard_layout(fig, xaxis_title="Iniciativa", yaxis_title="Acurácia (%)")
        return fig
    return px.bar()
