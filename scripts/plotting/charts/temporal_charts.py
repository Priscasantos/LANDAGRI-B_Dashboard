#!/usr/bin/env python3
"""
Timeline Chart Module
=====================

Generates the timeline chart for LULC initiatives.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import re
from typing import Any

import pandas as pd
import plotly.express as px  # Ensure px is imported
import plotly.graph_objects as go  # Ensure go is imported
import streamlit as st

from scripts.plotting.chart_core import add_display_names_to_df, apply_standard_layout
from scripts.utilities.config import get_initiative_color_map
from scripts.utilities.modern_themes import apply_modern_theme, get_modern_colors, get_modern_colorscale
from scripts.utilities.modern_chart_theme import (
    apply_modern_styling,
    get_modern_layout_config,
    get_modern_color_palette,
    get_modern_timeline_config,
    get_modern_line_config
)
from scripts.utilities.table_charts import (
    create_brazilian_regions_table,
    create_mesoregions_table,
)
# Download form import removed for cleaner interface


# Renamed from plot_timeline to plot_timeline_chart
def plot_timeline_chart(
    metadata: dict[str, Any],
    filtered_df: pd.DataFrame,
    chart_height: int | None = None,
    chart_width: int | None = None,
    item_spacing: int = 25,
    line_width: int = 15,
    margin_config: dict | None = None,
) -> go.Figure:
    """
    Plot an improved timeline using anos_disponiveis from metadata, with acronyms from DataFrame.

    Args:
        metadata: Initiative metadata
        filtered_df: Filtered DataFrame
        chart_height: Custom chart height (None for auto)
        chart_width: Custom chart width (None for auto)
        item_spacing: Vertical spacing between items (pixels)
        line_width: Width of timeline bars
        margin_config: Custom margins dict
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (Insufficient data)"
        )

    # Create a working copy and ensure Display_Name column exists, using the centralized function
    plot_df = filtered_df.copy()
    # Ensure 'Name' column exists for mapping with metadata keys
    if (
        "Name" not in plot_df.columns and "Nome" in plot_df.columns
    ):  # Handle legacy 'Nome'
        plot_df.rename(columns={"Nome": "Name"}, inplace=True)
    if "Display_Name" not in plot_df.columns:
        plot_df = add_display_names_to_df(
            plot_df
        )  # Add/overwrite Display_Name using chart_core

    timeline_data = []
    all_years = set()

    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]

        if initiative_row_series.empty:
            continue

        initiative_row = initiative_row_series.iloc[0]
        display_name = initiative_row["Display_Name"]
        metodologia = initiative_row.get("Methodology", "N/A")

        # Get coverage information from metadata
        coverage = meta_content.get("coverage", "N/A")

        years_key = (
            "available_years"
            if "available_years" in meta_content
            else "anos_disponiveis"
        )
        if years_key in meta_content and meta_content[years_key]:
            # Ensure years are integers
            valid_years_for_initiative = [
                int(y)
                for y in meta_content[years_key]
                if pd.notna(y) and str(y).strip().isdigit()
            ]
            if not valid_years_for_initiative:
                continue

            for ano in valid_years_for_initiative:
                timeline_data.append(
                    {
                        "produto": nome_original_metadata,
                        "produto_display_name": display_name,
                        "ano": int(ano),  # Ensure ano is int
                        "disponivel": 1,
                        "metodologia": metodologia,
                        "coverage": coverage,
                    }
                )
                all_years.add(int(ano))

    if not timeline_data:  # Simplified check, all_years would also be empty
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No temporal data for selected initiatives)"
        )
    timeline_df = pd.DataFrame(timeline_data)

    # Calculate dynamic range based on actual data
    min_year_data = int(timeline_df["ano"].min()) if not timeline_df.empty else 1985
    max_year_data = int(timeline_df["ano"].max()) if not timeline_df.empty else 2024

    # Use dynamic range: start at first year, end at last year + 1
    chart_min_year, chart_max_year = min_year_data, max_year_data + 1
    all_years_range = list(
        range(min_year_data, max_year_data + 1)
    )  # Define the specific order based on the provided image
    desired_order = [
        "CGLS",
        "GDW",
        "ESRI-10m LULC",
        "UMD-GLC",
        "GPW",
        "UMD-SASM",
        "ESA-WC",
        "WorldCereal",
        "PRODES",
        "DETER",
        "TerraClass Amazon",
        "TerraClass Cerrado",
        "MapBiomas",
        "IBGE-MLCU",
        "CONAB-AM",
    ]

    # Create list of unique items (original_name, metadata) for efficient sorting
    unique_items = []
    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]
        if not initiative_row_series.empty:
            initiative_row = initiative_row_series.iloc[0]
            # Use o acrônimo do metadata, se existir, senão use o nome
            acronym = meta_content.get("acronym", initiative_row["Display_Name"])
            coverage = meta_content.get("coverage", "N/A")
            unique_items.append(
                (nome_original_metadata, {"coverage": coverage, "acronym": acronym})
            )

    # Sort items based on the desired order from the image (reversed from top to bottom)
    try:
        sorted_items = sorted(
            unique_items,
            key=lambda x: (
                desired_order.index(x[1]["acronym"])
                if x[1]["acronym"] in desired_order
                else len(desired_order)
            ),
            reverse=True,
        )
    except (ValueError, KeyError):
        sorted_items = sorted(unique_items, key=lambda x: x[1]["acronym"], reverse=True)

    # Agora a lista de exibição usa acrônimos
    display_acronyms_sorted = [item[1]["acronym"] for item in sorted_items]
    if not display_acronyms_sorted:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No unique initiatives to display)"
        )

    # Ajuste o DataFrame para usar o acrônimo
    matrix_data = []
    for item in sorted_items:
        nome_original_metadata = item[0]
        acronym = item[1]["acronym"]
        produto_data_for_matrix_rows = timeline_df[
            timeline_df["produto"] == nome_original_metadata
        ]
        if produto_data_for_matrix_rows.empty:
            continue
        produto_anos = produto_data_for_matrix_rows["ano"].tolist()
        produto_metodologia = produto_data_for_matrix_rows["metodologia"].iloc[0]
        for ano_iter in all_years_range:
            matrix_data.append(
                {
                    "produto": nome_original_metadata,
                    "produto_acronym": acronym,
                    "ano": ano_iter,
                    "disponivel": 1 if ano_iter in produto_anos else 0,
                    "metodologia": produto_metodologia,
                }
            )

    if not matrix_data:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No data for matrix generation)"
        )

    matrix_df = pd.DataFrame(matrix_data)

    fig_timeline = go.Figure()
    unique_original_names_for_colors = [item[0] for item in sorted_items]
    color_map = get_initiative_color_map(unique_original_names_for_colors)

    for acronym in display_acronyms_sorted:
        produto_data_plot = matrix_df[matrix_df["produto_acronym"] == acronym]
        if produto_data_plot.empty:
            continue
        anos_disponiveis = sorted(
            produto_data_plot[produto_data_plot["disponivel"] == 1]["ano"].tolist()
        )
        metodologia = produto_data_plot["metodologia"].iloc[0]
        original_name_for_color_key = produto_data_plot["produto"].iloc[0]
        cor = color_map.get(
            original_name_for_color_key,
            px.colors.qualitative.Set1[
                display_acronyms_sorted.index(acronym) % len(px.colors.qualitative.Set1)
            ],
        )

        if anos_disponiveis:
            segments = []
            start_year_segment = anos_disponiveis[0]
            end_year_segment = anos_disponiveis[0]
            for j in range(1, len(anos_disponiveis)):
                if anos_disponiveis[j] == end_year_segment + 1:
                    end_year_segment = anos_disponiveis[j]
                else:
                    segments.append((start_year_segment, end_year_segment))
                    start_year_segment = anos_disponiveis[j]
                    end_year_segment = anos_disponiveis[j]
            segments.append((start_year_segment, end_year_segment))

            for seg_start, seg_end in segments:
                # Add a line segment for each continuous range of years
                fig_timeline.add_trace(
                    go.Scatter(
                        x=[
                            seg_start,
                            seg_end + 1,
                        ],  # Use seg_end + 1 to extend the line to the next year
                        y=[acronym, acronym],
                        mode="lines",
                        line={
                            "color": cor,
                            "width": line_width,
                        },  # Use parametrized width
                        name=acronym,
                        showlegend=False,  # Remove legend
                        legendgroup=acronym,
                        hovertemplate=f"<b>{acronym}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>",
                    )
                )

    apply_modern_theme(fig_timeline, "Initiative Timeline", "Year", "Initiatives", chart_type="timeline")

    # Custom margins for timeline - preserve left margin for initiative names
    # Use chart_core margins as base but increase left for initiative names
    from scripts.plotting.chart_core import CHART_CONFIG

    default_margins = {
        "l": 220,  # Large left margin for initiative names
        "r": CHART_CONFIG["margins"]["right"],
        "t": CHART_CONFIG["margins"]["top"],
        "b": CHART_CONFIG["margins"]["bottom"],  # Use standardized bottom margin
    }
    margins = margin_config if margin_config else default_margins

    # Calculate height
    if chart_height is None:
        calculated_height = max(300, len(display_acronyms_sorted) * item_spacing)
    else:
        calculated_height = chart_height

    # Padronizar espessura dos ticks
    tick_width_standard = 0.8

    # Get modern config and remove conflicting parameters
    modern_config = get_modern_timeline_config()
    # Remove parameters that will be specifically set to avoid conflicts
    modern_config.pop('margin', None)
    modern_config.pop('yaxis', None)
    modern_config.pop('xaxis', None)
    
    fig_timeline.update_layout(
        **modern_config,
        height=calculated_height,
        margin=margins,
    )
    
    # Apply specific axis configurations after modern config
    fig_timeline.update_yaxes(
        tickmode="array",
        tickvals=display_acronyms_sorted,
        ticktext=display_acronyms_sorted,
        type="category",
        categoryorder="array",
        categoryarray=display_acronyms_sorted,
        showgrid=False,
        ticks="outside",
        ticklen=8,
        tickwidth=tick_width_standard,
        tickcolor="#4A5568",  # Modern gray
        showline=True,
        linewidth=1,
        linecolor="black",
    )
    
    fig_timeline.update_xaxes(
        range=[chart_min_year - 0.5, chart_max_year + 0.5],
        tickmode="array",
        tickvals=list(range(chart_min_year, chart_max_year + 2)),
        ticktext=[
            str(year) for year in range(chart_min_year, chart_max_year + 2)
        ],
        tickformat="d",
        tickangle=45,
        # tickfont removed - using chart_core standard configuration
        ticks="outside",
        ticklen=8,
        tickwidth=tick_width_standard,
        tickcolor="black",
        showgrid=True,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="black",
        type="linear",
        dtick=1,
        autorange=False,
        fixedrange=False,
    )
    
    fig_timeline.update_layout(
        showlegend=True,
        legend={"traceorder": "normal"},
    )
    # reduzir a margem da figura na direita
    fig_timeline.update_layout(
        margin={
            "l": margins["l"],
            "r": 20,
            "t": margins["t"],
            "b": margins["b"],
        }  # Reduced right margin
    )
    return fig_timeline


