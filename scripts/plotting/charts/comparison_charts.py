#!/usr/bin/env python3
"""
Comparison Charts Module
========================

Generates various comparison-related charts for LULC initiatives,
including scatter plots, correlation matrices, and ranking charts.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from scripts.plotting.chart_core import apply_standard_layout, get_display_name, get_chart_colors, get_chart_colorscale
from scripts.plotting.universal_cache import smart_cache_data
# Download form import removed for cleaner interface
from scripts.utilities.modern_themes import apply_modern_theme, get_modern_colors, get_modern_colorscale
from scripts.utilities.modern_chart_theme import (
    apply_modern_styling,
    get_modern_layout_config,
    get_modern_color_palette,
    get_modern_scatter_config,
    get_modern_bar_config
)


@smart_cache_data(ttl=300)
def plot_resolution_accuracy_scatter(filtered_df: pd.DataFrame) -> go.Figure:
    """Create an enhanced scatter plot of Resolution vs. Accuracy with display names.
    Handles variations in input column names for resolution, accuracy, and classes."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Resolution vs. Accuracy Comparison (Insufficient data)"
        )
        return fig

    plot_df = filtered_df.copy()

    # Standardize column names internally
    rename_map = {}
    if "Resolution" in plot_df.columns and "Resolution (m)" not in plot_df.columns:
        rename_map["Resolution"] = "Resolution (m)"
    if "Accuracy" in plot_df.columns and "Accuracy (%)" not in plot_df.columns:
        rename_map["Accuracy"] = "Accuracy (%)"
    if "Number_of_Classes" in plot_df.columns and "Classes" not in plot_df.columns:
        rename_map["Number_of_Classes"] = "Classes"
    if rename_map:
        plot_df.rename(columns=rename_map, inplace=True)

    # Ensure required columns are present after potential rename
    required_cols = ["Resolution (m)", "Accuracy (%)"]
    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(
            title=f"Resolution vs. Accuracy (Missing columns: {', '.join(missing_cols)})"
        )
        return fig

    # Ensure Display_Name exists, using get_display_name from chart_core
    if "Display_Name" not in plot_df.columns or plot_df["Display_Name"].isnull().any():
        plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    fig = px.scatter(
        plot_df,
        x="Resolution (m)",
        y="Accuracy (%)",
        color="Type" if "Type" in plot_df.columns else None,
        size="Classes" if "Classes" in plot_df.columns else None,
        hover_name="Display_Name",
        hover_data=(
            ["Classes", "Type"]
            if all(col in plot_df.columns for col in ["Classes", "Type"])
            else None
        ),
        # Use modern semantic colors instead of hardcoded colors
        color_discrete_map={
            "Global": get_modern_colors(3)[0] if get_modern_colors else "#ff6b6b",
            "Nacional": get_modern_colors(3)[1] if get_modern_colors else "#4dabf7", 
            "Regional": get_modern_colors(3)[2] if get_modern_colors else "#51cf66",
        },
    )

    # Apply modern standardized layout
    apply_modern_theme(
        fig, 
        title="Accuracy vs Resolution",
        xaxis_title="Resolution (m)", 
        yaxis_title="Accuracy (%)", 
        chart_type="scatter"
    )

    return fig


@smart_cache_data(ttl=300)
def plot_spatial_resolution_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart comparing spatial resolutions of initiatives."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Spatial Resolution Comparison (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Ensure 'Resolution_max_val' and 'Display_Name' columns exist
    # 'Resolution_max_val' is preferred as it represents the finest resolution if a range is given.
    # If only 'Resolution (m)' exists, use that.
    resolution_col = None
    if (
        "Resolution_max_val" in plot_df.columns
        and plot_df["Resolution_max_val"].notna().any()
    ):
        resolution_col = "Resolution_max_val"
    elif (
        "Resolution (m)" in plot_df.columns and plot_df["Resolution (m)"].notna().any()
    ):
        resolution_col = "Resolution (m)"
    elif "Resolution" in plot_df.columns:
        # Standardize to expected column name
        plot_df.rename(columns={"Resolution": "Resolution (m)"}, inplace=True)
        resolution_col = "Resolution (m)"

    if not resolution_col:
        fig = go.Figure()
        fig.update_layout(title="Spatial Resolution Comparison (Missing resolution data)")
        return fig

    # Ensure Display_Name exists
    if "Display_Name" not in plot_df.columns or plot_df["Display_Name"].isnull().any():
        plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    # Remove rows where resolution data is missing
    plot_df = plot_df.dropna(subset=[resolution_col])

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Spatial Resolution Comparison (No valid resolution data)")
        return fig

    # Sort by resolution for better visualization
    plot_df = plot_df.sort_values(by=resolution_col)

    fig = px.bar(
        plot_df,
        x="Display_Name",
        y=resolution_col,
        color="Type" if "Type" in plot_df.columns else None,
        hover_data=["Country"] if "Country" in plot_df.columns else None,
        color_discrete_map={
            "Global": get_modern_colors(3)[0] if get_modern_colors else "#3b82f6",
            "Nacional": get_modern_colors(3)[1] if get_modern_colors else "#10b981", 
            "Regional": get_modern_colors(3)[2] if get_modern_colors else "#f59e0b",
        },
    )

    # Apply modern theme
    apply_modern_theme(
        fig,
        title="Spatial Resolution Comparison", 
        xaxis_title="Initiatives",
        yaxis_title="Resolution (m)",
        chart_type="bar"
    )

    # Rotate x-axis labels for better readability
    fig.update_layout(xaxis_tickangle=-45)

    return fig





