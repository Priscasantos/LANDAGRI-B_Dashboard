"""
National Calendar Matrix Charts
==============================

Módulo de gráficos de matriz de calendário nacional consolidados do old_calendar.
Implementa visualizações de heatmaps e matrizes consolidadas para análise nacional.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional


def create_consolidated_calendar_matrix_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria matriz consolidada do calendário agrícola.
    
    Equivalente ao: consolidated_calendar_matrix.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para matriz consolidada")
            return None

        # Meses para matriz
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Prepara dados da matriz
        matrix_data = []
        crops = list(crop_calendar.keys())
        
        for crop in crops:
            crop_row = []
            states_data = crop_calendar[crop]
            
            for month in months:
                # Conta atividades (plantio + colheita) por mês
                activity_count = 0
                
                for state, activities in states_data.items():
                    if month in activities.get('planting_months', []):
                        activity_count += 1
                    if month in activities.get('harvesting_months', []):
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
            colorbar=dict(title="Número de<br>Atividades")
        ))

        # Personaliza layout
        fig.update_layout(
            title="🗓️ Matriz Consolidada do Calendário Agrícola Nacional",
            xaxis_title="Mês do Ano",
            yaxis_title="Tipo de Cultura",
            height=400 + (len(crops) * 20),
            font=dict(size=12)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar matriz consolidada do calendário: {e}")
        return None


def create_calendar_heatmap_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria heatmap do calendário agrícola.
    
    Equivalente ao: calendario_agricola_heatmap.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para heatmap")
            return None

        # Meses para heatmap
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Prepara dados com diferenciação de atividades
        heatmap_data = []
        
        for crop, states_data in crop_calendar.items():
            # Cria linha para plantio
            planting_row = []
            harvesting_row = []
            
            for month in months:
                planting_count = 0
                harvesting_count = 0
                
                for state, activities in states_data.items():
                    if month in activities.get('planting_months', []):
                        planting_count += 1
                    if month in activities.get('harvesting_months', []):
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
            colorbar=dict(title="Número de<br>Estados")
        ))

        # Personaliza layout
        fig.update_layout(
            title="🔥 Heatmap do Calendário Agrícola (🌱 Plantio | 🌾 Colheita)",
            xaxis_title="Mês do Ano",
            yaxis_title="Cultura e Tipo de Atividade",
            height=400 + (len(y_labels) * 15),
            font=dict(size=11)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar heatmap do calendário agrícola: {e}")
        return None


def create_regional_activity_comparison_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de comparação de atividades regionais.
    
    Equivalente ao: regional_activity_comparison.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para comparação regional")
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

        # Conta atividades por região e mês
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                region = state_to_region.get(state, 'Indefinido')
                if region == 'Indefinido':
                    continue
                
                # Conta plantio e colheita
                for month in activities.get('planting_months', []):
                    if month in region_month_data[region]:
                        region_month_data[region][month] += 1
                
                for month in activities.get('harvesting_months', []):
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
            title="📊 Comparação de Atividades Agrícolas por Região",
            xaxis_title="Mês do Ano",
            yaxis_title="Número Total de Atividades",
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
        st.error(f"❌ Erro ao criar gráfico de comparação regional: {e}")
        return None


def render_national_calendar_matrix_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de matriz de calendário nacional.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 🗓️ Matriz Nacional do Calendário Agrícola")
    
    # Primeira linha: matriz consolidada
    st.markdown("#### 📋 Matriz Consolidada")
    fig1 = create_consolidated_calendar_matrix_chart(filtered_data)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)
    
    # Segunda linha: heatmap detalhado
    st.markdown("#### 🔥 Heatmap Detalhado")
    fig2 = create_calendar_heatmap_chart(filtered_data)
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    
    # Terceira linha: comparação regional
    st.markdown("#### 📊 Comparação Regional")
    fig3 = create_regional_activity_comparison_chart(filtered_data)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)
