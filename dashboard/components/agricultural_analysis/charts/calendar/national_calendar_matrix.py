"""
National Calendar Matrix Charts
==============================

National calendar matrix charts module consolidated from old_calendar.
Implements heatmap and consolidated matrix visualizations for national analysis.

Author: LANDAGRI-B Project Team 
Date: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional

# Import das funções seguras
from ...agricultural_loader import safe_get_data, validate_data_structure


def create_consolidated_calendar_matrix_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates consolidated agricultural calendar matrix.
    
    Equivalent to: consolidated_calendar_matrix.png from old_calendar/national/
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        # Safe access to calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for consolidated matrix")
            return None

        # Months for matrix
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Prepare matrix data
        matrix_data = []
        crops = list(crop_calendar.keys())
        
        for crop in crops:
            crop_row = []
            states_data = crop_calendar[crop]
            
            for month in months:
                # Conta atividades (plantio + colheita) por mês usando acesso seguro
                activity_count = 0
                
                # Verificar se é estrutura CONAB (lista de estados) ou IBGE (dict)
                if isinstance(states_data, list):
                    # Estrutura CONAB: lista de estados com calendários
                    month_mapping = {
                        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
                        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
                    }
                    
                    month_en = month_mapping.get(month, month)
                    
                    for state_entry in states_data:
                        if isinstance(state_entry, dict) and 'calendar' in state_entry:
                            calendar = state_entry['calendar']
                            activity = calendar.get(month_en, '')
                            
                            if activity and activity.strip():  # Qualquer atividade
                                activity_count += 1
                                
                elif isinstance(states_data, dict):
                    # Estrutura IBGE: dict de estados
                    for state, activities in states_data.items():
                        if isinstance(activities, dict):
                            # Acesso seguro aos meses de plantio
                            planting_months = safe_get_data(activities, 'planting_months') or []
                            if month in planting_months:
                                activity_count += 1
                            
                            # Acesso seguro aos meses de colheita
                            harvesting_months = safe_get_data(activities, 'harvesting_months') or []
                            if month in harvesting_months:
                                activity_count += 1
                
                crop_row.append(activity_count)
            
            matrix_data.append(crop_row)

        if not matrix_data:
            st.info("📊 Nenhum dado de matriz encontrado")
            return None

        # Cria heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=months,
            y=crops,
            colorscale='Viridis',
            text=matrix_data,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(title="Number of<br>Activities")
        ))

        # Personaliza layout
        fig.update_layout(
            title="🗓️ National Agricultural Calendar Consolidated Matrix",
            xaxis_title="Month of Year",
            yaxis_title="Crop Type",
            height=400 + (len(crops) * 20),
            font=dict(size=12)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating matriz consolidada do calendário: {e}")
        return None


def create_calendar_heatmap_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates agricultural calendar heatmap.
    
    Equivalente ao: calendario_agricola_heatmap.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No data de calendário available para heatmap")
            return None

        # Meses para heatmap
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Prepara dados com diferenciação de atividades usando acesso seguro
        heatmap_data = []
        
        for crop, states_data in crop_calendar.items():
            # Cria linha para plantio
            planting_row = []
            harvesting_row = []
            
            for month in months:
                planting_count = 0
                harvesting_count = 0
                
                # Verificar se é estrutura CONAB (lista de estados) ou IBGE (dict)
                if isinstance(states_data, list):
                    # Estrutura CONAB: lista de estados com calendários
                    month_mapping = {
                        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
                        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
                    }
                    
                    month_en = month_mapping.get(month, month)
                    
                    for state_entry in states_data:
                        if isinstance(state_entry, dict) and 'calendar' in state_entry:
                            calendar = state_entry['calendar']
                            activity = calendar.get(month_en, '')
                            
                            if 'P' in activity:  # Planting
                                planting_count += 1
                            if 'H' in activity:  # Harvesting
                                harvesting_count += 1
                                
                elif isinstance(states_data, dict):
                    # Estrutura IBGE: dict de estados
                    for state, activities in states_data.items():
                        if isinstance(activities, dict):
                            # Acesso seguro aos meses de plantio
                            planting_months = safe_get_data(activities, 'planting_months') or []
                            if month in planting_months:
                                planting_count += 1
                            
                            # Acesso seguro aos meses de colheita
                            harvesting_months = safe_get_data(activities, 'harvesting_months') or []
                            if month in harvesting_months:
                                harvesting_count += 1
                
                planting_row.append(planting_count)
                harvesting_row.append(harvesting_count)
            
            heatmap_data.extend([planting_row, harvesting_row])

        if not heatmap_data:
            st.info("📊 Nenhum dado de heatmap encontrado")
            return None

        # Cria labels para y-axis
        crops = list(crop_calendar.keys())
        y_labels = []
        for crop in crops:
            y_labels.extend([f"{crop} (🌱)", f"{crop} (🌾)"])

        # Cria heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=months,
            y=y_labels,
            colorscale='RdYlGn',
            text=heatmap_data,
            texttemplate="%{text}",
            textfont={"size": 9},
            hoverongaps=False,
            colorbar=dict(title="Number of<br>States")
        ))

        # Personaliza layout
        fig.update_layout(
            title="🔥 Agricultural Calendar Heatmap (🌱 Planting | 🌾 Harvesting)",
            xaxis_title="Month of Year",
            yaxis_title="Crop and Activity Type",
            height=400 + (len(y_labels) * 15),
            font=dict(size=11)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating agricultural calendar heatmap: {e}")
        return None


def create_regional_activity_comparison_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de comparação de atividades regionais.
    
    Equivalente ao: regional_activity_comparison.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No data de calendário available para comparação regional")
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

        # Meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Prepara dados por região e mês
        regions = list(set(state_to_region.values()))
        region_month_data = {region: {month: 0 for month in months} for region in regions}

        # Conta atividades por região e mês usando acesso seguro
        for crop, states_data in crop_calendar.items():
            if isinstance(states_data, dict):
                for state, activities in states_data.items():
                    region = state_to_region.get(state, 'Indefinido')
                    if region == 'Indefinido':
                        continue
                    
                    if isinstance(activities, dict):
                        # Acesso seguro ao plantio
                        planting_months = safe_get_data(activities, 'planting_months') or []
                        for month in planting_months:
                            if month in region_month_data[region]:
                                region_month_data[region][month] += 1
                        
                        # Acesso seguro à colheita
                        harvesting_months = safe_get_data(activities, 'harvesting_months') or []
                        for month in harvesting_months:
                            if month in region_month_data[region]:
                                region_month_data[region][month] += 1

        # Cria gráfico de linhas múltiplas
        fig = go.Figure()

        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, region in enumerate(regions):
            values = [region_month_data[region][month] for month in months]
            
            fig.add_trace(go.Scatter(
                x=months,
                y=values,
                mode='lines+markers',
                name=region,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8)
            ))

        # Personaliza layout
        fig.update_layout(
            title="📊 Agricultural Activities Comparison by Region",
            xaxis_title="Month of Year",
            yaxis_title="Total Number of Activities",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico de comparação regional: {e}")
        return None


def render_national_calendar_matrix_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de matriz de calendário nacional.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 🗓️ National Agricultural Calendar Matrix")
    
    # Primeira linha: matriz consolidada
    st.markdown("#### 📋 Consolidated Matrix")
    fig1 = create_consolidated_calendar_matrix_chart(filtered_data)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True, key="consolidated_calendar_matrix")
    
    # Segunda linha: heatmap detalhado
    st.markdown("#### 🔥 Detailed Heatmap")
    fig2 = create_calendar_heatmap_chart(filtered_data)
    if fig2:
        st.plotly_chart(fig2, use_container_width=True, key="calendar_heatmap_detailed")
    
    # Terceira linha: comparação regional
    st.markdown("#### 📊 Regional Comparison")
    fig3 = create_regional_activity_comparison_chart(filtered_data)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True, key="regional_activity_comparison")
