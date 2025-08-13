"""
Calendar Charts Module - Consolidated from old_calendar
======================================================

Consolidated chart modules from old_calendar agricultural calendar.
Each type of analysis is implemented in its own module for better organization.

Available Modules:
-------------------
- crop_distribution_charts: Crop distribution and diversity
- monthly_activity_charts: Monthly activities and temporal comparisons  
- national_calendar_matrix: National matrices and heatmaps
- timeline_charts: Timelines and seasonality
- regional_calendar_charts: Detailed regional analyses
- enhanced_calendar_heatmap: Enhanced heatmap (existing)
- activity_intensity: Intensity analysis (existing)
- temporal_analysis: Temporal analysis (existing)
- seasonality_analysis: Seasonality analysis (existing)
- regional_analysis: Basic regional analysis (existing)
- polar_activity_chart: Polar activity chart (existing)
- interactive_timeline: Interactive timeline (existing)
- enhanced_statistics: Enhanced statistics (existing)
- additional_analysis: Additional analyses (existing)

Author: LANDAGRI-B Project Team 
Date: 2025-08-07
"""

# Imports from consolidated modules from old_calendar
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
    create_monthly_activities_stacked_bar_chart,
    create_planting_harvesting_periods_chart,
    render_monthly_activity_charts
)

from .national_calendar_matrix import (
    create_consolidated_calendar_matrix_chart,
    create_calendar_heatmap_chart,
    create_regional_activity_comparison_chart,
    render_national_calendar_matrix_charts
)

from .crop_gantt_chart import (
    render_crop_gantt_chart,
    create_gantt_chart_with_filters
)

from .timeline_charts import (
    create_timeline_activities_chart,
    create_monthly_activities_timeline_chart,
    create_main_crops_seasonality_chart
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
    Renders complete consolidated agricultural calendar analysis.
    
    Includes all consolidated old_calendar charts organized
    in logical sections for comprehensive analysis.
    
    Args:
        filtered_data: Filtered agricultural calendar data
    """
    import streamlit as st
    
    st.markdown("## 📅 Complete Agricultural Calendar Analysis")
    st.markdown("*Consolidated old_calendar charts organized modularly*")
    
    # Section 1: Distribution and Diversity
    with st.expander("🌾 Crop Distribution and Diversity", expanded=True):
        render_crop_distribution_charts(filtered_data)
    
    # Section 2: Monthly Activities
    with st.expander("📅 Monthly Activities Analysis", expanded=False):
        render_monthly_activity_charts(filtered_data)

    # Section 3: National Matrix
    with st.expander("🗓️ National Calendar Matrix", expanded=False):
        render_national_calendar_matrix_charts(filtered_data)    # Section 4: Timeline and Seasonality
    with st.expander("⏰ Timeline and Seasonality", expanded=False):
        # Timeline activities chart
        timeline_fig = create_timeline_activities_chart(filtered_data)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("📊 Timeline chart: Insufficient data for visualization")
            
        # Monthly activities timeline
        monthly_timeline_fig = create_monthly_activities_timeline_chart(filtered_data)
        if monthly_timeline_fig:
            st.plotly_chart(monthly_timeline_fig, use_container_width=True)
        else:
            st.info("📊 Monthly timeline: Insufficient data for visualization")
            
        # Main crops seasonality
        seasonality_fig = create_main_crops_seasonality_chart(filtered_data)
        if seasonality_fig:
            st.plotly_chart(seasonality_fig, use_container_width=True)
        else:
            st.info("📊 Seasonality chart: Insufficient data for visualization")
    
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
    'render_all_regional_analysis',
    'render_regional_analysis_for_region',
    
    # Individual distribution functions
    'create_crop_type_distribution_chart',
    'create_crop_diversity_by_region_chart',
    'create_number_of_crops_per_region_chart',
    
    # Funções individuais de atividades mensais
    'create_total_activities_per_month_chart',
    'create_planting_vs_harvesting_per_month_chart',
    'create_simultaneous_planting_harvesting_chart',
    'create_monthly_activities_stacked_bar_chart',
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