@smart_cache_data(ttl=300)
def plot_global_accuracy_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart comparing global accuracy of initiatives."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Global Accuracy Comparison (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Ensure 'Accuracy_max_val' and 'Display_Name' columns exist
    # 'Accuracy_max_val' is preferred as it represents the best reported accuracy.
    # If only 'Accuracy (%)' exists, use that.
    accuracy_col = None
    if (
        "Accuracy_max_val" in plot_df.columns
        and plot_df["Accuracy_max_val"].notna().any()
    ):
        accuracy_col = "Accuracy_max_val"
    elif "Accuracy (%)" in plot_df.columns and plot_df["Accuracy (%)"].notna().any():
        accuracy_col = "Accuracy (%)"

    if not accuracy_col:
        fig = go.Figure()
        fig.update_layout(title="Global Accuracy Comparison (Missing Accuracy Data)")
        return fig

    if "Display_Name" not in plot_df.columns or plot_df["Display_Name"].isnull().any():
        plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    # Sort by accuracy for better visualization (higher is better)
    plot_df = plot_df.sort_values(
        by=accuracy_col, ascending=True
    )  # Ascending for horizontal bar, highest at top

    fig = px.bar(
        plot_df,
        x=accuracy_col,
        y="Display_Name",
        orientation="h",  # Horizontal bar chart
        color="Type" if "Type" in plot_df.columns else None,
        labels={accuracy_col: "Global Accuracy (%)", "Display_Name": "Initiative"},
        hover_name="Display_Name",
        hover_data={
            accuracy_col: ":.1f%",  # Format hover accuracy to one decimal place
            "Type": "Type" in plot_df.columns,
            # Corrected to use 'Acronym' or 'Source' if 'Acronym' is not available
            "Acronym": (
                True
                if "Acronym" in plot_df.columns
                else ("Source" if "Source" in plot_df.columns else False)
            ),
        },
        # Use modern semantic colors for better consistency
        color_discrete_map={
            "Global": get_modern_colors(3)[0] if get_modern_colors else "#ff6b6b",
            "Nacional": get_modern_colors(3)[1] if get_modern_colors else "#4dabf7",
            "Regional": get_modern_colors(3)[2] if get_modern_colors else "#51cf66",
        },
    )

    apply_modern_theme(fig, "Accuracy Comparison by Initiative", "Global Accuracy (%)", "Initiative", chart_type="bar")
    fig.update_layout(
        yaxis={"autorange": "reversed"},  # Ensure highest accuracy is at the top
        height=max(
            400, len(plot_df) * 25
        ),  # Adjust height based on number of initiatives
    )
    return fig