def timeline_with_controls(metadata: dict[str, Any], filtered_df: pd.DataFrame):
    """Timeline chart with interactive controls for Streamlit."""

    st.sidebar.subheader("📐 Timeline Dimensions")

    # Controles de dimensão
    chart_height = st.sidebar.slider(
        "Chart Height",
        min_value=200,
        max_value=1200,
        value=600,
        step=50,
        help="Total height of the chart in pixels",
    )

    item_spacing = st.sidebar.slider(
        "Item Spacing",
        min_value=15,
        max_value=50,
        value=25,
        step=5,
        help="Vertical spacing between timeline items",
    )

    line_width = st.sidebar.slider(
        "Line Width",
        min_value=5,
        max_value=30,
        value=15,
        step=2,
        help="Width of the timeline bars",
    )

    # Controles de margem
    with st.sidebar.expander("🔧 Advanced Margins"):
        margin_left = st.number_input(
            "Left Margin",
            value=220,
            min_value=50,
            max_value=400,
            help="Space for initiative names on the left",
        )
        margin_right = st.number_input(
            "Right Margin", value=30, min_value=10, max_value=100
        )
        margin_top = st.number_input(
            "Top Margin",
            value=60,
            min_value=20,
            max_value=150,
            help="Space for title at the top",
        )
        margin_bottom = st.number_input(
            "Bottom Margin",
            value=40,
            min_value=20,
            max_value=100,
            help="Space for year labels at the bottom",
        )

    margin_config = {
        "l": margin_left,
        "r": margin_right,
        "t": margin_top,
        "b": margin_bottom,
    }

    # Gerar gráfico com configurações
    # Updated to call the renamed function
    fig = plot_timeline_chart(
        metadata,
        filtered_df,
        chart_height=chart_height,
        item_spacing=item_spacing,
        line_width=line_width,
        margin_config=margin_config,
    )
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

    # Download functionality removed for cleaner interface
    if fig:
        pass

    # Show current settings
    with st.sidebar.expander("📊 Current Settings"):
        st.json(
            {
                "chart_height": chart_height,
                "item_spacing": item_spacing,
                "line_width": line_width,
                "margins": margin_config,
            }
        )


