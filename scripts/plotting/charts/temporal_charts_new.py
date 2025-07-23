#!/usr/bin/env python3
"""
Optimized Temporal Charts Module
===============================

Streamlined temporal analysis charts with standardized styling and enhanced caching.
Removed excessive customization options for better user experience.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scripts.plotting.chart_core import add_display_names_to_df, apply_standard_layout

# Import enhanced caching and core functions
from scripts.plotting.universal_cache import cache_figure
from scripts.utilities.config import get_initiative_color_map


@cache_figure(ttl=600)
def plot_timeline_chart(
    metadata: dict[str, Any], filtered_df: pd.DataFrame
) -> go.Figure:
    """
    Optimized timeline chart with standardized dimensions and caching.
    Removed excessive customization parameters for cleaner interface.

    Args:
        metadata: Initiative metadata
        filtered_df: Filtered DataFrame with initiative data
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (Insufficient data)"
        )

    # Create working copy with display names
    plot_df = filtered_df.copy()
    if "Name" not in plot_df.columns and "Nome" in plot_df.columns:
        plot_df.rename(columns={"Nome": "Name"}, inplace=True)
    if "Display_Name" not in plot_df.columns:
        plot_df = add_display_names_to_df(plot_df)

    timeline_data = []
    all_years = set()

    # Process metadata for timeline data
    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]

        if initiative_row_series.empty:
            continue

        initiative_row = initiative_row_series.iloc[0]
        display_name = initiative_row["Display_Name"]
        metodologia = initiative_row.get("Methodology", "N/A")
        coverage = meta_content.get("coverage", "N/A")

        years_key = (
            "available_years"
            if "available_years" in meta_content
            else "anos_disponiveis"
        )
        if years_key in meta_content and meta_content[years_key]:
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
                        "ano": int(ano),
                        "disponivel": 1,
                        "metodologia": metodologia,
                        "coverage": coverage,
                    }
                )
                all_years.add(int(ano))

    if not timeline_data:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No temporal data for selected initiatives)"
        )

    timeline_df = pd.DataFrame(timeline_data)

    # Calculate dynamic range based on actual data
    min_year_data = int(timeline_df["ano"].min()) if not timeline_df.empty else 1985
    max_year_data = int(timeline_df["ano"].max()) if not timeline_df.empty else 2024
    chart_min_year, chart_max_year = min_year_data, max_year_data + 1
    all_years_range = list(range(min_year_data, max_year_data + 1))

    # Standardized order for initiatives
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

    # Create sorted list of initiatives
    unique_items = []
    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df["Name"] == nome_original_metadata]
        if not initiative_row_series.empty:
            initiative_row = initiative_row_series.iloc[0]
            acronym = meta_content.get("acronym", initiative_row["Display_Name"])
            coverage = meta_content.get("coverage", "N/A")
            unique_items.append(
                (nome_original_metadata, {"coverage": coverage, "acronym": acronym})
            )

    # Sort based on desired order
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

    display_acronyms_sorted = [item[1]["acronym"] for item in sorted_items]
    if not display_acronyms_sorted:
        return go.Figure().update_layout(
            title="Timeline of Initiatives (No unique initiatives to display)"
        )

    # Create matrix data for timeline visualization
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

    # Create the timeline figure
    fig_timeline = go.Figure()
    unique_original_names_for_colors = [item[0] for item in sorted_items]
    color_map = get_initiative_color_map(unique_original_names_for_colors)

    # Add timeline traces
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
            # Create segments for continuous year ranges
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
                fig_timeline.add_trace(
                    go.Scatter(
                        x=[seg_start, seg_end + 1],
                        y=[acronym, acronym],
                        mode="lines",
                        line={"color": cor, "width": 12},  # Standardized line width
                        name=acronym,
                        showlegend=False,
                        legendgroup=acronym,
                        hovertemplate=f"<b>{acronym}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>",
                    )
                )

    # Apply standardized layout with timeline-specific configurations
    apply_standard_layout(fig_timeline, "Year", "Initiatives")

    # Calculate standardized height based on number of initiatives
    calculated_height = max(400, len(display_acronyms_sorted) * 30)

    # Timeline-specific layout updates
    fig_timeline.update_layout(
        height=calculated_height,
        margin={"l": 200, "r": 40, "t": 60, "b": 80},  # Standardized margins
        yaxis={
            "tickmode": "array",
            "tickvals": display_acronyms_sorted,
            "ticktext": display_acronyms_sorted,
            "type": "category",
            "categoryorder": "array",
            "categoryarray": display_acronyms_sorted,
            "showgrid": False,
            "ticks": "outside",
            "ticklen": 8,
            "tickwidth": 0.8,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
        },
        xaxis={
            "range": [chart_min_year - 0.5, chart_max_year + 0.5],
            "tickmode": "array",
            "tickvals": list(range(chart_min_year, chart_max_year + 2)),
            "ticktext": [
                str(year) for year in range(chart_min_year, chart_max_year + 2)
            ],
            "tickformat": "d",
            "tickangle": 45,
            "ticks": "outside",
            "ticklen": 8,
            "tickwidth": 0.8,
            "tickcolor": "black",
            "showgrid": True,
            "zeroline": False,
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
            "type": "linear",
            "dtick": 1,
            "autorange": False,
            "fixedrange": False,
        },
        showlegend=False,  # Remove legend for cleaner timeline
    )

    return fig_timeline


