"""
Backward-compatibility shim for agricultural charts.

Many parts of the codebase import `plot_crop_calendar_heatmap`,
`plot_monthly_activity_calendar` and `plot_crop_seasons_comparison`
from `dashboard.components.agricultural_analysis.charts.agricultural_charts`.
During refactors these implementations moved into the `calendar/` subpackage.
This shim re-exports thin wrappers around the new implementations so
old imports continue to work.

Do not add heavy logic here; keep as lightweight wrappers.
"""

from typing import Any, Optional

# Import the current implementations from the calendar subpackage
from .calendar.enhanced_calendar_heatmap import create_enhanced_calendar_heatmap
from .calendar.monthly_activity_charts import create_monthly_activities_stacked_bar_chart
from .calendar.seasonality_analysis import create_seasonality_index_chart


def plot_crop_calendar_heatmap(filtered_data: dict, *args: Any, **kwargs: Any) -> Optional[Any]:
    """Legacy name -> new `create_enhanced_calendar_heatmap`.

    Parameters are forwarded. Return value follows the underlying
    implementation (typically a Plotly Figure or None, or displays
    directly in Streamlit for functions that render).
    """
    return create_enhanced_calendar_heatmap(filtered_data, *args, **kwargs)


def plot_monthly_activity_calendar(filtered_data: dict, *args: Any, **kwargs: Any) -> Optional[Any]:
    """Legacy name -> new `create_monthly_activities_stacked_bar_chart`."""
    return create_monthly_activities_stacked_bar_chart(filtered_data, *args, **kwargs)


def plot_crop_seasons_comparison(filtered_data: dict, *args: Any, **kwargs: Any) -> Optional[Any]:
    """Legacy name -> new `create_seasonality_index_chart`."""
    return create_seasonality_index_chart(filtered_data, *args, **kwargs)


__all__ = [
    'plot_crop_calendar_heatmap',
    'plot_monthly_activity_calendar',
    'plot_crop_seasons_comparison',
]
