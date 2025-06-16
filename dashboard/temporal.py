import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Local application imports should come after third-party libraries
from scripts.utilities.ui_elements import setup_download_form

# Add scripts to path - This should be at the very top
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
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
    CHARTS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Some chart functions not available: {e}")
    CHARTS_AVAILABLE = False

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
        show_timeline_chart(df_for_analysis, meta_geral)

    with tab2:
        show_gaps_analysis(temporal_data)
        
    with tab3:
        show_evolution_analysis(temporal_data)
        
    with tab4:
        show_coverage_heatmap(temporal_data)

def prepare_temporal_data(meta_geral, df_original=None):
    """Prepare temporal data with standardized display names using chart_core"""
    try:
        if CHARTS_AVAILABLE and 'prepare_temporal_display_data' in globals():
            temporal_df = prepare_temporal_display_data(meta_geral, df_original)
        else:
            temporal_df = create_temporal_data_fallback(meta_geral, df_original)
    except Exception as e:
        st.warning(f"Error preparing temporal display data: {e}")
        # Fallback: create temporal data manually
        temporal_df = create_temporal_data_fallback(meta_geral, df_original)
    
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

def create_temporal_data_fallback(meta_geral, df_original=None):
    """Fallback function to create temporal data if prepare_temporal_display_data fails"""
    temporal_data = []
    
    # Create name to acronym mapping
    nome_to_sigla = {}
    if df_original is not None and 'Acronym' in df_original.columns and 'Name' in df_original.columns:
        for _, row in df_original.iterrows():
            if pd.notna(row['Name']) and pd.notna(row['Acronym']):
                nome_to_sigla[row['Name']] = row['Acronym']
    
    for nome, details in meta_geral.items():
        if isinstance(details, dict) and 'available_years' in details:
            anos_lista = details['available_years'] if isinstance(details['available_years'], list) else []
            if anos_lista:
                display_name = nome_to_sigla.get(nome, nome[:15])
                
                # Get type from df_original if available
                tipo = "Uncategorized"
                if df_original is not None and 'Type' in df_original.columns:
                    type_row = df_original[df_original['Name'] == nome]
                    if not type_row.empty:
                        tipo = type_row['Type'].iloc[0] if pd.notna(type_row['Type'].iloc[0]) else "Uncategorized"
                
                temporal_data.append({
                    'Nome': nome,
                    'Display_Name': display_name,
                    'Tipo': tipo,
                    'Anos_Lista': anos_lista,
                    'Primeiro_Ano': min(anos_lista),
                    'Ultimo_Ano': max(anos_lista)
                })
    
    return pd.DataFrame(temporal_data)

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

