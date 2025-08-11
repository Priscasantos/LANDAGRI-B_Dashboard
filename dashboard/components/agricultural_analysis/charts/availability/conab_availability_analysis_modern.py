"""
Análise de Disponibilidade CONAB
================================

Módulo para análise de disponibilidade baseado exclusivamente em dados CONAB.
Implementa visualizações modernas por região e estado usando Plotly.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .conab_availability_matrix import create_conab_availability_matrix


def render_conab_availability_analysis(conab_data: dict) -> None:
    """
    Renderiza análise completa de disponibilidade CONAB.
    
    Parâmetros:
    -----------
    conab_data : dict
        Dados CONAB com estrutura completa do JSON
    """
    if not conab_data or not isinstance(conab_data, dict):
        st.warning("⚠️ Dados CONAB não disponíveis para análise.")
        return
    
    st.markdown("### 📊 Análise de Disponibilidade CONAB")
    st.markdown("*Análise baseada em dados oficiais CONAB por região e estado*")
    
    try:
        # Extrair dados principais do JSON CONAB
        crop_calendar = conab_data.get('crop_calendar', {})
        states_info = conab_data.get('states', {})
        
        if not crop_calendar:
            st.warning("⚠️ Dados de calendário agrícola não encontrados.")
            return
        
        # Análises principais em tabs
        tab1, tab2, tab3 = st.tabs([
            "🗺️ Análise Regional", 
            "📅 Sazonalidade", 
            "📈 Tendências"
        ])
        
        with tab1:
            _render_regional_analysis(crop_calendar, states_info)
        
        with tab2:
            _render_seasonality_analysis(crop_calendar, states_info)
        
        with tab3:
            _render_trends_analysis(crop_calendar, states_info)
            
    except Exception as e:
        st.error(f"❌ Erro na análise de disponibilidade CONAB: {e}")


def _render_regional_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise por região brasileira."""
    st.markdown("#### 🗺️ Disponibilidade por Região")
    
    # Agregar dados por região
    regional_data = _aggregate_by_region(crop_calendar, states_info)
    
    if not regional_data:
        st.info("📊 Dados regionais não disponíveis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Diversidade por Região")
        # Gráfico de barras por região
        regions = list(regional_data.keys())
        counts = list(regional_data.values())
        
        fig_regions = px.bar(
            x=regions,
            y=counts,
            title="Diversidade de Culturas por Região",
            labels={'x': 'Região', 'y': 'Número de Culturas'},
            color=counts,
            color_continuous_scale='Viridis',
            text=counts
        )
        fig_regions.update_traces(texttemplate='%{text}', textposition='outside')
        fig_regions.update_layout(showlegend=False, xaxis_tickangle=45)
        st.plotly_chart(fig_regions, use_container_width=True, key="regional_diversity_chart_modern")
    
    with col2:
        st.markdown("##### 🗺️ Matriz de Disponibilidade")
        # Matriz de disponibilidade
        try:
            fig_matrix = create_conab_availability_matrix({
                'crop_calendar': crop_calendar,
                'states': states_info
            })
            if fig_matrix:
                st.plotly_chart(fig_matrix, use_container_width=True, key="conab_matrix_regional")
        except Exception as e:
            st.error(f"❌ Erro ao gerar matriz: {e}")


