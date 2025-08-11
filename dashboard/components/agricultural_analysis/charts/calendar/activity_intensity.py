"""
Activity Intensity Analysis Charts
=================================

Creates charts for analyzing intensity and peaks of agricultural activities.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional
from ...agricultural_loader import safe_get_data


def create_intensity_heatmap(filtered_data: dict) -> None:
    """
    Create intensity heatmap analysis chart.
    
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
            st.warning("⚠️ Dados insuficientes para análise de intensidade")
            return
            
        # Criar matriz de intensidade
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        crops = list(crop_calendar.keys())
        intensity_matrix = []
        
        for crop in crops:
            crop_data = crop_calendar[crop]
            monthly_intensity = [0] * 12
            
            # Verificar se é estrutura CONAB (lista de estados) ou IBGE (dict)
            if isinstance(crop_data, list):
                # Estrutura CONAB: lista de estados com calendários
                for state_entry in crop_data:
                    if isinstance(state_entry, dict) and 'calendar' in state_entry:
                        calendar = state_entry['calendar']
                        for month_en, activity in calendar.items():
                            if activity and activity.strip():
                                # Mapear mês inglês para índice
                                month_mapping = {
                                    'January': 0, 'February': 1, 'March': 2, 'April': 3,
                                    'May': 4, 'June': 5, 'July': 6, 'August': 7,
                                    'September': 8, 'October': 9, 'November': 10, 'December': 11
                                }
                                if month_en in month_mapping:
                                    monthly_intensity[month_mapping[month_en]] += 1
            elif isinstance(crop_data, dict):
                # Estrutura IBGE: dict de estados
                for state, activities in crop_data.items():
                    if isinstance(activities, dict):
                        for activity, months_list in activities.items():
                            if isinstance(months_list, list):
                                for month in months_list:
                                    if isinstance(month, int) and 1 <= month <= 12:
                                        monthly_intensity[month - 1] += 1
            
            intensity_matrix.append(monthly_intensity)
        
        # Criar heatmap
        fig = go.Figure(data=go.Heatmap(
            z=intensity_matrix,
            x=months,
            y=crops,
            colorscale='Viridis',
            colorbar=dict(title="Intensidade de Atividade")
        ))
        
        fig.update_layout(
            title="🔥 Mapa de Intensidade de Atividades Agrícolas",
            xaxis_title="Meses",
            yaxis_title="Culturas",
            height=max(400, len(crops) * 30),
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True, key="activity_intensity_heatmap")
        
    except Exception as e:
        st.error(f"❌ Erro ao criar mapa de intensidade: {str(e)}")


def create_peak_activity_analysis(filtered_data: dict) -> None:
    """
    Create peak activity analysis chart.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    st.info("🔧 Peak activity analysis - Feature under development")


def create_activity_overlap_matrix(filtered_data: dict) -> None:
    """
    Create activity overlap matrix chart.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    st.info("🔧 Activity overlap matrix - Feature under development")
