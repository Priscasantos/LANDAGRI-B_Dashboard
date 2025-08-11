"""
Availability Charts Package
===========================

Modules for crop availability analysis.
Includes agricultural calendar and CONAB data analysis.
"""

from .calendar_availability_analysis import render_calendar_availability_analysis
from .conab_availability_analysis import render_conab_availability_analysis
from .conab_availability_matrix import create_conab_availability_matrix
from .conab_specific_charts import render_conab_charts_tab
from .spatial_coverage import plot_conab_spatial_coverage, plot_conab_spatial_coverage_by_state, plot_conab_spatial_coverage_by_region
from .crop_diversity import plot_conab_crop_diversity, plot_conab_crop_diversity_by_state, plot_conab_crop_diversity_by_region
from .seasonal_patterns import (
    plot_seasonal_patterns,
    plot_crop_seasonal_distribution,
    plot_monthly_activity_intensity
)
from .regional_activity import (
    plot_regional_activity_comparison,
    plot_state_activity_heatmap,
    plot_regional_crop_specialization,
    plot_activity_timeline_by_region
)
from .activity_intensity import (
    plot_activity_intensity_matrix,
    plot_peak_activity_analysis,
    plot_activity_density_map,
    plot_activity_concentration_index
)

__all__ = [
    "render_calendar_availability_analysis",
    "render_conab_availability_analysis",
    "create_conab_availability_matrix",
    "render_conab_charts_tab",
    "plot_conab_spatial_coverage",
    "plot_conab_spatial_coverage_by_state",
    "plot_conab_spatial_coverage_by_region",
    "plot_conab_crop_diversity",
    "plot_conab_crop_diversity_by_state",
    "plot_conab_crop_diversity_by_region",
    "plot_seasonal_patterns",
    "plot_crop_seasonal_distribution",
    "plot_monthly_activity_intensity",
    "plot_regional_activity_comparison",
    "plot_state_activity_heatmap",
    "plot_regional_crop_specialization",
    "plot_activity_timeline_by_region",
    "plot_activity_intensity_matrix",
    "plot_peak_activity_analysis",
    "plot_activity_density_map",
    "plot_activity_concentration_index"
]