def show_timeline_chart(df_for_analysis, raw_initiatives_metadata):
    """Timeline chart showing discrete years for each initiative with proper gaps."""
    st.subheader("📊 LULC Initiatives Timeline - Discrete Years Availability")
    
    # Generate and display the main timeline chart
    fig_timeline = None
    if CHARTS_AVAILABLE and 'plot_timeline_chart' in globals():
        fig_timeline = plot_timeline_chart(raw_initiatives_metadata, df_for_analysis)
    
    if fig_timeline is None:
        # Fallback: create basic timeline chart
        fig_timeline = create_basic_timeline_chart(raw_initiatives_metadata, df_for_analysis)
    
    if fig_timeline is None:
        st.info("No data to display for the timeline chart.")
        return
        
    st.plotly_chart(fig_timeline, use_container_width=True, key="main_timeline_chart")
    if fig_timeline:
        setup_download_form(fig_timeline, default_filename="timeline_iniciatives", key_prefix="timeline_tab1")
    
    # Create name to acronym mapping
    nome_to_sigla = {}
    if df_for_analysis is not None and 'Acronym' in df_for_analysis.columns and 'Name' in df_for_analysis.columns:
        for _, row in df_for_analysis.iterrows():
            if pd.notna(row['Name']) and pd.notna(row['Acronym']):
                nome_to_sigla[row['Name']] = row['Acronym']
    
    # Prepare temporal data for metrics
    temporal_data = []
    for nome, details in raw_initiatives_metadata.items():
        if isinstance(details, dict) and 'available_years' in details:
            anos_lista = details['available_years'] if isinstance(details['available_years'], list) else []
            if anos_lista:
                temporal_data.append({
                    'Nome': nome,
                    'Display_Name': nome_to_sigla.get(nome, nome[:15]),
                    'Anos_Lista': anos_lista,
                    'Primeiro_Ano': min(anos_lista),
                    'Ultimo_Ano': max(anos_lista)
                })
    
    temporal_df = pd.DataFrame(temporal_data)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Initiatives", len(temporal_df))
    with col2:
        if not temporal_df.empty and 'Primeiro_Ano' in temporal_df.columns and 'Ultimo_Ano' in temporal_df.columns:
            primeiro_ano_geral = temporal_df['Primeiro_Ano'].min()
            ultimo_ano_geral = temporal_df['Ultimo_Ano'].max()
            periodo_total = f"{primeiro_ano_geral}-{ultimo_ano_geral}"
        else:
            periodo_total = "N/A"
        st.metric("Total Period Covered", periodo_total)
    with col3:
        if not temporal_df.empty:
            total_anos_disponiveis = sum(len(anos) for anos in temporal_df['Anos_Lista'])
            st.metric("Total Years Available", total_anos_disponiveis)
        else:
            st.metric("Total Years Available", "N/A")
    
    st.markdown("---")
    st.markdown("#### Interactive Timeline Controls")
    try:
        timeline_with_controls(raw_initiatives_metadata, temporal_df)
    except Exception as e:
        st.warning(f"Interactive controls not available: {e}")

