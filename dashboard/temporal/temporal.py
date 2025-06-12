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

from utils import safe_download_image
from config import get_initiative_color_map

def run():
    st.header("⏳ Análise Temporal Abrangente das Iniciativas LULC")
    
    if 'metadata' not in st.session_state:
        st.warning("⚠️ Metadados não encontrados. Execute a página principal (app.py) primeiro.")
        st.stop()
    
    meta_geral = st.session_state.metadata
    
    # Preparar dados temporais
    temporal_data = prepare_temporal_data(meta_geral)
    
    if temporal_data.empty:
        st.warning("Não há dados temporais disponíveis para análise.")
        st.stop()
    
    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Linha do Tempo", 
        "🔍 Cobertura Temporal", 
        "⚠️ Lacunas Temporais",
        "📈 Evolução da Disponibilidade"
    ])
    
    with tab1:
        show_timeline_chart(temporal_data)
    
    with tab2:
        show_coverage_analysis(temporal_data)
    
    with tab3:
        show_gaps_analysis(temporal_data)
    
    with tab4:
        show_evolution_analysis(temporal_data)

def prepare_temporal_data(meta_geral):
    """Prepara dados temporais estruturados para análise"""
    data_list = []
    
    for nome, meta_data in meta_geral.items():
        anos_disponiveis = meta_data.get('anos_disponiveis', [])
        if not anos_disponiveis:
            continue
            
        # Converter para lista de inteiros
        anos_int = []
        for ano in anos_disponiveis:
            if isinstance(ano, (int, float)) and pd.notna(ano):
                anos_int.append(int(ano))
        
        if not anos_int:
            continue
            
        anos_int = sorted(anos_int)
        
        # Calcular estatísticas temporais
        primeiro_ano = min(anos_int)
        ultimo_ano = max(anos_int)
        span_total = ultimo_ano - primeiro_ano + 1
        anos_com_dados = len(anos_int)
        
        # Calcular lacunas
        anos_esperados = set(range(primeiro_ano, ultimo_ano + 1))
        anos_faltando = anos_esperados - set(anos_int)
        maior_lacuna = calculate_largest_gap(anos_int) if len(anos_int) > 1 else 0
        
        data_list.append({
            'Nome': nome,
            'Primeiro_Ano': primeiro_ano,
            'Ultimo_Ano': ultimo_ano,
            'Span_Total': span_total,
            'Anos_Com_Dados': anos_com_dados,
            'Anos_Faltando': len(anos_faltando),
            'Cobertura_Percentual': (anos_com_dados / span_total) * 100,
            'Maior_Lacuna': maior_lacuna,
            'Anos_Lista': anos_int,
            'Tipo': meta_data.get('tipo', 'Não especificado')
        })
    
    return pd.DataFrame(data_list)

