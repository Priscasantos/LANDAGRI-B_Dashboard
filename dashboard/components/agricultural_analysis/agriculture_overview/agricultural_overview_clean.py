"""
Agricultural Overview Component
==============================

Componente responsável por renderizar o overview consolidado de dados agrícolas.
APENAS dados de visão geral - sem abas, menu único.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Any
from .overview_data import (
    get_agricultural_overview_stats,
    get_crops_overview_data,
    get_regional_summary
)


def render_agricultural_overview() -> None:
    """
    Renderizar overview agrícola consolidado.
    Página única sem abas - apenas visão geral.
    """
    
    # Header do overview
    st.markdown("# 📊 Overview Agrícola")
    st.markdown("*Visão geral consolidada do monitoramento agrícola brasileiro*")
    
    # Carregar dados específicos do overview
    overview_stats = get_agricultural_overview_stats()
    crops_data = get_crops_overview_data()
    regional_data = get_regional_summary()
    
    # Métricas principais
    _render_overview_metrics(overview_stats)
    
    st.markdown("---")
    
    # Status do sistema
    _render_system_status(overview_stats)
    
    st.markdown("---")
    
    # Análises em duas colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌱 Culturas Monitoradas")
        _render_crops_overview(crops_data)
        
    with col2:
        st.markdown("#### 🗺️ Distribuição Regional")
        _render_regional_overview(regional_data)
    
    # Resumo técnico
    st.markdown("---")
    _render_technical_summary(overview_stats)


def _render_overview_metrics(overview_stats: dict[str, Any]) -> None:
    """
    Renderizar métricas principais do overview.
    """
    if not overview_stats:
        st.warning("⚠️ Dados de estatísticas não disponíveis")
        return
    
    # Layout de 5 colunas para métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🗺️ Estados", 
            overview_stats.get('states_covered', 'N/A'),
            help="Estados brasileiros cobertos pelo monitoramento"
        )
    
    with col2:
        st.metric(
            "🌱 Culturas",
            overview_stats.get('total_crops', 'N/A'),
            help="Culturas agrícolas monitoradas"
        )
    
    with col3:
        resolution = overview_stats.get('resolution', 'N/A')
        st.metric(
            "🔍 Resolução",
            resolution,
            help="Resolução espacial dos dados"
        )
    
    with col4:
        accuracy = overview_stats.get('accuracy', 0)
        accuracy_str = f"{accuracy:.1f}%" if accuracy > 0 else "N/A"
        st.metric(
            "🎯 Precisão",
            accuracy_str,
            help="Precisão geral do monitoramento"
        )
    
    with col5:
        area = overview_stats.get('total_area_monitored', 'N/A')
        st.metric(
            "📏 Cobertura",
            area,
            help="Área total monitorada"
        )


def _render_system_status(overview_stats: dict[str, Any]) -> None:
    """
    Renderizar status do sistema de monitoramento.
    """
    st.markdown("#### ⚡ Status do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        provider = overview_stats.get('provider', 'N/A')
        st.info(f"**Provedor:** {provider}")
    
    with col2:
        methodology = overview_stats.get('methodology', 'N/A')
        st.info(f"**Metodologia:** {methodology}")
    
    with col3:
        # Calcular status baseado na disponibilidade de dados
        total_crops = overview_stats.get('total_crops', 0)
        states_covered = overview_stats.get('states_covered', 0)
        
        if total_crops > 5 and states_covered > 10:
            st.success("🟢 **Sistema Operacional**")
        elif total_crops > 2 and states_covered > 5:
            st.warning("🟡 **Funcionamento Parcial**")
        else:
            st.error("🔴 **Dados Limitados**")


def _render_crops_overview(crops_data: pd.DataFrame) -> None:
    """
    Renderizar overview das culturas.
    """
    if crops_data.empty:
        st.info("📊 Dados de culturas não disponíveis")
        return
    
    # Mostrar tabela das culturas
    st.dataframe(
        crops_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Gráfico de barras das culturas por estados
    if 'Estados' in crops_data.columns:
        fig = px.bar(
            crops_data.head(10),
            x='Cultura',
            y='Estados',
            color='Dupla Safra',
            title="Top 10 Culturas por Número de Estados",
            labels={'Estados': 'Número de Estados', 'Cultura': 'Cultura'}
        )
        fig.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def _render_regional_overview(regional_data: pd.DataFrame) -> None:
    """
    Renderizar overview regional.
    """
    if regional_data.empty:
        st.info("📊 Dados regionais não disponíveis")
        return
    
    # Mostrar tabela regional
    st.dataframe(
        regional_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Gráfico de pizza das regiões
    if 'Culturas' in regional_data.columns:
        fig = px.pie(
            regional_data,
            values='Culturas',
            names='Região',
            title="Distribuição de Culturas por Região"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def _render_technical_summary(overview_stats: dict[str, Any]) -> None:
    """
    Renderizar resumo técnico do sistema.
    """
    st.markdown("#### 🔧 Resumo Técnico")
    
    # Informações técnicas em expandir
    with st.expander("Detalhes Técnicos do Sistema"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Dados do Sistema:**")
            st.write(f"• **Provedor:** {overview_stats.get('provider', 'N/A')}")
            st.write(f"• **Metodologia:** {overview_stats.get('methodology', 'N/A')}")
            st.write(f"• **Resolução:** {overview_stats.get('resolution', 'N/A')}")
        
        with col2:
            st.markdown("**Cobertura:**")
            st.write(f"• **Estados:** {overview_stats.get('states_covered', 'N/A')}")
            st.write(f"• **Culturas:** {overview_stats.get('total_crops', 'N/A')}")
            st.write(f"• **Área Total:** {overview_stats.get('total_area_monitored', 'N/A')}")
    
    # Resumo em métricas
    if overview_stats:
        total_crops = overview_stats.get('total_crops', 0)
        states_covered = overview_stats.get('states_covered', 0)
        
        if total_crops > 0 and states_covered > 0:
            coverage_ratio = total_crops / states_covered if states_covered > 0 else 0
            st.metric(
                "📈 Densidade de Monitoramento",
                f"{coverage_ratio:.1f}",
                help="Média de culturas por estado monitorado"
            )
