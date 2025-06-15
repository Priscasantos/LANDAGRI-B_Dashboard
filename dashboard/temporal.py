import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Local application imports should come after third-party libraries
from scripts.utilities.ui_elements import setup_download_form
from scripts.plotting.chart_core import (
    prepare_temporal_display_data
)
from scripts.plotting.charts.temporal_charts import (
    timeline_with_controls, 
    plot_timeline_chart, 
    plot_coverage_heatmap_chart, 
    plot_gaps_bar_chart, 
    plot_evolution_line_chart, 
    plot_evolution_heatmap_chart
)

# Add scripts to path - This should be at the very top
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

def run(metadata=None, df_original=None):
    """
    Run temporal analysis with optional data parameters.
    If metadata and df_original are provided, use them directly.
    Otherwise, try to get from st.session_state for Streamlit compatibility.
    """
    st.header("⏳ Comprehensive Temporal Analysis of LULC Initiatives")
    
    # Check if we have the new interpreted data structure from app.py's cached load
    if 'df_interpreted' in st.session_state and not st.session_state.df_interpreted.empty:
        df_for_analysis = st.session_state.df_interpreted
        meta_geral = st.session_state.get('metadata', {})
        if not meta_geral: 
            try:
                from scripts.utilities.json_interpreter import _load_jsonc_file
                metadata_file_path = _project_root / "data" / "initiatives_metadata.jsonc" 
                meta_geral = _load_jsonc_file(metadata_file_path)
                st.session_state.metadata = meta_geral 
            except Exception as e:
                st.error(f"❌ Error loading raw metadata in temporal.py: {e}")
                meta_geral = {}
    elif metadata is not None and df_original is not None: 
        df_for_analysis = df_original
        meta_geral = metadata
    else:
        st.error("❌ Data not available for temporal analysis. Ensure data is loaded in app.py or passed directly.")
        return
    
    # Ensure df_for_analysis and meta_geral are defined before this call
    temporal_data = prepare_temporal_data(meta_geral, df_for_analysis) 
    
    if temporal_data.empty:
        st.warning("No temporal data available for analysis. This might be due to missing metadata or issues in data preparation.")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Timeline Comparison", 
        "⚠️ Temporal Gaps", 
        "📈 Availability Evolution",
        "🔥 Coverage Heatmap"
    ])
    
    with tab1:
        # Pass df_for_analysis and meta_geral to show_timeline_chart if they are needed by timeline_with_controls
        show_timeline_chart(df_for_analysis, meta_geral) # Updated to pass necessary data


    with tab2:
        show_gaps_analysis(temporal_data)
        
    with tab3:
        show_evolution_analysis(temporal_data)
        
    with tab4:
        show_coverage_heatmap(temporal_data)