# Placeholder functions for missing charts


def plot_coverage_heatmap_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """Generates the Plotly figure for the coverage heatmap."""
    if temporal_data.empty:
        fig = go.Figure()
        apply_modern_theme(fig, "Coverage Heatmap (No Data Available)", chart_type="heatmap")
        return fig
    
    try:
        # Create pivot table for heatmap - availability by type and year
        if "Tipo" in temporal_data.columns and "Anos_Lista" in temporal_data.columns:
            # Explode years for each initiative
            heatmap_data = []
            for _, row in temporal_data.iterrows():
                if row["Anos_Lista"]:
                    for year in row["Anos_Lista"]:
                        heatmap_data.append({
                            "Year": year,
                            "Type": row.get("Tipo", "Unknown"),
                            "Initiative": row.get("Display_Name", "Unknown"),
                            "Count": 1
                        })
            
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                pivot_df = heatmap_df.groupby(["Type", "Year"]).size().reset_index(name="Count")
                pivot_table = pivot_df.pivot(index="Type", columns="Year", values="Count").fillna(0)
                
                # Create heatmap
                fig = px.imshow(
                    pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    color_continuous_scale=get_modern_colorscale("blues"),
                    aspect="auto",
                    labels={"x": "Year", "y": "Initiative Type", "color": "Active Initiatives"}
                )
                
                apply_modern_theme(
                    fig,
                    title="Initiative Coverage Heatmap by Type and Year",
                    xaxis_title="Year",
                    yaxis_title="Initiative Type",
                    chart_type="heatmap",
                    num_items=len(pivot_table)
                )
                return fig
        
        # Fallback basic heatmap
        fig = go.Figure()
        apply_modern_theme(fig, "Coverage Heatmap (Insufficient Data)", chart_type="heatmap")
        return fig
        
    except Exception as e:
        fig = go.Figure()
        apply_modern_theme(fig, f"Coverage Heatmap (Error: {str(e)})", chart_type="heatmap")
        return fig


