"""
Comparison Analysis Components
=============================

Componentes modulares para análise comparativa de iniciativas LULC.
Cada componente corresponde a uma aba específica da análise comparativa.
"""


from .accuracy_resolution_component import render_accuracy_resolution_tab
from .distributions_component import render_distributions_tab
from .performance_heatmap_component import render_performance_heatmap_tab
from .detailed_table_component import render_detailed_table_tab
from .class_details_component import render_class_details_tab
from .methodology_deepdive_component import render_methodology_deepdive_tab

__all__ = [
    "render_accuracy_resolution_tab",
    "render_distributions_tab",
    "render_performance_heatmap_tab",
    "render_detailed_table_tab",
    "render_class_details_tab",
    "render_methodology_deepdive_tab",
]
