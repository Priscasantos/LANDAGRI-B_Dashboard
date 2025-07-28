import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add scripts to path if necessary
current_dir = Path(__file__).parent.parent  # This should be dashboard-iniciativas/
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


def run():
    """
    Main orchestrator function for the CONAB dashboard.
    
    This function coordinates all components of the CONAB page:
    1. Data loading and validation
    2. UI styling  
    3. CONAB-specific visualizations
    4. Agricultural data analysis
    """
    # Load data from session state
    if "metadata" not in st.session_state or "df_interpreted" not in st.session_state:
        st.error(
            "❌ Interpreted data not found in session state. Ensure app.py loads data correctly."
        )
        return  # Stop if data isn't loaded

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    meta = st.session_state.get("metadata", {})

    # Page header
    st.title("🌾 CONAB Dashboard")
    st.markdown("---")
    
    # Check if we have CONAB data
    if df.empty:
        st.warning("⚠️ No data available for CONAB analysis.")
        return
    
    # Basic information section
    st.subheader("📊 Data Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Initiatives", len(df))
    
    with col2:
        if "Type" in df.columns:
            unique_types = df["Type"].nunique()
            st.metric("Initiative Types", unique_types)
        else:
            st.metric("Initiative Types", "N/A")
    
    with col3:
        if "Start_Year" in df.columns:
            year_range = f"{df['Start_Year'].min():.0f} - {df['Start_Year'].max():.0f}"
            st.metric("Year Range", year_range)
        else:
            st.metric("Year Range", "N/A")
    
    # Display data table
    st.subheader("📋 Data Table")
    
    # Select columns to display
    display_columns = []
    if "Name" in df.columns:
        display_columns.append("Name")
    if "Display_Name" in df.columns:
        display_columns.append("Display_Name")
    if "Type" in df.columns:
        display_columns.append("Type")
    if "Start_Year" in df.columns:
        display_columns.append("Start_Year")
    if "End_Year" in df.columns:
        display_columns.append("End_Year")
    
    if display_columns:
        st.dataframe(df[display_columns], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    
    # CONAB-specific analysis section
    st.subheader("🌾 Agricultural Analysis")
    
    # Check for CONAB-related data
    conab_related = df[df.get('Name', '').str.contains('CONAB|Crop|Agriculture', case=False, na=False)]
    
    if not conab_related.empty:
        st.success(f"Found {len(conab_related)} CONAB/Agriculture-related initiatives")
        
        # Display CONAB-related initiatives
        st.dataframe(conab_related, use_container_width=True)
        
        # Basic visualization if we have the data
        try:
            from scripts.plotting.charts.conab_charts import plot_conab_treemap
            
            # Try to create a simple chart
            if len(conab_related) > 0:
                st.subheader("📊 CONAB Data Visualization")
                st.info("CONAB-specific charts will be implemented here.")
                
        except ImportError:
            st.info("CONAB charts module not available. Basic visualization shown instead.")
            
    else:
        st.info("No CONAB-specific data found in current dataset.")
    
    # Future features placeholder
    st.subheader("🚧 Coming Soon")
    st.info("""
    This CONAB dashboard will include:
    - Agricultural crop calendars
    - Regional crop availability analysis
    - Temporal trends in agricultural data
    - Interactive maps and visualizations
    """)


if __name__ == "__main__":
    run()
