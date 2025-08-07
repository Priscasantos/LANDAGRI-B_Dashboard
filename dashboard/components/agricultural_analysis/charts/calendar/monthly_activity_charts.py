"""
Monthly Activity Charts
======================

Módulo de gráficos de atividades mensais consolidados do old_calendar.
Implementa visualizações para análise temporal de atividades agrícolas.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional


def create_total_activities_per_month_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de total de atividades por mês.
    
    Equivalente ao: total_activities_per_month.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para atividades mensais")
            return None

        # Inicializa contadores mensais
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_activities = {month: 0 for month in months}

        # Conta atividades por mês
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                # Conta plantio
                for month in activities.get('planting_months', []):
                    if month in monthly_activities:
                        monthly_activities[month] += 1
                
                # Conta colheita
                for month in activities.get('harvesting_months', []):
                    if month in monthly_activities:
                        monthly_activities[month] += 1

        if not any(monthly_activities.values()):
            st.info("📊 Nenhuma atividade mensal encontrada nos dados")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(monthly_activities.items()), columns=['Mês', 'Total_Atividades'])

        # Cria gráfico de linhas
        fig = px.line(
            df,
            x='Mês',
            y='Total_Atividades',
            title="📅 Total de Atividades Agrícolas por Mês",
            labels={
                'Total_Atividades': 'Número Total de Atividades',
                'Mês': 'Mês do Ano'
            },
            markers=True
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            xaxis_title="Mês do Ano",
            yaxis_title="Número Total de Atividades",
            showlegend=False
        )

        # Adiciona valores nos pontos
        fig.update_traces(
            mode='lines+markers+text',
            text=df['Total_Atividades'],
            textposition='top center'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de atividades mensais: {e}")
        return None


def create_planting_vs_harvesting_per_month_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico comparativo de plantio vs colheita por mês.
    
    Equivalente ao: planting_vs_harvesting_per_month.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para comparação plantio vs colheita")
            return None

        # Inicializa contadores mensais
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        planting_counts = {month: 0 for month in months}
        harvesting_counts = {month: 0 for month in months}

        # Conta atividades por mês
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                # Conta plantio
                for month in activities.get('planting_months', []):
                    if month in planting_counts:
                        planting_counts[month] += 1
                
                # Conta colheita
                for month in activities.get('harvesting_months', []):
                    if month in harvesting_counts:
                        harvesting_counts[month] += 1

        # Cria DataFrame
        df = pd.DataFrame({
            'Mês': months,
            'Plantio': [planting_counts[month] for month in months],
            'Colheita': [harvesting_counts[month] for month in months]
        })

        # Cria gráfico de barras agrupadas
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='🌱 Plantio',
            x=df['Mês'],
            y=df['Plantio'],
            marker_color='lightgreen',
            text=df['Plantio'],
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='🌾 Colheita',
            x=df['Mês'],
            y=df['Colheita'],
            marker_color='orange',
            text=df['Colheita'],
            textposition='outside'
        ))

        # Personaliza layout
        fig.update_layout(
            title="🌱📅 Comparação Plantio vs Colheita por Mês",
            xaxis_title="Mês do Ano",
            yaxis_title="Número de Atividades",
            barmode='group',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico plantio vs colheita: {e}")
        return None


def create_simultaneous_planting_harvesting_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de atividades simultâneas de plantio e colheita.
    
    Equivalente ao: simultaneous_planting_harvesting.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para atividades simultâneas")
            return None

        # Inicializa contadores mensais
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        simultaneous_activities = {month: 0 for month in months}

        # Identifica atividades simultâneas por mês
        for crop, states_data in crop_calendar.items():
            for state, activities in states_data.items():
                planting_months = set(activities.get('planting_months', []))
                harvesting_months = set(activities.get('harvesting_months', []))
                
                # Encontra meses com atividades simultâneas
                simultaneous_months = planting_months.intersection(harvesting_months)
                
                for month in simultaneous_months:
                    if month in simultaneous_activities:
                        simultaneous_activities[month] += 1

        if not any(simultaneous_activities.values()):
            st.info("📊 Nenhuma atividade simultânea encontrada nos dados")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(simultaneous_activities.items()), columns=['Mês', 'Atividades_Simultâneas'])

        # Cria gráfico de barras
        fig = px.bar(
            df,
            x='Mês',
            y='Atividades_Simultâneas',
            title="🔄 Atividades Simultâneas de Plantio e Colheita por Mês",
            labels={
                'Atividades_Simultâneas': 'Número de Atividades Simultâneas',
                'Mês': 'Mês do Ano'
            },
            color='Atividades_Simultâneas',
            color_continuous_scale='Reds'
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            xaxis_title="Mês do Ano",
            yaxis_title="Número de Atividades Simultâneas",
            showlegend=False,
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de atividades simultâneas: {e}")
        return None


def create_planting_harvesting_periods_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de períodos de plantio e colheita.
    
    Equivalente ao: planting_harvesting_periods.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 Sem dados de calendário disponíveis para períodos de plantio e colheita")
            return None

        # Prepara dados para heatmap de períodos
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        heatmap_data = []
        
        for crop, states_data in crop_calendar.items():
            crop_row_planting = []
            crop_row_harvesting = []
            
            for month in months:
                # Conta estados com plantio neste mês
                planting_count = 0
                harvesting_count = 0
                
                for state, activities in states_data.items():
                    if month in activities.get('planting_months', []):
                        planting_count += 1
                    if month in activities.get('harvesting_months', []):
                        harvesting_count += 1
                
                crop_row_planting.append(planting_count)
                crop_row_harvesting.append(harvesting_count)
            
            # Adiciona dados ao heatmap
            heatmap_data.append({
                'Cultura': f"{crop} (Plantio)",
                'Tipo': 'Plantio',
                **{months[i]: crop_row_planting[i] for i in range(len(months))}
            })
            
            heatmap_data.append({
                'Cultura': f"{crop} (Colheita)",
                'Tipo': 'Colheita',
                **{months[i]: crop_row_harvesting[i] for i in range(len(months))}
            })

        if not heatmap_data:
            st.info("📊 Nenhum período encontrado nos dados")
            return None

        # Cria DataFrame
        df = pd.DataFrame(heatmap_data)
        
        # Prepara matriz para heatmap
        z_data = df[months].values
        y_labels = df['Cultura'].tolist()

        # Cria heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=months,
            y=y_labels,
            colorscale='RdYlGn',
            text=z_data,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))

        # Personaliza layout
        fig.update_layout(
            title="🗓️ Períodos de Plantio e Colheita por Cultura",
            xaxis_title="Mês do Ano",
            yaxis_title="Cultura (Tipo de Atividade)",
            height=400 + (len(y_labels) * 15)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de períodos de plantio e colheita: {e}")
        return None


def render_monthly_activity_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de atividades mensais.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 📅 Análise de Atividades Mensais")
    
    # Primeira linha: atividades totais e comparação plantio vs colheita
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = create_total_activities_per_month_chart(filtered_data)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = create_planting_vs_harvesting_per_month_chart(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    # Segunda linha: atividades simultâneas
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = create_simultaneous_planting_harvesting_chart(filtered_data)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.info("📊 Espaço reservado para métricas adicionais")
    
    # Terceira linha: períodos completos (largura total)
    st.markdown("#### 🗓️ Períodos Detalhados de Plantio e Colheita")
    fig4 = create_planting_harvesting_periods_chart(filtered_data)
    if fig4:
        st.plotly_chart(fig4, use_container_width=True)
