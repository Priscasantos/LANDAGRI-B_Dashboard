"""
Timeline Charts
==============

Módulo de gráficos de timeline consolidados do old_calendar.
Implementa visualizações de linha do tempo para atividades agrícolas.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional


def create_timeline_activities_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria timeline de atividades agrícolas.
    
    Equivalente ao: timeline_atividades_agricolas.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para timeline")
            return None

        # Prepara dados para timeline
        timeline_data = []
        
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                # Adiciona períodos de plantio
                planting_months = activities.get('planting_months', [])
                if planting_months:
                    start_month = min(planting_months, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x))
                    end_month = max(planting_months, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x))
                    
                    timeline_data.append({
                        'Cultura': crop,
                        'Estado': state,
                        'Atividade': 'Plantio',
                        'Início': start_month,
                        'Fim': end_month,
                        'Tipo': f"{crop} - {state} (🌱)"
                    })
                
                # Adiciona períodos de colheita
                harvesting_months = activities.get('harvesting_months', [])
                if harvesting_months:
                    start_month = min(harvesting_months, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x))
                    end_month = max(harvesting_months, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x))
                    
                    timeline_data.append({
                        'Cultura': crop,
                        'Estado': state,
                        'Atividade': 'Colheita',
                        'Início': start_month,
                        'Fim': end_month,
                        'Tipo': f"{crop} - {state} (🌾)"
                    })

        if not timeline_data:
            st.info("📊 Nenhum dado de timeline encontrado")
            return None

        # Converte para DataFrame
        df = pd.DataFrame(timeline_data)

        # Mapeia meses para números para ordenação
        month_to_num = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        df['Início_Num'] = df['Início'].map(month_to_num)
        df['Fim_Num'] = df['Fim'].map(month_to_num)

        # Cria gráfico Gantt-like
        fig = px.timeline(
            df,
            x_start='Início',
            x_end='Fim',
            y='Tipo',
            color='Atividade',
            title="📅 Timeline de Atividades Agrícolas",
            color_discrete_map={
                'Plantio': 'lightgreen',
                'Colheita': 'orange'
            }
        )

        # Personaliza layout
        fig.update_layout(
            height=400 + (len(df) * 15),
            xaxis_title="Período do Ano",
            yaxis_title="Cultura - Estado (Atividade)",
            showlegend=True
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar timeline de atividades: {e}")
        return None


def create_monthly_activities_timeline_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria timeline de atividades mensais condensado.
    
    Equivalente ao: atividades_mensais.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para timeline mensal")
            return None

        # Meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Prepara dados agregados por mês
        monthly_planting = {month: 0 for month in months}
        monthly_harvesting = {month: 0 for month in months}

        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                # Conta plantio
                for month in activities.get('planting_months', []):
                    if month in monthly_planting:
                        monthly_planting[month] += 1
                
                # Conta colheita
                for month in activities.get('harvesting_months', []):
                    if month in monthly_harvesting:
                        monthly_harvesting[month] += 1

        # Cria subplots para mostrar ambas as atividades
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['🌱 Atividades de Plantio por Mês', '🌾 Atividades de Colheita por Mês'],
            vertical_spacing=0.15
        )

        # Adiciona gráfico de plantio
        fig.add_trace(
            go.Bar(
                x=months,
                y=[monthly_planting[month] for month in months],
                name='Plantio',
                marker_color='lightgreen',
                text=[monthly_planting[month] for month in months],
                textposition='outside'
            ),
            row=1, col=1
        )

        # Adiciona gráfico de colheita
        fig.add_trace(
            go.Bar(
                x=months,
                y=[monthly_harvesting[month] for month in months],
                name='Colheita',
                marker_color='orange',
                text=[monthly_harvesting[month] for month in months],
                textposition='outside'
            ),
            row=2, col=1
        )

        # Personaliza layout
        fig.update_layout(
            title="📊 Timeline Mensal de Atividades Agrícolas",
            height=600,
            showlegend=False
        )

        # Atualiza eixos
        fig.update_xaxes(title_text="Mês do Ano", row=2, col=1)
        fig.update_yaxes(title_text="Número de Atividades", row=1, col=1)
        fig.update_yaxes(title_text="Número de Atividades", row=2, col=1)

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar timeline mensal: {e}")
        return None


def create_main_crops_seasonality_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de sazonalidade das principais culturas.
    
    Equivalente ao: sazonalidade_culturas_principais.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para sazonalidade")
            return None

        # Identifica principais culturas (por número de estados)
        crop_coverage = {}
        for crop, states_data in crop_calendar.items():
            crop_coverage[crop] = len(states_data)

        # Pega top 6 culturas mais difundidas
        main_crops = sorted(crop_coverage.items(), key=lambda x: x[1], reverse=True)[:6]
        main_crop_names = [crop[0] for crop in main_crops]

        # Meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Cria gráfico de radar para cada cultura principal
        fig = go.Figure()

        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

        for i, crop in enumerate(main_crop_names):
            if crop not in crop_calendar:
                continue
            
            # Calcula atividade total por mês para esta cultura
            monthly_activity = {month: 0 for month in months}
            
            states_data = crop_calendar[crop]
            for state, activities in states_data.items():
                for month in activities.get('planting_months', []):
                    if month in monthly_activity:
                        monthly_activity[month] += 1
                for month in activities.get('harvesting_months', []):
                    if month in monthly_activity:
                        monthly_activity[month] += 1

            # Adiciona linha para esta cultura
            values = [monthly_activity[month] for month in months]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=months,
                fill='toself',
                name=crop,
                line_color=colors[i % len(colors)]
            ))

        # Personaliza layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([max([monthly_activity[month] for month in months]) 
                                  for crop in main_crop_names 
                                  if crop in crop_calendar 
                                  for monthly_activity in [
                                      {month: sum(1 for state, activities in crop_calendar[crop].items() 
                                                 if month in activities.get('planting_months', []) + activities.get('harvesting_months', []))
                                       for month in months}
                                  ]])]
                )
            ),
            title="🌟 Sazonalidade das Principais Culturas",
            height=600,
            showlegend=True
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de sazonalidade: {e}")
        return None


def render_timeline_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de timeline.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### ⏰ Timeline e Sazonalidade")
    
    # Primeira linha: timeline principal
    st.markdown("#### 📅 Timeline de Atividades")
    fig1 = create_timeline_activities_chart(filtered_data)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)
    
    # Segunda linha: timeline mensal e sazonalidade
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Atividades Mensais")
        fig2 = create_monthly_activities_timeline_chart(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌟 Sazonalidade Principal")
        fig3 = create_main_crops_seasonality_chart(filtered_data)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
