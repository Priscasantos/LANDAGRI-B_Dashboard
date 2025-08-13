"""
Chart Configuration and Standards
=================================

Standard configurations for responsive charts with modern design.
Provides consistent styling across all dashboard visualizations.

Author: LANDAGRI-B Project Team 
Date: 2025
"""

from typing import Any

import plotly.graph_objects as go

# Import modern themes system
from .modern_themes import ModernThemes, modern_colors

# Initialize modern theme
ModernThemes.setup_modern_theme()

# Modern color palettes based on the modern theme system
MODERN_COLORS = {
    "primary": [modern_colors["primary"], "#1d4ed8", "#2563eb", "#1e40af", "#1e3a8a"],
    "success": [modern_colors["success"], "#059669", "#047857", "#065f46", "#064e3b"],
    "warning": [modern_colors["warning"], "#d97706", "#b45309", "#92400e", "#78350f"],
    "danger": [modern_colors["danger"], "#dc2626", "#b91c1c", "#991b1b", "#7f1d1d"],
    "info": [modern_colors["info"], "#0891b2", "#0e7490", "#155e75", "#164e63"],
    "purple": [modern_colors["purple"], "#7c3aed", "#6d28d9", "#5b21b6", "#4c1d95"],
    "gradient": [modern_colors["primary"], "#6366f1", "#8b5cf6", "#a855f7", "#c084fc"],
}

# Extended palette for more categories - using modern color system
EXTENDED_PALETTE = [
    modern_colors["primary"],
    modern_colors["secondary"],
    modern_colors["accent"],
    modern_colors["danger"],
    modern_colors["purple"],
    modern_colors["info"],
    "#84cc16",
    modern_colors["warning"],
    modern_colors["pink"],
    "#14b8a6",
    modern_colors["indigo"],
    modern_colors["success"],
    "#eab308",
    "#f43f5e",
    "#a855f7",
    "#0ea5e9",
    "#65a30d",
    "#ea580c",
    "#e11d48",
    "#9333ea",
]


def get_standard_layout(
    title: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
    height: int = 500,
    showlegend: bool = True,
    template: str = "plotly_white",
) -> dict[str, Any]:
    """
    Get standard layout configuration for charts.

    Args:
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        height: Chart height in pixels
        showlegend: Whether to show legend
        template: Plotly template to use

    Returns:
        Dictionary with layout configuration
    """
    return {
        "title": {
            "text": title,
            "font": {"size": 20, "family": "Inter, sans-serif", "color": "#0f172a"},
            "x": 0.5,
            "xanchor": "center",
        },
        "xaxis": {
            "title": {
                "text": xaxis_title,
                "font": {"size": 14, "family": "Inter, sans-serif"},
            },
            "tickfont": {"size": 12, "family": "Inter, sans-serif"},
            "gridcolor": "rgba(0,0,0,0.1)",
            "linecolor": "rgba(0,0,0,0.2)",
        },
        "yaxis": {
            "title": {
                "text": yaxis_title,
                "font": {"size": 14, "family": "Inter, sans-serif"},
            },
            "tickfont": {"size": 12, "family": "Inter, sans-serif"},
            "gridcolor": "rgba(0,0,0,0.1)",
            "linecolor": "rgba(0,0,0,0.2)",
        },
        "height": height,
        "showlegend": showlegend,
        "legend": {
            "font": {"size": 12, "family": "Inter, sans-serif"},
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02,
        },
        "template": template,
        "margin": {"l": 60, "r": 60, "t": 80, "b": 60},
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "font": {"family": "Inter, sans-serif", "color": "#0f172a"},
    }


def get_responsive_config() -> dict[str, Any]:
    """
    Get configuration for responsive charts.

    Returns:
        Dictionary with responsive configuration
    """
    return {
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "pan2d",
            "lasso2d",
            "select2d",
            "autoScale2d",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
        ],
        "toImageButtonOptions": {
            "format": "png",
            "filename": "chart",
            "height": 600,
            "width": 1000,
            "scale": 2,
        },
        "responsive": True,
    }


def apply_modern_style(fig: go.Figure, **kwargs) -> go.Figure:
    """
    Apply modern styling to a Plotly figure.

    Args:
        fig: Plotly figure to style
        **kwargs: Additional layout parameters

    Returns:
        Styled Plotly figure
    """
    layout_config = get_standard_layout(**kwargs)
    fig.update_layout(layout_config)

    # Update traces for better visual appeal
    fig.update_traces(
        marker={"line": {"width": 0.5, "color": "white"}}, textposition="auto"
    )

    return fig


def create_metric_card_figure(
    value: float, title: str, prefix: str = "", suffix: str = "", color: str = "#3b82f6"
) -> go.Figure:
    """
    Create a modern metric card figure.

    Args:
        value: Metric value
        title: Metric title
        prefix: Value prefix (e.g., "$")
        suffix: Value suffix (e.g., "%")
        color: Primary color for the card

    Returns:
        Plotly figure for metric card
    """
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=value,
            title={"text": title, "font": {"size": 16, "color": "#64748b"}},
            number={
                "font": {"size": 36, "color": color, "family": "Inter, sans-serif"},
                "prefix": prefix,
                "suffix": suffix,
            },
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )

    fig.update_layout(
        height=150,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_family="Inter, sans-serif",
    )

    return fig


def get_color_palette(n_colors: int, palette: str = "primary") -> list:
    """
    Get a color palette with specified number of colors.

    Args:
        n_colors: Number of colors needed
        palette: Palette name or "auto" for automatic selection

    Returns:
        List of color codes
    """
    if palette == "auto" or palette not in MODERN_COLORS:
        if n_colors <= len(EXTENDED_PALETTE):
            return EXTENDED_PALETTE[:n_colors]
        else:
            # Cycle through colors if more needed
            return [
                EXTENDED_PALETTE[i % len(EXTENDED_PALETTE)] for i in range(n_colors)
            ]

    colors = MODERN_COLORS[palette]
    if n_colors <= len(colors):
        return colors[:n_colors]
    else:
        # Repeat colors if more needed
        return [colors[i % len(colors)] for i in range(n_colors)]


# Chart size presets for different contexts
CHART_SIZES = {
    "small": {"height": 300, "width": None},
    "medium": {"height": 500, "width": None},
    "large": {"height": 700, "width": None},
    "dashboard": {"height": 400, "width": None},
    "fullscreen": {"height": 800, "width": None},
}


def get_chart_size(size_preset: str = "medium") -> dict[str, int | None]:
    """
    Get chart size configuration.

    Args:
        size_preset: Size preset name

    Returns:
        Dictionary with height and width
    """
    return CHART_SIZES.get(size_preset, CHART_SIZES["medium"])
