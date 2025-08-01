"""
Detailed Analysis Components
===========================

Componentes modulares para análise detalhada de iniciativas LULC.
Cada componente corresponde a uma aba específica da análise detalhada.
"""

from .dual_bars_component import render_dual_bars_tab
from .radar_chart_component import render_radar_chart_tab
from .heatmap_component import render_heatmap_tab
from .data_table_component import render_data_table_tab
from .annual_coverage_component import render_annual_coverage_tab

__all__ = [
    "render_dual_bars_tab",
    "render_radar_chart_tab",
    "render_heatmap_tab",
    "render_data_table_tab",
    "render_annual_coverage_tab",
]