def calculate_largest_gap(anos_list):
    """Calcula a maior lacuna consecutiva em uma lista de anos"""
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
    """Gráfico de linha do tempo estilo Gantt mostrando a cobertura de cada iniciativa"""
    st.subheader("📊 Timeline Comparativa das Iniciativas LULC - Períodos de Disponibilidade")
    
    # Preparar dados para o gráfico Gantt igual à imagem de referência
    gantt_data = []
    color_map = get_initiative_color_map(temporal_data['Nome'].tolist())
    
    for idx, row in temporal_data.iterrows():
        gantt_data.append({
            'Task': row['Nome'],
            'Start': f"{row['Primeiro_Ano']}-01-01",
            'Finish': f"{row['Ultimo_Ano']}-12-31",
            'Resource': row['Tipo'],
            'Description': f"{row['Nome']} ({row['Primeiro_Ano']}-{row['Ultimo_Ano']})",
            'Color': color_map.get(row['Nome'], '#3B82F6')
        })
    
    gantt_df = pd.DataFrame(gantt_data)
    
    # Criar gráfico Gantt igual à imagem de referência
    fig = go.Figure()
    
    # Adicionar barras Gantt personalizadas
    for idx, row in gantt_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Start'], row['Finish']],
            y=[row['Task'], row['Task']],
            mode='lines',
            line=dict(color=row['Color'], width=20),
            name=row['Task'],
            hovertemplate=f"<b>{row['Task']}</b><br>" +
                         f"Início: {row['Start'][:4]}<br>" +
                         f"Fim: {row['Finish'][:4]}<br>" +
                         f"Tipo: {row['Resource']}<extra></extra>",
            showlegend=False
        ))
      # Layout com tema claro
    fig.update_layout(
        title={
            'text': "Timeline de Disponibilidade das Iniciativas LULC",
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
            title=dict(text="Ano", font=dict(size=14, color='#2D3748')),
            gridcolor='#E2E8F0',
            gridwidth=0.5,
            tickfont=dict(size=12, color='#2D3748'),
            showgrid=True,
            zeroline=False,
            linecolor='#E2E8F0',
            tickmode='linear',
            dtick=2  # Tick a cada 2 anos
        ),
        yaxis=dict(
            title=dict(text="Iniciativas", font=dict(size=14, color='#2D3748')),
            gridcolor='#E2E8F0',
            gridwidth=0.5,
            tickfont=dict(size=11, color='#2D3748'),
            showgrid=True,
            zeroline=False,
            linecolor='#E2E8F0',
            categoryorder='array',
            categoryarray=temporal_data.sort_values('Primeiro_Ano')['Nome'].tolist()
        ),
        margin=dict(l=180, r=50, t=80, b=60),
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    safe_download_image(fig, "timeline_iniciativas.png", "⬇️ Baixar Timeline (PNG)")
    
    # Adicionar informações complementares
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Iniciativas", len(temporal_data))
    with col2:
        periodo_total = f"{temporal_data['Primeiro_Ano'].min()} - {temporal_data['Ultimo_Ano'].max()}"
        st.metric("Período Total Coberto", periodo_total)
    with col3:
        cobertura_media = temporal_data['Cobertura_Percentual'].mean()
        st.metric("Cobertura Média", f"{cobertura_media:.1f}%")

def show_coverage_analysis(temporal_data):
    """Análise da cobertura temporal"""
    st.subheader("🔍 Análise de Cobertura Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras: Cobertura percentual
        fig_coverage = px.bar(
            temporal_data.sort_values('Cobertura_Percentual', ascending=True),
            x='Cobertura_Percentual',
            y='Nome',
            color='Tipo',
            title="Cobertura Temporal por Iniciativa (%)",
            labels={'Cobertura_Percentual': 'Cobertura (%)', 'Nome': 'Iniciativa'},
            height=500
        )
        fig_coverage.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_coverage, use_container_width=True)
        safe_download_image(fig_coverage, "cobertura_temporal.png", "⬇️ Baixar Cobertura (PNG)")
    
    with col2:
        # Gráfico de dispersão: Span vs Cobertura
        fig_scatter = px.scatter(
            temporal_data,
            x='Span_Total',
            y='Cobertura_Percentual',
            size='Anos_Com_Dados',
            color='Tipo',
            hover_name='Nome',
            title="Span Temporal vs Cobertura",
            labels={
                'Span_Total': 'Span Total (anos)',
                'Cobertura_Percentual': 'Cobertura (%)',
                'Anos_Com_Dados': 'Anos com Dados'
            },
            height=500
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        safe_download_image(fig_scatter, "span_vs_cobertura.png", "⬇️ Baixar Scatter (PNG)")
    
    # Estatísticas resumo
    st.markdown("### 📈 Estatísticas Resumo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cobertura Média", f"{temporal_data['Cobertura_Percentual'].mean():.1f}%")
    
    with col2:
        st.metric("Span Médio", f"{temporal_data['Span_Total'].mean():.1f} anos")
    
    with col3:
        melhor_cobertura = temporal_data.loc[temporal_data['Cobertura_Percentual'].idxmax()]
        st.metric("Melhor Cobertura", f"{melhor_cobertura['Nome']}", f"{melhor_cobertura['Cobertura_Percentual']:.1f}%")
    
    with col4:
        maior_span = temporal_data.loc[temporal_data['Span_Total'].idxmax()]
        st.metric("Maior Span", f"{maior_span['Nome']}", f"{maior_span['Span_Total']} anos")

def show_gaps_analysis(temporal_data):
    """Análise de lacunas temporais"""
    st.subheader("⚠️ Análise de Lacunas Temporais")
    
    # Filtrar apenas iniciativas com lacunas
    gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()
    
    if gaps_data.empty:
        st.success("🎉 Excelente! Nenhuma iniciativa possui lacunas temporais significativas.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras: Lacunas por iniciativa
        fig_gaps = px.bar(
            gaps_data.sort_values('Anos_Faltando', ascending=True),
            x='Anos_Faltando',
            y='Nome',
            color='Maior_Lacuna',
            title="Anos Faltando por Iniciativa",
            labels={'Anos_Faltando': 'Anos Faltando', 'Nome': 'Iniciativa'},
            color_continuous_scale='Reds',
            height=400
        )
        fig_gaps.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_gaps, use_container_width=True)
        safe_download_image(fig_gaps, "lacunas_temporais.png", "⬇️ Baixar Lacunas (PNG)")
    
    with col2:
        # Distribuição das lacunas por tipo
        gaps_by_type = gaps_data.groupby('Tipo').agg({
            'Anos_Faltando': 'mean',
            'Maior_Lacuna': 'mean',
            'Nome': 'count'
        }).round(1)
        gaps_by_type.columns = ['Média Anos Faltando', 'Média Maior Lacuna', 'Qtd Iniciativas']
        
        st.markdown("#### 📊 Lacunas por Tipo de Iniciativa")
        st.dataframe(gaps_by_type, use_container_width=True)
    
    # Tabela detalhada de lacunas
    st.markdown("#### 📋 Detalhamento das Lacunas")
    gaps_display = gaps_data[['Nome', 'Primeiro_Ano', 'Ultimo_Ano', 'Span_Total', 'Anos_Faltando', 'Maior_Lacuna', 'Cobertura_Percentual', 'Tipo']].copy()
    gaps_display['Cobertura_Percentual'] = gaps_display['Cobertura_Percentual'].round(1)
    gaps_display = gaps_display.sort_values('Anos_Faltando', ascending=False)
    
    st.dataframe(gaps_display, use_container_width=True)

def show_evolution_analysis(temporal_data):
    """Análise da evolução da disponibilidade de dados ao longo do tempo"""
    st.subheader("📈 Evolução da Disponibilidade de Dados")
    
    # Criar dataframe de contagem por ano
    all_years = []
    for _, row in temporal_data.iterrows():
        all_years.extend(row['Anos_Lista'])
    
    if not all_years:
        st.warning("Não há dados suficientes para análise de evolução.")
        return
    
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Ano': year_counts.index,
        'Numero_Iniciativas': year_counts.values
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de linha: Evolução do número de iniciativas
        fig_evolution = px.line(
            years_df,
            x='Ano',
            y='Numero_Iniciativas',
            title="Número de Iniciativas com Dados por Ano",
            markers=True,
            height=400
        )
        fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
        fig_evolution.update_layout(
            xaxis_title="Ano",
            yaxis_title="Número de Iniciativas"
        )
        st.plotly_chart(fig_evolution, use_container_width=True)
        safe_download_image(fig_evolution, "evolucao_disponibilidade.png", "⬇️ Baixar Evolução (PNG)")
    
    with col2:
        # Heatmap de disponibilidade por tipo e ano
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            for ano in row['Anos_Lista']:
                heatmap_data.append({
                    'Ano': ano,
                    'Tipo': row['Tipo'],
                    'Iniciativa': row['Nome']
                })
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            pivot_df = heatmap_df.groupby(['Tipo', 'Ano']).size().reset_index(name='Count')
            pivot_table = pivot_df.pivot(index='Tipo', columns='Ano', values='Count').fillna(0)
            
            fig_heatmap = px.imshow(
                pivot_table,
                title="Disponibilidade por Tipo e Ano",
                labels=dict(x="Ano", y="Tipo", color="Iniciativas"),
                aspect="auto",
                height=400
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            safe_download_image(fig_heatmap, "heatmap_tipo_ano.png", "⬇️ Baixar Heatmap (PNG)")
    
    # Estatísticas da evolução
    st.markdown("### 📊 Estatísticas de Evolução")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Período Total", f"{years_df['Ano'].min()} - {years_df['Ano'].max()}")
    
    with col2:
        st.metric("Pico de Iniciativas", f"{years_df['Numero_Iniciativas'].max()}", f"em {years_df.loc[years_df['Numero_Iniciativas'].idxmax(), 'Ano']}")
    
    with col3:
        st.metric("Média por Ano", f"{years_df['Numero_Iniciativas'].mean():.1f}")
    
    with col4:
        primeiro_ano = years_df['Ano'].min()
        ultimo_ano = years_df['Ano'].max()
        crescimento = years_df[years_df['Ano'] == ultimo_ano]['Numero_Iniciativas'].iloc[0] - years_df[years_df['Ano'] == primeiro_ano]['Numero_Iniciativas'].iloc[0]
        st.metric("Crescimento Total", f"+{crescimento}" if crescimento > 0 else str(crescimento))
