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
    plot_crop_seasons_comparison
)

from .charts.conab_charts import (
    plot_conab_spatial_coverage,
    plot_conab_temporal_coverage,
    plot_conab_crop_diversity,
    plot_conab_spatial_temporal_distribution,
    plot_conab_quality_metrics,
    plot_conab_seasonal_analysis,
    plot_conab_methodology_overview,
    plot_conab_crop_production_trends
)

# Overview components  
from .agriculture_overview.agricultural_overview import render_agricultural_overview
from .agriculture_overview.overview_data import (
    get_agricultural_overview_stats,
    get_crops_overview_data,
    get_states_summary
)

# Charts module
from .charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar,
    plot_crop_seasons_comparison,
    plot_conab_spatial_coverage,
    plot_conab_temporal_coverage,
    plot_conab_crop_diversity,
    plot_conab_spatial_temporal_distribution,
    plot_conab_quality_metrics,
    plot_conab_seasonal_analysis,
    plot_conab_methodology_overview,
    plot_conab_crop_production_trends
)

__all__ = [
    # Charts
    "plot_crop_calendar_heatmap",
    "plot_monthly_activity_calendar",
    "plot_crop_seasons_comparison",
    "plot_conab_spatial_coverage",
    "plot_conab_temporal_coverage",
    "plot_conab_crop_diversity",
    "plot_conab_spatial_temporal_distribution",
    "plot_conab_quality_metrics",
    "plot_conab_seasonal_analysis",
    "plot_conab_methodology_overview",
    "plot_conab_crop_production_trends",
    
    # Overview functions
    "render_agricultural_overview",
    "get_agricultural_overview_stats",
    "get_crops_overview_data",
    "get_states_summary"
]