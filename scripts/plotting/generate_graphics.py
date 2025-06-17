#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Graphics Module - Import Hub
=====================================

Central import hub for all chart generation functions.
All chart functions have been modularized into separate files for better organization.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

# Import modularized chart functions
from scripts.plotting.charts.temporal_charts import plot_timeline_chart # Updated to plot_timeline_chart
from scripts.plotting.charts.coverage_charts import plot_annual_coverage_multiselect, plot_ano_overlap, plot_heatmap
from scripts.plotting.charts.distribution_charts import (
    plot_distribuicao_classes, 
    plot_classes_por_iniciativa, 
    plot_distribuicao_metodologias,
    plot_acuracia_por_metodologia,
    plot_resolution_accuracy
)
from scripts.plotting.charts.comparison_charts import (
    plot_resolution_accuracy_scatter, # Corrected name
    plot_comparison_matrix,
    plot_initiative_ranking,
    plot_correlation_matrix,
    plot_radar_comparison,
    plot_spatial_resolution_comparison, # New
    plot_global_accuracy_comparison,    # New
    plot_temporal_evolution_frequency,  # New
    plot_class_diversity_focus,         # New
    plot_classification_methodology,     # New
    plot_classes_frequency_boxplot,      # Added missing import here
    plot_normalized_performance_heatmap # Added import for the new heatmap
)
from scripts.plotting.charts.resolution_comparison_charts import (
    plot_resolution_vs_launch_year,
    plot_initiatives_by_resolution_category,
    plot_resolution_coverage_heatmap,
    plot_resolution_by_sensor_family,
    plot_resolution_slopegraph
)

# Re-export all functions for backward compatibility
__all__ = [
    # Timeline charts
    'plot_timeline_chart', # Updated to plot_timeline_chart
    # Coverage charts
    'plot_annual_coverage_multiselect', 
    'plot_ano_overlap', 
    'plot_heatmap',
    # Distribution charts
    'plot_distribuicao_classes',
    'plot_classes_por_iniciativa',
    'plot_distribuicao_metodologias',
    'plot_acuracia_por_metodologia',
    'plot_resolution_accuracy',
    # Comparison charts
    'plot_resolution_accuracy_scatter', # Corrected name
    'plot_comparison_matrix',
    'plot_initiative_ranking',
    'plot_correlation_matrix',
    'plot_radar_comparison',
    'plot_spatial_resolution_comparison', # New
    'plot_global_accuracy_comparison',    # New
    'plot_temporal_evolution_frequency',  # New
    'plot_class_diversity_focus',         # New
    'plot_classification_methodology',    # New
    'plot_classes_frequency_boxplot',      # Added to __all__
    'plot_normalized_performance_heatmap', # Added to __all__
    # Resolution Comparison Charts
    'plot_resolution_vs_launch_year',
    'plot_initiatives_by_resolution_category',
    'plot_resolution_coverage_heatmap',
    'plot_resolution_by_sensor_family',
    'plot_resolution_slopegraph'
]