@smart_cache_data(ttl=300)
def plot_temporal_evolution_frequency(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a timeline or stacked bar chart for temporal coverage and update frequency."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Temporal Evolution & Update Frequency (Insufficient data)"
        )
        return fig

    plot_df = filtered_df.copy()

    # Required columns for this chart
    required_cols = ["Start_Year", "End_Year", "Temporal_Frequency"]
    if "Display_Name" not in plot_df.columns or plot_df["Display_Name"].isnull().any():
        plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(
            title=f"Temporal Evolution (Missing: {', '.join(missing_cols)})"
        )
        return fig

    # Convert year columns to numeric, coercing errors
    plot_df["Start_Year"] = pd.to_numeric(plot_df["Start_Year"], errors="coerce")
    plot_df["End_Year"] = pd.to_numeric(plot_df["End_Year"], errors="coerce")

    # Drop rows where start or end year could not be converted or are missing
    plot_df.dropna(subset=["Start_Year", "End_Year"], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Temporal Evolution (No valid year data)")
        return fig

    # Sort by Start_Year for timeline view
    plot_df = plot_df.sort_values(by="Start_Year", ascending=True)

    # Create the timeline chart using px.timeline
    # For px.timeline, we need 'start', 'end', and 'y' (resource/initiative)
    # We can use 'Display_Name' for y, 'Start_Year' for start, and 'End_Year' for end.
    # Color can be by 'Temporal_Frequency' or 'Type'. Let's use 'Temporal_Frequency' for this specific chart.

    # Simpler custom_data construction
    custom_data_cols = []
    if "Temporal_Frequency" in plot_df.columns:
        custom_data_cols.append("Temporal_Frequency")
    if "Type" in plot_df.columns:
        custom_data_cols.append("Type")
    if "Acronym" in plot_df.columns:
        custom_data_cols.append("Acronym")
    elif "Source" in plot_df.columns:  # Fallback if Acronym is not there
        custom_data_cols.append("Source")

    fig = px.timeline(
        plot_df,
        x_start="Start_Year",
        x_end="End_Year",
        y="Display_Name",
        color="Temporal_Frequency" if "Temporal_Frequency" in plot_df.columns else None,
        hover_name="Display_Name",
        labels={
            "Display_Name": "Initiative",
            "Start_Year": "Start Year",
            "End_Year": "End Year",
            "Temporal_Frequency": "Update Frequency",
        },
        custom_data=custom_data_cols if custom_data_cols else None,
    )

    # Improve hover information - adjust customdata indices based on what's available
    hover_template_parts = ["<b>%{y}</b><br>Period: %{base|%Y} - %{xEnd|%Y}"]
    # custom_data_mapping = [] # This was used to build customdata, now custom_data_cols serves this

    # Rebuild hovertemplate based on the actual order in custom_data_cols
    for i, col_name in enumerate(custom_data_cols):
        display_label = col_name.replace("_", " ").title()
        if (
            col_name == "Acronym"
            and "Acronym" not in plot_df.columns
            and "Source" in plot_df.columns
        ):
            display_label = "Source"  # Adjust label if we fell back to Source
        hover_template_parts.append(f"{display_label}: %{{customdata[{i}]}}")

    if custom_data_cols:  # Only update custom_data if we have something to map
        # fig.update_traces(customdata=plot_df[custom_data_cols].values) # custom_data is now directly passed to px.timeline
        hover_template_parts.append("<extra></extra>")
        fig.update_traces(hovertemplate="<br>".join(hover_template_parts))

    apply_modern_theme(fig, "Initiative Timeline", "Year", "Initiative", chart_type="timeline")
    fig.update_layout(
        height=max(400, len(plot_df) * 30),  # Adjust height
        xaxis_type="linear",  # Ensure years are treated linearly
    )
    # Ensure y-axis categories are sorted as per the sorted DataFrame for consistent display
    fig.update_yaxes(
        categoryorder="array", categoryarray=plot_df["Display_Name"].unique()
    )

    return fig


@smart_cache_data(ttl=300)
def plot_class_diversity_focus(filtered_df: pd.DataFrame) -> go.Figure:
    """Create an enhanced scatter plot for class diversity and agricultural focus analysis."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Class Diversity & Agricultural Focus (Insufficient data)"
        )
        return fig

    plot_df = filtered_df.copy()

    # Required columns
    required_cols = ["Number_of_Classes", "Number_of_Agricultural_Classes"]
    if "Display_Name" not in plot_df.columns or plot_df["Display_Name"].isnull().any():
        plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Class Diversity (Missing: {', '.join(missing_cols)})")
        return fig

    # Convert class count columns to numeric, coercing errors
    plot_df["Number_of_Classes"] = pd.to_numeric(
        plot_df["Number_of_Classes"], errors="coerce"
    )
    plot_df["Number_of_Agricultural_Classes"] = pd.to_numeric(
        plot_df["Number_of_Agricultural_Classes"], errors="coerce"
    )

    # Drop rows where class counts are missing or invalid
    plot_df.dropna(
        subset=["Number_of_Classes", "Number_of_Agricultural_Classes"], inplace=True
    )

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Class Diversity (No valid class count data)")
        return fig

    # Calculate agricultural focus percentage
    plot_df["Agricultural_Focus_Percent"] = (
        plot_df["Number_of_Agricultural_Classes"] / plot_df["Number_of_Classes"] * 100
    ).round(1)
    
    # Create size column based on total classes for bubble size
    plot_df["Bubble_Size"] = plot_df["Number_of_Classes"]
    
    # Normalize bubble sizes for better visualization
    max_size = plot_df["Bubble_Size"].max()
    min_size = plot_df["Bubble_Size"].min()
    if max_size != min_size:
        plot_df["Normalized_Size"] = (
            (plot_df["Bubble_Size"] - min_size) / (max_size - min_size) * 30 + 10
        )
    else:
        plot_df["Normalized_Size"] = 20
    
    # Get initiative types for color coding
    initiative_types = plot_df.get("Type", "Unknown").fillna("Unknown")
    unique_types = initiative_types.unique()
    
    # Create modern color palette
    colors = [
        "#2E8B57",  # Sea green
        "#4682B4",  # Steel blue
        "#CD5C5C",  # Indian red
        "#DAA520",  # Goldenrod
        "#9370DB",  # Medium purple
        "#20B2AA",  # Light sea green
        "#FF6347",  # Tomato
        "#4169E1"   # Royal blue
    ]
    
    color_map = {t: colors[i % len(colors)] for i, t in enumerate(unique_types)}

    # Create enhanced scatter plot
    fig = go.Figure()
    
    for init_type in unique_types:
        type_data = plot_df[initiative_types == init_type]
        
        fig.add_trace(go.Scatter(
            x=type_data["Number_of_Classes"],
            y=type_data["Agricultural_Focus_Percent"],
            mode="markers",
            marker=dict(
                size=type_data["Normalized_Size"],
                color=color_map[init_type],
                opacity=0.7,
                line=dict(width=2, color="white"),
                sizemode="diameter"
            ),
            name=str(init_type),
            text=type_data["Display_Name"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Total Classes: %{x}<br>"
                "Agricultural Focus: %{y}%<br>"
                "Agricultural Classes: %{customdata}<br>"
                "Type: " + str(init_type) + "<extra></extra>"
            ),
            customdata=type_data["Number_of_Agricultural_Classes"]
        ))

    # Add reference lines
    # Average agricultural focus line
    if not plot_df.empty:
        avg_focus = plot_df["Agricultural_Focus_Percent"].mean()
        fig.add_hline(
            y=avg_focus,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Avg Focus: {avg_focus:.1f}%",
            annotation_position="bottom right"
        )
        
        # Average total classes line
        avg_classes = plot_df["Number_of_Classes"].mean()
        fig.add_vline(
            x=avg_classes,
            line_dash="dash", 
            line_color="gray",
            annotation_text=f"Avg Classes: {avg_classes:.1f}",
            annotation_position="top left"
        )

    # Apply modern styling
    fig.update_layout(
        title={
            'text': "Diversidade de Classes e Foco Agrícola",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial, sans-serif', 'color': '#2E3440'}
        },
        xaxis={
            'title': 'Total Number of Classes',
            'showgrid': True,
            'gridcolor': 'rgba(128,128,128,0.1)',
            'zeroline': False,
            'title_font': {'family': 'Arial, sans-serif', 'size': 14},
            'tickfont': {'family': 'Arial, sans-serif', 'size': 12}
        },
        yaxis={
            'title': 'Agricultural Focus (%)',
            'showgrid': True,
            'gridcolor': 'rgba(128,128,128,0.1)',
            'zeroline': False,
            'range': [-5, 105],
            'title_font': {'family': 'Arial, sans-serif', 'size': 14},
            'tickfont': {'family': 'Arial, sans-serif', 'size': 12}
        },
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend={
            'title': 'Initiative Type',
            'orientation': 'v',
            'yanchor': 'top',
            'y': 1,
            'xanchor': 'left',
            'x': 1.02,
            'font': {'family': 'Arial, sans-serif', 'size': 12}
        },
        margin=dict(l=80, r=120, t=80, b=60)
    )
    
    # Add annotation explaining bubble sizes
    fig.add_annotation(
        text="Bubble size represents total number of classes",
        xref="paper", yref="paper",
        x=0, y=-0.08,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor="left"
    )

    return fig


@smart_cache_data(ttl=300)
def plot_classification_methodology(
    filtered_df: pd.DataFrame, chart_type: str = "pie"
) -> go.Figure:
    """Create a pie or bar chart showing the distribution of classification methodologies."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Classification Methodology Distribution (Insufficient data)"
        )
        return fig

    plot_df = filtered_df.copy()

    # Required column
    methodology_col = "Methodology"  # Assuming this is the column name
    if methodology_col not in plot_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=f"Methodology Distribution (Missing column: {methodology_col})"
        )
        return fig

    # Drop rows where methodology is missing
    plot_df.dropna(subset=[methodology_col], inplace=True)
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Methodology Distribution (No valid methodology data)")
        return fig

    # Count occurrences of each methodology
    methodology_counts = plot_df[methodology_col].value_counts().reset_index()
    methodology_counts.columns = [methodology_col, "Count"]

    if chart_type == "pie":
        fig = px.pie(
            methodology_counts,
            names=methodology_col,
            values="Count",
            hover_name=methodology_col,
            hole=0.3,  # Donut-like pie chart
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        apply_standard_layout(fig, "", "", chart_type="pie")  # Pass empty strings for axis titles for pie
    elif chart_type == "bar":
        # Sort by count for bar chart
        methodology_counts = methodology_counts.sort_values(by="Count", ascending=False)
        fig = px.bar(
            methodology_counts,
            x=methodology_col,
            y="Count",
            color=methodology_col,  # Color by methodology
            labels={methodology_col: "Methodology", "Count": "Number of Initiatives"},
            hover_name=methodology_col,
        )

        # Apply modern styling
        fig = apply_modern_styling(fig, **get_modern_bar_config())
        fig.update_layout(
            xaxis_title="Methodology",
            yaxis_title="Number of Initiatives",
            xaxis_tickangle=-45
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            title=f"Invalid chart type: {chart_type}. Choose 'pie' or 'bar'."
        )
        return fig

    fig.update_layout(
        showlegend=(chart_type == "bar")
    )  # Show legend for bar, pie has labels
    return fig


@smart_cache_data(ttl=300)
def plot_comparison_matrix(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a comparison matrix heatmap for multiple numeric metrics."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (Insufficient data)")
        return fig

    # Select numeric columns for comparison
    numeric_columns = []
    for col in filtered_df.columns:
        if filtered_df[col].dtype in ["int64", "float64"] and col not in ["Name"]:
            # Check if column has sufficient non-null values
            if filtered_df[col].notna().sum() > 0:
                numeric_columns.append(col)

    if len(numeric_columns) < 2:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (Insufficient numeric data)")
        return fig

    # Create a subset with numeric data and add display names
    plot_df = filtered_df[["Name"] + numeric_columns].copy()
    plot_df = plot_df.dropna(subset=numeric_columns, how="all")

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (No valid data)")
        return fig

    # Add display names
    plot_df["Display_Name"] = plot_df.apply(lambda row: get_display_name(row), axis=1)

    # Normalize the data for better visualization
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()

    # Fill NaN values with column means before scaling
    numeric_df = plot_df[numeric_columns].fillna(plot_df[numeric_columns].mean())
    normalized_data = scaler.fit_transform(numeric_df)

    # Create heatmap with modern colorscale
    # --- Colorbar configuration: Only valid Plotly properties allowed ---
    # See: https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html#plotly.graph_objects.heatmap.ColorBar
    # To customize, use only the properties listed in the user-provided list.
    colorbar_config = dict(
        # --- Main label and ticks ---
        title="Normalized Value",
        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
        ticktext=["Low", "Below Avg", "Average", "Good", "High"],
        # --- Size and orientation ---
        thickness=18,
        len=0.8,
        orientation="v",
        # --- Positioning ---
        x=1.02,
        xanchor="left",
        y=0.5,
        yanchor="middle",
        # --- Border and background ---
        outlinewidth=1,
        outlinecolor="#888",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#ccc",
        borderwidth=1,
        # --- Font ---
        tickfont=dict(family="Inter, Arial, sans-serif", size=12, color="#222"),
        titlefont=dict(family="Inter, Arial, sans-serif", size=14, color="#222"),
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=normalized_data,
            x=numeric_columns,
            y=plot_df["Display_Name"].values,
            colorscale=get_modern_colorscale("diverging") if get_modern_colorscale else "RdYlBu_r",
            hoverongaps=False,
            showscale=True,
            colorbar=colorbar_config,
        )
    )

    # Apply standardized layout for heatmap
    apply_standard_layout(fig, "Metrics", "Initiative", chart_type="heatmap")

    return fig