def plot_gaps_bar_chart(gaps_data: pd.DataFrame) -> go.Figure:
    """Generates the Plotly bar chart for temporal gaps analysis."""
    if gaps_data.empty:
        fig = go.Figure()
        apply_modern_theme(fig, "Data Gaps Analysis (No Data Available)", chart_type="bar")
        return fig
    
    try:
        # Calculate data gaps by analyzing years coverage
        gap_analysis = []
        
        for _, row in gaps_data.iterrows():
            initiative_name = row.get("Display_Name", "Unknown")
            years_list = row.get("Anos_Lista", [])
            
            if years_list and len(years_list) > 1:
                # Convert all years to integers and filter out invalid values
                try:
                    years_int = []
                    for year in years_list:
                        if isinstance(year, (int, float)):
                            years_int.append(int(year))
                        elif isinstance(year, str) and year.strip().isdigit():
                            years_int.append(int(year.strip()))
                    
                    if len(years_int) > 1:
                        # Calculate gaps in year coverage
                        years_sorted = sorted(years_int)
                        total_years = years_sorted[-1] - years_sorted[0] + 1
                        actual_years = len(years_int)
                        gap_percentage = ((total_years - actual_years) / total_years) * 100 if total_years > 0 else 0
                        
                        gap_analysis.append({
                            "Initiative": initiative_name,
                            "Type": row.get("Tipo", "Unknown"),
                            "Gap_Percentage": gap_percentage,
                            "Missing_Years": total_years - actual_years,
                            "Total_Period": total_years,
                            "Available_Years": actual_years
                        })
                except (ValueError, TypeError):
                    # Skip initiatives with invalid year data
                    continue
        
        if gap_analysis:
            gaps_df = pd.DataFrame(gap_analysis)
            gaps_df = gaps_df.sort_values("Gap_Percentage", ascending=True)
            
            # Top 15 initiatives with gaps
            top_gaps = gaps_df.head(15)
            
            # Create bar chart
            colors = get_modern_colors(f"distinct_{len(top_gaps)}")
            
            fig = go.Figure(data=[
                go.Bar(
                    x=top_gaps["Gap_Percentage"],
                    y=top_gaps["Initiative"],
                    orientation='h',
                    marker=dict(
                        color=colors,
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{gap:.1f}% ({missing}/{total})" 
                          for gap, missing, total in zip(
                              top_gaps["Gap_Percentage"], 
                              top_gaps["Missing_Years"], 
                              top_gaps["Total_Period"]
                          )],
                    textposition='auto',
                    hovertemplate="<b>%{y}</b><br>" +
                                  "Gap: %{x:.1f}%<br>" +
                                  "Missing: %{customdata[0]} years<br>" +
                                  "Available: %{customdata[1]} years<br>" +
                                  "Total Period: %{customdata[2]} years<extra></extra>",
                    customdata=top_gaps[["Missing_Years", "Available_Years", "Total_Period"]].values
                )
            ])
            
            apply_modern_theme(
                fig,
                title="Data Gaps Analysis - Top 15 Initiatives with Missing Years",
                xaxis_title="Gap Percentage (%)",
                yaxis_title="Initiative",
                chart_type="bar",
                num_items=len(top_gaps)
            )
            
            # Adjust layout for horizontal bar chart
            fig.update_layout(
                height=max(400, len(top_gaps) * 30),
                xaxis=dict(range=[0, max(100, top_gaps["Gap_Percentage"].max() * 1.1)])
            )
            
            return fig
        
        # No gaps found
        fig = go.Figure()
        apply_modern_theme(fig, "Data Gaps Analysis (No Gaps Detected)", chart_type="bar")
        fig.add_annotation(
            text="All initiatives have complete year coverage",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="green")
        )
        return fig
        
    except Exception as e:
        fig = go.Figure()
        apply_modern_theme(fig, f"Data Gaps Analysis (Error: {str(e)})", chart_type="bar")
        return fig


