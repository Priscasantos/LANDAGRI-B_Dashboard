"""
Chart Core Utilities
===================

Core utilities for chart processing and data transformation.

Author: LANDAGRI-B Project Team 
Date: 2025-07-30
"""

import pandas as pd


def add_display_names_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add display names to DataFrame for better visualization.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with display names added
    """
    # Simple implementation - just return the original DataFrame
    # This can be expanded with actual display name logic if needed
    return df.copy()


def apply_chart_styling(fig):
    """
    Apply consistent styling to charts.

    Args:
        fig: Plotly figure object

    Returns:
        Styled figure
    """
    return fig


def apply_standard_layout(fig, title: str = "", **kwargs):
    """
    Apply standard layout to Plotly figures.

    Args:
        fig: Plotly figure object
        title: Chart title
        **kwargs: Additional layout parameters

    Returns:
        Figure with standard layout applied
    """
    standard_layout = {
        "title": title,
        "template": "plotly_white",
        "height": 400,
        "showlegend": True,
        **kwargs,
    }

    fig.update_layout(**standard_layout)
    return fig


def get_display_name(row) -> str:
    """
    Get display name for a data row.

    Args:
        row: DataFrame row

    Returns:
        Display name string
    """
    if hasattr(row, "get"):
        name = row.get("Name", "Unknown")
        acronym = row.get("Acronym", "")
        if acronym and acronym != "N/A":
            return f"{name} ({acronym})"
        return name
    return str(row)


def get_chart_colors():
    """
    Get standard chart color palette.

    Returns:
        List of color codes
    """
    return [
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
    ]


def get_chart_colorscale():
    """
    Get standard chart colorscale.

    Returns:
        Plotly colorscale
    """
    return "Viridis"


def get_standard_colorbar_config():
    """
    Get standard colorbar configuration.

    Returns:
        Dictionary with colorbar settings
    """
    return {
        # Use nested title object for Plotly colorbar title settings
        "title": {"text": "Value", "side": "right"},
        "tickmode": "linear",
        "showticklabels": True,
    }


# ----------------------
# Chart theme helpers
# ----------------------
HOVER_TEMPLATE_CROP = "<b>{}</b><br>State: %{{y}}<br>Intensity: %{{x}}<extra></extra>"
HOVER_TEMPLATE_REGION = "<b>{}</b><br>Region: %{{y}}<br>Intensity: %{{x}}<extra></extra>"


def calc_height(n_rows: int, min_height: int = 400, per_row: int = 25) -> int:
    """Calculate a reasonable figure height based on number of rows.

    Keeps existing behavior used in crop_diversity.py while centralizing logic.
    """
    try:
        return max(min_height, int(n_rows) * per_row)
    except Exception:
        return min_height


def build_standard_layout(title: str = "", title_x: float = 0.5, **overrides) -> dict:
    """Return a standard layout dict for Plotly figures.

    This centralizes common layout values used across charts. Callers can
    pass overrides to customize specific keys (e.g., height, margins).
    """
    base = {
        "title": {"text": title, "x": title_x, "xanchor": "center", "font": {"size": 15, "color": "#2C3E50", "family": "Arial, sans-serif"}},
        "barmode": "stack",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Arial, sans-serif", "size": 12, "color": "#2C3E50"},
        "legend": {"orientation": "v", "x": 1.02, "y": 1, "bordercolor": "rgba(44,62,80,0.1)", "borderwidth": 1, "bgcolor": "rgba(255,255,255,0.9)"},
    }
    base.update(overrides)
    return base