def timeline_with_controls(metadata: dict[str, Any], filtered_df: pd.DataFrame):
    """Simplified timeline chart with modern interface and no excessive controls."""

    # Generate optimized timeline chart with standardized configuration
    fig = plot_timeline_chart(metadata, filtered_df)

    # Display chart with modern container
    st.plotly_chart(fig, use_container_width=True)

    # Simple download button using native Streamlit
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📥 Download Chart", key="timeline_download"):
            st.success("Chart ready for download! Use browser context menu to save.")

    # Modern info panel with key statistics
    with st.expander("📊 Timeline Statistics", expanded=False):
        if not filtered_df.empty:
            total_initiatives = len(filtered_df)
            all_years = []
            for meta in metadata.values():
                years = meta.get("available_years", meta.get("anos_disponiveis", []))
                if years:
                    all_years.extend(years)

            if all_years:
                temporal_coverage = f"{min(all_years)}-{max(all_years)}"
                st.metric("Total Initiatives", total_initiatives)
                st.metric("Temporal Coverage", temporal_coverage)

                # Coverage by type
                if "Coverage" in filtered_df.columns:
                    coverage_counts = filtered_df["Coverage"].value_counts()
                    if len(coverage_counts) > 0:
                        st.bar_chart(coverage_counts)


def add_chart_download(fig: go.Figure, default_filename: str, key_prefix: str):
    """
    Helper function to add download functionality to any chart.

    Args:
        fig: Plotly figure object
        default_filename: Default filename for download
        key_prefix: Unique prefix for widget keys
    """
    if fig and st.button(
        f"📥 Download {default_filename}", key=f"{key_prefix}_download"
    ):
        st.success("Chart ready for download! Use browser context menu to save.")


def display_brazilian_geographic_tables():
    """
    Display simplified geographic information using modern Streamlit components.
    """

    st.subheader("📍 Informações Geográficas do Brasil")

    # Create metrics for key geographic statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Estados", "27", "26 Estados + 1 DF")
    with col2:
        st.metric("Regiões", "5", "Norte, Nordeste, Centro-Oeste, Sudeste, Sul")
    with col3:
        st.metric("Maior Região", "Nordeste", "9 estados")
    with col4:
        st.metric("Menor Região", "Centro-Oeste", "4 estados")

    # Simple geographic data display using native Streamlit
    with st.expander("🗺️ Regiões e Estados", expanded=False):
        geographic_data = {
            "Norte": [
                "Acre",
                "Amapá",
                "Amazonas",
                "Pará",
                "Rondônia",
                "Roraima",
                "Tocantins",
            ],
            "Nordeste": [
                "Alagoas",
                "Bahia",
                "Ceará",
                "Maranhão",
                "Paraíba",
                "Pernambuco",
                "Piauí",
                "Rio Grande do Norte",
                "Sergipe",
            ],
            "Centro-Oeste": [
                "Distrito Federal",
                "Goiás",
                "Mato Grosso",
                "Mato Grosso do Sul",
            ],
            "Sudeste": [
                "Espírito Santo",
                "Minas Gerais",
                "Rio de Janeiro",
                "São Paulo",
            ],
            "Sul": ["Paraná", "Rio Grande do Sul", "Santa Catarina"],
        }

        for region, states in geographic_data.items():
            st.markdown(f"**{region}** ({len(states)} estados)")
            st.write(", ".join(states))
            st.divider()


# Enhanced placeholder chart functions with caching
@cache_figure(ttl=3600)
def plot_coverage_heatmap_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """Generates cached heatmap figure for coverage analysis."""
    fig = go.Figure()
    apply_standard_layout(fig, "Year", "Initiative Type")
    fig.add_annotation(
        text="Coverage Heatmap - Coming Soon",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": "gray"},
    )
    return fig


@cache_figure(ttl=3600)
def plot_gaps_bar_chart(gaps_data: pd.DataFrame) -> go.Figure:
    """Generates cached bar chart for temporal gaps analysis."""
    fig = go.Figure()
    apply_standard_layout(fig, "Missing Years", "Initiative")
    fig.add_annotation(
        text="Temporal Gaps Analysis - Coming Soon",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": "gray"},
    )
    return fig


@cache_figure(ttl=3600)
def plot_evolution_line_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """
    Generates cached line chart for evolution analysis showing how data availability
    evolves over time across all initiatives.

    Args:
        temporal_data: DataFrame with temporal data containing 'Anos_Lista' and 'Tipo' columns
    """
    if temporal_data.empty or "Anos_Lista" not in temporal_data.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Year", "Number of Active Initiatives")
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
        apply_standard_layout(fig, "Year", "Number of Active Initiatives")
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

    fig.add_annotation(
        x=max_initiatives_year["Year"],
        y=max_initiatives_year["Number_Initiatives"],
        text=f"Peak: {max_initiatives_year['Number_Initiatives']} initiatives",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="rgba(0, 150, 136, 1)",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 150, 136, 1)",
        borderwidth=1,
    )

    # Apply standard layout
    apply_standard_layout(fig, "Year", "Number of Active Initiatives")

    return fig
