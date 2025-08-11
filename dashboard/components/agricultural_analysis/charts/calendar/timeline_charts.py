"""
Timeline Charts Module
=====================

Module for creating timeline and seasonality charts for agricultural calendar.
Includes temporal activity charts, monthly timeline and crop seasonality.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional, Union


def create_timeline_activities_chart(calendar_data: Dict) -> Optional[go.Figure]:
    """
    Criar gráfico de timeline das atividades agrícolas.
    
    Parameters:
    -----------
    calendar_data : Dict
        Dados do calendário agrícola
        
    Returns:
    --------
    Optional[go.Figure]
        Figura do Plotly ou None se dados insuficientes
    """
    if not calendar_data:
        return None
    
    try:
        # Lista para armazenar dados do timeline
        timeline_data = []
        
        # Verificar se temos dados do calendário
        crop_calendar = calendar_data.get('crop_calendar', calendar_data)
        if not crop_calendar:
            return None
        
        # Mapeamento de meses inglês para índice
        month_en_to_index = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        month_names_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        for crop, crop_info in crop_calendar.items():
            if isinstance(crop_info, list):
                # Estrutura CONAB: lista de estados com calendários
                for state_entry in crop_info:
                    if isinstance(state_entry, dict) and 'calendar' in state_entry:
                        state_name = state_entry.get('state_name', 'Unknown')
                        calendar = state_entry['calendar']
                        
                        for month_en, activity in calendar.items():
                            if activity and activity.strip():
                                month_idx = month_en_to_index.get(month_en, 0)
                                if month_idx > 0:
                                    # Determinar tipo de atividade
                                    activity_type = 'Plantio' if 'P' in activity else ('Colheita' if 'H' in activity else 'Outra')
                                    
                                    timeline_data.append({
                                        'Cultura': crop,
                                        'Estado': state_name,
                                        'Atividade': activity_type,
                                        'Mês': month_idx,
                                        'Mês_Nome': month_names_pt[month_idx],
                                        'Código_Atividade': activity
                                    })
            elif isinstance(crop_info, dict):
                # Estrutura IBGE: dict de estados
                for state, activities in crop_info.items():
                    if isinstance(activities, dict):
                        for activity, months in activities.items():
                            if isinstance(months, list):
                                for month in months:
                                    if isinstance(month, int) and 1 <= month <= 12:
                                        timeline_data.append({
                                            'Cultura': crop,
                                            'Estado': state,
                                            'Atividade': activity,
                                            'Mês': month,
                                            'Mês_Nome': month_names_pt[month]
                                        })
        
        if not timeline_data:
            return None
        
        # Converter para DataFrame
        df = pd.DataFrame(timeline_data)
        
        # Criar gráfico de linha temporal com pontos e linhas
        fig = go.Figure()
        
        # Cores para diferentes atividades
        activity_colors = {
            'Plantio': '#2E8B57',
            'Colheita': '#FF6B35',
            'plantio': '#2E8B57',
            'colheita': '#FF6B35',
            'preparo': '#4682B4',
            'manejo': '#DAA520',
            'Outra': '#9370DB'
        }
        
        # Agrupar por cultura e criar linhas
        for crop in df['Cultura'].unique():
            crop_data = df[df['Cultura'] == crop]
            
            # Contar atividades por mês
            monthly_count = crop_data.groupby('Mês').size().reset_index(name='count')
            monthly_count['Mês_Nome'] = monthly_count['Mês'].map(month_names_pt)
            monthly_count = monthly_count.sort_values('Mês')
            
            # Adicionar linha para a cultura
            fig.add_trace(go.Scatter(
                x=monthly_count['Mês'],
                y=monthly_count['count'],
                mode='lines+markers',
                name=crop,
                line=dict(width=2),
                marker=dict(size=8),
                hovertemplate=f"<b>{crop}</b><br>Mês: %{{customdata}}<br>Atividades: %{{y}}<extra></extra>",
                customdata=monthly_count['Mês_Nome']
            ))
        
        # Personalizar layout
        fig.update_layout(
            title="📅 Timeline de Atividades Agrícolas",
            xaxis_title="Mês",
            yaxis_title="Número de Atividades",
            height=500,
            hovermode='x unified',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=list(month_names_pt.values()),
                tickangle=-45
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao criar timeline: {str(e)}")
        return None


def create_monthly_activities_timeline_chart(calendar_data: Dict) -> Optional[go.Figure]:
    """
    Criar gráfico de timeline mensal das atividades.

    Parameters:
    -----------
    calendar_data : Dict
        Dados do calendário agrícola

    Returns:
    --------
    Optional[go.Figure]
        Figura do Plotly ou None se dados insuficientes
    """
    if not calendar_data:
        return None

    try:
        # Matriz mensal de atividades
        monthly_matrix = {}

        for crop, crop_info in calendar_data.items():
            if isinstance(crop_info, str):
                continue

            monthly_matrix[crop] = {month: [] for month in range(1, 13)}

            # Handle both dict and list structures
            if isinstance(crop_info, dict):
                # Dict format: crop -> state -> activities
                for state, activities in crop_info.items():
                    if isinstance(activities, dict):
                        for activity, months in activities.items():
                            if isinstance(months, list):
                                for month in months:
                                    if 1 <= month <= 12:
                                        monthly_matrix[crop][month].append(activity)
            elif isinstance(crop_info, list):
                # List format: crop -> [state_entries]
                for entry in crop_info:
                    if isinstance(entry, dict):
                        activities = entry.get('atividades', {})
                        if isinstance(activities, dict):
                            for activity, months in activities.items():
                                if isinstance(months, list):
                                    for month in months:
                                        if 1 <= month <= 12:
                                            monthly_matrix[crop][month].append(activity)

        if not monthly_matrix:
            return None

        # Criar subplots para cada mês
        fig = make_subplots(
            rows=3, cols=4,
            subplot_titles=[_get_month_name(i) for i in range(1, 13)],
            specs=[[{"type": "bar"}] * 4 for _ in range(3)]
        )

        # Precompute color palette for performance and visual consistency
        viridis_colors = px.colors.sequential.Viridis
        viridis_len = len(viridis_colors)

        for month in range(1, 13):
            row = (month - 1) // 4 + 1
            col = (month - 1) % 4 + 1

            # Contar atividades por cultura para este mês
            month_data = []
            for crop, months_data in monthly_matrix.items():
                activity_count = len(months_data[month])
                if activity_count > 0:
                    month_data.append({
                        'Cultura': crop,
                        'Atividades': activity_count
                    })

            if month_data:
                df_month = pd.DataFrame(month_data)

                fig.add_trace(
                    go.Bar(
                        x=df_month['Cultura'],
                        y=df_month['Atividades'],
                        name=_get_month_name(month),
                        showlegend=False,
                        marker_color=viridis_colors[(month - 1) % viridis_len]
                    ),
                    row=row, col=col
                )

        # Configurar layout
        fig.update_layout(
            title="Timeline Mensal de Atividades por Cultura",
            height=800,
            margin=dict(t=80, l=40, r=40, b=40),
            showlegend=False,
            bargap=0.2
        )

        # Optimize axis for readability
        for i in range(1, 13):
            fig.update_xaxes(
                tickangle=-45,
                row=(i - 1) // 4 + 1,
                col=(i - 1) % 4 + 1
            )

        return fig

    except Exception as e:
        st.error(f"Erro ao criar timeline mensal: {str(e)}")
        return None


def create_main_crops_seasonality_chart(calendar_data: Dict) -> Optional[go.Figure]:
    """
    Criar gráfico polar de sazonalidade das principais culturas.
    
    Parameters:
    -----------
    calendar_data : Dict
        Dados do calendário agrícola
        
    Returns:
    --------
    Optional[go.Figure]
        Figura do Plotly ou None se dados insuficientes
    """
    if not calendar_data:
        return None
    
    try:
        # Calcular intensidade de atividades por mês para cada cultura
        seasonality_data = {}
        
        for crop, crop_info in calendar_data.items():
            if isinstance(crop_info, str):
                continue
                
            monthly_intensity = [0] * 12  # 12 meses
            
            # Handle both dict and list structures
            if isinstance(crop_info, dict):
                # Dict format: crop -> state -> activities
                for state, activities in crop_info.items():
                    if isinstance(activities, dict):
                        for activity, months in activities.items():
                            if isinstance(months, list):
                                for month in months:
                                    if 1 <= month <= 12:
                                        monthly_intensity[month - 1] += 1
            elif isinstance(crop_info, list):
                # List format: crop -> [state_entries]
                for entry in crop_info:
                    if isinstance(entry, dict):
                        activities = entry.get('atividades', {})
                        if isinstance(activities, dict):
                            for activity, months in activities.items():
                                if isinstance(months, list):
                                    for month in months:
                                        if 1 <= month <= 12:
                                            monthly_intensity[month - 1] += 1
            
            # Só incluir culturas com atividades
            if sum(monthly_intensity) > 0:
                seasonality_data[crop] = monthly_intensity
        
        if not seasonality_data:
            return None
        
        # Criar gráfico polar
        fig = go.Figure()
        
        # Meses como ângulos (0-360°)
        months = [_get_month_name(i) for i in range(1, 13)]
        angles = list(range(0, 360, 30))  # 30° por mês
        
        # Cores para diferentes culturas
        colors = px.colors.qualitative.Set3
        
        for i, (crop, intensity) in enumerate(seasonality_data.items()):
            # Adicionar primeiro ponto no final para fechar o círculo
            intensity_closed = intensity + [intensity[0]]
            angles_closed = angles + [360]
            
            fig.add_trace(go.Scatterpolar(
                r=intensity_closed,
                theta=angles_closed,
                fill='toself',
                name=crop,
                line_color=colors[i % len(colors)],
                fillcolor=colors[i % len(colors)],
                opacity=0.6
            ))
        
        # Configurar layout polar
        fig.update_layout(
            title="Sazonalidade das Principais Culturas",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(intensity) for intensity in seasonality_data.values()) + 1]
                ),
                angularaxis=dict(
                    tickmode='array',
                    tickvals=angles,
                    ticktext=months,
                    direction='clockwise',
                    period=360
                )
            ),
            height=600,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de sazonalidade: {str(e)}")
        return None


def _get_month_name(month_num: int) -> str:
    """
    Converter número do mês para nome.
    
    Parameters:
    -----------
    month_num : int
        Número do mês (1-12)
        
    Returns:
    --------
    str
        Nome do mês
    """
    months = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    return months.get(month_num, f'M{month_num}')
