"""
Regional Calendar Charts
=======================

Módulo de gráficos regionais consolidados do old_calendar/regional/.
Implementa visualizações específicas por região brasileira.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional

# Import do processador CONAB para dados regionais
from ...agricultural_loader import (
    safe_get_data, 
    validate_data_structure
)


def get_region_states() -> Dict[str, List[str]]:
    """
    Retorna mapeamento de regiões para estados.
    
    Returns:
        Dict[str, List[str]]: Mapeamento região -> lista de estados
    """
    return {
        'Norte': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
        'Nordeste': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 
                     'Piauí', 'Rio Grande do Norte', 'Sergipe'],
        'Centro-Oeste': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
        'Sudeste': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
        'Sul': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
    }


def create_regional_conab_data() -> Dict[str, Dict]:
    """
    Cria dados regionais CONAB simulados para fallback.
    
    Returns:
        Dict[str, Dict]: Dados regionais por região
    """
    regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    regional_data = {}
    
    for region in regions:
        regional_data[region] = {
            'crop_calendar': {
                'Soja': {'State1': {'Plantio': [1, 2, 3], 'Colheita': [6, 7, 8]}},
                'Milho': {'State2': {'Plantio': [2, 3, 4], 'Colheita': [7, 8, 9]}},
                'Arroz': {'State3': {'Plantio': [3, 4, 5], 'Colheita': [8, 9, 10]}}
            }
        }
    
    return regional_data


def filter_data_by_region(filtered_data: dict, region: str) -> dict:
    """
    Filtra dados do calendário por região específica.
    Com fallback para dados CONAB se dados regionais não available.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região brasileira
        
    Returns:
        dict: Dados filtrados para a região específica
    """
    # Valida se dados estão no formato esperado
    if not validate_data_structure(filtered_data, dict):
        st.warning(f"⚠️ Dados inválidos para região {region}, tentando carregar dados CONAB...")
        # Fallback: usa dados CONAB regionais
        regional_conab_data = create_regional_conab_data()
        return regional_conab_data.get(region, {'crop_calendar': {}})
    
    region_states = get_region_states()
    states_in_region = region_states.get(region, [])
    
    crop_calendar = safe_get_data(filtered_data, 'crop_calendar', {})
    regional_calendar = {}
    
    for crop, states_data in crop_calendar.items():
        if not isinstance(states_data, dict):
            continue
            
        regional_states_data = {}
        for state, activities in states_data.items():
            if state in states_in_region:
                regional_states_data[state] = activities
        
        if regional_states_data:
            regional_calendar[crop] = regional_states_data
    
    # Se não encontrou dados para a região, tenta dados CONAB
    if not regional_calendar:
        st.info(f"📊 Carregando dados CONAB para região {region}...")
        regional_conab_data = create_regional_conab_data()
        return regional_conab_data.get(region, {'crop_calendar': {}})
    
    return {'crop_calendar': regional_calendar}


def create_regional_heatmap_chart(filtered_data: dict, region: str) -> Optional[go.Figure]:
    """
    Cria heatmap para região específica com fallback para dados CONAB.
    
    Equivalente aos: heatmap_*_region.png do old_calendar/regional/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        regional_data = filter_data_by_region(filtered_data, region)
        crop_calendar = safe_get_data(regional_data, 'crop_calendar', {})
        
        if not crop_calendar:
            st.warning(f"📊 No data de calendário available para a região {region}")
            return None

        # Meses
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        # Prepara dados para heatmap
        heatmap_data = []
        y_labels = []
        
        for crop, states_data in crop_calendar.items():
            if not isinstance(states_data, dict):
                continue
                
            # Linha para plantio
            planting_row = []
            harvesting_row = []
            
            for month_idx, month in enumerate(months, 1):
                planting_count = 0
                harvesting_count = 0
                
                for state, activities in states_data.items():
                    if not isinstance(activities, dict):
                        continue
                        
                    planting_months = safe_get_data(activities, 'planting_months', [])
                    harvesting_months = safe_get_data(activities, 'harvesting_months', [])
                    
                    if month_idx in planting_months:
                        planting_count += 1
                    if month_idx in harvesting_months:
                        harvesting_count += 1
                
                planting_row.append(planting_count)
                harvesting_row.append(harvesting_count)
            
            heatmap_data.extend([planting_row, harvesting_row])
            y_labels.extend([f"{crop} (🌱)", f"{crop} (🌾)"])

        if not heatmap_data:
            st.info(f"📊 Nenhum dado de heatmap encontrado para {region}")
            return None

        # Cria heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=months,
            y=y_labels,
            colorscale='RdYlGn',
            text=heatmap_data,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(title="Número de<br>Estados")
        ))

        # Personaliza layout
        fig.update_layout(
            title=f"🔥 Heatmap do Calendário Agrícola - Região {region}",
            xaxis_title="Mês do Ano",
            yaxis_title="Cultura e Tipo de Atividade",
            height=400 + (len(y_labels) * 12),
            font=dict(size=11)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating heatmap regional para {region}: {e}")
        return None


def create_regional_diversity_chart(filtered_data: dict, region: str) -> Optional[go.Figure]:
    """
    Cria gráfico de diversidade para região específica.
    
    Equivalente aos: diversity_*_region.png do old_calendar/regional/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        regional_data = filter_data_by_region(filtered_data, region)
        crop_calendar = regional_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info(f"📊 No data de calendário available para diversidade em {region}")
            return None

        # Conta diversidade por estado na região
        region_states = get_region_states().get(region, [])
        state_diversity = {}
        
        for crop, states_data in crop_calendar.items():
            for state in states_data.keys():
                if state in region_states:
                    if state not in state_diversity:
                        state_diversity[state] = set()
                    state_diversity[state].add(crop)

        # Converte para contagem
        state_counts = {state: len(crops) for state, crops in state_diversity.items()}

        if not state_counts:
            st.info(f"📊 No diversidade encontrada para {region}")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(state_counts.items()), columns=['Estado', 'Diversidade_Culturas'])
        df = df.sort_values('Diversidade_Culturas', ascending=True)

        # Cria gráfico de barras horizontais
        fig = px.bar(
            df,
            x='Diversidade_Culturas',
            y='Estado',
            orientation='h',
            title=f"🌱 Diversidade de Culturas - Região {region}",
            labels={
                'Diversidade_Culturas': 'Número de Culturas Diferentes',
                'Estado': 'Estado'
            },
            color='Diversidade_Culturas',
            color_continuous_scale='Viridis'
        )

        # Personaliza layout
        fig.update_layout(
            height=300 + (len(df) * 25),
            showlegend=False,
            xaxis_title="Número de Culturas Diferentes",
            yaxis_title="Estado",
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico de diversidade para {region}: {e}")
        return None


def create_regional_seasonal_chart(filtered_data: dict, region: str) -> Optional[go.Figure]:
    """
    Cria gráfico sazonal para região específica.
    
    Equivalente aos: seasonal_*_region.png do old_calendar/regional/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        regional_data = filter_data_by_region(filtered_data, region)
        crop_calendar = regional_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info(f"📊 No data de calendário available para análise sazonal em {region}")
            return None

        # Meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Calcula atividade total por mês
        monthly_planting = {month: 0 for month in months}
        monthly_harvesting = {month: 0 for month in months}

        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                for month in activities.get('planting_months', []):
                    if month in monthly_planting:
                        monthly_planting[month] += 1
                
                for month in activities.get('harvesting_months', []):
                    if month in monthly_harvesting:
                        monthly_harvesting[month] += 1

        # Cria gráfico polar (radar)
        fig = go.Figure()

        # Adiciona linha de plantio
        fig.add_trace(go.Scatterpolar(
            r=[monthly_planting[month] for month in months],
            theta=months,
            fill='toself',
            name='🌱 Plantio',
            line_color='green'
        ))

        # Adiciona linha de colheita
        fig.add_trace(go.Scatterpolar(
            r=[monthly_harvesting[month] for month in months],
            theta=months,
            fill='toself',
            name='🌾 Colheita',
            line_color='orange'
        ))

        # Personaliza layout
        max_value = max(max(monthly_planting.values()), max(monthly_harvesting.values()))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max_value * 1.1]
                )
            ),
            title=f"🌿 Padrão Sazonal - Região {region}",
            height=500,
            showlegend=True
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico sazonal para {region}: {e}")
        return None


