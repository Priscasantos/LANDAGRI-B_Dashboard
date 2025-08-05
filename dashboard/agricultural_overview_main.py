"""
Agricultural Overview Dashboard - Página Principal
=================================================

Dashboard principal focado apenas no Overview Agrícola.
Sem abas - página única consolidada.

Funcionalidades:
- Overview consolidado com métricas e distribuições
- Gráficos dinâmicos de calendário agrícola
- Análise integrada de dados CONAB
- Interface limpa e responsiva

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import sys
from pathlib import Path
from typing import Dict

import streamlit as st

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Adicionar o diretório dashboard ao path
_dashboard_root = Path(__file__).resolve().parent
if str(_dashboard_root) not in sys.path:
    sys.path.insert(0, str(_dashboard_root))

# Importar componentes
from components.agricultural_analysis.agricultural_loader import (
    load_conab_detailed_data,
    load_conab_crop_calendar,
    validate_conab_data_quality
)
from components.agricultural_analysis.overview.agricultural_overview import (
    render_agricultural_overview
)
from components.agricultural_analysis.charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar
)


def run():
    """
    Executar dashboard principal do Overview Agrícola.
    """
    
    # Configuração da página
    st.set_page_config(
        page_title="Agricultural Overview",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Header visual aprimorado
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(22, 163, 74, 0.2);
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                🌾 Overview Agrícola Brasileiro
            </h1>
            <p style="color: #dcfce7; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Visão consolidada da agricultura brasileira - CONAB & Embrapa 2025
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Carregar dados
    calendar_data, conab_data = _load_agricultural_data()

    if not calendar_data and not conab_data:
        st.error("❌ Nenhum dado agrícola disponível para análise.")
        st.info("🔧 Verifique se os arquivos de dados estão disponíveis na pasta data/json/")
        return

    # Validar qualidade dos dados
    if conab_data:
        quality_metrics = validate_conab_data_quality(conab_data)
        if quality_metrics['completeness_score'] < 0.7:
            st.warning(f"⚠️ Completude dos dados: {quality_metrics['completeness_score']:.1%}. Algumas funcionalidades podem estar limitadas.")

    # Renderizar Overview principal
    render_agricultural_overview(calendar_data, conab_data)
    
    # Seção adicional com gráficos dinâmicos de calendário
    st.markdown("---")
    st.markdown("## 📅 Calendários Agrícolas Dinâmicos")
    
    # Layout em colunas para gráficos de calendário
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("### 🗓️ Calendário de Plantio e Colheita")
        if calendar_data:
            fig_heatmap = plot_crop_calendar_heatmap(calendar_data)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)
                st.caption("Mapa de calor mostrando períodos de plantio e colheita por estado e cultura.")
            else:
                st.info("📊 Dados de calendário não disponíveis para heatmap")
        else:
            st.info("📊 Dados de calendário não carregados")
    
    with col2:
        st.markdown("### 📊 Atividade Mensal")
        if calendar_data:
            fig_monthly = plot_monthly_activity_calendar(calendar_data)
            if fig_monthly:
                st.plotly_chart(fig_monthly, use_container_width=True)
                st.caption("Resumo mensal das atividades agrícolas em todo o Brasil.")
            else:
                st.info("📊 Dados mensais não disponíveis")
        else:
            st.info("📊 Dados de calendário não carregados")
    
    # Seção com informações de navegação
    st.markdown("---")
    _render_navigation_info()


def _load_agricultural_data():
    """
    Carregar dados agrícolas dos arquivos JSONC.

    Returns:
        tuple: (calendar_data, conab_data)
    """
    with st.spinner("🔄 Carregando dados agrícolas..."):
        try:
            # Carregar calendário agrícola
            calendar_data = load_conab_crop_calendar()
            
            # Carregar dados detalhados CONAB
            conab_data = load_conab_detailed_data()
            
            return calendar_data, conab_data
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados agrícolas: {e}")
            return {}, {}


def _render_navigation_info():
    """
    Renderizar informações de navegação para outras páginas.
    """
    st.markdown("### 🧭 Navegação")
    
    # Info boxes para outras páginas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📅 Calendário Agrícola**
        
        Acesse o calendário interativo com:
        - Filtros por estado e cultura
        - Análise temporal detalhada
        - Gráficos de sazonalidade
        
        *[Menu: Calendário Agrícola]*
        """)
    
    with col2:
        st.info("""
        **🌾 Análise CONAB**
        
        Explore dados especializados:
        - Cobertura espacial e temporal
        - Métricas de qualidade
        - Tendências de produção
        
        *[Menu: Análise CONAB]*
        """)
    
    with col3:
        st.info("""
        **📋 Disponibilidade**
        
        Analise disponibilidade de dados:
        - Matriz de cobertura
        - Análise de dupla safra
        - Status por região
        
        *[Menu: Disponibilidade]*
        """)


if __name__ == "__main__":
    run()
