"""
Calendar Charts Module - Consolidated from old_calendar
======================================================

Módulos consolidados de gráficos de calendário agrícola do old_calendar.
Cada tipo de análise é implementado em seu próprio módulo para melhor organização.

Módulos Disponíveis:
-------------------
- crop_distribution_charts: Distribuição e diversidade de culturas
- monthly_activity_charts: Atividades mensais e comparações temporais  
- national_calendar_matrix: Matrizes e heatmaps nacionais
- timeline_charts: Timelines e sazonalidade
- regional_calendar_charts: Análises regionais detalhadas
- enhanced_calendar_heatmap: Heatmap aprimorado (existente)
- activity_intensity: Análise de intensidade (existente)
- temporal_analysis: Análise temporal (existente)
- seasonality_analysis: Análise de sazonalidade (existente)
- regional_analysis: Análise regional básica (existente)
- polar_activity_chart: Gráfico polar de atividades (existente)
- interactive_timeline: Timeline interativo (existente)
- enhanced_statistics: Estatísticas aprimoradas (existente)
- additional_analysis: Análises adicionais (existente)

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

# Importações dos módulos consolidados do old_calendar
from .crop_distribution_charts import (
    create_crop_type_distribution_chart,
    create_crop_diversity_by_region_chart,
    create_number_of_crops_per_region_chart,
    render_crop_distribution_charts
)

from .monthly_activity_charts import (
    create_total_activities_per_month_chart,
    create_planting_vs_harvesting_per_month_chart,
    create_simultaneous_planting_harvesting_chart,
    create_planting_harvesting_periods_chart,
    render_monthly_activity_charts
)

from .national_calendar_matrix import (
    create_consolidated_calendar_matrix_chart,
    create_calendar_heatmap_chart,
    create_regional_activity_comparison_chart,
    render_national_calendar_matrix_charts
)

from .timeline_charts import (
    create_timeline_activities_chart,
    create_monthly_activities_timeline_chart,
    create_main_crops_seasonality_chart,
    render_timeline_charts
)

from .regional_calendar_charts import (
    create_regional_heatmap_chart,
    create_regional_diversity_chart,
    create_regional_seasonal_chart,
    create_regional_timeline_chart,
    render_regional_analysis_for_region,
    render_all_regional_analysis,
    get_region_states,
    filter_data_by_region
)

# Importações dos módulos existentes
from .enhanced_calendar_heatmap import create_enhanced_calendar_heatmap
from .activity_intensity import *
from .temporal_analysis import *
from .seasonality_analysis import *
from .regional_analysis import *
from .polar_activity_chart import *
from .interactive_timeline import *
from .enhanced_statistics import *
from .additional_analysis import *


def render_complete_calendar_analysis(filtered_data: dict) -> None:
    """
    Renderiza análise completa consolidada do calendário agrícola.
    
    Inclui todos os gráficos consolidados do old_calendar organizados
    em seções lógicas para análise abrangente.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    import streamlit as st
    
    st.markdown("## 📅 Análise Completa do Calendário Agrícola")
    st.markdown("*Gráficos consolidados do old_calendar organizados modularmente*")
    
    # Seção 1: Distribuição e Diversidade
    with st.expander("🌾 Distribuição e Diversidade de Culturas", expanded=True):
        render_crop_distribution_charts(filtered_data)
    
    # Seção 2: Atividades Mensais
    with st.expander("📅 Análise de Atividades Mensais", expanded=False):
        render_monthly_activity_charts(filtered_data)
    
    # Seção 3: Matriz Nacional
    with st.expander("🗓️ Matriz Nacional do Calendário", expanded=False):
        render_national_calendar_matrix_charts(filtered_data)
    
    # Seção 4: Timeline e Sazonalidade
    with st.expander("⏰ Timeline e Sazonalidade", expanded=False):
        render_timeline_charts(filtered_data)
    
    # Seção 5: Análise Regional Detalhada
    with st.expander("🌍 Análise Regional Detalhada", expanded=False):
        render_all_regional_analysis(filtered_data)
    
    # Seção 6: Análises Avançadas (componentes existentes)
    with st.expander("🔬 Análises Avançadas", expanded=False):
        st.markdown("#### 🔥 Heatmap Aprimorado")
        create_enhanced_calendar_heatmap(filtered_data)


__all__ = [
    # Funções consolidadas do old_calendar
    'render_complete_calendar_analysis',
    'render_crop_distribution_charts',
    'render_monthly_activity_charts', 
    'render_national_calendar_matrix_charts',
    'render_timeline_charts',
    'render_all_regional_analysis',
    'render_regional_analysis_for_region',
    
    # Funções individuais de distribuição
    'create_crop_type_distribution_chart',
    'create_crop_diversity_by_region_chart',
    'create_number_of_crops_per_region_chart',
    
    # Funções individuais de atividades mensais
    'create_total_activities_per_month_chart',
    'create_planting_vs_harvesting_per_month_chart',
    'create_simultaneous_planting_harvesting_chart',
    'create_planting_harvesting_periods_chart',
    
    # Funções individuais de matriz nacional
    'create_consolidated_calendar_matrix_chart',
    'create_calendar_heatmap_chart',
    'create_regional_activity_comparison_chart',
    
    # Funções individuais de timeline
    'create_timeline_activities_chart',
    'create_monthly_activities_timeline_chart',
    'create_main_crops_seasonality_chart',
    
    # Funções individuais regionais
    'create_regional_heatmap_chart',
    'create_regional_diversity_chart',
    'create_regional_seasonal_chart',
    'create_regional_timeline_chart',
    'get_region_states',
    'filter_data_by_region',
    
    # Funções existentes
    'create_enhanced_calendar_heatmap'
]
