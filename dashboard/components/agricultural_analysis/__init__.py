"""
Agricultural Analysis Module
===========================

Módulo para análise de dados agrícolas e calendário de culturas.
Estrutura modular seguindo PEP8.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

from .charts.agricultural_charts import (
    create_agricultural_summary_stats,
    load_conab_data,
    plot_agricultural_performance_metrics,
    plot_crop_calendar_heatmap,
    plot_crop_diversity_by_region,
    plot_regional_crop_coverage,
    plot_temporal_crop_trends,
)

__all__ = [
    "load_conab_data",
    "plot_crop_calendar_heatmap",
    "plot_regional_crop_coverage",
    "plot_temporal_crop_trends",
    "plot_crop_diversity_by_region",
    "plot_agricultural_performance_metrics",
    "create_agricultural_summary_stats",
]
