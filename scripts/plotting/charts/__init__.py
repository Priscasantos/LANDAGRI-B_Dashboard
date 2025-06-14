#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Charts Package
==============

Modular chart generation functions organized by category.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

# Import all chart functions for easy access
from .timeline_chart import plot_timeline, timeline_with_controls
from .coverage_charts import plot_annual_coverage_multiselect, plot_ano_overlap, plot_heatmap
from .distribution_charts import (
    plot_distribuicao_classes, 
    plot_classes_por_iniciativa, 
    plot_distribuicao_metodologias,
    plot_acuracia_por_metodologia,
    plot_resolution_accuracy
)
from .comparison_charts import (
    plot_scatter_resolution_accuracy,
    plot_comparison_matrix,
    plot_initiative_ranking,
    plot_correlation_matrix,
    plot_radar_comparison
)

__all__ = [
    # Timeline charts
    'plot_timeline',
    'timeline_with_controls',
    # Coverage charts
    'plot_annual_coverage_multiselect', 
    'plot_ano_overlap', 
    'plot_heatmap',
    # Distribution charts
    'plot_distribuicao_classes',
    'plot_classes_por_iniciativa',
    'plot_distribuicao_metodologias',
    'plot_acuracia_por_metodologia',
    'plot_resolution_accuracy',    # Comparison charts
    'plot_scatter_resolution_accuracy',
    'plot_comparison_matrix',
    'plot_initiative_ranking',
    'plot_correlation_matrix',
    'plot_radar_comparison'
]
