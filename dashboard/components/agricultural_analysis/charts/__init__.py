"""
Agricultural Analysis Charts Module
==================================

Módulo de gráficos para análise agrícola.
Centraliza todas as funções de visualização de dados agrícolas e CONAB.

Autor: LANDAGRI-B Project Team 
Data: 2025-08-07
"""

# Importações dos módulos de gráficos principais
from .agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar,
    plot_crop_seasons_comparison
)

# Importações do módulo de calendário
from .calendar import (
    create_monthly_activities_stacked_bar_chart
)

__all__ = [
    # Agricultural charts
    'plot_crop_calendar_heatmap',
    'plot_monthly_activity_calendar',
    'plot_crop_seasons_comparison',
    
    # Calendar charts
    'create_monthly_activities_stacked_bar_chart',
    
]
