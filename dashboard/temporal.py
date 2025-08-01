import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px



# Add scripts to path - This should be at the very top
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from scripts.plotting.chart_core import (
        prepare_temporal_display_data
    )
    from scripts.plotting.charts.temporal_charts import (
        plot_timeline_chart, 
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
    
    tab1, tab2 = st.tabs([
        "📊 Timeline Comparison", 
        "📈 Availability Evolution"
    ])
    
    with tab1:
        show_timeline_chart(df_for_analysis, meta_geral)

    with tab2:
        show_evolution_analysis(temporal_data)

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
        if not temporal_df.empty and 'Primeiro_Ano' in temporal_df.columns and 'Ultimo_Ano' in temporal_df.columns:
            primeiro_ano_geral = temporal_df['Primeiro_Ano'].min()
            ultimo_ano_geral = temporal_df['Ultimo_Ano'].max()
            total_anos_disponiveis = ultimo_ano_geral - primeiro_ano_geral + 1
            st.metric("Total Years Available", total_anos_disponiveis)
        else:
            st.metric("Total Years Available", "N/A")

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
    
    # First chart: Evolution of Data Availability Over Time
    st.markdown("#### Evolution of Data Availability Over Time")
    fig_evolution = plot_evolution_line_chart(temporal_data_for_evolution)
    if fig_evolution is None:
        # Fallback: create basic evolution chart
        fig_evolution = create_basic_evolution_chart(years_df)
    

    else:
        st.info("Could not generate evolution chart.")
    
    # Second chart: Spatial Resolution Evolution
    st.markdown("#### Evolution of Spatial Resolution in LULC (1985-2024)")
    metadata = st.session_state.get('metadata', {})
    filtered_df = st.session_state.get('df_interpreted', pd.DataFrame())
    
    if metadata and not filtered_df.empty:
        if CHARTS_AVAILABLE and 'plot_evolution_heatmap_chart' in globals():
            fig_evolution_heatmap = plot_evolution_heatmap_chart(metadata, filtered_df)
            if fig_evolution_heatmap:
                st.plotly_chart(fig_evolution_heatmap, use_container_width=True, key="evolution_heatmap_chart")

            else:
                # Show summary statistics instead
                st.markdown("#### Evolution Statistics")
                peak_year = years_df.loc[years_df['Number_Initiatives'].idxmax(), 'Year']
                peak_count = years_df['Number_Initiatives'].max()
                avg_initiatives = years_df['Number_Initiatives'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Peak Year", f"{peak_year}")
                with col2:
                    st.metric("Peak Initiatives", f"{peak_count}")
                with col3:
                    st.metric("Average per Year", f"{avg_initiatives:.1f}")
        else:
            st.info("Spatial resolution evolution chart not available.")
    else:
        # Show summary statistics if no metadata available
        st.markdown("#### Evolution Statistics")
        if not years_df.empty:
            peak_year = years_df.loc[years_df['Number_Initiatives'].idxmax(), 'Year']
            peak_count = years_df['Number_Initiatives'].max()
            avg_initiatives = years_df['Number_Initiatives'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Peak Year", f"{peak_year}")
            with col2:
                st.metric("Peak Initiatives", f"{peak_count}")
            with col3:
                st.metric("Average per Year", f"{avg_initiatives:.1f}")
        else:
            st.info("No data available for statistics.")
    
    # Third chart: LULC Initiative Growth & Resolution Combined
    st.markdown("#### LULC Initiative Growth & Resolution (1985-2024)")
    fig_combined = create_combined_evolution_chart(metadata, filtered_df, years_df)
    if fig_combined:
        st.plotly_chart(fig_combined, use_container_width=True, key="combined_evolution_chart")

    else:
        st.info("Could not generate combined evolution chart.")

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
            height=500,  # Standardized height
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating evolution chart: {e}")
        return None

def create_combined_evolution_chart(metadata, filtered_df, years_df):
    """Create combined evolution chart showing initiatives count, min/avg resolution over time"""
    try:
        import pandas as pd
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if not metadata or filtered_df is None or filtered_df.empty or years_df.empty:
            return None
        
        # Process metadata to extract resolution and years data
        resolution_data = []
        
        for initiative_name, meta_info in metadata.items():
            if not isinstance(meta_info, dict):
                continue
                
            # Get available years
            years_key = 'available_years' if 'available_years' in meta_info else 'anos_disponiveis'
            if years_key not in meta_info or not meta_info[years_key]:
                continue
                
            years = meta_info[years_key]
            if not isinstance(years, list):
                continue
                
            # Get spatial resolution
            spatial_res = meta_info.get('spatial_resolution')
            if spatial_res is None:
                continue
                
            # Parse resolution to get a single representative value
            resolution_value = _parse_resolution_for_combined_chart(spatial_res)
            if resolution_value is None:
                continue
                
            # Add data for each year
            for year in years:
                if isinstance(year, (int, float)) and 1985 <= year <= 2024:
                    resolution_data.append({
                        'initiative': initiative_name,
                        'year': int(year),
                        'resolution_value': resolution_value
                    })
        
        if not resolution_data:
            return None
        
        # Create DataFrame and aggregate
        df_resolution = pd.DataFrame(resolution_data)
        
        # Calculate yearly statistics
        yearly_stats = df_resolution.groupby('year').agg({
            'resolution_value': ['min', 'mean'],
            'initiative': 'count'
        }).reset_index()
        
        # Flatten column names
        yearly_stats.columns = ['year', 'min_res', 'avg_res', 'count']
        
        # Ensure we have all years from 1985 to 2024
        all_years = list(range(1985, 2025))
        full_df = pd.DataFrame({'year': all_years})
        full_df = full_df.merge(yearly_stats, on='year', how='left')
        full_df = full_df.merge(years_df.rename(columns={'Year': 'year', 'Number_Initiatives': 'total_initiatives'}), 
                               on='year', how='left')
        
        # Fill missing values
        full_df['count'] = full_df['count'].fillna(0)
        full_df['total_initiatives'] = full_df['total_initiatives'].fillna(0)
        
        # Create subplots with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add initiatives count (line)
        fig.add_trace(
            go.Scatter(
                x=full_df['year'],
                y=full_df['total_initiatives'],
                mode='lines+markers',
                name='Initiatives',
                line=dict(color='#26828e', width=3),
                marker=dict(size=6, color='#26828e'),
                hovertemplate='<b>Year: %{x}</b><br>Initiatives: %{y}<extra></extra>'
            ),
            secondary_y=False,
        )
        
        # Add min resolution (line)
        fig.add_trace(
            go.Scatter(
                x=full_df['year'],
                y=full_df['min_res'],
                mode='lines',
                name='Min Res (m)',
                line=dict(color='#c62d42', width=2),
                connectgaps=False,
                hovertemplate='<b>Year: %{x}</b><br>Min Resolution: %{y}m<extra></extra>'
            ),
            secondary_y=True,
        )
        
        # Add avg resolution (line with dots)
        fig.add_trace(
            go.Scatter(
                x=full_df['year'],
                y=full_df['avg_res'],
                mode='lines+markers',
                name='Avg Res (m)',
                line=dict(color='#f39800', width=2, dash='dot'),
                marker=dict(size=4, color='#f39800'),
                connectgaps=False,
                hovertemplate='<b>Year: %{x}</b><br>Avg Resolution: %{y:.1f}m<extra></extra>'
            ),
            secondary_y=True,
        )
        
        # Add milestone annotations
        milestones = {
            2000: "Milestone 2000",
            2010: "Milestone 2010", 
            2020: "Milestone 2020"
        }
        
        for year, label in milestones.items():
            fig.add_vline(
                x=year,
                line_dash="dash",
                line_color="rgba(128,128,128,0.4)",
                line_width=1,
                annotation_text=label,
                annotation_position="top",
                annotation_font_size=10,
                annotation_font_color="rgba(139,69,19,0.6)"
            )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Year", range=[1985, 2024])
        
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Initiatives</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Res (m)</b>", secondary_y=True)
        
        # Update layout
        fig.update_layout(
            title="LULC Initiative Growth & Resolution (1985-2024)",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                tickformat='d',
                dtick=5
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating combined evolution chart: {e}")
        return None

def _parse_resolution_for_combined_chart(spatial_res):
    """Parse spatial resolution for the combined chart"""
    if spatial_res is None:
        return None
    
    try:
        if isinstance(spatial_res, (int, float)):
            return float(spatial_res)
        elif isinstance(spatial_res, str):            # Extract numeric value from string
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', spatial_res)
            if numbers:
                return float(numbers[0])
    except (ValueError, TypeError, AttributeError):
        pass
    
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
        
        print(" Generating evolution analysis...")
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
