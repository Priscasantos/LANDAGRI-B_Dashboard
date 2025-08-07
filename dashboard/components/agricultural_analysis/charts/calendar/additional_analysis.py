"""
Additional Analysis Charts
=========================

Creates additional analysis charts for seasonality, temporal comparison,
and regional distribution analysis.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_seasonality_analysis(calendar_data: dict) -> None:
    """
    Render seasonality analysis with polar chart.
    
    Parameters:
    -----------
    calendar_data : dict
        Dictionary containing complete calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    st.markdown("### 🔄 Análise de Sazonalidade")
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Seasonality data
        monthly_activity = {f"Mês {i}": 0 for i in range(1, 13)}
        
        for _crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                for month, activity in calendar_entry.items():
                    if activity:
                        month_num = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"].index(month) + 1
                        monthly_activity[f"Mês {month_num}"] += 1
        
        # Seasonality chart
        months = list(monthly_activity.keys())
        activities = list(monthly_activity.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=activities,
            theta=months,
            fill='toself',
            name='Atividade Agrícola'
        ))
        
        fig.update_layout(
            polar={
                "radialaxis": {
                    "visible": True,
                    "range": [0, max(activities)]
                }},
            title="Distribuição Sazonal da Atividade Agrícola",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Gráfico polar mostrando a intensidade das atividades agrícolas ao longo do ano.")
        
    except Exception as e:
        st.error(f"Erro na análise de sazonalidade: {e}")


def render_temporal_comparison(calendar_data: dict) -> None:
    """
    Render temporal comparison analysis.
    
    Parameters:
    -----------
    calendar_data : dict
        Dictionary containing complete calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    st.markdown("### 📊 Comparação Temporal")
    
    try:
        # Basic temporal comparison analysis
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        temporal_data = []
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                years = state_entry.get('years', [2024])
                state_name = state_entry.get('state_name', '')
                
                for year in years:
                    temporal_data.append({
                        'Ano': year,
                        'Estado': state_name,
                        'Cultura': crop,
                        'Atividade': 1
                    })
        
        if temporal_data:
            df_temporal = pd.DataFrame(temporal_data)
            
            # Temporal line chart
            yearly_summary = df_temporal.groupby(['Ano', 'Cultura'])['Atividade'].sum().reset_index()
            
            fig = px.line(
                yearly_summary,
                x='Ano',
                y='Atividade',
                color='Cultura',
                title="Evolução Temporal das Culturas"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Evolução da atividade por cultura ao longo dos anos.")
            
        else:
            st.info("📊 Dados temporais não disponíveis")
        
    except Exception as e:
        st.error(f"Erro na comparação temporal: {e}")


def render_regional_distribution(calendar_data: dict) -> None:
    """
    Render regional distribution analysis.
    
    Parameters:
    -----------
    calendar_data : dict
        Dictionary containing complete calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    st.markdown("### 🗺️ Distribuição Regional")
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        regional_data = []
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_name = state_entry.get('state_name', '')
                calendar_entry = state_entry.get('calendar', {})
                
                # Count activities by state
                activity_count = sum(1 for activity in calendar_entry.values() if activity)
                
                regional_data.append({
                    'Estado': state_name,
                    'Cultura': crop,
                    'Atividades': activity_count
                })
        
        if regional_data:
            df_regional = pd.DataFrame(regional_data)
            
            # Heatmap by state and crop
            pivot_regional = df_regional.pivot_table(
                index='Estado',
                columns='Cultura',
                values='Atividades',
                fill_value=0
            )
            
            fig = px.imshow(
                pivot_regional.values,
                x=pivot_regional.columns,
                y=pivot_regional.index,
                aspect="auto",
                title="Intensidade de Atividade por Estado e Cultura"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Mapa de calor da intensidade de atividades agrícolas por estado e cultura.")
            
        else:
            st.info("📊 Dados regionais não disponíveis")
        
    except Exception as e:
        st.error(f"Erro na distribuição regional: {e}")
