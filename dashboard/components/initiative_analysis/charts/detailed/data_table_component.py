"""
Data Table Component - Detailed Analysis
=======================================

Component for rendering detailed data table in detailed analysis.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

from dashboard.components.shared.nomenclature import clean_column_names


def render_data_table_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render detailed data table tab.
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    if filtered_df.empty:
        st.warning("⚠️ No data available for detailed table.")
        return
    
    # Apply friendly column names
    df_display = clean_column_names(filtered_df, use_friendly_names=True)
    
    st.dataframe(df_display, use_container_width=True)