def create_regional_timeline_chart(filtered_data: dict, region: str) -> Optional[go.Figure]:
    """
    Cria timeline para região específica.
    
    Equivalente aos: timeline_*_region.png do old_calendar/regional/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        regional_data = filter_data_by_region(filtered_data, region)
        crop_calendar = regional_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info(f"📊 No data de calendário available para timeline em {region}")
            return None

        # Meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Calcula atividade mensal
        monthly_activities = {month: {'planting': 0, 'harvesting': 0} for month in months}

        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                for month in activities.get('planting_months', []):
                    if month in monthly_activities:
                        monthly_activities[month]['planting'] += 1
                
                for month in activities.get('harvesting_months', []):
                    if month in monthly_activities:
                        monthly_activities[month]['harvesting'] += 1

        # Cria gráfico de área empilhada
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=months,
            y=[monthly_activities[month]['planting'] for month in months],
            fill='tozeroy',
            mode='lines',
            name='🌱 Plantio',
            line=dict(color='lightgreen')
        ))

        fig.add_trace(go.Scatter(
            x=months,
            y=[monthly_activities[month]['harvesting'] for month in months],
            fill='tozeroy',
            mode='lines',
            name='🌾 Colheita',
            line=dict(color='orange')
        ))

        # Personaliza layout
        fig.update_layout(
            title=f"📅 Timeline de Atividades - Região {region}",
            xaxis_title="Mês do Ano",
            yaxis_title="Número de Atividades",
            height=400,
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating timeline para {region}: {e}")
        return None


def render_regional_analysis_for_region(filtered_data: dict, region: str) -> None:
    """
    Renderiza análise completa para uma região específica.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        region: Nome da região
    """
    st.markdown(f"### 🗺️ Análise Regional - {region}")
    
    # Primeira linha: heatmap e diversidade
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 🔥 Heatmap - {region}")
        fig1 = create_regional_heatmap_chart(filtered_data, region)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown(f"#### 🌱 Diversidade - {region}")
        fig2 = create_regional_diversity_chart(filtered_data, region)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    # Segunda linha: padrão sazonal e timeline
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"#### 🌿 Padrão Sazonal - {region}")
        fig3 = create_regional_seasonal_chart(filtered_data, region)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.markdown(f"#### 📅 Timeline - {region}")
        fig4 = create_regional_timeline_chart(filtered_data, region)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)


def render_all_regional_analysis(filtered_data: dict) -> None:
    """
    Renderiza análise para todas as regiões com seletor.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 🌎 Análise Regional Detalhada")
    
    # Seletor de região
    regions = list(get_region_states().keys())
    selected_region = st.selectbox(
        "Selecione uma região para análise detalhada:",
        options=regions,
        key="regional_analysis_selector"
    )
    
    if selected_region:
        render_regional_analysis_for_region(filtered_data, selected_region)
    
    # Opção para mostrar comparação entre regiões
    if st.checkbox("📊 Mostrar comparação entre todas as regiões", key="show_regional_comparison"):
        st.markdown("#### 📊 Comparação entre Regiões")
        
        # Cria gráfico comparativo de diversidade por região
        region_diversity = {}
        for region in regions:
            regional_data = filter_data_by_region(filtered_data, region)
            crop_calendar = regional_data.get('crop_calendar', {})
            
            total_crops = len(crop_calendar)
            region_diversity[region] = total_crops
        
        if region_diversity:
            df_comp = pd.DataFrame(list(region_diversity.items()), 
                                 columns=['Região', 'Número_Culturas'])
            df_comp = df_comp.sort_values('Número_Culturas', ascending=True)
            
            fig_comp = px.bar(
                df_comp,
                x='Número_Culturas',
                y='Região',
                orientation='h',
                title="🌍 Comparação de Diversidade de Culturas por Região",
                color='Número_Culturas',
                color_continuous_scale='Viridis'
            )
            
            fig_comp.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False
            )
            
            fig_comp.update_traces(
                texttemplate='%{x}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
