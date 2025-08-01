"""
Componentes modulares para análise temporal das iniciativas LULC.
"""


from .timeline_component import render_timeline_tab
from .evolution_analysis_component import render_evolution_analysis
from .coverage_matrix_heatmap_component import render_coverage_matrix_heatmap
from .gaps_analysis_component import render_gaps_analysis

__all__ = [
    "render_timeline_tab",
    "render_evolution_analysis",
    "render_coverage_matrix_heatmap",
    "render_gaps_analysis",
]
