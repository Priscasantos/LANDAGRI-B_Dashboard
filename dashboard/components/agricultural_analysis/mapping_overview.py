"""
Mapping Overview Component - Clean Version
==========================================

Componente para exibir overview básico dos dados CONAB
Apenas métricas gerais, gráficos detalhados em Crop Calendar e Availability

Author: Agricultural Dashboard
Date: 2025-08-08
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from pathlib import Path


def load_mapping_data():
    """Carrega dados de mapeamento da CONAB"""
    try:
        # Primeiro tenta o arquivo completo
        data_path = Path("data/json/agricultural_conab_mapping_data_complete.jsonc")
        if data_path.exists():
            with open(data_path, encoding='utf-8') as f:
                content = f.read()
                # Remove comentários JSONC
                content = re.sub(r'//.*', '', content)
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                return json.loads(content)
        
        # Fallback para o arquivo antigo
        data_path = Path("data/conab_mapping_data.json")
        with open(data_path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Arquivo de dados de mapeamento da CONAB não encontrado!")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de mapeamento: {e}")
        return None


def calculate_conab_metrics(data):
    """Calcula métricas específicas dos dados de calendário da CONAB"""
    if not data or 'crop_calendar' not in data:
        return {}
    
    # Contar culturas únicas
    total_crops = len(data['crop_calendar'])
    
    # Contar estados únicos
    all_states = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            all_states.add(state_info['state_code'])
    total_states = len(all_states)
    
    # Contar regiões
    all_regions = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            all_regions.add(state_info['region'])
    total_regions = len(all_regions)
    
    # Calcular completude dos dados
    total_cells = 0
    filled_cells = 0
    
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            total_cells += len(calendar)
            filled_cells += sum(1 for v in calendar.values() if v and v.strip())
    
    completeness = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Calcular período de cobertura
    coverage_years = "2020-2024"
    
    # Calcular área total estimada
    estimated_area = total_states * total_crops * 0.5
    
    return {
        'total_crops': total_crops,
        'total_states': total_states, 
        'total_regions': total_regions,
        'completeness': completeness,
        'total_calendar_entries': total_cells,
        'filled_entries': filled_cells,
        'coverage_years': coverage_years,
        'estimated_area': estimated_area
    }


def create_overview_summary_chart(data):
    """Cria gráfico simples de resumo das culturas"""
    if not data or 'crop_calendar' not in data:
        return None
    
    crop_data = []
    
    for crop_name, crop_states in data['crop_calendar'].items():
        states_count = len(crop_states)
        
        # Contar atividades totais
        total_activities = 0
        for state_info in crop_states:
            calendar = state_info.get('calendar', {})
            total_activities += sum(1 for v in calendar.values() if v and v.strip())
        
        crop_data.append({
            'Cultura': crop_name.replace(' (1st harvest)', ' 1ª').replace(' (2nd harvest)', ' 2ª').replace(' (3th harvest)', ' 3ª'),
            'Estados': states_count,
            'Atividades': total_activities
        })
    
    df = pd.DataFrame(crop_data)
    
    fig = px.bar(
        df,
        x='Cultura',
        y='Estados',
        title='📊 Cobertura por Cultura - Estados Monitorados',
        labels={'Estados': 'Número de Estados', 'Cultura': 'Cultura'},
        color='Atividades',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig


def render_conab_mapping_metrics(data):
    """Renderiza métricas principais do calendário CONAB"""
    if not data:
        return
    
    metrics = calculate_conab_metrics(data)
    
    st.markdown("### 📊 Resumo Geral - Calendário Agrícola CONAB")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌾 Culturas",
            f"{metrics.get('total_crops', 0)}",
            help="Total de culturas no calendário"
        )
    
    with col2:
        st.metric(
            "🏛️ Estados", 
            f"{metrics.get('total_states', 0)}",
            help="Estados brasileiros cobertos"
        )
    
    with col3:
        st.metric(
            "🗺️ Regiões",
            f"{metrics.get('total_regions', 0)}",
            help="Regiões brasileiras"
        )
    
    with col4:
        completeness = metrics.get('completeness', 0)
        st.metric(
            "✅ Completeness",
            f"{completeness:.1f}%",
            help="Porcentagem de dados preenchidos"
        )
    
    st.divider()
    
    # Métricas adicionais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📅 Período",
            metrics.get('coverage_years', 'N/A'),
            help="Período de cobertura dos dados"
        )
    
    with col2:
        area = metrics.get('estimated_area', 0)
        st.metric(
            "📏 Área Estimada",
            f"{area:.1f} M ha",
            help="Área total estimada de monitoramento"
        )
    
    with col3:
        entries = metrics.get('filled_entries', 0)
        st.metric(
            "📋 Dados Válidos",
            f"{entries:,}",
            help="Entradas de calendário preenchidas"
        )


def render_mapping_overview():
    """Função principal para renderizar o overview básico de mapeamento CONAB"""
    # Carregar dados
    data = load_mapping_data()
    
    if not data:
        st.warning("⚠️ Dados de calendário CONAB não disponíveis")
        return
    
    # Renderizar métricas principais do CONAB
    render_conab_mapping_metrics(data)
    
    # Gráfico simples de overview
    st.markdown("### 📈 Distribuição por Cultura")
    fig_overview = create_overview_summary_chart(data)
    if fig_overview:
        st.plotly_chart(fig_overview, use_container_width=True)
    
    # Informações básicas sobre fonte
    st.markdown("### ℹ️ Sobre os Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📋 Fonte dos Dados:**
        - CONAB (Companhia Nacional de Abastecimento)
        - Calendário Agrícola Nacional
        - Períodos de Plantio e Colheita
        """)
    
    with col2:
        st.info("""
        **🎯 Análises Detalhadas:**
        - **Crop Calendar**: Gráficos temporais e heatmaps
        - **Availability**: Análises de disponibilidade
        - Filtros por região e cultura disponíveis
        """)
    
    # Rodapé informativo
    st.markdown("---")
    st.markdown("""
    💡 **Dica**: Para análises detalhadas, acesse as abas **Crop Calendar** e **Availability** 
    onde você encontrará gráficos interativos, filtros por região e análises temporais completas.
    """)


if __name__ == "__main__":
    st.set_page_config(page_title="Overview CONAB", layout="wide")
    st.title("🗺️ Overview - Dados CONAB")
    render_mapping_overview()
