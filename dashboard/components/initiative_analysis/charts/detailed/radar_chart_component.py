"""
Radar Chart Component - Detailed Analysis
========================================

Componente para renderizar a aba de radar chart na análise detalhada.

Author: Dashboard Iniciativas LULC
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

def render_radar_chart_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de radar chart para análise detalhada.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🎯 Radar Chart - Comparação Multidimensional")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para radar chart.")
        return
    fig = create_radar_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            label="📥 Download Radar Chart",
            data=fig.to_html(),
            file_name="radar_chart.html",
            mime="text/html"
        )
    else:
        st.error("❌ Erro ao gerar radar chart.")

@smart_cache_data(ttl=300)
def create_radar_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Criar radar chart detalhado para múltiplas iniciativas.
    Args:
        filtered_df: DataFrame filtrado
    Returns:
        Figura Plotly com radar chart
    """
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível para radar chart",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig
    # Selecionar métricas
    metrics = [col for col in ["Accuracy (%)", "Resolution"] if col in filtered_df.columns]
    if not metrics:
        return go.Figure()
    # Normalizar dados
    df_norm = filtered_df[metrics].copy()
    for col in metrics:
        max_val = df_norm[col].max()
        min_val = df_norm[col].min()
        if max_val > min_val:
            df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0.5
    fig = go.Figure()
    colors = get_chart_colors()
    for i, (_, row) in enumerate(df_norm.iterrows()):
        values = row.tolist() + [row.tolist()[0]]
        categories = metrics + [metrics[0]]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=filtered_df.iloc[i].get("Display_Name", f"Iniciativa {i+1}"),
            line_color=colors[i % len(colors)],
        ))
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 1]}},
        showlegend=True,
        title="Radar Chart: Comparação Multidimensional",
    )
    return fig
