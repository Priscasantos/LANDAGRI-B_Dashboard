"""
Crop Availability Tab Handler
============================

Módulo principal para renderização da aba de disponibilidade de culturas.
Integra análises de calendário agrícola e dados CONAB.
"""

import streamlit as st

from .calendar_availability_analysis import render_calendar_availability_analysis
from .conab_availability_analysis import render_conab_availability_analysis


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
        st.markdown("---")
        
        # Importar função de gráfico mensal se necessário
        st.info("📊 Calendário de atividade mensal disponível através de outros módulos")
    
    if data_source in ["Dados CONAB", "Ambos"] and conab_data:
        st.markdown("---")
        st.markdown("#### 🌾 Disponibilidade CONAB")
        render_conab_availability_analysis(conab_data)
        st.markdown("---")
        
        # Importar função de distribuição espacial-temporal se necessário
        st.info("📊 Gráfico de distribuição espacial-temporal disponível através de outros módulos")
