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
from components.agricultural_analysis.overview.agricultural_overview import (
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


def _create_conab_availability_matrix(conab_data: dict):
    """Criar matriz de disponibilidade personalizada para dados CONAB."""
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Preparar dados para a matriz
        matrix_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Combinar todas as regiões
            all_regions = set(first_crop_years.keys()) | set(second_crop_years.keys())
            
            for region in all_regions:
                first_years = first_crop_years.get(region, [])
                second_years = second_crop_years.get(region, [])
                
                # Calcular disponibilidade
                has_first = len(first_years) > 0
                has_second = len(second_years) > 0
                
                availability_score = 0
                if has_first and has_second:
                    availability_score = 2  # Dupla safra
                elif has_first:
                    availability_score = 1  # Safra única
                
                matrix_data.append({
                    'crop': crop,
                    'region': region,
                    'availability': availability_score,
                    'years_coverage': len(set(first_years + second_years))
                })
        
        if not matrix_data:
            return None
        
        df_matrix = pd.DataFrame(matrix_data)
        
        # Criar pivot para heatmap
        pivot_matrix = df_matrix.pivot(index='crop', columns='region', values='availability')
        pivot_matrix = pivot_matrix.fillna(0)
        
        # Criar heatmap
        fig = px.imshow(
            pivot_matrix.values,
            x=pivot_matrix.columns,
            y=pivot_matrix.index,
            color_continuous_scale=['white', 'lightblue', 'darkblue'],
            title="Matriz de Disponibilidade CONAB (0=Sem dados, 1=Safra única, 2=Dupla safra)",
            labels={'x': 'Região', 'y': 'Cultura', 'color': 'Disponibilidade'}
        )
        
        fig.update_layout(
            height=max(400, len(pivot_matrix.index) * 30),
            xaxis_tickangle=45
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro criando matriz de disponibilidade: {e}")
        return None


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
        _render_crop_availability_tab(calendar_data, conab_data)


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


def _render_crop_availability_tab(calendar_data: dict, conab_data: dict) -> None:
    st.markdown("### 🌾 Crop Availability by Region and Period")
    st.markdown("*Detailed analysis of crop temporal and spatial availability*")
    if not calendar_data and not conab_data:
        st.warning("⚠️ No crop availability data available.")
        return
    data_source = st.radio(
        "📊 Select data source:",
        ["Agricultural Calendar", "CONAB Data", "Both"],
        index=2,
        horizontal=True
    )
    st.markdown("---")
    if data_source in ["Agricultural Calendar", "Both"] and calendar_data:
        st.markdown("#### 📅 Calendar Availability")
        _render_calendar_availability_analysis(calendar_data)
        st.markdown("---")
        st.markdown("#### 📊 Monthly Activity Calendar")
        fig_monthly = plot_monthly_activity_calendar(calendar_data)
        if fig_monthly:
            st.plotly_chart(fig_monthly, use_container_width=True)
            st.caption("Monthly activity calendar summarizing crop activities across Brazil.")
    if data_source in ["CONAB Data", "Both"] and conab_data:
        st.markdown("---")
        st.markdown("#### 🌾 CONAB Availability")
        _render_conab_availability_analysis(conab_data)
        st.markdown("---")
        st.markdown("#### 🗺️ Spatial-Temporal Distribution")
        try:
            fig_integrated = plot_conab_spatial_temporal_distribution(conab_data)
            if fig_integrated:
                st.plotly_chart(fig_integrated, use_container_width=True)
                st.caption("Spatial-temporal distribution of crop availability across regions and years.")
        except Exception as e:
            st.error(f"Error creating integrated analysis: {e}")


def _render_calendar_availability_analysis(calendar_data: dict) -> None:
    """Renderizar análise de disponibilidade do calendário."""
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        states_info = calendar_data.get('states', {})
        
        if not crop_calendar:
            st.info("📊 No calendar data available for availability analysis")
            return

        # Preparar dados de disponibilidade
        availability_data = []
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_code = state_entry.get('state_code', '')
                state_name = state_entry.get('state_name', state_code)
                calendar_entry = state_entry.get('calendar', {})
                
                # Contar meses com atividade
                active_months = sum(1 for activity in calendar_entry.values() if activity)
                planting_months = sum(1 for activity in calendar_entry.values() if 'P' in activity)
                harvest_months = sum(1 for activity in calendar_entry.values() if 'H' in activity)
                
                availability_data.append({
                    'crop': crop,
                    'state': state_name,
                    'state_code': state_code,
                    'active_months': active_months,
                    'planting_months': planting_months,
                    'harvest_months': harvest_months,
                    'availability_score': active_months / 12.0  # Normalizar para 0-1
                })

        if availability_data:
            df_availability = pd.DataFrame(availability_data)
            
            # Gráfico de disponibilidade por estado
            col1, col2 = st.columns(2)
            
            with col1:
                # Disponibilidade média por estado
                state_avg = df_availability.groupby('state')['availability_score'].mean().reset_index()
                state_avg = state_avg.sort_values('availability_score', ascending=False)
                
                fig_state = px.bar(
                    state_avg.head(15),
                    x='availability_score',
                    y='state',
                    orientation='h',
                    title="Score de Disponibilidade por Estado",
                    labels={'availability_score': 'Score de Disponibilidade', 'state': 'Estado'}
                )
                st.plotly_chart(fig_state, use_container_width=True)
            
            with col2:
                # Disponibilidade por cultura
                crop_avg = df_availability.groupby('crop')['availability_score'].mean().reset_index()
                crop_avg = crop_avg.sort_values('availability_score', ascending=False)
                
                fig_crop = px.bar(
                    crop_avg,
                    x='crop',
                    y='availability_score',
                    title="Score de Disponibilidade por Cultura",
                    labels={'availability_score': 'Score de Disponibilidade', 'crop': 'Cultura'}
                )
                fig_crop.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_crop, use_container_width=True)

            # Tabela de resumo
            st.markdown("##### 📋 Resumo da Disponibilidade")
            summary_stats = df_availability.groupby('crop').agg({
                'state': 'count',
                'active_months': 'mean',
                'availability_score': 'mean'
            }).round(2)
            summary_stats.columns = ['Estados Cobertos', 'Meses Ativos (Média)', 'Score Disponibilidade']
            st.dataframe(summary_stats, use_container_width=True)

    except Exception as e:
        st.error(f"Erro na análise de disponibilidade do calendário: {e}")


def _render_conab_availability_analysis(conab_data: dict) -> None:
    """Renderizar análise de disponibilidade CONAB."""
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            st.info("📊 No CONAB data available for availability analysis")
            return

        # Análise de matriz de disponibilidade
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🗺️ Matriz de Disponibilidade")
            try:
                # Criar matriz de disponibilidade personalizada
                fig_matrix = _create_conab_availability_matrix(conab_data)
                if fig_matrix:
                    st.plotly_chart(fig_matrix, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating availability matrix: {e}")
        
        with col2:
            st.markdown("##### 🔄 Análise de Dupla Safra")
            
            # Análise de dupla safra
            double_crop_data = []
            
            for crop, crop_data in detailed_coverage.items():
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                first_regions = len([r for r, years in first_crop_years.items() if years])
                second_regions = len([r for r, years in second_crop_years.items() if years])
                
                double_crop_data.append({
                    'crop': crop,
                    'single_crop': first_regions - second_regions if first_regions > second_regions else 0,
                    'double_crop': second_regions
                })
            
            if double_crop_data:
                df_double = pd.DataFrame(double_crop_data)
                
                fig_double = px.bar(
                    df_double,
                    x='crop',
                    y=['single_crop', 'double_crop'],
                    title="Regiões com Safra Única vs Dupla Safra",
                    barmode='stack'
                )
                fig_double.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_double, use_container_width=True)

    except Exception as e:
        st.error(f"Erro na análise de disponibilidade CONAB: {e}")


if __name__ == "__main__":
    run()