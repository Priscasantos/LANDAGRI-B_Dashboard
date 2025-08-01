"""
Agricultural Analysis Module
===========================

Módulo para análise de dados agrícolas e calendário de culturas.
Estrutura modular seguindo PEP8.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
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

__all__ = [
    "plot_crop_calendar_heatmap",
    "plot_monthly_activity_calendar",
    "plot_conab_spatial_coverage",
    "plot_conab_temporal_coverage",
    "plot_conab_crop_diversity",
    "plot_conab_spatial_temporal_distribution",
    "plot_crop_seasons_comparison"
]
