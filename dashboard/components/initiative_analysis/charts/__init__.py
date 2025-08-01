"""
Initiative Analysis Charts Package
=================================

Gráficos específicos para análise de iniciativas LULC.
Organização modular por tipo de análise.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

# Temporal Analysis Charts
# Comparison Analysis Charts
from .comparison_charts import (
    plot_accuracy_resolution_scatter,
    plot_correlation_matrix,
    plot_methodology_comparison,
    plot_performance_radar,
    plot_spatial_resolution_comparison,
    plot_temporal_coverage_comparison,
)

# Detailed Analysis Charts
from .detailed_charts import (
    create_distribution_plot,
    create_dual_bars_chart,
    create_heatmap_chart,
    create_radar_chart,
)
from .temporal_charts import (
    plot_coverage_gaps_chart,
    plot_temporal_availability_heatmap,
    plot_temporal_evolution_frequency,
    plot_timeline_chart,
)

__all__ = [
    # Temporal Charts
    "plot_temporal_evolution_frequency",
    "plot_timeline_chart",
    "plot_coverage_gaps_chart",
    "plot_temporal_availability_heatmap",
    # Comparison Charts
    "plot_accuracy_resolution_scatter",
    "plot_methodology_comparison",
    "plot_temporal_coverage_comparison",
    "plot_performance_radar",
    "plot_spatial_resolution_comparison",
    "plot_correlation_matrix",
    # Detailed Charts
    "create_dual_bars_chart",
    "create_radar_chart",
    "create_heatmap_chart",
    "create_distribution_plot",
]
