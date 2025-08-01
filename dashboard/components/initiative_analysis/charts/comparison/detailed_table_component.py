"""
Detailed Table Component - Comparison Analysis
=============================================

Component to render detailed table tab for comparative analysis.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import hashlib
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
    
    # Generate unique key for download button
    key_content = f"detailed_table_{filtered_df.shape[0]}_{filtered_df.columns.tolist()}"
    key_hash = hashlib.md5(key_content.encode()).hexdigest()[:8]
    
    st.download_button(
        label="📥 Download Detailed Table",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="detailed_initiative_table.csv",
        mime="text/csv",
        key=f"download_detailed_table_{key_hash}"
    )
