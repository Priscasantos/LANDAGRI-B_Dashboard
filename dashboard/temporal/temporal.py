import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
from pathlib import Path

# Adicionar scripts ao path
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir / "scripts"))

from scripts.utilities.utils import safe_download_image
from scripts.utilities.config import get_initiative_color_map
from scripts.utilities.english_translations import (
    translate_text, 
    INTERFACE_TRANSLATIONS,
    translate_chart_elements
)

def run():
    st.header("⏳ Comprehensive Temporal Analysis of LULC Initiatives")
    
    if 'metadata' not in st.session_state:
        st.warning("⚠️ Metadata not found. Run the main page (app.py) first.")
        st.stop()
    
    meta_geral = st.session_state.metadata
    
    # Get DataFrame for sigla mapping
    df_original = st.session_state.get('df_original', pd.DataFrame())
    
    # Prepare temporal data with sigla mapping
    temporal_data = prepare_temporal_data(meta_geral, df_original)
    
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
    """Prepare structured temporal data for analysis with sigla mapping"""
    data_list = []
    
    # Create nome to sigla mapping from DataFrame
    nome_to_sigla = {}
    if df_original is not None and not df_original.empty and 'Sigla' in df_original.columns:
        for _, row in df_original.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']
    
    for nome, meta_data in meta_geral.items():
        anos_disponiveis = meta_data.get('anos_disponiveis', [])
        if not anos_disponiveis:
            continue
            
        # Convert to list of integers
        anos_int = []
        for ano in anos_disponiveis:
            if isinstance(ano, (int, float)) and pd.notna(ano):
                anos_int.append(int(ano))
        
        if not anos_int:
            continue
            
        anos_int = sorted(anos_int)
        
        # Calculate temporal statistics
        primeiro_ano = min(anos_int)
        ultimo_ano = max(anos_int)
        span_total = ultimo_ano - primeiro_ano + 1
        anos_com_dados = len(anos_int)
        
        # Calculate gaps
        anos_esperados = set(range(primeiro_ano, ultimo_ano + 1))
        anos_faltando = anos_esperados - set(anos_int)
        maior_lacuna = calculate_largest_gap(anos_int) if len(anos_int) > 1 else 0
        
        # Get sigla for display
        sigla = nome_to_sigla.get(nome, nome[:10])  # Use sigla or truncate name
        
        data_list.append({
            'Nome': nome,
            'Sigla': sigla,
            'Display_Name': sigla,  # Use sigla for display
            'Primeiro_Ano': primeiro_ano,
            'Ultimo_Ano': ultimo_ano,
            'Span_Total': span_total,
            'Anos_Com_Dados': anos_com_dados,
            'Anos_Faltando': len(anos_faltando),
            'Cobertura_Percentual': (anos_com_dados / span_total) * 100,
            'Maior_Lacuna': maior_lacuna,
            'Anos_Lista': anos_int,
            'Tipo': meta_data.get('tipo', 'Not specified')
        })
    
    return pd.DataFrame(data_list)

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
            showlegend=False
        ))
    
    # Layout with light theme and English labels
    fig.update_layout(
        title={
            'text': "LULC Initiatives Availability Timeline",
            'x': 0.02,
            'y': 0.95,
            'font': {'size': 18, 'color': '#2D3748', 'family': 'Arial Black'}
        },
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#2D3748', family='Arial'),
        height=max(600, len(temporal_data) * 30),
        width=1000,
        xaxis=dict(
            title=dict(text="Year", font=dict(size=14, color='#2D3748')),
            gridcolor='#E2E8F0',
            gridwidth=0.5,
            tickfont=dict(size=12, color='#2D3748'),
            showgrid=True,
            zeroline=False,
            linecolor='#E2E8F0',
            tickmode='linear',
            dtick=2  # Tick every 2 years
        ),
        yaxis=dict(
            title=dict(text="Initiatives", font=dict(size=14, color='#2D3748')),
            gridcolor='#E2E8F0',
            gridwidth=0.5,
            tickfont=dict(size=11, color='#2D3748'),
            showgrid=True,            zeroline=False,
            linecolor='#E2E8F0',
            categoryorder='array',
            categoryarray=temporal_data.sort_values('Primeiro_Ano')['Display_Name'].tolist()  # Use siglas for ordering
        ),
        margin=dict(l=180, r=50, t=80, b=60),
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    safe_download_image(fig, "timeline_initiatives.png", "⬇️ Download Timeline (PNG)")
    
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
            title="Temporal Coverage by Initiative (%)",
            labels={'Cobertura_Percentual': 'Coverage (%)', 'Display_Name': 'Initiative'},
            height=500
        )
        fig_coverage.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_coverage, use_container_width=True)
        safe_download_image(fig_coverage, "temporal_coverage.png", "⬇️ Download Coverage (PNG)")
    
    with col2:
        # Scatter plot: Span vs Coverage using siglas
        fig_scatter = px.scatter(
            temporal_data,
            x='Span_Total',
            y='Cobertura_Percentual',            size='Anos_Com_Dados',
            color='Tipo',
            hover_name='Display_Name',  # Use siglas for hover
            title="Temporal Span vs Coverage",
            labels={
                'Span_Total': 'Total Span (years)',
                'Cobertura_Percentual': 'Coverage (%)',
                'Anos_Com_Dados': 'Years with Data'
            },
            height=500
        )
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
            y='Display_Name',  # Use siglas for y-axis            color='Maior_Lacuna',
            title="Missing Years by Initiative",
            labels={'Anos_Faltando': 'Missing Years', 'Display_Name': 'Initiative'},
            color_continuous_scale='Reds',
            height=400
        )
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
            title="Number of Initiatives with Data by Year",
            markers=True,
            height=400
        )
        fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
        fig_evolution.update_layout(
            xaxis_title="Year",
            yaxis_title="Number of Initiatives"
        )
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
                title="Availability by Type and Year",
                labels=dict(x="Year", y="Type", color="Initiatives"),
                aspect="auto",
                height=400
            )
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
