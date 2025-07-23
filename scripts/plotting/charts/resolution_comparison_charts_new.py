#!/usr/bin/env python3
"""
Resolution Comparison Charts Module - Simplified
==============================================

Charts for resolution analysis and comparison between initiatives.
"""

import pandas as pd
import plotly.graph_objects as go

from scripts.plotting.chart_core import apply_standard_layout


def plot_resolution_vs_launch_year(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a scatter plot showing resolution vs launch year."""
    fig = go.Figure()

    if filtered_df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, "Start Year", "Resolution (m)")
        return fig

    # Create scatter plot
    if "Start_Year" in filtered_df.columns and "Resolution" in filtered_df.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_df["Start_Year"],
                y=filtered_df["Resolution"],
                mode="markers",
                text=filtered_df.get("Acronym", filtered_df.get("Name", "")),
                textposition="top center",
                marker={"size": 10, "opacity": 0.7},
            )
        )

    apply_standard_layout(fig, "Start Year", "Resolution (m)")
    return fig


def plot_initiatives_by_resolution_category(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing number of initiatives by resolution category."""
    fig = go.Figure()

    if filtered_df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, "Resolution Category", "Number of Initiatives")
        return fig
    # Categorize resolutions (placeholder logic)
    categories = ["High (≤10m)", "Medium (10-100m)", "Low (>100m)"]
    counts = [10, 20, 5]  # Placeholder data

    fig.add_trace(go.Bar(x=categories, y=counts))

    # Apply standard bar and layout configuration
    from scripts.plotting.chart_core import get_standard_bar_config

    fig.update_layout(**get_standard_bar_config())

    apply_standard_layout(fig, "Resolution Category", "Number of Initiatives")
    return fig


def plot_resolution_coverage_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a heatmap showing resolution vs coverage type."""
    fig = go.Figure()

    if filtered_df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, "Coverage Type", "Resolution Category")
        return fig

    # Placeholder heatmap
    fig.add_trace(
        go.Heatmap(
            z=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            x=["Type A", "Type B", "Type C"],
            y=["High", "Medium", "Low"],
        )
    )

    apply_standard_layout(fig, "Coverage Type", "Resolution Category")
    return fig


def plot_resolution_by_sensor_family(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a chart showing resolution distribution by sensor family."""
    fig = go.Figure()

    if filtered_df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, "Sensor Family", "Resolution (m)")
        return fig

    # Placeholder scatter plot
    families = ["Landsat", "Sentinel", "MODIS"]
    resolutions = [30, 10, 250]

    fig.add_trace(
        go.Scatter(x=families, y=resolutions, mode="markers", marker={"size": 12})
    )

    apply_standard_layout(fig, "Sensor Family", "Resolution (m)")
    return fig


def plot_resolution_slopegraph(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a slopegraph showing resolution evolution."""
    fig = go.Figure()

    if filtered_df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, "Time Period", "Resolution (m)")
        return fig

    # Placeholder line plot
    years = [1990, 2000, 2010, 2020]
    avg_resolution = [1000, 500, 100, 30]

    fig.add_trace(
        go.Scatter(x=years, y=avg_resolution, mode="lines+markers", line={"width": 3})
    )

    apply_standard_layout(fig, "Year", "Average Resolution (m)")
    return fig
