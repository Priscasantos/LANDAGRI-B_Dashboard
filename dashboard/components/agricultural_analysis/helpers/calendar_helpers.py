"""
Agricultural Calendar Helpers
============================

Module with helper functions for processing and visualizing agricultural calendars.
Processes data from agricultural_data_complete.jsonc and generates correct visualizations.

Author: LANDAGRI-B Project Team 
Date: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Any


def extract_crop_calendar_data(agricultural_data: dict[str, Any]) -> pd.DataFrame:
    """
    Extracts and structures agricultural calendar data from agricultural_data.
    
    Args:
        agricultural_data: Data loaded from agricultural_data_complete.jsonc
        
    Returns:
        Structured DataFrame with calendar data
    """
    calendar_rows = []
    
    if 'crop_calendar' not in agricultural_data:
        st.warning("⚠️ Calendar data not found in crop_calendar")
        return pd.DataFrame()
    
    crop_calendar = agricultural_data['crop_calendar']
    
    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue
            
        for state_data in crop_data:
            if not isinstance(state_data, dict):
                continue
                
            state_code = state_data.get('state_code', 'N/A')
            state_name = state_data.get('state_name', 'N/A')
            region = state_data.get('region', 'N/A')
            calendar = state_data.get('calendar', {})
            
            # Process each month of the calendar
            for month, activity in calendar.items():
                if activity:  # Only add if there's activity
                    calendar_rows.append({
                        'crop': crop_name,
                        'state_code': state_code,
                        'state_name': state_name,
                        'region': region,
                        'month': month,
                        'activity': activity,
                        'activity_type': _get_activity_type(activity)
                    })
    
    if not calendar_rows:
        st.warning("⚠️ No calendar data processed")
        return pd.DataFrame()
        
    return pd.DataFrame(calendar_rows)


def _get_activity_type(activity: str) -> str:
    """
    Classifies activity type based on code.
    
    Args:
        activity: Activity code (P, H, PH, etc.)
        
    Returns:
        Activity type in English
    """
    activity = str(activity).upper().strip()
    
    if 'P' in activity and 'H' in activity:
        return 'Planting and Harvesting'
    elif 'P' in activity:
        return 'Planting'
    elif 'H' in activity:
        return 'Harvesting'
    else:
        return 'Other'


def get_month_order() -> list[str]:
    """Returns the correct order of months."""
    return [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]


def get_month_names_pt() -> dict[str, str]:
    """Mapping of English month names to Portuguese."""
    return {
        'January': 'Janeiro',
        'February': 'Fevereiro', 
        'March': 'Março',
        'April': 'Abril',
        'May': 'Maio',
        'June': 'Junho',
        'July': 'Julho',
        'August': 'Agosto',
        'September': 'Setembro',
        'October': 'Outubro',
        'November': 'Novembro',
        'December': 'Dezembro'
    }


def get_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates summary of activities by region.
    
    Args:
        df: DataFrame with calendar data
        
    Returns:
        DataFrame with regional summary
    """
    if df.empty:
        return pd.DataFrame()
        
    summary = df.groupby(['region', 'activity_type']).agg({
        'crop': 'nunique',
        'state_code': 'nunique'
    }).reset_index()
    
    summary.columns = ['region', 'activity_type', 'crops_count', 'states_count']
    
    return summary


