"""
Boxplot Component - Detailed Analysis
====================================

Component for rendering boxplot tab in detailed analysis.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout

def render_boxplot_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render boxplot tab for detailed analysis.
    Args:
        filtered_df: Filtered DataFrame with initiatives data
    """
    st.markdown("#### 📦 Detailed Initiative Boxplot")
    if filtered_df.empty:
        st.warning("⚠️ No data available for boxplot.")
        return
    fig = create_boxplot_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="detailed_boxplot_chart")
    else:
        st.error("❌ Error generating boxplot.")

@smart_cache_data(ttl=300)
def create_boxplot_chart(filtered_df: pd.DataFrame) -> px.box:
    """
    Create detailed boxplot for multiple initiatives.
    Args:
        filtered_df: Filtered DataFrame
    Returns:
        Plotly Express figure with boxplot
    """
    if filtered_df.empty or "Display_Name" not in filtered_df.columns:
        return px.box()
    # Example: accuracy boxplot by initiative
    if "Accuracy (%)" in filtered_df.columns:
        fig = px.box(
            filtered_df,
            x="Display_Name",
            y="Accuracy (%)",
            color="Display_Name",
        )
        apply_standard_layout(fig, xaxis_title="Initiative", yaxis_title="Accuracy (%)")
        return fig
    return px.box()
