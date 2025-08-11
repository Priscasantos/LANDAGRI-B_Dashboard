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
    validate_conab_data,
    get_conab_summary_stats,
    # Timeline functions (consolidated from timeline_charts.py)
    create_timeline_activities_chart,
    create_monthly_activities_timeline_chart,
    create_main_crops_seasonality_chart
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
    'validate_conab_data',
    'get_conab_summary_stats',
    
    # Timeline charts (consolidated)
    'create_timeline_activities_chart',
    'create_monthly_activities_timeline_chart',
    'create_main_crops_seasonality_chart',
    
    # Availability
    'render_crop_availability_tab'
]
