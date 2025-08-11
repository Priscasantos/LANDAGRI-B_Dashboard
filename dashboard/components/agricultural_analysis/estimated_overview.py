"""
Overview Agrícola do Brasil
Página principal que permite alternar entre dados do IBGE e CONAB
"""

import streamlit as st
from dashboard import brazilian_ibge_agricultural_data
from dashboard import conab_agricultural_data

def render():
    """Renderiza a página de overview agrícola com alternância entre fontes"""
    
    st.title("🌾 Overview Agrícola do Brasil")
    st.markdown("Dados de produção agrícola brasileira de fontes oficiais")
    
    # Seletor de fonte de dados
    st.sidebar.markdown("### 📊 Fonte de Dados")
    data_source = st.sidebar.selectbox(
        "Selecione a fonte dos dados:",
        ["CONAB", "IBGE"],
        help="CONAB: Companhia Nacional de Abastecimento\nIBGE: Instituto Brasileiro de Geografia e Estatística"
    )
    
    # Informações sobre as fontes
    if data_source == "CONAB":
        st.sidebar.markdown(
            """
            **CONAB**
            - Companhia Nacional de Abastecimento
            - Dados especializados em safras de grãos
            - Levantamentos mensais
            - Foco em commodities agrícolas
            - Período: 2018/19 a 2023/24
            """
        )
    else:  # IBGE
        st.sidebar.markdown(
            """
            **IBGE**
            - Instituto Brasileiro de Geografia e Estatística
            - Produção Agrícola Municipal (PAM)
            - Dados anuais por município
            - Ampla cobertura de culturas
            - Período: 2018 a 2023
            """
        )
    
    # Renderizar componente baseado na seleção
    if data_source == "CONAB":
        st.info("📊 Exibindo dados da **CONAB** - Companhia Nacional de Abastecimento")
        conab_agricultural_data.render()
    else:  # IBGE
        st.info("📊 Exibindo dados do **IBGE** - Instituto Brasileiro de Geografia e Estatística")
        brazilian_ibge_agricultural_data.render()
    
    # Comparação entre fontes
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Comparação de Fontes")
    
    with st.sidebar.expander("Diferenças entre CONAB e IBGE"):
        st.markdown(
            """
            **CONAB:**
            - Foco em grãos e commodities
            - Dados por safra (ex: 2023/24)
            - Levantamentos frequentes
            - Estimativas e previsões
            
            **IBGE:**
            - Cobertura ampla de culturas
            - Dados anuais (ex: 2023)
            - Base municipal
            - Dados consolidados oficiais
            """
        )

if __name__ == "__main__":
    st.set_page_config(
        page_title="Overview Agrícola Brasil",
        page_icon="🌾",
        layout="wide"
    )
    render()