def plot_evolution_line_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """
    Generates the Plotly line chart for evolution analysis showing how data availability
    evolves over time across all initiatives.

    Args:
        temporal_data: DataFrame with temporal data containing 'Anos_Lista' and 'Tipo' columns
          Returns:
        go.Figure: Plotly figure showing evolution of data availability
    """
    if temporal_data.empty or "Anos_Lista" not in temporal_data.columns:
        fig = go.Figure()
        apply_modern_theme(fig, "Evolution Line Chart (No Data Available)", chart_type="line")
        fig.add_annotation(
            text="No temporal data available for evolution analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 16, "color": "gray"},
        )
        return fig

    # Process data to count initiatives per year
    all_years = []
    for _, row in temporal_data.iterrows():
        if isinstance(row["Anos_Lista"], list):
            all_years.extend(row["Anos_Lista"])

    if not all_years:
        fig = go.Figure()
        apply_modern_theme(fig, "Evolution Line Chart (No Year Data)", chart_type="line")
        fig.add_annotation(
            text="No year data available for evolution analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 16, "color": "gray"},
        )
        return fig

    # Count initiatives per year
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame(
        {"Year": year_counts.index, "Number_Initiatives": year_counts.values}
    )

    # Create the figure
    fig = go.Figure()

    # Add the main evolution line with area fill
    fig.add_trace(
        go.Scatter(
            x=years_df["Year"],
            y=years_df["Number_Initiatives"],
            mode="lines+markers",
            name="Active Initiatives",
            line={"color": "rgba(0, 150, 136, 1)", "width": 3},
            marker={
                "size": 8,
                "color": "rgba(0, 150, 136, 0.8)",
                "line": {"width": 2, "color": "rgba(0, 150, 136, 1)"},
            },
            fill="tonexty",
            fillcolor="rgba(0, 150, 136, 0.2)",
            hovertemplate="<b>Year: %{x}</b><br>Active Initiatives: %{y}<extra></extra>",
        )
    )
    # Add trend markers for key points
    max_initiatives_year = years_df.loc[years_df["Number_Initiatives"].idxmax()]

    # Mark peak year
    fig.add_trace(
        go.Scatter(
            x=[max_initiatives_year["Year"]],
            y=[max_initiatives_year["Number_Initiatives"]],
            mode="markers",
            name="Peak Year",
            marker={
                "size": 12,
                "color": "rgba(255, 193, 7, 1)",
                "symbol": "star",
                "line": {"width": 2, "color": "rgba(255, 152, 0, 1)"},
            },
            hovertemplate=f"<b>Peak Year: {max_initiatives_year['Year']}</b><br>Initiatives: {max_initiatives_year['Number_Initiatives']}<extra></extra>",
            showlegend=True,
        )
    )
    # Apply standard layout with line chart dimensions
    apply_modern_theme(
        fig,
        "Initiative Evolution Over Time",
        xaxis_title="Year",
        yaxis_title="Number of Active Initiatives",
        chart_type="line",
        num_items=len(years_df),
    )

    # Apply modern styling
    fig = apply_modern_styling(fig, **get_modern_line_config())
    
    # Enhanced layout specific to evolution chart
    fig.update_layout(
        showlegend=True,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.08)",
            "gridwidth": 1,
            "tickformat": "d",
            "dtick": 2,  # Show every 2 years for better readability
            "tickangle": 45 if len(years_df) > 15 else 0,  # Rotate labels if many years
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.08)",
            "gridwidth": 1,
            "tickformat": "d",
            "zeroline": True,
            "zerolinecolor": "rgba(128,128,128,0.4)",
            "zerolinewidth": 1,
        },
        hovermode="x unified",
    )

    # Add annotations for context
    avg_initiatives = years_df["Number_Initiatives"].mean()
    fig.add_hline(
        y=avg_initiatives,
        line_dash="dash",
        line_color="rgba(128,128,128,0.6)",
        annotation_text=f"Average: {avg_initiatives:.1f}",
        annotation_position="bottom right",
    )

    return fig


