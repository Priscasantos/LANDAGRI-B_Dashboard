"""
Agricultural Analysis Module
===========================

Module for agricultural data analysis and crop calendar.
Modular structure following PEP8.

Author: Dashboard Iniciativas LULC
Date: 2025-08-05
"""

from .charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar,
    plot_crop_seasons_comparison
)

# Commented out non-existent module
# from .charts.conab_charts import (
#     plot_conab_spatial_coverage,
#     plot_conab_temporal_coverage,
#     plot_conab_crop_diversity,
#     plot_conab_spatial_temporal_distribution,
#     validate_conab_data,
#     get_conab_summary_stats
# )

# Overview components
from .agriculture_overview.agricultural_overview import render_agricultural_overview
from .agriculture_overview.overview_data import (
    get_agricultural_overview_stats,
    get_crops_overview_data,
    get_states_summary
)

# Availability components
from .charts.availability import (
    render_calendar_availability_analysis,
    render_conab_availability_analysis,
    create_conab_availability_matrix
)

# Calendar components
from .charts.calendar import render_complete_calendar_analysis

__all__ = [
    # Charts
    "plot_crop_calendar_heatmap",
    "plot_monthly_activity_calendar",
    "plot_crop_seasons_comparison",
    
    # Overview functions
    "render_agricultural_overview",
    "get_agricultural_overview_stats",
    "get_crops_overview_data",
    "get_states_summary",
    
    # Availability functions
    "render_calendar_availability_analysis",
    "render_conab_availability_analysis",
    "create_conab_availability_matrix",
    
    # Calendar functions
    "render_complete_calendar_analysis"
]