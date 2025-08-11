"""
Crop Availability Tab Handler
============================

Módulo principal para renderização da aba de disponibilidade de culturas.
Integra análises de calendário agrícola e dados CONAB.
"""

import streamlit as st

from .calendar_availability_analysis import render_calendar_availability_analysis
from .conab_availability_analysis import render_conab_availability_analysis
from .conab_specific_charts import render_conab_charts_tab
from ..conab_charts import (
    create_timeline_activities_chart,
    create_monthly_activities_timeline_chart,
    create_main_crops_seasonality_chart
)
from ..calendar.additional_analysis import (
    render_seasonality_analysis,
    render_temporal_comparison,
    render_regional_distribution
)


def render_crop_availability_tab(calendar_data: dict, conab_data: dict) -> None:
    """
    Renderizar aba completa de disponibilidade de culturas.
    
    Parameters:
    -----------
    calendar_data : dict
        Dados do calendário agrícola
    conab_data : dict
        Dados CONAB
        
    Returns:
    --------
    None
        Renderiza diretamente no Streamlit
    """
    st.markdown("### 🌾 Disponibilidade de Culturas por Região e Período")
    st.markdown("*Análise detalhada da disponibilidade temporal e espacial de culturas*")
    
    if not calendar_data and not conab_data:
        st.warning("⚠️ Nenhum dado de disponibilidade de culturas disponível.")
        return
    
    data_source = st.radio(
        "📊 Selecionar fonte de dados:",
        ["Calendário Agrícola", "Dados CONAB", "Ambos"],
        index=2,
        horizontal=True
    )
    
    st.markdown("---")
    
    if data_source in ["Calendário Agrícola", "Ambos"] and calendar_data:
        st.markdown("#### 📅 Disponibilidade do Calendário")
        render_calendar_availability_analysis(calendar_data)
        
        # Timeline Charts Section
        st.markdown("---")
        st.markdown("#### ⏰ Timeline e Sazonalidade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📅 Activities Timeline")
            try:
                timeline_fig = create_timeline_activities_chart(calendar_data)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.info("📊 Dados insuficientes para gráfico de timeline")
            except Exception as e:
                st.error(f"❌ Error creating activity timeline: {str(e)}")
        
        with col2:
            st.markdown("##### 📅 Timeline Mensal")
            try:
                monthly_fig = create_monthly_activities_timeline_chart(calendar_data)
                if monthly_fig:
                    st.plotly_chart(monthly_fig, use_container_width=True)
                else:
                    st.info("📊 Dados insuficientes para timeline mensal")
            except Exception as e:
                st.error(f"❌ Error creating timeline mensal: {str(e)}")
        
        # Seasonality Chart
        st.markdown("##### 🌟 Main Seasonality")
        try:
            seasonality_fig = create_main_crops_seasonality_chart(calendar_data)
            if seasonality_fig:
                st.plotly_chart(seasonality_fig, use_container_width=True)
            else:
                st.info("📊 Dados insuficientes para gráfico de sazonalidade")
        except Exception as e:
            st.error(f"❌ Error creating gráfico de sazonalidade: {str(e)}")
        
        # Additional Charts Tab
        st.markdown("---")
        st.markdown("#### 📊 Análises Adicionais")
        
        # Criar abas para diferentes análises
        tab1, tab2, tab3 = st.tabs(["🔄 Sazonalidade", "📊 Temporal", "🗺️ Regional"])
        
        with tab1:
            render_seasonality_analysis(calendar_data)
        
        with tab2:
            render_temporal_comparison(calendar_data)
        
        with tab3:
            render_regional_distribution(calendar_data)
        
        st.markdown("---")
    
    if data_source in ["Dados CONAB", "Ambos"] and conab_data:
        st.markdown("---")
        st.markdown("#### 🌾 Disponibilidade CONAB")
        render_conab_availability_analysis(conab_data)
        
        # Additional analysis for CONAB data if needed
        st.markdown("---")
        st.markdown("#### 📊 Análises Complementares CONAB")
        
        # Use dedicated CONAB charts
        render_conab_charts_tab(conab_data)
        
        st.markdown("---")
