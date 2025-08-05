"""
Agricultural Analysis Module
===========================

Módulo para análise de dados agrícolas e calendário de culturas.
Estrutura modular seguindo PEP8.

Author: Dashboard Iniciativas LULC
Date: 2025-08-05
"""

from .charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar,
    plot_conab_spatial_coverage,
    plot_conab_temporal_coverage,
    plot_conab_crop_diversity,
    plot_conab_spatial_temporal_distribution,
    plot_crop_seasons_comparison
)

# Overview components
from .overview.agricultural_overview import render_agricultural_overview
from .overview.overview_data import (
    get_agricultural_overview_stats,
    get_crops_overview_data,
    get_states_summary
)

# Calendar components
from .calendar_data import (
    get_calendar_heatmap_data,
    get_crop_seasons_calendar,
    get_monthly_activity_summary,
    get_regional_calendar_patterns
)

# Availability components
from .availability_data import (
    get_data_availability_status,
    get_data_quality_metrics,
    get_spatial_coverage_status,
    get_temporal_coverage_analysis,
    get_data_access_information
)

# New specialized components
from .crop_availability import render_crop_availability
from .agricultural_calendar import run as render_agricultural_calendar  
from .conab_analysis import run as render_conab_analysis

__all__ = [
    # Charts
    "plot_crop_calendar_heatmap",
    "plot_monthly_activity_calendar",
    "plot_conab_spatial_coverage",
    "plot_conab_temporal_coverage",
    "plot_conab_crop_diversity",
    "plot_conab_spatial_temporal_distribution",
    "plot_crop_seasons_comparison",
    
    # Overview functions
    "render_agricultural_overview",
    "get_agricultural_overview_stats",
    "get_crops_overview_data",
    "get_states_summary",
    
    # Calendar functions
    "get_calendar_heatmap_data",
    "get_crop_seasons_calendar",
    "get_monthly_activity_summary",
    "get_regional_calendar_patterns",
    
    # Availability functions
    "get_data_availability_status",
    "get_data_quality_metrics",
    "get_spatial_coverage_status",
    "get_temporal_coverage_analysis",
    "get_data_access_information",
    
    # Specialized components
    "render_crop_availability",
    "render_agricultural_calendar",
    "render_conab_analysis"
]