def _render_seasonality_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise de sazonalidade."""
    st.markdown("#### 📅 Análise de Sazonalidade")
    
    # Extrair dados sazonais
    seasonal_data = _extract_seasonal_data(crop_calendar)
    
    if not seasonal_data:
        st.info("📊 Dados sazonais não disponíveis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔄 Sazonalidade Geral")
        # Criar gráfico polar de sazonalidade
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        fig_polar = go.Figure()
        
        # Adicionar trace para cada tipo de atividade
        colors = {'P': '#2E8B57', 'H': '#FF6B35', 'PH': '#4682B4'}
        names = {'P': 'Plantio', 'H': 'Colheita', 'PH': 'Plantio/Colheita'}
        
        for activity_type in ['P', 'H', 'PH']:
            monthly_counts = [seasonal_data.get(month, {}).get(activity_type, 0) for month in months]
            
            if sum(monthly_counts) > 0:  # Só adicionar se houver dados
                fig_polar.add_trace(go.Scatterpolar(
                    r=monthly_counts,
                    theta=months,
                    fill='toself',
                    name=names[activity_type],
                    line_color=colors[activity_type],
                    opacity=0.7
                ))
        
        max_value = max(
            max(seasonal_data.get(month, {}).values()) 
            for month in months
            if seasonal_data.get(month)
        ) if seasonal_data else 1
        
        fig_polar.update_layout(
            polar={
                'radialaxis': {'visible': True, 'range': [0, max_value]}
            },
            title="Sazonalidade de Atividades Agrícolas",
            showlegend=True
        )
        
        st.plotly_chart(fig_polar, use_container_width=True, key="seasonality_polar_chart")
    
    with col2:
        st.markdown("##### 📊 Atividades por Mês")
        # Gráfico de barras empilhadas por mês
        if seasonal_data:
            df_seasonal = pd.DataFrame(seasonal_data).T.fillna(0)
            df_seasonal = df_seasonal.reset_index()
            df_seasonal.rename(columns={'index': 'Mês'}, inplace=True)
            
            fig_bars = px.bar(
                df_seasonal,
                x='Mês',
                y=['P', 'H', 'PH'],
                title="Distribuição Mensal de Atividades",
                labels={'value': 'Número de Atividades', 'variable': 'Tipo'},
                color_discrete_map={'P': '#2E8B57', 'H': '#FF6B35', 'PH': '#4682B4'}
            )
            fig_bars.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_bars, use_container_width=True, key="monthly_activities_bars")


def _render_trends_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise de tendências."""
    st.markdown("#### 📈 Análise de Tendências")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🌾 Culturas com Múltiplas Safras")
        # Análise de safras múltiplas
        crops_with_multiple_harvests = _analyze_multiple_harvests(crop_calendar)
        
        if crops_with_multiple_harvests:
            crops = list(crops_with_multiple_harvests.keys())
            harvests = list(crops_with_multiple_harvests.values())
            
            fig_harvests = px.bar(
                x=crops,
                y=harvests,
                title="Culturas com Múltiplas Safras",
                labels={'x': 'Cultura', 'y': 'Número de Safras'},
                color=harvests,
                color_continuous_scale='Plasma',
                text=harvests
            )
            fig_harvests.update_traces(texttemplate='%{text}', textposition='outside')
            fig_harvests.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_harvests, use_container_width=True, key="multiple_harvests_chart")
        else:
            st.info("📊 Nenhuma cultura com múltiplas safras identificada.")
    
    with col2:
        st.markdown("##### 🗺️ Distribuição Geográfica")
        # Análise de distribuição por estado
        state_distribution = _analyze_state_distribution(crop_calendar, states_info)
        
        if state_distribution:
            df_states = pd.DataFrame(list(state_distribution.items()), 
                                   columns=['Estado', 'Culturas'])
            df_states = df_states.sort_values('Culturas', ascending=False).head(10)
            
            fig_states = px.bar(
                df_states,
                x='Estado',
                y='Culturas',
                title="Top 10 Estados - Diversidade de Culturas",
                labels={'Estado': 'Estado', 'Culturas': 'Número de Culturas'},
                color='Culturas',
                color_continuous_scale='Blues'
            )
            fig_states.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_states, use_container_width=True, key="state_distribution_chart")


def _aggregate_by_region(crop_calendar: dict, states_info: dict) -> dict[str, int]:
    """Agrega dados por região brasileira."""
    regional_data = {}
    
    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue
            
        for state_entry in crop_data:
            state_code = state_entry.get('state_code', '')
            region = states_info.get(state_code, {}).get('region', 'Desconhecida')
            
            if region not in regional_data:
                regional_data[region] = set()
            
            # Verificar se há atividades no calendário
            calendar_data = state_entry.get('calendar', {})
            if any(activity for activity in calendar_data.values() if activity):
                regional_data[region].add(crop_name)
    
    # Converter sets para contagem
    return {region: len(crops) for region, crops in regional_data.items() if crops}


def _extract_seasonal_data(crop_calendar: dict) -> dict:
    """Extrai dados sazonais de atividades."""
    seasonal_data = {}
    
    # Mapeamento de meses em inglês para português abreviado
    month_mapping = {
        'January': 'Jan', 'February': 'Fev', 'March': 'Mar', 'April': 'Abr',
        'May': 'Mai', 'June': 'Jun', 'July': 'Jul', 'August': 'Ago',
        'September': 'Set', 'October': 'Out', 'November': 'Nov', 'December': 'Dez'
    }
    
    for _crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue
            
        for state_entry in crop_data:
            calendar_data = state_entry.get('calendar', {})
            
            for month, activity in calendar_data.items():
                if activity and month in month_mapping:
                    month_short = month_mapping[month]
                    
                    if month_short not in seasonal_data:
                        seasonal_data[month_short] = {'P': 0, 'H': 0, 'PH': 0}
                    
                    if activity in ['P', 'H', 'PH']:
                        seasonal_data[month_short][activity] += 1
    
    return seasonal_data


def _analyze_multiple_harvests(crop_calendar: dict) -> dict[str, int]:
    """Analisa culturas com múltiplas safras."""
    harvest_counts = {}
    
    for crop_name in crop_calendar:
        if '(' in crop_name and ('harvest' in crop_name.lower() or 'safra' in crop_name.lower()):
            base_crop = crop_name.split('(')[0].strip()
            
            if base_crop not in harvest_counts:
                harvest_counts[base_crop] = 0
            
            harvest_counts[base_crop] += 1
    
    return {crop: count for crop, count in harvest_counts.items() if count > 1}


def _analyze_state_distribution(crop_calendar: dict, states_info: dict) -> dict[str, int]:
    """Analisa distribuição de culturas por estado."""
    state_distribution = {}
    
    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue
            
        for state_entry in crop_data:
            state_code = state_entry.get('state_code', '')
            state_name = states_info.get(state_code, {}).get('name', state_code)
            
            # Verificar se há atividades no calendário
            calendar_data = state_entry.get('calendar', {})
            if any(activity for activity in calendar_data.values() if activity):
                if state_name not in state_distribution:
                    state_distribution[state_name] = set()
                state_distribution[state_name].add(crop_name)
    
    # Converter sets para contagem
    return {state: len(crops) for state, crops in state_distribution.items() if crops}