@smart_cache_data(ttl=300)
def plot_normalized_performance_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a normalized performance heatmap for specific metrics with customizable display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Normalized Performance Heatmap (Insufficient data)")
        return fig

    # Define available metrics by checking what columns exist in the DataFrame
    available_metrics = {}

    # Priority order for resolution columns
    if "Resolution (m)" in filtered_df.columns:
        available_metrics["Resolution (m)"] = "Resolution (m)"
    elif "Resolution_max_val" in filtered_df.columns:
        available_metrics["Resolution_max_val"] = "Resolution (m)"
    elif "Resolution_min_val" in filtered_df.columns:
        available_metrics["Resolution_min_val"] = "Min Resolution (m)"

    # Priority order for accuracy columns
    if "Accuracy (%)" in filtered_df.columns:
        available_metrics["Accuracy (%)"] = "Accuracy (%)"
    elif "Accuracy_max_val" in filtered_df.columns:
        available_metrics["Accuracy_max_val"] = "Accuracy (%)"
    elif "Accuracy_min_val" in filtered_df.columns:
        available_metrics["Accuracy_min_val"] = "Min Accuracy (%)"

    # Priority order for classes columns
    if "Number_of_Classes" in filtered_df.columns:
        available_metrics["Number_of_Classes"] = "Total Classes (qnt)"
    elif "Classes" in filtered_df.columns:
        available_metrics["Classes"] = "Total Classes (qnt)"

    # Agricultural classes
    if "Num_Agri_Classes" in filtered_df.columns:
        available_metrics["Num_Agri_Classes"] = "Agricultural Classes (qnt)"

    if not available_metrics:
        fig = go.Figure()
        fig.update_layout(
            title="Normalized Performance Heatmap (Required metric columns not found)"
        )
        return fig

    internal_metric_names = list(available_metrics.keys())
    display_metric_names = list(
        available_metrics.values()
    )  # Create a subset with numeric data and add display names

    # Ensure 'Name' or another identifier is present for get_display_name
    cols_for_plot_df = internal_metric_names
    if "Name" in filtered_df.columns:  # Primary identifier
        cols_for_plot_df = ["Name"] + internal_metric_names
    elif "Acronym" in filtered_df.columns:  # Fallback
        cols_for_plot_df = ["Acronym"] + internal_metric_names
    elif "Source" in filtered_df.columns:  # Further fallback
        cols_for_plot_df = ["Source"] + internal_metric_names

    plot_df = filtered_df[cols_for_plot_df].copy()

    # Convert metric columns to numeric, coercing errors. This is important before dropna and fillna.
    for col in internal_metric_names:
        plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce")

    plot_df = plot_df.dropna(subset=internal_metric_names, how="all")

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Normalized Performance Heatmap (No valid data after filtering for specified metrics)"
        )
        return fig

    # Add display names using the imported get_display_name function
    # Apply to the original filtered_df rows corresponding to plot_df indices
    temp_display_name_df = filtered_df.loc[plot_df.index].copy()
    temp_display_name_df["Display_Name"] = temp_display_name_df.apply(
        get_display_name, axis=1
    )
    plot_df["Display_Name"] = temp_display_name_df["Display_Name"]

    # Normalize the data for better visualization
    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()

    # Fill NaN values with column means before scaling for internal_metric_names only
    numeric_df_for_scaling = plot_df[internal_metric_names].fillna(
        plot_df[internal_metric_names].mean()
    )

    if numeric_df_for_scaling.empty or numeric_df_for_scaling.isnull().all().all():
        fig = go.Figure()
        fig.update_layout(
            title="Normalized Performance Heatmap (No numeric data to scale for specified metrics)"
        )
        return fig

    normalized_data = scaler.fit_transform(numeric_df_for_scaling)

    # Custom normalization with specific rules for each metric
    normalized_data = []

    for col in internal_metric_names:
        col_values = numeric_df_for_scaling[col]

        if col_values.isna().all():
            # If all values are NaN, assign neutral score (0.5)
            normalized_col = [0.5] * len(col_values)
        else:
            min_val = col_values.min()
            max_val = col_values.max()

            if min_val == max_val:
                # If all values are the same, assign neutral score (0.5)
                normalized_col = [0.5] * len(col_values)
            else:
                # Apply specific normalization rules based on metric type
                if any(
                    resolution_term in col.lower() for resolution_term in ["resolution"]
                ):
                    # For Resolution: LOWER values are BETTER (inverted scale)
                    # Best = 10m (high score), Worst = 100m+ (low score)
                    normalized_col = [
                        (max_val - val) / (max_val - min_val) for val in col_values
                    ]

                elif any(
                    accuracy_term in col.lower() for accuracy_term in ["accuracy"]
                ):
                    # For Accuracy: HIGHER values are BETTER (normal scale)
                    # Best = 100% (high score), Worst = low % (low score)
                    normalized_col = [
                        (val - min_val) / (max_val - min_val) for val in col_values
                    ]

                elif any(class_term in col.lower() for class_term in ["class", "agri"]):
                    # For Classes/Agricultural Classes: HIGHER values are BETTER (normal scale)
                    # More classes = better coverage (high score)
                    normalized_col = [
                        (val - min_val) / (max_val - min_val) for val in col_values
                    ]

                else:
                    # Default normalization (higher is better)
                    normalized_col = [
                        (val - min_val) / (max_val - min_val) for val in col_values
                    ]

        normalized_data.append(normalized_col)

    # Transpose to get the correct shape for the heatmap (initiatives x metrics)
    normalized_data = list(map(list, zip(*normalized_data)))


    # --- Colorbar configuration: Only valid Plotly properties allowed ---
    # See: https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html#plotly.graph_objects.heatmap.ColorBar
    # To customize, use only the properties listed in the user-provided list.
    colorbar_config = dict(
        # --- Main label and ticks ---
        title="Performance Score",
        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
        ticktext=["Poor", "Below Avg", "Average", "Good", "Excellent"],
        # --- Size and orientation ---
        thickness=18,  # px
        len=0.8,       # fraction of plot
        orientation="v",
        # --- Positioning ---
        x=1.02,
        xanchor="left",
        y=0.5,
        yanchor="middle",
        # --- Border and background ---
        outlinewidth=1,
        outlinecolor="#888",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#ccc",
        borderwidth=1,
        # --- Font ---
        tickfont=dict(family="Inter, Arial, sans-serif", size=12, color="#222"),
        titlefont=dict(family="Inter, Arial, sans-serif", size=14, color="#222"),
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=normalized_data,
            x=display_metric_names,
            y=plot_df["Display_Name"].values,
            colorscale="Viridis",
            hoverongaps=False,
            showscale=True,
            colorbar=colorbar_config,
            customdata=plot_df[internal_metric_names].values,
            hovertemplate="<b>Initiative:</b> %{y}<br>"
                + "<b>Metric:</b> %{x}<br>"
                + "<b>Original Value:</b> <b>%{customdata:.2f}</b><br>"
                + "<b>Performance Score:</b> <b>%{z:.2f}</b><br>"
                + "<b>Rating:</b> <b>%{z|.0%}</b><extra></extra>",
            zmin=0,
            zmax=1,
        )
    )

    # Modern, clean layout for heatmap
    fig.update_layout(
        title={
            'text': "🔥 Heatmap de Performance Normalizada",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter, Arial, sans-serif'}
        },
        xaxis_title="Metrics",
        yaxis_title="Initiative",
        margin=dict(l=80, r=40, t=60, b=60),
        height=480 + 18 * len(plot_df["Display_Name"].unique()),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", size=14),
    )

    return fig