def get_crop_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates summary of activities by crop.
    
    Args:
        df: DataFrame with calendar data
        
    Returns:
        DataFrame with summary by crop
    """
    if df.empty:
        return pd.DataFrame()
        
    summary = df.groupby(['crop', 'activity_type']).agg({
        'state_code': 'nunique',
        'region': 'nunique'
    }).reset_index()
    
    summary.columns = ['crop', 'activity_type', 'states_count', 'regions_count']
    
    return summary


def create_monthly_activity_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates monthly activities chart.
    
    Args:
        df: DataFrame com dados do calendário
        
    Returns:
        Figure do plotly
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado de atividade mensal encontrado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    # Traduzir meses para português
    month_names_pt = get_month_names_pt()
    df_plot = df.copy()
    df_plot['month_pt'] = df_plot['month'].map(month_names_pt)
    
    # Contar atividades por mês
    monthly_counts = df_plot.groupby(['month', 'month_pt', 'activity_type']).size().reset_index(name='count')
    
    # Ordenar por mês
    month_order = get_month_order()
    monthly_counts['month_order'] = monthly_counts['month'].map({m: i for i, m in enumerate(month_order)})
    monthly_counts = monthly_counts.sort_values('month_order')
    
    # Create chart
    fig = px.bar(
        monthly_counts,
        x='month_pt',
        y='count',
        color='activity_type',
        title='Distribution of Agricultural Activities by Month',
        labels={
            'month_pt': 'Month',
            'count': 'Number of Activities',
            'activity_type': 'Activity Type'
        },
        color_discrete_map={
            'Planting': '#2E7D32',
            'Harvesting': '#FF6F00',
            'Planting and Harvesting': '#1976D2',
            'Other': '#757575'
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=True
    )
    
    return fig


def create_regional_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates regional distribution chart of crops.
    
    Args:
        df: DataFrame with calendar data
        
    Returns:
        Plotly figure
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No regional distribution data found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    # Count crops by region
    regional_counts = df.groupby('region')['crop'].nunique().reset_index()
    regional_counts.columns = ['region', 'crops_count']
    regional_counts = regional_counts.sort_values('crops_count', ascending=True)
    
    fig = px.bar(
        regional_counts,
        x='crops_count',
        y='region',
        orientation='h',
        title='Diversidade de Culturas por Região',
        labels={
            'crops_count': 'Número de Culturas',
            'region': 'Região'
        },
        color='crops_count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_crop_calendar_heatmap(df: pd.DataFrame, crop: str | None = None) -> go.Figure:
    """
    Creates agricultural calendar heatmap.
    
    Args:
        df: DataFrame com dados do calendário
        crop: Cultura específica (opcional)
        
    Returns:
        Figure do plotly
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado encontrado para o heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    # Filtrar por cultura se especificado
    if crop:
        df_filtered = df[df['crop'] == crop].copy()
        title = f'Agricultural Calendar - {crop}'
    else:
        df_filtered = df.copy()
        title = 'National Agricultural Calendar'
    
    if df_filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Nenhum dado encontrado para {crop if crop else 'todas as culturas'}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    # Prepare data for heatmap
    month_names_pt = get_month_names_pt()
    df_filtered['month_pt'] = df_filtered['month'].map(month_names_pt)
    
    # Criar matriz de atividades
    if crop:
        pivot_data = df_filtered.groupby(['state_name', 'month_pt']).size().reset_index(name='count')
        pivot_table = pivot_data.pivot(index='state_name', columns='month_pt', values='count').fillna(0)
    else:
        pivot_data = df_filtered.groupby(['crop', 'month_pt']).size().reset_index(name='count')
        pivot_table = pivot_data.pivot(index='crop', columns='month_pt', values='count').fillna(0)
    
    # Ordenar colunas por mês
    month_order = get_month_order()
    month_order_pt = [month_names_pt[m] for m in month_order if month_names_pt[m] in pivot_table.columns]
    pivot_table = pivot_table.reindex(columns=month_order_pt)
    
    # Criar heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Viridis',
        colorbar=dict(title="Atividades")
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Mês',
        yaxis_title='Estado' if crop else 'Cultura',
        height=max(400, len(pivot_table.index) * 25)
    )
    
    return fig


def validate_calendar_data(agricultural_data: dict[str, Any]) -> dict[str, Any]:
    """
    Validates the quality of agricultural calendar data.
    
    Args:
        agricultural_data: Data loaded from file
        
    Returns:
        Dict com métricas de qualidade
    """
    validation = {
        'has_crop_calendar': False,
        'total_crops': 0,
        'total_states': 0,
        'total_regions': 0,
        'missing_data_percentage': 0.0,
        'data_completeness': 0.0,
        'issues': []
    }
    
    if 'crop_calendar' not in agricultural_data:
        validation['issues'].append("Campo 'crop_calendar' não encontrado")
        return validation
    
    validation['has_crop_calendar'] = True
    crop_calendar = agricultural_data['crop_calendar']
    
    states_set = set()
    regions_set = set()
    total_entries = 0
    missing_entries = 0
    
    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            validation['issues'].append(f"Data for {crop_name} is not a list")
            continue
            
        validation['total_crops'] += 1
        
        for state_data in crop_data:
            if not isinstance(state_data, dict):
                validation['issues'].append(f"Entrada inválida em {crop_name}")
                continue
                
            states_set.add(state_data.get('state_code', 'N/A'))
            regions_set.add(state_data.get('region', 'N/A'))
            
            calendar = state_data.get('calendar', {})
            for _month, activity in calendar.items():
                total_entries += 1
                if not activity or activity.strip() == '':
                    missing_entries += 1
    
    validation['total_states'] = len(states_set)
    validation['total_regions'] = len(regions_set)
    
    if total_entries > 0:
        validation['missing_data_percentage'] = (missing_entries / total_entries) * 100
        validation['data_completeness'] = ((total_entries - missing_entries) / total_entries) * 100
    
    return validation
