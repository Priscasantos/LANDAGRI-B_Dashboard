"""
Annual Coverage Component - Detailed Analysis
============================================

Componente para renderizar cobertura anual das iniciativas na análise detalhada.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_annual_coverage_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de cobertura anual das iniciativas.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📅 Cobertura Anual das Iniciativas")
    if filtered_df.empty or "available_years" not in filtered_df.columns:
        st.warning("⚠️ Nenhum dado de cobertura anual disponível.")
        return
    # Prepare data for timeline chart
    import plotly.graph_objects as go
    initiatives = []
    start_years = []
    end_years = []
    for idx, row in filtered_df.iterrows():
        display_name = row.get('Display_Name', row.get('Name', 'Iniciativa'))
        years = row.get("available_years", [])
        if isinstance(years, list) and years:
            initiatives.append(display_name)
            start_years.append(min(years))
            end_years.append(max(years))
    if not initiatives:
        st.info("Sem dados de anos disponíveis.")
        return
    fig = go.Figure()
    for i, name in enumerate(initiatives):
        fig.add_trace(go.Bar(
            x=[end_years[i] - start_years[i] + 1],
            y=[name],
            orientation='h',
            base=[start_years[i]],
            marker_color='#3b82f6',
            hovertext=f"{name}: {start_years[i]} - {end_years[i]}"
        ))
    fig.update_layout(
        title="<b>Annual Coverage Timeline</b>",
        xaxis_title="Year",
        yaxis_title="Initiative",
        font=dict(family="Inter", size=12),
        title_font=dict(size=14, family="Inter", color="#1f2937"),
        bargap=0.3,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