@smart_cache_data(ttl=300)
def plot_initiative_ranking(
    filtered_df: pd.DataFrame, ranking_criteria: dict[str, float] | None = None
) -> go.Figure:
    """Create a ranking chart based on multiple criteria with display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Initiative Ranking (Insufficient data)")
        return fig

    # Default ranking criteria if not provided
    if ranking_criteria is None:
        ranking_criteria = {
            "Accuracy (%)": 0.4,
            "Classes": 0.3,
            "Resolution (m)": -0.3,  # Negative because lower resolution is better
        }

    # Check if required columns exist
    available_criteria = {
        k: v for k, v in ranking_criteria.items() if k in filtered_df.columns
    }

    if not available_criteria:
        fig = go.Figure()
        fig.update_layout(title="Initiative Ranking (Missing ranking criteria columns)")
        return fig

    plot_df = filtered_df.copy()
    plot_df["Display_Name"] = plot_df.apply(get_display_name, axis=1)

    # Calculate composite score
    plot_df["Composite_Score"] = 0
    for column, weight in available_criteria.items():
        # Normalize column values to 0-100 scale
        col_values = plot_df[column].dropna()
        if len(col_values) > 0:
            # Ensure max and min are different to avoid division by zero if all values are the same
            min_val, max_val = col_values.min(), col_values.max()
            if max_val == min_val:
                normalized = pd.Series(
                    50, index=col_values.index
                )  # Assign a neutral 50 if all values are same
            elif weight > 0:  # Higher values are better
                normalized = (col_values - min_val) / (max_val - min_val) * 100
            else:  # Lower values are better (like resolution)
                normalized = (max_val - col_values) / (max_val - min_val) * 100
            plot_df.loc[col_values.index, "Composite_Score"] += normalized * abs(weight)

    # Sort by composite score
    plot_df = plot_df.sort_values("Composite_Score", ascending=True)

    # Create horizontal bar chart
    fig = px.bar(
        plot_df,
        x="Composite_Score",
        y="Display_Name",
        color="Type" if "Type" in plot_df.columns else None,
        orientation="h",
        # Use modern colors for consistent branding
        color_discrete_map={
            "Global": get_modern_colors(3)[0] if get_modern_colors else "#ff6b6b",
            "Nacional": get_modern_colors(3)[1] if get_modern_colors else "#4dabf7",
            "Regional": get_modern_colors(3)[2] if get_modern_colors else "#51cf66",
        },
        hover_data=[col for col in available_criteria if col in plot_df.columns],
    )

    # Apply standardized layout
    apply_standard_layout(
        fig,
        "Composite Score",
        "Initiative",
        chart_type="bar_horizontal",
        num_items=len(plot_df),
    )

    # Set the tick angle of the y-axis to 0 for horizontal bar chart readability
    fig.update_layout(
        xaxis={"tickangle": 0},
        yaxis={"tickangle": 0},
    )

    return fig


@smart_cache_data(ttl=300)
def plot_correlation_matrix(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a correlation matrix for numeric variables."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Correlation Matrix (Insufficient data)")
        return fig

    # Select numeric columns
    numeric_columns = []
    for col in filtered_df.columns:
        if filtered_df[col].dtype in ["int64", "float64"] and col not in ["Name"]:
            if (
                filtered_df[col].notna().sum() > 1
            ):  # Need at least 2 values for correlation
                numeric_columns.append(col)

    if len(numeric_columns) < 2:
        fig = go.Figure()
        fig.update_layout(title="Correlation Matrix (Need at least 2 numeric columns)")
        return fig

    # Calculate correlation matrix
    corr_matrix = filtered_df[numeric_columns].corr()

    # Import padronized colorbar configuration
    from scripts.plotting.chart_core import get_standard_colorbar_config

    # Create correlation heatmap with modern colorscale
    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=get_modern_colorscale("diverging") if get_modern_colorscale else "RdBu",
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            showscale=True,
            # Usar configuração padronizada da colorbar
            colorbar=get_standard_colorbar_config(
                title="Correlation",
                custom_tickvals=[-1, -0.5, 0, 0.5, 1],
                custom_ticktext=["-1.0", "-0.5", "0.0", "0.5", "1.0"],
            ),
        )
    )

    # Apply standardized layout
    apply_standard_layout(
        fig,
        "Variables",
        "Variables",
        chart_type="correlation_matrix",
        num_items=len(numeric_columns),
        show_legend=False,
    )

    fig.update_layout(xaxis={"tickangle": 45}, yaxis={"tickangle": 0})

    return fig


@smart_cache_data(ttl=300)
def plot_radar_comparison(
    data1: dict[str, Any],
    data2: dict[str, Any],
    filtered_df: pd.DataFrame,
    init1: str,
    init2: str,
) -> go.Figure:
    """Create a radar chart comparing two initiatives with standardized display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Radar Comparison (Insufficient data)")
        return fig
    # Available categories for comparison
    categories = ["Accuracy (%)", "Resolution (m)", "Classes"]
    available_categories = [cat for cat in categories if cat in filtered_df.columns]

    if len(available_categories) < 2:
        fig = go.Figure()
        fig.update_layout(title="Radar Comparison (Insufficient data columns)")
        return fig

    def normalize_for_radar(value, column, df):
        """Normalize values for radar chart (0-100 scale)"""
        if pd.isna(value) or df[column].isna().all():
            return 50  # Default middle value

        min_val, max_val = df[column].min(), df[column].max()
        if max_val == min_val:
            return 50  # All values are the same

        if column == "Resolution (m)":
            # For resolution, lower is better, so invert the scale
            return (max_val - value) / (max_val - min_val) * 100
        else:
            # For accuracy and classes, higher is better
            return (value - min_val) / (max_val - min_val) * 100

    # Get display names for the initiatives
    display_name_1 = init1
    display_name_2 = init2

    # Try to get acronyms if available
    for _, row in filtered_df.iterrows():
        name_col = "Name" if "Name" in row else "Nome" if "Nome" in row else None
        if name_col and row[name_col] == init1:
            display_name_1 = get_display_name(row)
        elif name_col and row[name_col] == init2:
            display_name_2 = get_display_name(row)

    # Calculate normalized values
    values1 = [
        normalize_for_radar(data1.get(cat, 0), cat, filtered_df)
        for cat in available_categories
    ]
    values2 = [
        normalize_for_radar(data2.get(cat, 0), cat, filtered_df)
        for cat in available_categories
    ]

    # Create radar chart
    fig = go.Figure()

    # Get modern colors for the two initiatives
    colors = get_modern_colors(2) if get_modern_colors else ["#ff6b6b", "#4dabf7"]
    
    fig.add_trace(
        go.Scatterpolar(
            r=values1 + [values1[0]],
            theta=available_categories + [available_categories[0]],
            fill="toself",
            name=display_name_1,
            line_color=colors[0],
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=values2 + [values2[0]],
            theta=available_categories + [available_categories[0]],
            fill="toself",
            name=display_name_2,
            line_color=colors[1],
        )
    )

    # Apply standardized layout
    apply_standard_layout(fig, "", "", chart_type="radar_chart")

    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}}, showlegend=True
    )

    return fig


