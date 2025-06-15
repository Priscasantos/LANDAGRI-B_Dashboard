import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Local application imports should come after third-party libraries
from scripts.utilities.config import get_initiative_color_map
from scripts.utilities.ui_elements import setup_download_form
from scripts.plotting.chart_core import (
    apply_standard_layout,
    prepare_temporal_display_data
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
    
    # Check if we have the new interpreted data structure
    if 'df_interpreted' in st.session_state:
        df_for_analysis = st.session_state.df_interpreted
        # For temporal analysis, we still need the raw metadata structure
        # Try to get it from session state, otherwise skip temporal analysis
        if 'metadata' in st.session_state:
            meta_geral = st.session_state.metadata
        else:
            st.warning("⚠️ Raw metadata not available. Temporal analysis requires the original metadata structure.")
            st.info("💡 Please ensure the main app loads the raw metadata alongside the interpreted data.")
            return
    elif metadata is not None and df_original is not None:
        meta_geral = metadata
        df_for_analysis = df_original
    elif 'metadata' in st.session_state and 'df_original' in st.session_state:
        meta_geral = st.session_state.metadata
        df_for_analysis = st.session_state.df_original
    else:
        st.warning("⚠️ Metadata or DataFrame not found. Please run the main application page (app.py) first or ensure data is loaded correctly.")
        st.info("💡 The temporal analysis module requires raw metadata to analyze temporal coverage patterns.")
        return
    
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
        show_timeline_chart(temporal_data)
    
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

def show_timeline_chart(temporal_data):
    """Timeline chart showing discrete years for each initiative with proper gaps"""
    st.subheader("📊 LULC Initiatives Timeline - Discrete Years Availability")
    fig = None # Initialize fig
    
    if temporal_data.empty:
        st.info("No data to display for the timeline chart.")
        return

    # Ensure 'Nome' column exists for color mapping, fallback to Display_Name if not
    name_column_for_color = 'Nome' if 'Nome' in temporal_data.columns else 'Display_Name'
    color_map = get_initiative_color_map(temporal_data[name_column_for_color].tolist())
    
    fig = go.Figure()
    
    # Sort initiatives by first year for better visualization
    temporal_data_sorted = temporal_data.sort_values('Primeiro_Ano')
    
    for idx, row in temporal_data_sorted.iterrows():
        if 'Anos_Lista' in row and isinstance(row['Anos_Lista'], list):
            years_list = row['Anos_Lista']
            initiative_name = row['Display_Name']
            color = color_map.get(row[name_column_for_color], '#3B82F6')
            
            # Create a separate trace for each year to show discrete points
            fig.add_trace(go.Scatter(
                x=years_list,
                y=[initiative_name] * len(years_list),
                mode='markers',
                marker=dict(
                    color=color,
                    size=12,
                    symbol='square',
                    line=dict(width=1, color='white')
                ),
                name=initiative_name,
                hovertemplate=f"<b>{initiative_name}</b><br>" +
                             "Year: %{x}<br>" +
                             f"Type: {row.get('Tipo', 'N/A')}<extra></extra>",
                showlegend=False
            ))
    
    apply_standard_layout(fig, "LULC Initiatives Timeline - Discrete Years", "Year", "Initiatives", "timeline")
    
    fig.update_layout(
        height=max(600, len(temporal_data) * 35),
        xaxis=dict(
            tickmode='linear', 
            dtick=2,
            range=[temporal_data['Primeiro_Ano'].min() - 1, temporal_data['Ultimo_Ano'].max() + 1]
        ),  
        yaxis=dict(
            categoryorder='array',
            categoryarray=temporal_data_sorted['Display_Name'].tolist()
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    # Use the new download form setup
    if fig:
        setup_download_form(fig, default_filename="timeline_iniciatives", key_prefix="timeline_tab1")
    
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

def show_coverage_heatmap(temporal_data):
    """Heatmap of initiative availability by type and year using display names"""
    st.subheader("🔥 Initiative Availability Heatmap (by Type and Year)")
    fig_heatmap = None # Initialize fig_heatmap
    
    if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns:
        st.info("No data to display for the coverage heatmap.")
        return

    heatmap_data = []
    for _, row in temporal_data.iterrows():
        if isinstance(row['Anos_Lista'], list):
            for ano in row['Anos_Lista']:
                heatmap_data.append({
                    'Year': ano,
                    'Type': row['Tipo'],
                    'Initiative': row['Display_Name'] 
                })
    
    if not heatmap_data:
        st.warning("No data available for heatmap generation after processing.")
        return

    heatmap_df = pd.DataFrame(heatmap_data)
    pivot_df = heatmap_df.groupby(['Type', 'Year']).size().reset_index(name='Count')
    pivot_table = pivot_df.pivot(index='Type', columns='Year', values='Count').fillna(0)
    
    if pivot_table.empty:
        st.info("Pivot table for heatmap is empty.")
        return

    fig_heatmap = px.imshow(
        pivot_table,
        labels=dict(x="Year", y="Initiative Type", color="Number of Initiatives"),
        color_continuous_scale="Viridis"
    )
    apply_standard_layout(fig_heatmap, "Heatmap of Initiative Availability by Type & Year", "Year", "Initiative Type")
    fig_heatmap.update_layout(height=max(400, len(pivot_table.index) * 50)) 
    st.plotly_chart(fig_heatmap, use_container_width=True)
    # Use the new download form setup
    if fig_heatmap:
        setup_download_form(fig_heatmap, default_filename="heatmap_type_year", key_prefix="heatmap_tab4")


def show_gaps_analysis(temporal_data):
    """Temporal gaps analysis using display names"""
    st.subheader("⚠️ Temporal Gaps Analysis")
    fig_gaps = None # Initialize fig_gaps
    
    if temporal_data.empty or 'Anos_Faltando' not in temporal_data.columns:
        st.info("No data to display for gaps analysis.")
        return

    # Ensure 'Tipo' column is handled if it was potentially created/filled in prepare_temporal_data
    gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
    if 'Tipo' not in gaps_data.columns:
        gaps_data['Tipo'] = "Uncategorized" # Should not happen if prepare_temporal_data is called first
    else:
        gaps_data['Tipo'] = gaps_data['Tipo'].fillna("Uncategorized")
    
    if gaps_data.empty:
        st.success("🎉 Excellent! No initiatives have significant temporal gaps.")
        return
    
    st.markdown("This section highlights initiatives with missing years in their time series.")
    
    col1, col2 = st.columns([3,2]) 
    
    with col1:
        st.markdown("#### 📊 Missing Years by Initiative")
        fig_gaps = px.bar(
            gaps_data.sort_values('Anos_Faltando', ascending=True),
            x='Anos_Faltando',
            y='Display_Name',  
            color='Maior_Lacuna',
            labels={'Anos_Faltando': 'Missing Years', 'Display_Name': 'Initiative', 'Maior_Lacuna': 'Largest Gap (Years)'},
            color_continuous_scale='Reds',
            orientation='h' 
        )
        apply_standard_layout(fig_gaps, "Missing Years by Initiative", "Missing Years", "Initiative")
        fig_gaps.update_layout(yaxis={'categoryorder': 'total ascending'}, height=max(400, len(gaps_data) * 25))
        st.plotly_chart(fig_gaps, use_container_width=True)
        # Use the new download form setup
        if fig_gaps:
            setup_download_form(fig_gaps, default_filename="temporal_gaps", key_prefix="gaps_tab2")
    
    with col2:
        st.markdown("#### Summary of Gaps by Type")
        if not gaps_data.empty: # 'Tipo' is now guaranteed to exist
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
    fig_evolution = None # Initialize fig_evolution
    fig_heatmap_evolution = None # Initialize fig_heatmap_evolution
    
    if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns:
        st.info("No data to display for evolution analysis.")
        return

    # Ensure 'Tipo' column is handled
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
        fig_evolution = px.line(
            years_df,
            x='Year',
            y='Number_Initiatives',
            markers=True,
            labels={'Number_Initiatives': 'Number of Active Initiatives'}
        )
        fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
        apply_standard_layout(fig_evolution, "Number of Initiatives with Data by Year", "Year", "Number of Initiatives")
        st.plotly_chart(fig_evolution, use_container_width=True)
        # Use the new download form setup
        if fig_evolution:
            setup_download_form(fig_evolution, default_filename="availability_evolution", key_prefix="evolution_tab3_line")
    
    with col2:
        st.markdown("#### Availability by Type and Year (Heatmap)")
        heatmap_data_evolution = []
        for _, row in temporal_data_for_evolution.iterrows(): # Use the copied and potentially modified dataframe
            if isinstance(row['Anos_Lista'], list):
                for ano in row['Anos_Lista']:
                    heatmap_data_evolution.append({
                        'Year': ano,
                        'Type': row['Tipo'], # This will now use 'Uncategorized' if original was NaN
                        'Initiative': row['Display_Name'] 
                    })
        
        if heatmap_data_evolution:
            heatmap_df_evolution = pd.DataFrame(heatmap_data_evolution)
            pivot_df_evolution = heatmap_df_evolution.groupby(['Type', 'Year']).size().reset_index(name='Count')
            pivot_table_evolution = pivot_df_evolution.pivot(index='Type', columns='Year', values='Count').fillna(0)
            
            if not pivot_table_evolution.empty:
                fig_heatmap_evolution = px.imshow(
                    pivot_table_evolution,
                    labels=dict(x="Year", y="Initiative Type", color="Number of Initiatives"),
                    color_continuous_scale="Greens"
                )
                apply_standard_layout(fig_heatmap_evolution, "Heatmap of Initiative Availability by Type & Year", "Year", "Initiative Type")
                fig_heatmap_evolution.update_layout(height=max(400, len(pivot_table_evolution.index) * 40))
                st.plotly_chart(fig_heatmap_evolution, use_container_width=True)
                # Use the new download form setup
                if fig_heatmap_evolution:
                    setup_download_form(fig_heatmap_evolution, default_filename="heatmap_type_year_evolution", key_prefix="evolution_tab3_heatmap")
            else:
                st.info("Pivot table for evolution heatmap is empty.")
