"""
Annual Coverage Component - Detailed Analysis
============================================

Component for rendering annual coverage of initiatives in detailed analysis.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

from turtle import title
import pandas as pd
import streamlit as st

def render_annual_coverage_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render annual coverage tab for initiatives.
    Args:
        filtered_df: Filtered DataFrame with initiatives data
    """
    if filtered_df.empty or "available_years" not in filtered_df.columns:
        st.warning("⚠️ No annual coverage data available.")
        return
    # Prepare data for timeline chart
    import plotly.graph_objects as go
    initiatives = []
    start_years = []
    end_years = []
    for idx, row in filtered_df.iterrows():
        display_name = row.get('Display_Name', row.get('Name', 'Initiative'))
        years = row.get("available_years", [])
        if isinstance(years, list) and years:
            initiatives.append(display_name)
            start_years.append(min(years))
            end_years.append(max(years))
    if not initiatives:
        st.info("No available years data.")
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
        title="Annual Coverage of Initiatives",
        xaxis_title="Year",
        yaxis_title="Initiative",
        font=dict(family="Inter", size=12),
        bargap=0.3,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, key="annual_coverage_chart")
