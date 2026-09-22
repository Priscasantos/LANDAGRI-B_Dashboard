"""
Seasonality Analysis Charts
==========================

Creates charts for analyzing seasonal patterns in agricultural activities.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, Dict, List
from ...agricultural_loader import safe_get_data


def create_seasonality_index_chart(filtered_data: dict, chart_key: str = "seasonality_analysis_chart") -> None:
    """
    Create seasonality index analysis chart.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
    chart_key : str, optional
        Unique key for the Streamlit chart component
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    try:
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar', {})
        
        if not crop_calendar:
            st.warning("⚠️ Insufficient data for seasonality analysis")
            return
            
        # Mapeamento de meses inglês -> português e inglês -> índice
        month_names_en = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        month_en_to_index = {
            'January': 0, 'February': 1, 'March': 2, 'April': 3,
            'May': 4, 'June': 5, 'July': 6, 'August': 7,
            'September': 8, 'October': 9, 'November': 10, 'December': 11
        }
        
        # Analisar padrões sazonais
        seasonal_data = {}
        
        for crop, crop_data in crop_calendar.items():
            monthly_activity = [0] * 12
            
            # Verificar se é estrutura CONAB (lista de estados) ou IBGE (dict)
            if isinstance(crop_data, list):
                # Estrutura CONAB: lista de estados com calendários
                for state_entry in crop_data:
                    if isinstance(state_entry, dict) and 'calendar' in state_entry:
                        calendar = state_entry['calendar']
                        for month_en, activity in calendar.items():
                            if month_en in month_en_to_index and activity and activity.strip():
                                month_idx = month_en_to_index[month_en]
                                monthly_activity[month_idx] += 1
            elif isinstance(crop_data, dict):
                # Estrutura IBGE: dict de estados
                for state, activities in crop_data.items():
                    if isinstance(activities, dict):
                        for activity, months_list in activities.items():
                            if isinstance(months_list, list):
                                for month in months_list:
                                    if isinstance(month, int) and 1 <= month <= 12:
                                        monthly_activity[month - 1] += 1
                                    elif isinstance(month, str) and month in month_en_to_index:
                                        month_idx = month_en_to_index[month]
                                        monthly_activity[month_idx] += 1
            
            seasonal_data[crop] = monthly_activity
        
        # Criar gráfico de sazonalidade
        fig = go.Figure()
        
        months = list(month_names_en.values())
        
        for crop, activity in seasonal_data.items():
            fig.add_trace(go.Scatter(
                x=months,
                y=activity,
                mode='lines+markers',
                name=crop,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Seasonality Analysis by Crop",
            xaxis_title="Months",
            yaxis_title="Activities Intensity",
            height=500,
            showlegend=True,
            hovermode='x unified',
            legend=dict(
            title={'text': 'Crop Type', 'font': {'size': 12}}
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
        
    except Exception as e:
        st.error(f"❌ Erro na análise de sazonalidade: {str(e)}")


def create_concentration_matrix(filtered_data: dict) -> None:
    """
    Create concentration matrix analysis chart.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    try:
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar', {})
        
        if not crop_calendar:
            st.warning("⚠️ Dados insuficientes para matriz de concentração")
            return
            
        # Calcular concentração por trimestre
        quarters = ['Q1 (Jan-Mar)', 'Q2 (Abr-Jun)', 'Q3 (Jul-Set)', 'Q4 (Out-Dez)']
        crops = list(crop_calendar.keys())
        concentration_matrix = []
        
        for crop in crops:
            crop_data = crop_calendar[crop]
            quarterly_activity = [0, 0, 0, 0]
            
            for state, activities in crop_data.items():
                if isinstance(activities, dict):
                    for activity, months_list in activities.items():
                        if isinstance(months_list, list):
                            for month in months_list:
                                if isinstance(month, int) and 1 <= month <= 12:
                                    quarter_index = (month - 1) // 3
                                    quarterly_activity[quarter_index] += 1
            
            concentration_matrix.append(quarterly_activity)
        
        # Criar matriz de concentração
        fig = go.Figure(data=go.Heatmap(
            z=concentration_matrix,
            x=quarters,
            y=crops,
            colorscale='Blues',
            colorbar=dict(title="Concentração de Atividade")
        ))
        
        fig.update_layout(
            title="📊 Matriz de Concentração Sazonal",
            height=max(400, len(crops) * 25),
            font=dict(size=11)
        )
        
        st.plotly_chart(fig, use_container_width=True, key="concentration_matrix_chart")
        
    except Exception as e:
        st.error(f"❌ Erro na matriz de concentração: {str(e)}")


def create_seasonal_waves_3d(filtered_data: dict) -> None:
    """
    Create 3D seasonal waves visualization.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    try:
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Dados insuficientes para visualização 3D")
            return
            
        # Simulação de visualização 3D (implementação básica)
        months = list(range(1, 13))
        crops = list(crop_calendar.keys())[:5]  # Limitar a 5 culturas para visualização
        
        fig = go.Figure()
        
        for i, crop in enumerate(crops):
            crop_data = crop_calendar[crop]
            monthly_activity = [0] * 12
            
            for state, activities in crop_data.items():
                if isinstance(activities, dict):
                    for activity, months_list in activities.items():
                        if isinstance(months_list, list):
                            for month in months_list:
                                if isinstance(month, int) and 1 <= month <= 12:
                                    monthly_activity[month - 1] += 1
            
            # Criar superfície 3D
            fig.add_trace(go.Scatter3d(
                x=[i] * 12,
                y=months,
                z=monthly_activity,
                mode='lines+markers',
                name=crop,
                line=dict(width=4),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title="🌊 Ondas Sazonais 3D - Atividade por Cultura",
            scene=dict(
                xaxis_title="Culturas",
                yaxis_title="Meses",
                zaxis_title="Intensidade"
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True, key="seasonal_waves_3d")
        
    except Exception as e:
        st.error(f"❌ Erro na visualização 3D: {str(e)}")


def create_polar_seasonality_analysis(filtered_data: dict, chart_key: str = "polar_seasonality_chart") -> None:
    """
    Create polar seasonality analysis chart showing agricultural activities throughout the year.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
    chart_key : str, optional
        Unique key for the Streamlit chart component
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    try:
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar', {})
        
        if not crop_calendar:
            st.warning("⚠️ Dados insuficientes para análise polar de sazonalidade")
            return
            
        # Extrair dados sazonais
        seasonal_data = _extract_seasonal_data(crop_calendar)
        
        if not seasonal_data:
            st.info("📊 Dados sazonais não disponíveis.")
            return
        
        # Meses em português
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig_polar = go.Figure()
        
        # Configuração de cores e nomes para atividades
        colors = {'P': '#2E8B57', 'H': '#FF6B35', 'PH': '#4682B4'}
        names = {'P': 'Planting', 'H': 'Harvest', 'PH': 'Planting/Harvest'}
        
        # Adicionar trace para cada tipo de atividade
        for activity_type in ['P', 'H', 'PH']:
            monthly_counts = [seasonal_data.get(month, {}).get(activity_type, 0) for month in months]
            
            if sum(monthly_counts) > 0:  # Só adicionar se houver dados
                fig_polar.add_trace(go.Scatterpolar(
                    r=monthly_counts,
                    theta=months,
                    fill='toself',
                    name=names[activity_type],
                    line_color=colors[activity_type],
                    opacity=0.7,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
        
        # Calcular valor máximo para escala
        max_value = max(
            max(seasonal_data.get(month, {}).values()) 
            for month in months
            if seasonal_data.get(month)
        ) if seasonal_data else 1
        
        fig_polar.update_layout(
            polar={
            'radialaxis': {
                'visible': True, 
                'range': [0, max_value],
                'tickfont': {'size': 12}
            },
            'angularaxis': {
                'tickfont': {'size': 12}
            }
            },
            showlegend=True,
            legend=dict(
            title={'text': 'Crop period', 'font': {'size': 12}},
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
            ),
            height=600,
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_polar, use_container_width=True, key=chart_key)
        
        # Add complementary information
        st.markdown("**Data Summary**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_planting = sum(seasonal_data.get(month, {}).get('P', 0) for month in months)
            st.metric("🌱 Total Planting", total_planting)

        with col2:
            total_harvest = sum(seasonal_data.get(month, {}).get('H', 0) for month in months)
            st.metric("🌾 Total Harvests", total_harvest)
            
        with col3:
            total_both = sum(seasonal_data.get(month, {}).get('PH', 0) for month in months)
            st.metric("🔄 Planting/Harvest", total_both)
        
    except Exception as e:
        st.error(f"❌ Erro na análise polar de sazonalidade: {str(e)}")


def _extract_seasonal_data(crop_calendar: dict) -> Dict[str, Dict[str, int]]:
    """
    Extract seasonal data from crop calendar for analysis.
    
    Parameters:
    -----------
    crop_calendar : dict
        Dictionary containing crop calendar data
        
    Returns:
    --------
    Dict[str, Dict[str, int]]
        Dictionary with months as keys and activity counts as values
    """
    try:
        # Mapeamento de meses
        month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        month_en_to_pt = {
            'January': 'Jan', 'February': 'Fev', 'March': 'Mar', 'April': 'Abr',
            'May': 'Mai', 'June': 'Jun', 'July': 'Jul', 'August': 'Ago',
            'September': 'Set', 'October': 'Out', 'November': 'Nov', 'December': 'Dez'
        }
        
        seasonal_data = {}
        
        # Inicializar dados sazonais
        for month in month_names:
            seasonal_data[month] = {'P': 0, 'H': 0, 'PH': 0}
        
        # Processar dados do calendário
        for crop, crop_data in crop_calendar.items():
            if isinstance(crop_data, list):
                # Estrutura CONAB: lista de estados com calendários
                for state_entry in crop_data:
                    if isinstance(state_entry, dict) and 'calendar' in state_entry:
                        calendar = state_entry['calendar']
                        for month_en, activity in calendar.items():
                            if month_en in month_en_to_pt and activity and activity.strip():
                                month_pt = month_en_to_pt[month_en]
                                activity_clean = activity.strip().upper()
                                
                                if activity_clean in ['P', 'H', 'PH']:
                                    seasonal_data[month_pt][activity_clean] += 1
                                elif 'P' in activity_clean and 'H' in activity_clean:
                                    seasonal_data[month_pt]['PH'] += 1
                                elif 'P' in activity_clean:
                                    seasonal_data[month_pt]['P'] += 1
                                elif 'H' in activity_clean:
                                    seasonal_data[month_pt]['H'] += 1
            
            elif isinstance(crop_data, dict):
                # Estrutura IBGE: dict de estados
                for state, activities in crop_data.items():
                    if isinstance(activities, dict):
                        for activity, months_list in activities.items():
                            if isinstance(months_list, list):
                                activity_type = 'P' if 'plant' in activity.lower() else 'H'
                                
                                for month in months_list:
                                    if isinstance(month, int) and 1 <= month <= 12:
                                        month_pt = month_names[month - 1]
                                        seasonal_data[month_pt][activity_type] += 1
        
        return seasonal_data
        
    except Exception as e:
        st.error(f"❌ Erro na extração de dados sazonais: {str(e)}")
        return {}

