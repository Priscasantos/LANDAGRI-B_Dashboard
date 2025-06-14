import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Adicionar scripts ao path
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir / "scripts"))

from scripts.utilities.utils import safe_download_image
from scripts.utilities.config import get_initiative_color_map
from scripts.utilities.chart_saver import save_chart_robust
from scripts.plotting.chart_core import (
    get_display_name, 
    create_display_name_mapping, 
    add_display_names_to_df,
    apply_standard_layout,
    prepare_temporal_display_data
)

def run(metadata=None, df_original=None):
    """
    Run temporal analysis with optional data parameters.
    If metadata and df_original are provided, use them directly.
    Otherwise, try to get from st.session_state for Streamlit compatibility.
    """
    st.header("⏳ Comprehensive Temporal Analysis of LULC Initiatives")
    
    # Try to get data from parameters first, then from session state
    if metadata is not None and df_original is not None:
        meta_geral = metadata
        df_for_analysis = df_original
    elif 'metadata' in st.session_state:
        meta_geral = st.session_state.metadata
        df_for_analysis = st.session_state.get('df_original', pd.DataFrame())
    else:
        st.warning("⚠️ Metadata not found. Run the main page (app.py) first or provide data parameters.")
        st.stop()
    
    # Prepare temporal data with sigla mapping
    temporal_data = prepare_temporal_data(meta_geral, df_for_analysis)
    
    if temporal_data.empty:
        st.warning("No temporal data available for analysis.")
        st.stop()
    
    # Tabs for different analyses (translated to English)
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Timeline", 
        "🔍 Temporal Coverage", 
        "⚠️ Temporal Gaps",
        "📈 Availability Evolution"
    ])
    
    with tab1:
        show_timeline_chart(temporal_data)
    
    with tab2:
        show_coverage_analysis(temporal_data)
    
    with tab3:
        show_gaps_analysis(temporal_data)
    
    with tab4:
        show_evolution_analysis(temporal_data)

def prepare_temporal_data(meta_geral, df_original=None):
    """Prepare temporal data with standardized display names using chart_core"""
    return prepare_temporal_display_data(meta_geral, df_original)

def calculate_largest_gap(anos_list):
    """Calculate the largest consecutive gap in a list of years"""
    if len(anos_list) <= 1:
        return 0
    
    anos_sorted = sorted(anos_list)
    gaps = []
    
    for i in range(len(anos_sorted) - 1):
        gap = anos_sorted[i + 1] - anos_sorted[i] - 1
        if gap > 0:
            gaps.append(gap)
    
    return max(gaps) if gaps else 0

