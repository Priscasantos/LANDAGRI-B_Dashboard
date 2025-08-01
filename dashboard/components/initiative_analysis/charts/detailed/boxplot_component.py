"""
Boxplot Component - Detailed Analysis
====================================

Componente para renderizar a aba de boxplot na análise detalhada.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_boxplot_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de boxplot para análise detalhada.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📦 Boxplot Detalhado das Iniciativas")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para boxplot.")
        return
    fig = create_boxplot_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            label="📥 Download Boxplot",
            data=fig.to_html(),
            file_name="detailed_boxplot.html",
            mime="text/html"
        )
    else:
        st.error("❌ Erro ao gerar boxplot.")

@smart_cache_data(ttl=300)
def create_boxplot_chart(filtered_df: pd.DataFrame) -> px.box:
    """
    Criar boxplot detalhado para múltiplas iniciativas.
    Args:
        filtered_df: DataFrame filtrado
    Returns:
        Figura Plotly Express com boxplot
    """
    if filtered_df.empty or "Display_Name" not in filtered_df.columns:
        return px.box()
    # Exemplo: boxplot de acurácia por iniciativa
    if "Accuracy (%)" in filtered_df.columns:
        fig = px.box(
            filtered_df,
            x="Display_Name",
            y="Accuracy (%)",
            color="Display_Name",
            title="Distribuição Detalhada da Acurácia por Iniciativa",
        )
        apply_standard_layout(fig, xaxis_title="Iniciativa", yaxis_title="Acurácia (%)")
        return fig
    return px.box()