def create_basic_timeline_chart(metadata, df_for_analysis):
    """Create a basic timeline chart as fallback"""
    try:
        # Create name to acronym mapping
        nome_to_sigla = {}
        if df_for_analysis is not None and 'Acronym' in df_for_analysis.columns and 'Name' in df_for_analysis.columns:
            for _, row in df_for_analysis.iterrows():
                if pd.notna(row['Name']) and pd.notna(row['Acronym']):
                    nome_to_sigla[row['Name']] = row['Acronym']
        
        fig = go.Figure()
        y_pos = 0
        colors = px.colors.qualitative.Plotly
        
        for i, (nome, details) in enumerate(metadata.items()):
            if isinstance(details, dict) and 'available_years' in details:
                years = details['available_years'] if isinstance(details['available_years'], list) else []
                if years:
                    display_name = nome_to_sigla.get(nome, nome[:15])
                    
                    # Add scatter plot for each year
                    fig.add_trace(go.Scatter(
                        x=years,
                        y=[y_pos] * len(years),
                        mode='markers',
                        name=display_name,
                        marker=dict(
                            size=10,
                            color=colors[i % len(colors)],
                            symbol='square'
                        ),
                        hovertemplate=f'<b>{display_name}</b><br>Year: %{{x}}<extra></extra>'
                    ))
                    y_pos += 1
        
        fig.update_layout(
            title='LULC Initiatives Timeline',
            xaxis_title='Year',
            yaxis_title='Initiative',
            height=max(400, y_pos * 40 + 100),
            showlegend=True
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating basic timeline chart: {e}")
        return None

def show_coverage_heatmap(temporal_data):
    """Heatmap of initiative availability by type and year using display names"""
    st.subheader("🔥 Initiative Availability Heatmap (by Type and Year)")
    
    fig_heatmap = plot_coverage_heatmap_chart(temporal_data)
    if fig_heatmap is None:
        # Fallback: create basic heatmap
        fig_heatmap = create_basic_coverage_heatmap(temporal_data)
    
    if fig_heatmap is None:
        st.info("No data to display for the coverage heatmap.")
        return
        
    st.plotly_chart(fig_heatmap, use_container_width=True, key="coverage_heatmap_tab4_chart")
    if fig_heatmap:
        setup_download_form(fig_heatmap, default_filename="heatmap_type_year", key_prefix="heatmap_tab4")

def create_basic_coverage_heatmap(temporal_data):
    """Create basic coverage heatmap as fallback"""
    try:
        if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns or 'Tipo' not in temporal_data.columns:
            return None
        
        # Create heatmap data
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            if isinstance(row['Anos_Lista'], list):
                for year in row['Anos_Lista']:
                    heatmap_data.append({
                        'Year': year,
                        'Type': row['Tipo'],
                        'Available': 1
                    })
        
        if not heatmap_data:
            return None
        
        heatmap_df = pd.DataFrame(heatmap_data)
        pivot_df = heatmap_df.pivot_table(
            values='Available',
            index='Type',
            columns='Year',
            aggfunc='sum',
            fill_value=0
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='<b>Type: %{y}</b><br>Year: %{x}<br>Active Initiatives: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Initiative Availability by Type and Year',
            xaxis_title='Year',
            yaxis_title='Initiative Type',
            height=400
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating coverage heatmap: {e}")
        return None

def show_gaps_analysis(temporal_data):
    """Temporal gaps analysis using display names"""
    st.subheader("⚠️ Temporal Gaps Analysis")
    
    if temporal_data.empty or 'Anos_Faltando' not in temporal_data.columns:
        st.warning("No temporal data available for gaps analysis.")
        return
    
    gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
    if 'Tipo' not in gaps_data.columns:
        gaps_data['Tipo'] = "Uncategorized"
    else:
        gaps_data['Tipo'] = gaps_data['Tipo'].fillna("Uncategorized")
    
    if gaps_data.empty:
        st.success("✅ No temporal gaps found in the initiatives!")
        return
    
    st.markdown("This section highlights initiatives with missing years in their time series.")
    
    col1, col2 = st.columns([3,2])
    with col1:
        fig_gaps = plot_gaps_bar_chart(temporal_data)
        if fig_gaps is None:
            # Fallback: create basic gaps chart
            fig_gaps = create_basic_gaps_chart(gaps_data)
        
        if fig_gaps:
            st.plotly_chart(fig_gaps, use_container_width=True, key="gaps_chart")
            setup_download_form(fig_gaps, default_filename="temporal_gaps", key_prefix="gaps_tab2")
        else:
            st.info("Could not generate gaps analysis chart.")
    
    with col2:
        st.markdown("#### Gap Statistics")
        avg_gap = gaps_data['Anos_Faltando'].mean()
        max_gap = gaps_data['Anos_Faltando'].max()
        initiatives_with_gaps = len(gaps_data)
        
        st.metric("Initiatives with Gaps", initiatives_with_gaps)
        st.metric("Average Missing Years", f"{avg_gap:.1f}")
        st.metric("Maximum Missing Years", f"{max_gap}")

def create_basic_gaps_chart(gaps_data):
    """Create basic gaps chart as fallback"""
    try:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=gaps_data['Display_Name'],
            y=gaps_data['Anos_Faltando'],
            name='Missing Years',
            marker_color='rgba(255, 99, 71, 0.8)',
            hovertemplate='<b>%{x}</b><br>Missing Years: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Missing Years in Time Series by Initiative',
            xaxis_title='Initiative',
            yaxis_title='Number of Missing Years',
            height=400,
            showlegend=False
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating gaps chart: {e}")
        return None

def show_evolution_analysis(temporal_data):
    """Analysis of data availability evolution over time"""
    st.subheader("📈 Data Availability Evolution")
    
    if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns:
        st.warning("No temporal data available for evolution analysis.")
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
        st.warning("No year data available for evolution analysis.")
        return
    
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Year': year_counts.index,
        'Number_Initiatives': year_counts.values
    })
    
    col1, col2 = st.columns(2)
    with col1:
        fig_evolution = plot_evolution_line_chart(temporal_data_for_evolution)
        if fig_evolution is None:
            # Fallback: create basic evolution chart
            fig_evolution = create_basic_evolution_chart(years_df)
        
        if fig_evolution:
            st.plotly_chart(fig_evolution, use_container_width=True, key="evolution_chart")
            setup_download_form(fig_evolution, default_filename="availability_evolution", key_prefix="evolution_tab3")
        else:
            st.info("Could not generate evolution chart.")
    
    with col2:
        fig_evolution_heatmap = plot_evolution_heatmap_chart(temporal_data_for_evolution)
        if fig_evolution_heatmap is None:
            # Show summary statistics instead
            st.markdown("#### Evolution Statistics")
            peak_year = years_df.loc[years_df['Number_Initiatives'].idxmax(), 'Year']
            peak_count = years_df['Number_Initiatives'].max()
            avg_initiatives = years_df['Number_Initiatives'].mean()
            
            st.metric("Peak Year", f"{peak_year}")
            st.metric("Peak Initiatives", f"{peak_count}")
            st.metric("Average per Year", f"{avg_initiatives:.1f}")
        else:
            st.plotly_chart(fig_evolution_heatmap, use_container_width=True, key="evolution_heatmap_chart")
            setup_download_form(fig_evolution_heatmap, default_filename="evolution_heatmap", key_prefix="evolution_heatmap_tab3")