def show_timeline_chart(temporal_data):
    """Gantt-style timeline chart showing coverage of each initiative using siglas"""
    st.subheader("📊 LULC Initiatives Timeline Comparison - Availability Periods")
    
    # Prepare data for Gantt chart using siglas for display
    gantt_data = []
    color_map = get_initiative_color_map(temporal_data['Nome'].tolist())
    
    for idx, row in temporal_data.iterrows():
        # Use sigla for Task display, keep Nome for color mapping
        gantt_data.append({
            'Task': row['Display_Name'],  # Use sigla for display
            'FullName': row['Nome'],      # Keep full name for reference
            'Start': f"{row['Primeiro_Ano']}-01-01",
            'Finish': f"{row['Ultimo_Ano']}-12-31",
            'Resource': row['Tipo'],
            'Description': f"{row['Display_Name']} ({row['Primeiro_Ano']}-{row['Ultimo_Ano']})",
            'Color': color_map.get(row['Nome'], '#3B82F6')
        })
    
    gantt_df = pd.DataFrame(gantt_data)    
    # Create Gantt chart with siglas
    fig = go.Figure()
    
    # Add custom Gantt bars
    for idx, row in gantt_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Start'], row['Finish']],
            y=[row['Task'], row['Task']],
            mode='lines',
            line=dict(color=row['Color'], width=20),
            name=row['Task'],
            hovertemplate=f"<b>{row['Task']}</b><br>" +
                         f"Start: {row['Start'][:4]}<br>" +
                         f"End: {row['Finish'][:4]}<br>" +
                         f"Type: {row['Resource']}<extra></extra>",
            showlegend=False        ))
    
    # Apply standardized layout
    apply_standard_layout(fig, "LULC Initiatives Availability Timeline", "Year", "Initiatives", "timeline")
    
    # Custom timeline-specific configurations
    fig.update_layout(
        height=max(600, len(temporal_data) * 30),
        xaxis=dict(tickmode='linear', dtick=2),  # Tick every 2 years
        yaxis=dict(
            categoryorder='array',
            categoryarray=temporal_data.sort_values('Primeiro_Ano')['Display_Name'].tolist()
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    safe_download_image(fig, "timeline_iniciatives.png", "⬇️ Download Timeline (PNG)")
    
    # Add complementary information in English
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Initiatives", len(temporal_data))
    with col2:
        periodo_total = f"{temporal_data['Primeiro_Ano'].min()} - {temporal_data['Ultimo_Ano'].max()}"
        st.metric("Total Period Covered", periodo_total)
    with col3:
        cobertura_media = temporal_data['Cobertura_Percentual'].mean()
        st.metric("Average Coverage", f"{cobertura_media:.1f}%")

def show_coverage_analysis(temporal_data):
    """Temporal coverage analysis using siglas"""
    st.subheader("🔍 Temporal Coverage Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart: Percentage coverage using siglas
        fig_coverage = px.bar(
            temporal_data.sort_values('Cobertura_Percentual', ascending=True),
            x='Cobertura_Percentual',
            y='Display_Name',  # Use siglas for y-axis
            color='Tipo',
            labels={'Cobertura_Percentual': 'Coverage (%)', 'Display_Name': 'Initiative'}
        )
        # Apply standardized layout
        apply_standard_layout(fig_coverage, "Temporal Coverage by Initiative (%)", "Coverage (%)", "Initiative")
        fig_coverage.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_coverage, use_container_width=True)
        safe_download_image(fig_coverage, "temporal_coverage.png", "⬇️ Download Coverage (PNG)")
    
    with col2:
        # Scatter plot: Span vs Coverage using siglas
        fig_scatter = px.scatter(
            temporal_data,
            x='Span_Total',
            y='Cobertura_Percentual',
            size='Anos_Com_Dados',
            color='Tipo',
            hover_name='Display_Name',  # Use sigla for hover
            labels={
                'Span_Total': 'Total Span (years)',
                'Cobertura_Percentual': 'Coverage (%)',
                'Anos_Com_Dados': 'Years with Data'
            }
        )
        # Apply standardized layout
        apply_standard_layout(fig_scatter, "Temporal Span vs Coverage", "Total Span (years)", "Coverage (%)")
        st.plotly_chart(fig_scatter, use_container_width=True)
        safe_download_image(fig_scatter, "span_vs_coverage.png", "⬇️ Download Scatter (PNG)")
    
    # Summary statistics in English
    st.markdown("### 📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Coverage", f"{temporal_data['Cobertura_Percentual'].mean():.1f}%")
    
    with col2:
        st.metric("Average Span", f"{temporal_data['Span_Total'].mean():.1f} years")
    
    with col3:
        melhor_cobertura = temporal_data.loc[temporal_data['Cobertura_Percentual'].idxmax()]
        st.metric("Best Coverage", f"{melhor_cobertura['Display_Name']}", f"{melhor_cobertura['Cobertura_Percentual']:.1f}%")  # Use sigla
    
    with col4:
        maior_span = temporal_data.loc[temporal_data['Span_Total'].idxmax()]
        st.metric("Largest Span", f"{maior_span['Display_Name']}", f"{maior_span['Span_Total']} years")  # Use sigla

def show_gaps_analysis(temporal_data):
    """Temporal gaps analysis using siglas"""
    st.subheader("⚠️ Temporal Gaps Analysis")
    
    # Filter only initiatives with gaps
    gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
    
    if gaps_data.empty:
        st.success("🎉 Excellent! No initiatives have significant temporal gaps.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart: Gaps by initiative using siglas
        fig_gaps = px.bar(
            gaps_data.sort_values('Anos_Faltando', ascending=True),
            x='Anos_Faltando',
            y='Display_Name',  # Use siglas for y-axis
            color='Maior_Lacuna',
            labels={'Anos_Faltando': 'Missing Years', 'Display_Name': 'Initiative'},
            color_continuous_scale='Reds'
        )
        # Apply standardized layout
        apply_standard_layout(fig_gaps, "Missing Years by Initiative", "Missing Years", "Initiative")
        fig_gaps.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_gaps, use_container_width=True)
        safe_download_image(fig_gaps, "temporal_gaps.png", "⬇️ Download Gaps (PNG)")
    
    with col2:
        # Distribution of gaps by type
        gaps_by_type = gaps_data.groupby('Tipo').agg({
            'Anos_Faltando': 'mean',
            'Maior_Lacuna': 'mean',
            'Display_Name': 'count'  # Use Display_Name for counting
        }).round(1)
        gaps_by_type.columns = ['Avg Missing Years', 'Avg Largest Gap', 'Qty Initiatives']
        
        st.markdown("#### 📊 Gaps by Initiative Type")
        st.dataframe(gaps_by_type, use_container_width=True)
    
    # Detailed gaps table using siglas
    st.markdown("#### 📋 Gap Details")
    gaps_display = gaps_data[['Display_Name', 'Primeiro_Ano', 'Ultimo_Ano', 'Span_Total', 'Anos_Faltando', 'Maior_Lacuna', 'Cobertura_Percentual', 'Tipo']].copy()
    gaps_display['Cobertura_Percentual'] = gaps_display['Cobertura_Percentual'].round(1)
    gaps_display = gaps_display.sort_values('Anos_Faltando', ascending=False)
    
    # Rename columns to English
    gaps_display.columns = ['Initiative', 'First Year', 'Last Year', 'Total Span', 'Missing Years', 'Largest Gap', 'Coverage %', 'Type']
    
    st.dataframe(gaps_display, use_container_width=True)

def show_evolution_analysis(temporal_data):
    """Analysis of data availability evolution over time"""
    st.subheader("📈 Data Availability Evolution")
    
    # Create year count dataframe
    all_years = []
    for _, row in temporal_data.iterrows():
        all_years.extend(row['Anos_Lista'])
    
    if not all_years:
        st.warning("Insufficient data for evolution analysis.")
        return
    
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Year': year_counts.index,
        'Number_Initiatives': year_counts.values
    })
    
    col1, col2 = st.columns(2)    
    with col1:
        # Line chart: Evolution of number of initiatives
        fig_evolution = px.line(
            years_df,
            x='Year',
            y='Number_Initiatives',
            markers=True
        )
        fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
        # Apply standardized layout
        apply_standard_layout(fig_evolution, "Number of Initiatives with Data by Year", "Year", "Number of Initiatives")
        st.plotly_chart(fig_evolution, use_container_width=True)
        safe_download_image(fig_evolution, "availability_evolution.png", "⬇️ Download Evolution (PNG)")
    
    with col2:
        # Heatmap of availability by type and year
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            for ano in row['Anos_Lista']:
                heatmap_data.append({
                    'Year': ano,
                    'Type': row['Tipo'],
                    'Initiative': row['Display_Name']  # Use sigla for initiative name
                })
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            pivot_df = heatmap_df.groupby(['Type', 'Year']).size().reset_index(name='Count')
            pivot_table = pivot_df.pivot(index='Type', columns='Year', values='Count').fillna(0)
            
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Year", y="Type", color="Initiatives"),
                aspect="auto"
            )
            # Apply standardized layout
            apply_standard_layout(fig_heatmap, "Availability by Type and Year", "Year", "Type")
            st.plotly_chart(fig_heatmap, use_container_width=True)
            safe_download_image(fig_heatmap, "heatmap_type_year.png", "⬇️ Download Heatmap (PNG)")
    
    # Evolution statistics in English
    st.markdown("### 📊 Evolution Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Period", f"{years_df['Year'].min()} - {years_df['Year'].max()}")
    
    with col2:
        st.metric("Peak Initiatives", f"{years_df['Number_Initiatives'].max()}", f"in {years_df.loc[years_df['Number_Initiatives'].idxmax(), 'Year']}")
    
    with col3:
        st.metric("Average per Year", f"{years_df['Number_Initiatives'].mean():.1f}")
    
    with col4:
        primeiro_ano = years_df['Year'].min()
        ultimo_ano = years_df['Year'].max()
        crescimento = years_df[years_df['Year'] == ultimo_ano]['Number_Initiatives'].iloc[0] - years_df[years_df['Year'] == primeiro_ano]['Number_Initiatives'].iloc[0]
        st.metric("Total Growth", f"+{crescimento}" if crescimento > 0 else str(crescimento))

