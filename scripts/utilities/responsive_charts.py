"""
Responsive Chart Utilities
===========================

Utilities for creating responsive and modern charts across all dashboard modules.
Provides consistent styling, responsive sizing, and modern design patterns.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scripts.utilities.chart_config import (
    apply_modern_style,
    get_chart_size,
    get_responsive_config,
)


def safe_plot_call(plot_function, *args, **kwargs) -> go.Figure | None:
    """
    Safely call a plotting function with error handling.

    Args:
        plot_function: Function to call for plotting
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Plotly figure or None if error occurred
    """
    try:
        return plot_function(*args, **kwargs)
    except Exception as e:
        st.error(f"❌ Error generating chart: {str(e)}")
        return None


def create_responsive_figure(
    data: Any,
    chart_type: str = "bar",
    title: str = "",
    x_column: str = "",
    y_column: str = "",
    color_column: str | None = None,
    size_preset: str = "medium",
    color_palette: str = "auto",
    **kwargs,
) -> go.Figure | None:
    """
    Create a responsive figure with modern styling.

    Args:
        data: Data for the chart
        chart_type: Type of chart (bar, line, scatter, etc.)
        title: Chart title
        x_column: X-axis column name
        y_column: Y-axis column name
        color_column: Color grouping column
        size_preset: Size preset for the chart
        color_palette: Color palette to use
        **kwargs: Additional arguments for the chart

    Returns:
        Styled Plotly figure
    """
    try:
        # Get chart size configuration
        size_config = get_chart_size(size_preset)

        # Create base figure based on chart type
        if chart_type == "bar":
            fig = px.bar(
                data, x=x_column, y=y_column, color=color_column, title=title, **kwargs
            )
        elif chart_type == "line":
            fig = px.line(
                data, x=x_column, y=y_column, color=color_column, title=title, **kwargs
            )
        elif chart_type == "scatter":
            fig = px.scatter(
                data, x=x_column, y=y_column, color=color_column, title=title, **kwargs
            )
        elif chart_type == "histogram":
            fig = px.histogram(
                data, x=x_column, color=color_column, title=title, **kwargs
            )
        else:
            # Default to bar chart
            fig = px.bar(
                data, x=x_column, y=y_column, color=color_column, title=title, **kwargs
            )

        # Apply modern styling
        fig = apply_modern_style(fig, title=title, height=size_config["height"])

        return fig

    except Exception as e:
        st.error(f"❌ Error creating responsive figure: {str(e)}")
        return None


def display_chart_with_download(
    fig: go.Figure | None, filename: str, key_prefix: str, container_width: bool = True
) -> None:
    """
    Display a chart with download functionality.

    Args:
        fig: Plotly figure to display
        filename: Default filename for download
        key_prefix: Unique prefix for Streamlit keys
        container_width: Whether to use container width
    """
    if fig:
        # Configure responsive settings
        config = get_responsive_config()

        # Display the chart
        st.plotly_chart(fig, use_container_width=container_width, config=config)

        # Add download functionality
        # Download functionality removed for cleaner interface
    else:
        st.error("❌ Chart could not be generated")


def create_metrics_grid(metrics: list[dict[str, Any]], columns: int = 4) -> None:
    """
    Create a responsive metrics grid.

    Args:
        metrics: List of metric dictionaries with 'label', 'value', 'delta' keys
        columns: Number of columns in the grid
    """
    cols = st.columns(columns)

    for i, metric in enumerate(metrics):
        col_index = i % columns

        with cols[col_index]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", "N/A"),
                delta=metric.get("delta", None),
            )


def create_info_expander(title: str, content: str, expanded: bool = False) -> None:
    """
    Create a standardized info expander.

    Args:
        title: Expander title
        content: Expander content
        expanded: Whether to start expanded
    """
    with st.expander(title, expanded=expanded):
        st.markdown(content)


def create_chart_tabs(tabs_config: list[dict[str, Any]]) -> None:
    """
    Create a standardized chart tabs layout.

    Args:
        tabs_config: List of tab configurations with 'title', 'content_function' keys
    """
    tab_titles = [config["title"] for config in tabs_config]
    tabs = st.tabs(tab_titles)

    for _i, (tab, config) in enumerate(zip(tabs, tabs_config)):
        with tab:
            if "content_function" in config:
                config["content_function"]()
            elif "content" in config:
                st.markdown(config["content"])


def apply_custom_css() -> None:
    """Apply custom CSS for improved chart responsiveness."""
    st.markdown(
        """
        <style>
        /* Responsive chart containers */
        .js-plotly-plot, .plotly {
            width: 100% !important;
            height: auto !important;
        }

        /* Modern metric cards */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Improved tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 8px;
            padding: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            margin: 0 0.25rem;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            [data-testid="column"] {
                width: 100% !important;
                margin-bottom: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Export commonly used functions
__all__ = [
    "safe_plot_call",
    "create_responsive_figure",
    "display_chart_with_download",
    "create_metrics_grid",
    "create_info_expander",
    "create_chart_tabs",
    "apply_custom_css",
]