@smart_cache_data(ttl=300)
def plot_classes_frequency_boxplot(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a box plot of Number of Classes by Temporal Frequency."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Classes vs. Temporal Frequency (Insufficient data)")
        return fig

    required_cols = ["Number_of_Classes", "Temporal_Frequency"]
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(
            title=f"Classes vs. Temporal Frequency (Missing: {', '.join(missing_cols)})"
        )
        return fig

    plot_df = filtered_df.dropna(subset=required_cols).copy()
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Classes vs. Temporal Frequency (No valid data after NaN drop)"
        )
        return fig

    # Ensure Temporal_Frequency is treated as a category (string)
    plot_df["Temporal_Frequency"] = plot_df["Temporal_Frequency"].astype(str)
    # Sort by a natural order if possible (e.g., if frequencies are like 'Annual', 'Biannual')
    # This might need a more sophisticated sorting if a specific order is required.
    # For now, default alphanumeric sort of unique string values will apply.

    fig = px.box(
        plot_df,
        x="Temporal_Frequency",
        y="Number_of_Classes",
        color="Type" if "Type" in plot_df.columns else None,
        hover_name="Display_Name" if "Display_Name" in plot_df.columns else None,
        points="all",  # Show all data points
        notched=True,  # Add notches for median comparison
        # Use modern color palette for consistency
        color_discrete_map={
            "Global": get_modern_colors(3)[0] if get_modern_colors else "#ff6b6b",
            "Nacional": get_modern_colors(3)[1] if get_modern_colors else "#4dabf7",
            "Regional": get_modern_colors(3)[2] if get_modern_colors else "#51cf66",
        },
    )

    apply_standard_layout(fig, "Temporal Frequency", "Number of Classes", chart_type="box")
    fig.update_layout(
        xaxis_categoryorder="category ascending"
    )  # Ensure consistent ordering
    return fig