def plot_evolution_heatmap_chart(
    metadata: dict[str, Any], filtered_df: pd.DataFrame
) -> go.Figure:
    """
    Generates an area chart showing the evolution of spatial resolution in LULC initiatives over time.
    Uses three resolution categories: Coarse (≥100m), Medium (30-99m), and High (<30m).

    Args:
        metadata: Initiative metadata containing spatial resolution and available years
        filtered_df: Filtered DataFrame with initiative data
          Returns:
        go.Figure: Plotly figure showing stacked area chart of resolution evolution
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        apply_modern_theme(fig, "Resolution Evolution (No Data Available)", chart_type="area")
        fig.add_annotation(
            text="No data available for resolution evolution analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 16, "color": "gray"},
        )
        return fig

    # Process metadata to extract resolution and years data
    resolution_data = []

    for initiative_name, meta_info in metadata.items():
        if not isinstance(meta_info, dict):
            continue

        # Get available years
        years_key = (
            "available_years" if "available_years" in meta_info else "anos_disponiveis"
        )
        if years_key not in meta_info or not meta_info[years_key]:
            continue

        years = meta_info[years_key]
        if not isinstance(years, list):
            continue

        # Get spatial resolution
        spatial_res = meta_info.get("spatial_resolution")
        if spatial_res is None:
            continue

        # Parse resolution to get a single representative value
        resolution_value = _parse_resolution_for_categorization(spatial_res)
        if resolution_value is None:
            continue

        # Categorize resolution into 4 categories:
        # ≥100m, <30-99m, <20-29m, <20m
        if resolution_value >= 100:
            category = "≥100m"
        elif resolution_value >= 50:
            category = "50≥SR>100m"
        elif resolution_value >= 30:
            category = "30≥SR>50m"
        else:
            category = "<30m"

        # Add data for each year
        for year in years:
            if isinstance(year, int | float) and 1985 <= year <= 2024:
                resolution_data.append(
                    {
                        "initiative": initiative_name,
                        "year": int(year),
                        "resolution_value": resolution_value,
                        "category": category,
                    }
                )

    if not resolution_data:
        fig = go.Figure()
        apply_modern_theme(fig, "Resolution Evolution (No Data Available)", chart_type="area")
        fig.add_annotation(
            text="No resolution data available for the selected initiatives",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 16, "color": "gray"},
        )
        return fig

    # Create DataFrame and aggregate by year and category
    df_resolution = pd.DataFrame(resolution_data)

    # Count initiatives by year and category
    yearly_counts = (
        df_resolution.groupby(["year", "category"]).size().reset_index(name="count")
    )

    # Pivot to get categories as columns
    pivot_df = yearly_counts.pivot(
        index="year", columns="category", values="count"
    ).fillna(0)

    # Ensure we have all years from 1985 to 2024
    all_years = list(range(1985, 2025))
    pivot_df = pivot_df.reindex(all_years, fill_value=0)
    # Parametrize legend/category order and colors using modern theme
    category_order = ["<30m", "30≥SR>50m", "50≥SR>100m", "≥100m"]
    modern_colors = get_modern_colors(4) if get_modern_colors else None
    colors = {
        "<30m": modern_colors[0] if modern_colors else "#5e4fa2",  # Modern blue
        "30≥SR>50m": modern_colors[1] if modern_colors else "#66c2a5",  # Modern green
        "50≥SR>100m": modern_colors[2] if modern_colors else "#fdae61",  # Modern orange
        "≥100m": modern_colors[3] if modern_colors else "#d53e4f",  # Modern red
    }

    # Ensure all categories exist in the DataFrame
    for category in category_order:
        if category not in pivot_df.columns:
            pivot_df[category] = 0
    # Create the figure
    fig = go.Figure()

    import numpy as np  # Add stacked area traces with modern styling - only fills, no lines

    for _i, category in enumerate(category_order):
        if category in pivot_df.columns:
            y_values = pivot_df[category].copy()
            if np.nansum(y_values) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=pivot_df.index,
                        y=y_values,
                        mode="none",  # No lines or markers
                        name=category,  # Simplified legend name
                        fill="tonexty",
                        fillcolor=colors[category],
                        line={"width": 0},  # No line border
                        hovertemplate=f"<b>Resolution {category}</b><br>Year: %{{x}}<br>Initiatives: %{{y}}<extra></extra>",
                        stackgroup="one",
                        opacity=0.85,  # Slight transparency for modern look
                    )
                )
    # Add subtle milestone annotations for key years
    milestones = {2000: "Trough", 2020: "Peak"}

    for year, label in milestones.items():
        if year in pivot_df.index:
            fig.add_vline(
                x=year,
                line_dash="dot",
                line_color="black",
                line_width=1,
                annotation_text=label,
                annotation_position="top",
                annotation_font_size=20,
                annotation_font_color="rgba(64,64,64,0.9)",
            )
    
    # Apply modern styling
    fig = apply_modern_styling(fig, **get_modern_line_config())
    
    fig.update_layout(
        showlegend=True,
        margin={"b": 120},  # Increase bottom margin for legend
        xaxis={
            "range": [1985, 2024],
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.08)",
            "gridwidth": 1,
            "tickformat": "d",
            "dtick": 1,
            "tickangle": 45,
            "tickmode": "linear",
        },
    )

    # Apply modern theme
    apply_modern_theme(
        fig, 
        title="Spatial Resolution Evolution", 
        xaxis_title="Year", 
        yaxis_title="Number of Initiatives", 
        chart_type="area"
    )  # Customize layout for modern area chart
    # do layout padrão, desabilite as alterações na legenda
    fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.27,  # Position below the x-axis
            "xanchor": "center",
            "x": 0.5,  # Center horizontally
            "bgcolor": "rgba(255,255,255,0.9)",
            "bordercolor": "rgba(0,0,0,0.1)",
            "borderwidth": 1,
            "font": {"size": 16},
        }
    )
    fig.update_layout(margin={"r": 40})
    return fig


def _parse_resolution_for_categorization(spatial_res: Any) -> float | None:
    """
    Helper function to parse spatial resolution for categorization.
    Returns a single representative resolution value in meters.
    """
    if spatial_res is None:
        return None

    # Handle direct numeric values
    if isinstance(spatial_res, int | float):
        return float(spatial_res)

    # Handle string values
    if isinstance(spatial_res, str):
        # Extract numeric value from string like "30m", "100", etc.
        res_str = re.sub(r"[^\d.]", "", spatial_res)
        if res_str:
            return float(res_str)
        return None

    # Handle list of values or objects
    if isinstance(spatial_res, list):
        values = []

        # Look for 'current' resolution first
        for item in spatial_res:
            if isinstance(item, dict) and item.get("current", False):
                val = item.get("resolution")
                if val is not None:
                    if isinstance(val, int | float):
                        return float(val)
                    elif isinstance(val, str):
                        res_str = re.sub(r"[^\d.]", "", val)
                        if res_str:
                            return float(res_str)

        # If no 'current' found, collect all values
        for item in spatial_res:
            val = item.get("resolution") if isinstance(item, dict) else item

            if val is not None:
                if isinstance(val, int | float):
                    values.append(float(val))
                elif isinstance(val, str):
                    res_str = re.sub(r"[^\d.]", "", val)
                    if res_str:
                        values.append(float(res_str))

        # Return the minimum resolution (highest detail) if multiple values
        if values:
            return min(values)

    return None


def add_chart_download(fig: go.Figure, default_filename: str, key_prefix: str):
    """
    Helper function to add download functionality to any chart.

    Args:
        fig: Plotly figure object
        default_filename: Default filename for download
        key_prefix: Unique prefix for widget keys
    """
    if fig:
        # Download functionality removed for cleaner interface
        pass


def display_brazilian_geographic_tables():
    """
    Display beautiful tables with Brazilian geographic information using Streamlit.
    Shows both regions/states table and mesoregions examples.
    """

    st.subheader("📍 Informações Geográficas do Brasil")

    # Create tabs for different tables
    tab1, tab2 = st.tabs(["🗺️ Regiões e Estados", "🏘️ Exemplos de Mesorregiões"])

    with tab1:
        st.markdown("### Estados Brasileiros por Região")

        # Generate and display the regions table
        fig_regions = create_brazilian_regions_table()
        st.plotly_chart(fig_regions, use_container_width=True)

        # Add some statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Estados", "27", "26 Estados + 1 DF")
        with col2:
            st.metric("Regiões", "5", "Norte, Nordeste, Centro-Oeste, Sudeste, Sul")
        with col3:
            st.metric("Maior Região", "Nordeste", "9 estados")

    with tab2:
        st.markdown("### Exemplos de Mesorregiões Brasileiras")

        # Generate and display the mesoregions table
        fig_meso = create_mesoregions_table()
        st.plotly_chart(fig_meso, use_container_width=True)

        st.info(
            "💡 **Nota**: Esta tabela apresenta exemplos selecionados de mesorregiões de diferentes estados brasileiros para demonstração."
        )
