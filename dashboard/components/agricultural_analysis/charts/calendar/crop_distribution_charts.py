"""
Crop Distribution Charts
=======================

Módulo de gráficos de distribuição de culturas consolidados do old_calendar.
Implementa visualizações para análise de distribuição geográfica e diversidade de culturas.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional


def create_crop_type_distribution_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de distribuição de tipos de cultura.
    
    Equivalente ao: crop_type_distribution.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para distribuição de tipos de cultura")
            return None

        # Conta tipos de cultura por região/estado
        crop_counts = {}
        for crop, states_data in crop_calendar.items():
            crop_counts[crop] = len(states_data)

        if not crop_counts:
            st.info("📊 Nenhum tipo de cultura encontrado nos dados")
            return None

        # Cria DataFrame para visualização
        df = pd.DataFrame(list(crop_counts.items()), columns=['Cultura', 'Número_Estados'])
        df = df.sort_values('Número_Estados', ascending=True)

        # Cria gráfico de barras horizontais
        fig = px.bar(
            df, 
            x='Número_Estados', 
            y='Cultura',
            orientation='h',
            title="🌾 Distribuição de Tipos de Cultura por Estados",
            labels={
                'Número_Estados': 'Número de Estados', 
                'Cultura': 'Tipo de Cultura'
            },
            color='Número_Estados',
            color_continuous_scale='Viridis'
        )

        # Personaliza layout
        fig.update_layout(
            height=400 + (len(df) * 15),  # Altura dinâmica baseada no número de culturas
            showlegend=False,
            xaxis_title="Número de Estados",
            yaxis_title="Tipo de Cultura",
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de distribuição de tipos de cultura: {e}")
        return None


def create_crop_diversity_by_region_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de diversidade de culturas por região.
    
    Equivalente ao: crop_diversity_by_region.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para diversidade por região")
            return None

        # Mapeia estados para regiões brasileiras
        state_to_region = {
            'Acre': 'Norte', 'Amapá': 'Norte', 'Amazonas': 'Norte', 'Pará': 'Norte',
            'Rondônia': 'Norte', 'Roraima': 'Norte', 'Tocantins': 'Norte',
            'Alagoas': 'Nordeste', 'Bahia': 'Nordeste', 'Ceará': 'Nordeste', 
            'Maranhão': 'Nordeste', 'Paraíba': 'Nordeste', 'Pernambuco': 'Nordeste',
            'Piauí': 'Nordeste', 'Rio Grande do Norte': 'Nordeste', 'Sergipe': 'Nordeste',
            'Distrito Federal': 'Centro-Oeste', 'Goiás': 'Centro-Oeste', 
            'Mato Grosso': 'Centro-Oeste', 'Mato Grosso do Sul': 'Centro-Oeste',
            'Espírito Santo': 'Sudeste', 'Minas Gerais': 'Sudeste', 
            'Rio de Janeiro': 'Sudeste', 'São Paulo': 'Sudeste',
            'Paraná': 'Sul', 'Rio Grande do Sul': 'Sul', 'Santa Catarina': 'Sul'
        }

        # Conta diversidade de culturas por região
        region_diversity = {}
        for crop, states_data in crop_calendar.items():
            for state in states_data.keys():
                region = state_to_region.get(state, 'Indefinido')
                if region not in region_diversity:
                    region_diversity[region] = set()
                region_diversity[region].add(crop)

        # Converte para contagem
        region_counts = {region: len(crops) for region, crops in region_diversity.items()}

        if not region_counts:
            st.info("📊 Nenhuma diversidade regional encontrada nos dados")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(region_counts.items()), columns=['Região', 'Diversidade_Culturas'])
        df = df.sort_values('Diversidade_Culturas', ascending=False)

        # Cria gráfico de barras
        fig = px.bar(
            df,
            x='Região',
            y='Diversidade_Culturas',
            title="🌱 Diversidade de Culturas por Região",
            labels={
                'Diversidade_Culturas': 'Número de Culturas Diferentes',
                'Região': 'Região Brasileira'
            },
            color='Diversidade_Culturas',
            color_continuous_scale='RdYlGn'
        )

        # Personaliza layout
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="Região Brasileira",
            yaxis_title="Número de Culturas Diferentes",
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de diversidade por região: {e}")
        return None


def create_number_of_crops_per_region_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico do número de culturas por região com detalhamento.
    
    Equivalente ao: number_of_crops_per_region.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para contagem por região")
            return None

        # Mapeia estados para regiões brasileiras
        state_to_region = {
            'Acre': 'Norte', 'Amapá': 'Norte', 'Amazonas': 'Norte', 'Pará': 'Norte',
            'Rondônia': 'Norte', 'Roraima': 'Norte', 'Tocantins': 'Norte',
            'Alagoas': 'Nordeste', 'Bahia': 'Nordeste', 'Ceará': 'Nordeste', 
            'Maranhão': 'Nordeste', 'Paraíba': 'Nordeste', 'Pernambuco': 'Nordeste',
            'Piauí': 'Nordeste', 'Rio Grande do Norte': 'Nordeste', 'Sergipe': 'Nordeste',
            'Distrito Federal': 'Centro-Oeste', 'Goiás': 'Centro-Oeste', 
            'Mato Grosso': 'Centro-Oeste', 'Mato Grosso do Sul': 'Centro-Oeste',
            'Espírito Santo': 'Sudeste', 'Minas Gerais': 'Sudeste', 
            'Rio de Janeiro': 'Sudeste', 'São Paulo': 'Sudeste',
            'Paraná': 'Sul', 'Rio Grande do Sul': 'Sul', 'Santa Catarina': 'Sul'
        }

        # Conta total de atividades por região
        region_activities = {}
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                region = state_to_region.get(state, 'Indefinido')
                if region not in region_activities:
                    region_activities[region] = 0
                # Conta plantio e colheita como atividades separadas
                if activities.get('planting_months'):
                    region_activities[region] += len(activities['planting_months'])
                if activities.get('harvesting_months'):
                    region_activities[region] += len(activities['harvesting_months'])

        if not region_activities:
            st.info("📊 Nenhuma atividade regional encontrada nos dados")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(region_activities.items()), columns=['Região', 'Total_Atividades'])
        df = df.sort_values('Total_Atividades', ascending=True)

        # Cria gráfico de barras horizontais
        fig = px.bar(
            df,
            x='Total_Atividades',
            y='Região',
            orientation='h',
            title="📈 Número Total de Atividades Agrícolas por Região",
            labels={
                'Total_Atividades': 'Total de Atividades (Plantio + Colheita)',
                'Região': 'Região Brasileira'
            },
            color='Total_Atividades',
            color_continuous_scale='Blues'
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Total de Atividades (Plantio + Colheita)",
            yaxis_title="Região Brasileira",
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de número de culturas por região: {e}")
        return None


def render_crop_distribution_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de distribuição de culturas.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 📊 Distribuição e Diversidade de Culturas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição de tipos de cultura
        fig1 = create_crop_type_distribution_chart(filtered_data)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de número de culturas por região
        fig3 = create_number_of_crops_per_region_chart(filtered_data)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Gráfico de diversidade por região
        fig2 = create_crop_diversity_by_region_chart(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
