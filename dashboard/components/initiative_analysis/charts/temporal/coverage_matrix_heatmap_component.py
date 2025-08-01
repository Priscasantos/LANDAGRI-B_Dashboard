"""
Temporal Coverage Heatmap (Initiatives vs Years)
===============================================

Component to visualize temporal coverage of each initiative across years.
Each row represents an initiative, each column a year, and colored cells indicate data presence.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.components.shared.chart_core import get_chart_colors

def render_coverage_matrix_heatmap(temporal_data: pd.DataFrame, metadata: dict) -> None:
    """
    Render a temporal coverage heatmap (initiatives vs years).
    Args:
        temporal_data: DataFrame with processed temporal data
        metadata: Dictionary of initiative metadata
    """
    st.markdown("#### 🗓️ Temporal Coverage Heatmap")
    if temporal_data.empty or not metadata:
        st.info("No temporal data available for heatmap.")
        return

    # Determine available years
    all_years = set()
    for details in metadata.values():
        available_years = details.get("available_years", [])
        if available_years:
            all_years.update([int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()])
        else:
            # Fallback for old structure
            years_data = details.get("years", {})
            if years_data:
                all_years.update([int(y) for y in years_data.keys() if str(y).isdigit()])
    if not all_years:
        st.info("No years available for heatmap.")
        return
    years_sorted = sorted(all_years)

    # Build matrix: rows = initiatives, columns = years
    initiatives = []
    matrix = []
    for name, details in metadata.items():
        available_years = details.get("available_years", [])
        if available_years:
            # Use available_years as list
            years_set = set(int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit())
        else:
            # Fallback for old structure
            years_data = details.get("years", {})
            years_set = set(int(y) for y in years_data.keys() if str(y).isdigit())
        row = []
        for year in years_sorted:
            row.append(1 if year in years_set else 0)
        initiatives.append(name[:40])
        matrix.append(row)

    # Create heatmap with improved styling
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=years_sorted,
        y=initiatives,
        colorscale=[[0, '#f3f4f6'], [1, '#2563eb']],
        showscale=True,
        colorbar=dict(
            title="<b>Data<br>Available</b>",
            titlefont=dict(size=12, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif"),
            tickvals=[0, 1],
            ticktext=["No", "Yes"],
            tickfont=dict(size=10, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif")
        ),
        hovertemplate="<b>Initiative:</b> %{y}<br><b>Year:</b> %{x}<br><b>Available:</b> %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        height=max(450, len(initiatives)*24),
        title=dict(
            text="<b>Temporal Coverage Matrix</b><br><span style='font-size:14px;color:#6b7280'>Data availability across initiatives and years</span>",
            x=0.5,
            font=dict(size=18, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#1f2937")
        ),
        xaxis=dict(
            title="<b>Year</b>",
            titlefont=dict(size=14, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#374151"),
            tickfont=dict(size=11, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#6b7280"),
            showgrid=False
        ),
        yaxis=dict(
            title="<b>Initiative</b>",
            titlefont=dict(size=14, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#374151"),
            tickfont=dict(size=10, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#4b5563"),
            showgrid=False
        ),
        margin=dict(l=200, r=80, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary statistics
    col1, col2, col3 = st.columns(3)
    total_cells = len(initiatives) * len(years_sorted)
    filled_cells = sum(sum(row) for row in matrix)
    coverage_percentage = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    
    with col1:
        st.metric("Total Initiatives", len(initiatives))
    with col2:
        st.metric("Years Covered", len(years_sorted))
    with col3:
        st.metric("Overall Coverage", f"{coverage_percentage:.1f}%")
