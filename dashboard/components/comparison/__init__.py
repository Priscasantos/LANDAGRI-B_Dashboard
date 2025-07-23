"""
Componentes para a página de Comparação
=======================================

Este pacote contém os componentes modulares para a análise comparativa
de iniciativas LULC.
"""

from .filters import apply_comparison_filters, render_comparison_filters
from .plotting_imports import get_plotting_placeholders, import_plotting_functions
from .tab_charts import (
    render_class_details_tab,
    render_class_diversity_tab,
    render_global_accuracy_tab,
    render_methodology_details_tab,
    render_methodology_distribution_tab,
    render_normalized_performance_tab,
    render_resolution_analysis_tab,
    render_spatial_resolution_tab,
    render_temporal_evolution_tab,
)

__all__ = [
    "render_comparison_filters",
    "apply_comparison_filters",
    "import_plotting_functions",
    "get_plotting_placeholders",
    "render_spatial_resolution_tab",
    "render_global_accuracy_tab",
    "render_temporal_evolution_tab",
    "render_class_diversity_tab",
    "render_methodology_distribution_tab",
    "render_resolution_analysis_tab",
    "render_class_details_tab",
    "render_methodology_details_tab",
    "render_normalized_performance_tab",
]