@smart_cache_data(ttl=300)
def plot_methodology_type_barchart(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of Methodology Breakdown by Initiative Type."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Methodology Breakdown by Type (Insufficient data)")
        return fig

    required_cols = ["Methodology", "Type"]
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(
            title=f"Methodology Breakdown by Type (Missing: {', '.join(missing_cols)})"
        )
        return fig

    plot_df = (
        filtered_df.groupby(["Type", "Methodology"], observed=False)
        .size()
        .reset_index(name="Count")
    )

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Methodology Breakdown by Type (No data after grouping)"
        )
        return fig

    fig = px.bar(
        plot_df,
        x="Type",
        y="Count",
        color="Methodology",
        barmode="group",
        hover_name="Methodology",  # Shows methodology on hover for the bar segment
        hover_data={
            "Type": True,
            "Count": True,
            "Methodology": False,
        },  # Customize hover data
    )

    # Apply modern styling
    fig = apply_modern_styling(fig, **get_modern_bar_config())
    fig.update_layout(
        xaxis_title="Initiative Type",
        yaxis_title="Number of Initiatives"
    )
    fig.update_layout(xaxis_categoryorder="category ascending")
    return fig


def add_comparison_chart_download(
    fig: go.Figure, default_filename: str, key_prefix: str
):
    """
    Helper function to add download functionality to comparison charts.

    Args:
        fig: Plotly figure object
        default_filename: Default filename for download
        key_prefix: Unique prefix for widget keys
    """
    if fig:
        # Download functionality removed for cleaner interface
        pass
