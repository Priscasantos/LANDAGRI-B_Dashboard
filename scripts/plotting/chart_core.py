"""
Chart Core Utilities
===================

Core utilities for chart processing and data transformation.

Author: Dashboard Iniciativas LULC
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


# Chart configuration dictionary for shared chart settings
CHART_CONFIG = {"margins": {"left": 220, "right": 40, "top": 40, "bottom": 40}}
