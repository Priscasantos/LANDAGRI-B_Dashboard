#!/usr/bin/env python3
"""
Charts Package
==============

Modular chart generation functions organized by category.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

# Import all chart functions for easy access
from .comparison_charts import plot_class_diversity_focus  # New
from .comparison_charts import plot_classification_methodology  # New
from .comparison_charts import plot_global_accuracy_comparison  # New
from .comparison_charts import (
    plot_resolution_accuracy_scatter,  # Corrected: This was plot_scatter_resolution_accuracy
)
from .comparison_charts import plot_spatial_resolution_comparison  # New
from .comparison_charts import plot_temporal_evolution_frequency  # New
from .comparison_charts import (
    plot_comparison_matrix,
    plot_correlation_matrix,
    plot_initiative_ranking,
    plot_radar_comparison,
)
from .coverage_charts import (
    plot_annual_coverage_multiselect,
    plot_ano_overlap,
    plot_heatmap,
)
from .distribution_charts import (
    plot_classes_por_iniciativa,  # This might be what was intended for plot_classes_frequency_boxplot
)
from .distribution_charts import (
    plot_acuracia_por_metodologia,
    plot_distribuicao_classes,
    plot_distribuicao_metodologias,
    plot_resolution_accuracy,
)
from .resolution_comparison_charts import (
    plot_initiatives_by_resolution_category,
    plot_resolution_by_sensor_family,
    plot_resolution_coverage_heatmap,
    plot_resolution_slopegraph,
    plot_resolution_vs_launch_year,
)
from .temporal_charts import (
    plot_coverage_heatmap_chart,
    plot_evolution_heatmap_chart,
    plot_evolution_line_chart,
    plot_gaps_bar_chart,
    plot_timeline_chart,
    timeline_with_controls,
)

__all__ = [
    # Timeline charts
    "plot_timeline_chart",  # Updated to plot_timeline_chart
    "timeline_with_controls",
    "plot_coverage_heatmap_chart",
    "plot_gaps_bar_chart",
    "plot_evolution_line_chart",
    "plot_evolution_heatmap_chart",
    # Coverage charts
    "plot_annual_coverage_multiselect",
    "plot_ano_overlap",
    "plot_heatmap",
    # Distribution charts
    "plot_distribuicao_classes",
    "plot_classes_por_iniciativa",
    "plot_distribuicao_metodologias",
    "plot_acuracia_por_metodologia",
    "plot_resolution_accuracy",
    # Comparison charts  # Added this section comment for clarity
    "plot_resolution_accuracy_scatter",  # Corrected: This was plot_scatter_resolution_accuracy
    "plot_comparison_matrix",
    "plot_initiative_ranking",
    "plot_correlation_matrix",
    "plot_radar_comparison",
    "plot_spatial_resolution_comparison",  # New
    "plot_global_accuracy_comparison",  # New
    "plot_temporal_evolution_frequency",  # New
    "plot_class_diversity_focus",  # New
    "plot_classification_methodology",  # New
    # Resolution Comparison Charts
    "plot_resolution_vs_launch_year",
    "plot_initiatives_by_resolution_category",
    "plot_resolution_coverage_heatmap",
    "plot_resolution_by_sensor_family",
    "plot_resolution_slopegraph",
]