def run_non_streamlit(metadata, df_original, output_dir="graphics/temporal"):
    """
    Run temporal analysis without Streamlit UI and save graphics to files.
    Used when called from command-line scripts like run_full_analysis.py
    """
    from pathlib import Path
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("🔄 Gerando análises temporais...")
    
    # Prepare temporal data
    temporal_data = prepare_temporal_data(metadata, df_original)
    
    if temporal_data.empty:
        print("❌ Dados temporais insuficientes para análise.")
        return False
    
    try:        # Generate timeline chart
        print("📊 Gerando timeline...")
        fig_timeline = create_timeline_chart_non_streamlit(temporal_data)
        if fig_timeline:
            print("💾 Salvando timeline com fallback robusto...")
            success, saved_path, format_used = save_chart_robust(
                fig_timeline, output_dir, "timeline_initiatives", 
                width=1200, height=800, scale=2
            )
            if success:
                print(f"✅ Timeline salvo como {format_used} em: {saved_path}")
            else:
                print("❌ Falha ao salvar timeline com todos os métodos")
        else:
            print("❌ Falha na criação do timeline chart")
          # Generate coverage analysis
        print("🔍 Gerando análise de cobertura...")
        fig_coverage, fig_scatter = create_coverage_charts_non_streamlit(temporal_data)
        if fig_coverage:
            success, saved_path, format_used = save_chart_robust(
                fig_coverage, output_dir, "temporal_coverage", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Cobertura temporal salva como {format_used} em: {saved_path}")
        if fig_scatter:
            success, saved_path, format_used = save_chart_robust(
                fig_scatter, output_dir, "span_vs_coverage", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Scatter plot salvo como {format_used} em: {saved_path}")
          # Generate gaps analysis
        print("⚠️ Gerando análise de lacunas...")
        fig_gaps = create_gaps_chart_non_streamlit(temporal_data)
        if fig_gaps:
            success, saved_path, format_used = save_chart_robust(
                fig_gaps, output_dir, "temporal_gaps", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Análise de lacunas salva como {format_used} em: {saved_path}")
          # Generate evolution analysis
        print("📈 Gerando análise de evolução...")
        fig_evolution, fig_heatmap = create_evolution_charts_non_streamlit(temporal_data)
        if fig_evolution:
            success, saved_path, format_used = save_chart_robust(
                fig_evolution, output_dir, "availability_evolution", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Evolução temporal salva como {format_used} em: {saved_path}")
        if fig_heatmap:
            success, saved_path, format_used = save_chart_robust(
                fig_heatmap, output_dir, "heatmap_type_year", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Heatmap salvo como {format_used} em: {saved_path}")
        
        print("✅ Análises temporais concluídas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar análises temporais: {e}")
        return False

def create_timeline_chart_non_streamlit(temporal_data):
    """Create timeline chart without Streamlit UI dependencies"""
    try:
        print("🔄 Iniciando criação do timeline chart...")
        
        if temporal_data is None or temporal_data.empty:
            print("❌ Dados temporais vazios ou nulos")
            return None
            
        print(f"📊 Processando {len(temporal_data)} iniciativas para timeline...")
        
        # Prepare data for Gantt chart using siglas for display
        gantt_data = []
        print("🎨 Obtendo mapa de cores...")
        color_map = get_initiative_color_map(temporal_data['Nome'].tolist())
        
        print("📋 Preparando dados do Gantt chart...")
        for idx, row in temporal_data.iterrows():
            # Use sigla for Task display, keep Nome for color mapping
            gantt_data.append({
                'Task': row['Display_Name'],  # Use sigla for display
                'FullName': row['Nome'],      # Keep full name for reference
                'Start': f"{row['Primeiro_Ano']}-01-01",
                'Finish': f"{row['Ultimo_Ano']}-12-31",
                'Resource': row['Tipo'],
                'Description': f"{row['Display_Name']} ({row['Primeiro_Ano']}-{row['Ultimo_Ano']})",
                'Color': color_map.get(row['Nome'], '#3B82F6')
            })
        
        print(f"✅ Dados do Gantt preparados: {len(gantt_data)} entradas")
        gantt_df = pd.DataFrame(gantt_data)    
        
        print("📈 Criando figura Plotly...")
        # Create Gantt chart with siglas
        fig = go.Figure()
        
        # Add custom Gantt bars
        print("🎯 Adicionando traces ao gráfico...")
        for idx, row in gantt_df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['Start'], row['Finish']],
                y=[row['Task'], row['Task']],
                mode='lines',
                line=dict(color=row['Color'], width=20),
                name=row['Task'],
                hovertemplate=f"<b>{row['Task']}</b><br>" +
                             f"Start: {row['Start'][:4]}<br>" +
                             f"End: {row['Finish'][:4]}<br>" +
                             f"Type: {row['Resource']}<extra></extra>",
                showlegend=False
            ))    
        print("🎨 Configurando layout do gráfico...")
        # Apply standardized layout
        apply_standard_layout(fig, "LULC Initiatives Availability Timeline", "Year", "Initiatives", "timeline")
        
        # Custom timeline-specific configurations
        fig.update_layout(
            height=max(600, len(temporal_data) * 30),
            xaxis=dict(tickmode='linear', dtick=2),  # Tick every 2 years
            yaxis=dict(
                categoryorder='array',
                categoryarray=temporal_data.sort_values('Primeiro_Ano')['Display_Name'].tolist()
            )
        )
        
        print("✅ Timeline chart criado com sucesso!")
        return fig
    except Exception as e:
        print(f"❌ Erro ao criar timeline chart: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return None

def create_coverage_charts_non_streamlit(temporal_data):
    """Create coverage analysis charts without Streamlit dependencies"""
    try:
        # Bar chart: Percentage coverage using siglas
        fig_coverage = px.bar(
            temporal_data.sort_values('Cobertura_Percentual', ascending=True),
            x='Cobertura_Percentual',
            y='Display_Name',  # Use siglas for y-axis
            color='Tipo',
            labels={'Cobertura_Percentual': 'Coverage (%)', 'Display_Name': 'Initiative'}
        )
        # Apply standardized layout
        apply_standard_layout(fig_coverage, "Temporal Coverage by Initiative (%)", "Coverage (%)", "Initiative")
        fig_coverage.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        # Scatter plot: Span vs Coverage using siglas
        fig_scatter = px.scatter(
            temporal_data,
            x='Span_Total',
            y='Cobertura_Percentual',
            size='Anos_Com_Dados',
            color='Tipo',
            hover_name='Display_Name',  # Use sigla for hover
            labels={
                'Span_Total': 'Total Span (years)',
                'Cobertura_Percentual': 'Coverage (%)',
                'Anos_Com_Dados': 'Years with Data'
            }
        )
        # Apply standardized layout
        apply_standard_layout(fig_scatter, "Temporal Span vs Coverage", "Total Span (years)", "Coverage (%)")
        
        return fig_coverage, fig_scatter
    except Exception as e:
        print(f"Erro ao criar coverage charts: {e}")
        return None, None

def create_gaps_chart_non_streamlit(temporal_data):
    """Create gaps analysis chart without Streamlit dependencies"""
    try:
        # Filter only initiatives with gaps
        gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
        
        if gaps_data.empty:
            print("🎉 Excelente! Nenhuma iniciativa tem lacunas temporais significativas.")
            return None
        
        # Bar chart: Gaps by initiative using siglas
        fig_gaps = px.bar(
            gaps_data.sort_values('Anos_Faltando', ascending=True),
            x='Anos_Faltando',
            y='Display_Name',  # Use siglas for y-axis
            color='Maior_Lacuna',
            labels={'Anos_Faltando': 'Missing Years', 'Display_Name': 'Initiative'},
            color_continuous_scale='Reds'
        )
        # Apply standardized layout
        apply_standard_layout(fig_gaps, "Missing Years by Initiative", "Missing Years", "Initiative")
        fig_gaps.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        return fig_gaps
    except Exception as e:
        print(f"Erro ao criar gaps chart: {e}")
        return None

def create_evolution_charts_non_streamlit(temporal_data):
    """Create evolution analysis charts without Streamlit dependencies"""
    try:
        # Create year count dataframe
        all_years = []
        for _, row in temporal_data.iterrows():
            all_years.extend(row['Anos_Lista'])
        
        if not all_years:
            print("Dados insuficientes para análise de evolução.")
            return None, None
        
        year_counts = pd.Series(all_years).value_counts().sort_index()
        years_df = pd.DataFrame({
            'Year': year_counts.index,
            'Number_Initiatives': year_counts.values
        })
        
        # Line chart: Evolution of number of initiatives
        fig_evolution = px.line(
            years_df,
            x='Year',
            y='Number_Initiatives',
            markers=True
        )
        fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
        # Apply standardized layout
        apply_standard_layout(fig_evolution, "Number of Initiatives with Data by Year", "Year", "Number of Initiatives")
        
        # Heatmap of availability by type and year
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            for ano in row['Anos_Lista']:
                heatmap_data.append({
                    'Year': ano,
                    'Type': row['Tipo'],
                    'Initiative': row['Display_Name']  # Use sigla for initiative name
                })
        
        fig_heatmap = None
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            pivot_df = heatmap_df.groupby(['Type', 'Year']).size().reset_index(name='Count')
            pivot_table = pivot_df.pivot(index='Type', columns='Year', values='Count').fillna(0)
            
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Year", y="Type", color="Initiatives"),
                aspect="auto"
            )
            # Apply standardized layout
            apply_standard_layout(fig_heatmap, "Availability by Type and Year", "Year", "Type")
        
        return fig_evolution, fig_heatmap
    except Exception as e:
        print(f"Erro ao criar evolution charts: {e}")
        return None, None