def create_basic_evolution_chart(years_df):
    """Create basic evolution chart as fallback"""
    try:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years_df['Year'],
            y=years_df['Number_Initiatives'],
            mode='lines+markers',
            name='Active Initiatives',
            line=dict(color='rgba(0, 150, 136, 1)', width=3),
            marker=dict(size=8, color='rgba(0, 150, 136, 0.8)'),
            fill='tonexty',
            fillcolor='rgba(0, 150, 136, 0.2)',
            hovertemplate='<b>Year: %{x}</b><br>Active Initiatives: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Evolution of Data Availability Over Time',
            xaxis_title='Year',
            yaxis_title='Number of Active Initiatives',
            height=450,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating evolution chart: {e}")
        return None

# Non-streamlit version for script execution
def run_non_streamlit(metadata, df_data, output_dir="graphics/temporal"):
    """Run temporal analysis without Streamlit UI and save graphics to files."""
    from pathlib import Path
    
    try:
        from scripts.utilities.chart_saver import save_chart_robust
    except ImportError:
        print("❌ Chart saver not available for non-Streamlit execution.")
        return False
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("🔄 Generating temporal analyses...")
    
    if not metadata:
        print("❌ No metadata available for temporal analysis.")
        return False
    
    try:
        temporal_data = prepare_temporal_data(metadata, df_data)
        if temporal_data.empty:
            print("❌ No temporal data could be prepared.")
            return False
        
        print("📊 Generating timeline chart...")
        fig_timeline = plot_timeline_chart(metadata, df_data)
        if fig_timeline:
            success, saved_path, format_used = save_chart_robust(
                fig_timeline, output_dir, "timeline_initiatives",
                width=1200, height=800, scale=2
            )
            if success:
                print(f"✅ Timeline chart saved as {format_used} in: {saved_path}")
        
        print("🔥 Generating coverage heatmap...")
        fig_heatmap = plot_coverage_heatmap_chart(temporal_data)
        if fig_heatmap:
            success, saved_path, format_used = save_chart_robust(
                fig_heatmap, output_dir, "coverage_heatmap",
                width=1000, height=600, scale=2
            )
            if success:
                print(f"✅ Coverage heatmap saved as {format_used} in: {saved_path}")
        
        print("⚠️ Generating gaps analysis...")
        fig_gaps = plot_gaps_bar_chart(temporal_data)
        if fig_gaps:
            success, saved_path, format_used = save_chart_robust(
                fig_gaps, output_dir, "temporal_gaps",
                width=1000, height=600, scale=2
            )
            if success:
                print(f"✅ Gaps analysis saved as {format_used} in: {saved_path}")
        
        print("📈 Generating evolution analysis...")
        fig_evolution = plot_evolution_line_chart(temporal_data)
        if fig_evolution:
            success, saved_path, format_used = save_chart_robust(
                fig_evolution, output_dir, "availability_evolution",
                width=1000, height=600, scale=2
            )
            if success:
                print(f"✅ Evolution analysis saved as {format_used} in: {saved_path}")
        
        print("✅ Temporal analyses completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating temporal analyses: {e}")
        return False
