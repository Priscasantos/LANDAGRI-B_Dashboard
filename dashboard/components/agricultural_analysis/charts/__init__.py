"""
Agricultural Analysis Charts Module
==================================

Módulo de gráficos para análise agrícola.
Centraliza todas as funções de visualização de dados agrícolas e CONAB.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

# Importações dos módulos de gráficos principais
from .agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar,
    plot_crop_seasons_comparison
)

from .conab_charts import (
    plot_conab_spatial_coverage,
    plot_conab_temporal_coverage,
    plot_conab_crop_diversity,
    plot_conab_spatial_temporal_distribution,
    plot_conab_quality_metrics,
    plot_conab_seasonal_analysis,
    plot_conab_methodology_overview,
    plot_conab_crop_production_trends
)

# Importações do módulo de disponibilidade
from .availability import (
    render_crop_availability_tab
)

__all__ = [
    # Agricultural charts
    'plot_crop_calendar_heatmap',
    'plot_monthly_activity_calendar',
    'plot_crop_seasons_comparison',
    
    # CONAB charts
    'plot_conab_spatial_coverage',
    'plot_conab_temporal_coverage',
    'plot_conab_crop_diversity',
    'plot_conab_spatial_temporal_distribution',
    'plot_conab_quality_metrics',
    'plot_conab_seasonal_analysis',
    'plot_conab_methodology_overview',
    'plot_conab_crop_production_trends',
    
    # Availability module
    'render_crop_availability_tab'
]
