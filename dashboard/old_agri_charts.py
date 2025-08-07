"""
Agricultural Analysis Dashboard - Refatoração Completa
=====================================================

Dashboard orquestrador para análise agrícola consolidando overview, calendário agrícola e dados CONAB.
Implementação modular baseada em inspirações dos dashboards USDA, FAO GIEWS e GEOGLAM Crop Monitor.

Funcionalidades:
- Overview consolidado com métricas e distribuições regionais
- Calendário agrícola interativo com filtros inteligentes
- Análise especializada de dados CONAB
- Disponibilidade de culturas por região e período
- Interface unificada com abas organizadas

Autor: Dashboard Iniciativas LULC
Data: 2025-08-01
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Adicionar project root ao path - deve estar no topo
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Adicionar o diretório dashboard ao path
_dashboard_root = Path(__file__).resolve().parent
if str(_dashboard_root) not in sys.path:
    sys.path.insert(0, str(_dashboard_root))

# Importar componentes modulares usando paths relativos
from components.agricultural_analysis.agricultural_loader import (
    load_conab_detailed_data,
    load_conab_crop_calendar,
    get_conab_crop_stats,
    validate_conab_data_quality
)
from components.agricultural_analysis.agriculture_overview.agricultural_overview import (
    render_agricultural_overview
)
from components.agricultural_analysis.charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar
)
from components.agricultural_analysis.charts.conab_charts import (
    plot_conab_spatial_coverage,
    plot_conab_temporal_coverage,
    plot_conab_crop_diversity,
    plot_conab_spatial_temporal_distribution,
    plot_conab_quality_metrics,
    plot_conab_seasonal_analysis,
    plot_conab_methodology_overview
)
from components.agricultural_analysis.charts.availability import (
    render_crop_availability_tab
)


def _extract_calendar_filters(calendar_data: dict) -> Tuple[List[str], List[str], List[int]]:
    """Extrair filtros disponíveis dos dados do calendário."""
    states_set = set()
    crops_set = set()
    years_set = set()
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    
    for crop, crop_states in crop_calendar.items():
        crops_set.add(crop)
        
        for state_entry in crop_states:
            state_name = state_entry.get('state_name', '')
            if state_name:
                states_set.add(state_name)
            
            # Extrair anos se disponível
            years = state_entry.get('years', [])
            if years:
                years_set.update(years)
    
    # Se não há anos específicos, usar anos padrão
    if not years_set:
        years_set = {2020, 2021, 2022, 2023, 2024}
    
    return sorted(list(states_set)), sorted(list(crops_set)), sorted(list(years_set))


def _filter_calendar_data(calendar_data: dict, selected_states: List[str], 
                         selected_crops: List[str], selected_years: List[int]) -> dict:
    """Filtrar dados do calendário com base nas seleções."""
    filtered_data = {'crop_calendar': {}}
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    
    for crop in selected_crops:
        if crop in crop_calendar:
            filtered_states = []
            
            for state_entry in crop_calendar[crop]:
                state_name = state_entry.get('state_name', '')
                
                if state_name in selected_states:
                    # Filtrar por anos se necessário
                    entry_years = state_entry.get('years', selected_years)
                    if any(year in selected_years for year in entry_years):
                        filtered_states.append(state_entry)
            
            if filtered_states:
                filtered_data['crop_calendar'][crop] = filtered_states
    
    return filtered_data



def run():
    """
    Executar análise agrícola completa com overview consolidado, calendário e análise CONAB.
    """

    # Header visual padronizado com tema agrícola
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
            🌾 Agricultural Analysis
        </h1>
        <p style="color: #dcfce7; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Comprehensive analysis of Brazilian agricultural landscape, crop calendars and monitoring data
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Carregar dados necessários
    calendar_data, conab_data = _load_agricultural_data()

    if not calendar_data and not conab_data:
        st.error("❌ No agricultural data available for analysis.")
        st.info(
            "🔧 Please check if the data files are available in the data/json/ folder"
        )
        return

    # Validar qualidade dos dados
    if conab_data:
        quality_metrics = validate_conab_data_quality(conab_data)
        
        # Mostrar alerta se dados não estão completos
        if quality_metrics['completeness_score'] < 0.7:
            st.warning(f"⚠️ Data completeness: {quality_metrics['completeness_score']:.1%}. Some features may be limited.")

    # Renderizar análise em abas organizadas - NOVA ESTRUTURA
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📅 Agricultural Calendar", 
        "🌾 CONAB Analysis", 
        "� Crop Availability"
    ])

    with tab1:
        _render_overview_tab(calendar_data, conab_data)

    with tab2:
        _render_agricultural_calendar_tab(calendar_data)

    with tab3:
        _render_conab_analysis_tab(conab_data)

    with tab4:
        render_crop_availability_tab(calendar_data, conab_data)


def _load_agricultural_data():
    """
    Carregar dados agrícolas dos arquivos JSONC usando os componentes modulares.

    Returns:
        tuple: (calendar_data, conab_data)
    """
    # Carregar dados com spinner
    with st.spinner("🔄 Loading agricultural data..."):
        try:
            # Carregar calendário agrícola
            calendar_data = load_conab_crop_calendar()
            
            # Carregar dados detalhados CONAB
            conab_data = load_conab_detailed_data()
            
            return calendar_data, conab_data
            
        except Exception as e:
            st.error(f"❌ Error loading agricultural data: {e}")
            return {}, {}


def _render_overview_tab(calendar_data: dict, conab_data: dict) -> None:
    st.markdown("### 🌍 Brazilian Agriculture Overview")
    st.markdown("*Consolidated view of available agricultural data in the system*")
    render_agricultural_overview(calendar_data, conab_data)
    st.markdown("---")
    st.markdown("#### 📅 Crop Calendar Heatmap")
    fig_heatmap = plot_crop_calendar_heatmap(calendar_data)
    if fig_heatmap:
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.caption("Heatmap showing crop planting and harvesting periods by state and crop.")
    st.markdown("---")
    st.markdown("#### 📊 Monthly Activity Calendar")
    fig_monthly = plot_monthly_activity_calendar(calendar_data)
    if fig_monthly:
        st.plotly_chart(fig_monthly, use_container_width=True)
        st.caption("Monthly activity calendar summarizing crop activities across Brazil.")

def _render_agricultural_calendar_tab(calendar_data: dict) -> None:
    if not calendar_data:
        st.warning("⚠️ No agricultural calendar data available.")
        return
    st.markdown("### 🗓️ Interactive Agricultural Calendar")
    st.markdown("*Explore planting and harvesting periods for major Brazilian crops*")
    states_data, crops_data, years_data = _extract_calendar_filters(calendar_data)
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_states = st.multiselect(
            "🗺️ Select States",
            options=states_data,
            default=states_data[:8] if len(states_data) > 8 else states_data,
            help="Select states to include in the analysis",
        )
    with col2:
        selected_crops = st.multiselect(
            "🌱 Select Crops",
            options=crops_data,
            default=crops_data[:6] if len(crops_data) > 6 else crops_data,
            help="Select crops to include in the calendar",
        )
    with col3:
        selected_years = st.multiselect(
            "📅 Select Years",
            options=years_data,
            default=years_data[-3:] if len(years_data) >= 3 else years_data,
            help="Select years for temporal analysis",
        )
    if selected_states and selected_crops and selected_years:
        try:
            filtered_data = _filter_calendar_data(
                calendar_data, selected_states, selected_crops, selected_years
            )
            fig_heatmap = plot_crop_calendar_heatmap(filtered_data)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)
                st.caption("Filtered crop calendar heatmap.")
            st.markdown("---")
            st.markdown("#### 📊 Monthly Activity Calendar")
            fig_monthly = plot_monthly_activity_calendar(calendar_data, selected_crops)
            if fig_monthly:
                st.plotly_chart(fig_monthly, use_container_width=True)
                st.caption("Monthly activity calendar for selected crops.")
        except Exception as e:
            st.error(f"Error creating calendar charts: {e}")
    else:
        st.info("👆 Please select states, crops, and years to display the calendar")


def _render_conab_analysis_tab(conab_data: dict) -> None:
    if not conab_data:
        st.warning("⚠️ No CONAB data available.")
        return
    st.markdown("### 🌾 CONAB - National Supply Company")
    st.markdown("*Specialized analysis of crop monitoring data*")
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    stats = get_conab_crop_stats(conab_data)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Coverage", value=stats.get('coverage_area', 'N/A'))
    with col2:
        st.metric(label="Resolution", value=stats.get('resolution', 'N/A'))
    with col3:
        years_span = f"{stats['temporal_span']} years" if stats['temporal_span'] > 0 else "N/A"
        st.metric(label="Temporal Span", value=years_span)
    with col4:
        st.metric(label="Crops", value=stats.get('total_crops', 0))
    with col5:
        accuracy = f"{stats['accuracy']:.1f}%" if stats['accuracy'] > 0 else "N/A"
        st.metric(label="Accuracy", value=accuracy)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🗺️ Spatial Coverage")
        try:
            fig_spatial = plot_conab_spatial_coverage(conab_data)
            if fig_spatial:
                st.plotly_chart(fig_spatial, use_container_width=True)
                st.caption("Spatial coverage of monitored crops across Brazilian regions.")
        except Exception as e:
            st.error(f"Error creating spatial coverage chart: {e}")
    with col2:
        st.markdown("#### ⏳ Temporal Coverage")
        try:
            fig_temporal = plot_conab_temporal_coverage(conab_data)
            if fig_temporal:
                st.plotly_chart(fig_temporal, use_container_width=True)
                st.caption("Temporal evolution of crop monitoring coverage.")
        except Exception as e:
            st.error(f"Error creating temporal coverage chart: {e}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🌱 Crop Diversity")
        try:
            fig_diversity = plot_conab_crop_diversity(conab_data)
            if fig_diversity:
                st.plotly_chart(fig_diversity, use_container_width=True)
                st.caption("Diversity of crops monitored by CONAB.")
        except Exception as e:
            st.error(f"Error creating crop diversity chart: {e}")
    with col2:
        st.markdown("#### 🔄 Seasonal Analysis")
        try:
            fig_seasonal = plot_conab_seasonal_analysis(conab_data)
            if fig_seasonal:
                st.plotly_chart(fig_seasonal, use_container_width=True)
                st.caption("Analysis of single and double cropping regions.")
        except Exception as e:
            st.error(f"Error creating seasonal analysis chart: {e}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 Quality Metrics")
        try:
            fig_quality = plot_conab_quality_metrics(conab_data)
            if fig_quality:
                st.plotly_chart(fig_quality, use_container_width=True)
                st.caption("Quality metrics for CONAB data completeness and accuracy.")
        except Exception as e:
            st.error(f"Error creating quality metrics: {e}")
    with col2:
        st.markdown("#### 📈 Production Trends")
        try:
            from components.agricultural_analysis.charts.conab_charts import plot_conab_crop_production_trends
            fig_prod = plot_conab_crop_production_trends(conab_data)
            if fig_prod:
                st.plotly_chart(fig_prod, use_container_width=True)
                st.caption("Trends in crop production over time.")
        except Exception as e:
            st.error(f"Error creating production trends chart: {e}")
    st.markdown("---")
    st.markdown("#### 🧪 Methodology Overview")
    try:
        fig_method = plot_conab_methodology_overview(conab_data)
        if fig_method:
            st.plotly_chart(fig_method, use_container_width=True)
            st.caption("Overview of CONAB monitoring methodology.")
    except Exception as e:
        st.error(f"Error creating methodology overview chart: {e}")



if __name__ == "__main__":
    run()
