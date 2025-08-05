"""
Detailed Table Component - Comparison Analysis
=============================================

Component to render detailed table tab for comparative analysis.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_detailed_table_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render detailed table tab for comparative analysis.
    
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    st.markdown("#### 📋 Detailed Initiative Table")
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for detailed table.")
        return
    
    st.dataframe(filtered_df, use_container_width=True)
    