def prepare_temporal_data(meta_geral, df_original=None):
    """Prepare temporal data with standardized display names using chart_core"""
    temporal_df = prepare_temporal_display_data(meta_geral, df_original)
    
    if temporal_df.empty:
        return pd.DataFrame()

    # Ensure 'Tipo' (Type) column exists and fill missing values
    if 'Tipo' not in temporal_df.columns:
        temporal_df['Tipo'] = "Uncategorized"
    else:
        temporal_df['Tipo'] = temporal_df['Tipo'].fillna("Uncategorized")

    temporal_df['Cobertura_Anos'] = temporal_df['Anos_Lista'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    temporal_df['Periodo_Total_Anos'] = temporal_df['Ultimo_Ano'] - temporal_df['Primeiro_Ano'] + 1
    # Ensure Periodo_Total_Anos is not zero to avoid division by zero
    temporal_df['Cobertura_Percentual'] = (
        (temporal_df['Cobertura_Anos'] / temporal_df['Periodo_Total_Anos'].replace(0, 1)) * 100 # Avoid division by zero
    ).round(1)
    
    temporal_df['Anos_Faltando'] = temporal_df['Periodo_Total_Anos'] - temporal_df['Cobertura_Anos']
    temporal_df['Maior_Lacuna'] = temporal_df['Anos_Lista'].apply(calculate_largest_gap)
    
    return temporal_df

def calculate_largest_gap(anos_list):
    """Calculate the largest consecutive gap in a list of years"""
    if not isinstance(anos_list, list) or len(anos_list) < 2:
        return 0
    anos_list = sorted(list(set(anos_list))) 
    max_gap = 0
    for i in range(len(anos_list) - 1):
        gap = anos_list[i+1] - anos_list[i] - 1
        if gap > max_gap:
            max_gap = gap
    return max_gap

def show_timeline_chart(temporal_data, raw_initiatives_metadata):
    """Timeline chart showing discrete years for each initiative with proper gaps."""
    st.subheader("📊 LULC Initiatives Timeline - Discrete Years Availability")
    # fig = plot_timeline_chart(temporal_data, raw_initiatives_metadata)
    # if fig is None:
    #     st.info("No data to display for the timeline chart.")
    #     return
    # st.plotly_chart(fig, use_container_width=True)
    # if fig:
    #     setup_download_form(fig, default_filename="timeline_iniciatives", key_prefix="timeline_tab1")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Initiatives", len(temporal_data))
    with col2:
        if not temporal_data.empty and 'Primeiro_Ano' in temporal_data.columns and 'Ultimo_Ano' in temporal_data.columns:
            periodo_total = f"{temporal_data['Primeiro_Ano'].min()} - {temporal_data['Ultimo_Ano'].max()}"
        else:
            periodo_total = "N/A"
        st.metric("Total Period Covered", periodo_total)
    with col3:
        if not temporal_data.empty and 'Cobertura_Percentual' in temporal_data.columns:
            cobertura_media = temporal_data['Cobertura_Percentual'].mean()
            st.metric("Average Coverage", f"{cobertura_media:.1f}%")
        else:
            st.metric("Average Coverage", "N/A")

    # The timeline_with_controls is called below, which uses plot_timeline_chart internally.
    # The direct call to plot_timeline_chart here would be redundant and cause duplication.
    # fig_direct_timeline = plot_timeline_chart(raw_initiatives_metadata, temporal_data) 
    # if fig_direct_timeline:
    #     st.plotly_chart(fig_direct_timeline, use_container_width=True, key="timeline_direct_tab1_chart") # Added key
    #     setup_download_form(fig_direct_timeline, default_filename="timeline_direct", key_prefix="timeline_direct_tab1")
    # else:
    #     st.info("Could not generate direct timeline chart.")

    # Call timeline_with_controls, using the parameters available in this function's scope.
    # timeline_with_controls handles its own internal plotly_chart calls and keys if necessary.
    timeline_with_controls(raw_initiatives_metadata, temporal_data) 


    # st.subheader("Coverage Heatmap") # This is a duplicate section, the actual heatmap is in tab4
    # temporal_df_for_heatmap = prepare_temporal_display_data(df_for_analysis, meta_geral)
    # fig_heatmap = plot_coverage_heatmap_chart(temporal_df_for_heatmap)
    # if fig_heatmap:
    #     st.plotly_chart(fig_heatmap, use_container_width=True)
    # else:
    #     st.info("Could not generate coverage heatmap.")

    # st.subheader("Temporal Gaps Analysis") # This is a duplicate section, actual gaps analysis is in tab2
    # temporal_df_for_gaps = prepare_temporal_display_data(df_for_analysis, meta_geral)
    # fig_gaps = plot_gaps_bar_chart(temporal_df_for_gaps)
    # if fig_gaps:
    #     st.plotly_chart(fig_gaps, use_container_width=True)
    # else:
    #     st.info("Could not generate gaps analysis chart.")

    # This subheader and chart seem to be a duplicate of what's in show_coverage_heatmap (tab4)
    # If it's intended to be here, it needs a unique key.
    # For now, assuming it's a duplicate and commenting out to avoid conflict with tab4.
    # st.subheader("Coverage Heatmap") 
    # fig_heatmap_tab1 = plot_coverage_heatmap_chart(temporal_data) # Renamed fig variable
    # if fig_heatmap_tab1 is None:
    #     st.info("No data to display for the coverage heatmap.")
    #     # return # This return would exit the function early, affecting subsequent tabs
    # else:
    #     st.plotly_chart(fig_heatmap_tab1, use_container_width=True, key="coverage_heatmap_tab1_chart") # Added key
    #     if fig_heatmap_tab1:
    #         setup_download_form(fig_heatmap_tab1, default_filename="heatmap_type_year_tab1", key_prefix="heatmap_tab1_dl")


def show_coverage_heatmap(temporal_data):
    """Heatmap of initiative availability by type and year using display names"""
    st.subheader("🔥 Initiative Availability Heatmap (by Type and Year)")
    fig_heatmap = plot_coverage_heatmap_chart(temporal_data)
    if fig_heatmap is None:
        st.info("No data to display for the coverage heatmap.")
        return
    st.plotly_chart(fig_heatmap, use_container_width=True, key="coverage_heatmap_tab4_chart") # Added key
    if fig_heatmap:
        setup_download_form(fig_heatmap, default_filename="heatmap_type_year", key_prefix="heatmap_tab4")


def show_gaps_analysis(temporal_data):
    """Temporal gaps analysis using display names"""
    st.subheader("⚠️ Temporal Gaps Analysis")
    if temporal_data.empty or 'Anos_Faltando' not in temporal_data.columns:
        st.info("No data to display for gaps analysis.")
        return
    gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
    if 'Tipo' not in gaps_data.columns:
        gaps_data['Tipo'] = "Uncategorized"
    else:
        gaps_data['Tipo'] = gaps_data['Tipo'].fillna("Uncategorized")
    if gaps_data.empty:
        st.success("🎉 Excellent! No initiatives have significant temporal gaps.")
        return
    st.markdown("This section highlights initiatives with missing years in their time series.")
    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("#### 📊 Missing Years by Initiative")
        fig_gaps = plot_gaps_bar_chart(gaps_data)
        if fig_gaps is None:
            st.info("No data to display for gaps bar chart.")
        else:
            st.plotly_chart(fig_gaps, use_container_width=True, key="gaps_bar_chart_tab2_chart") # Added key
            setup_download_form(fig_gaps, default_filename="temporal_gaps", key_prefix="gaps_tab2")
    with col2:
        st.markdown("#### Summary of Gaps by Type")
        if not gaps_data.empty:
            gaps_by_type = gaps_data.groupby('Tipo').agg(
                Avg_Missing_Years=('Anos_Faltando', 'mean'),
                Avg_Largest_Gap=('Maior_Lacuna', 'mean'),
                Qty_Initiatives_With_Gaps=('Display_Name', 'count')
            ).round(1)
            st.dataframe(gaps_by_type, use_container_width=True)
        else:
            st.info("No gap data to summarize by type.")
        st.markdown("#### Top 5 Initiatives with Largest Gaps")
        if not gaps_data.empty and 'Maior_Lacuna' in gaps_data.columns:
            top_gaps = gaps_data.nlargest(5, 'Maior_Lacuna')[['Display_Name', 'Maior_Lacuna', 'Anos_Faltando']]
            st.dataframe(top_gaps, use_container_width=True, hide_index=True)
        else:
            st.info("No gap data to show top initiatives.")

def show_evolution_analysis(temporal_data):
    """Analysis of data availability evolution over time"""
    st.subheader("📈 Data Availability Evolution")
    if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns:
        st.info("No data to display for evolution analysis.")
        return
    temporal_data_for_evolution = temporal_data.copy()
    if 'Tipo' not in temporal_data_for_evolution.columns:
        temporal_data_for_evolution['Tipo'] = "Uncategorized"
    else:
        temporal_data_for_evolution['Tipo'] = temporal_data_for_evolution['Tipo'].fillna("Uncategorized")
    all_years = []
    for _, row in temporal_data_for_evolution.iterrows():
        if isinstance(row['Anos_Lista'], list):
            all_years.extend(row['Anos_Lista'])
    if not all_years:
        st.warning("Insufficient data for evolution analysis after processing year lists.")
        return
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Year': year_counts.index,
        'Number_Initiatives': year_counts.values
    })
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Number of Initiatives Over Time")
        fig_evolution = plot_evolution_line_chart(years_df)
        if fig_evolution is None:
            st.info("No data to display for evolution line chart.")
        else:
            st.plotly_chart(fig_evolution, use_container_width=True, key="evolution_line_chart_tab3_chart") # Added key
            setup_download_form(fig_evolution, default_filename="availability_evolution", key_prefix="evolution_tab3_line")
    with col2:
        st.markdown("#### Availability by Type and Year (Heatmap)")
        fig_heatmap_evolution = plot_evolution_heatmap_chart(temporal_data_for_evolution)
        if fig_heatmap_evolution is None:
            st.info("Pivot table for evolution heatmap is empty.")
        else:
            st.plotly_chart(fig_heatmap_evolution, use_container_width=True, key="evolution_heatmap_tab3_chart") # Added key
            setup_download_form(fig_heatmap_evolution, default_filename="heatmap_type_year_evolution", key_prefix="evolution_tab3_heatmap")
