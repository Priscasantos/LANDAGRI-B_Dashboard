#!/usr/bin/env python3
"""
CONAB Chart Module
==================

Generates specialized charts for CONAB (Companhia Nacional de Abastecimento) data analysis.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from scripts.plotting.chart_core import apply_standard_layout
from scripts.utilities.type_safety import validate_plotly_params

# Brazilian states and their abbreviations
BRAZILIAN_STATES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Total states + DF = 27 for 100% coverage
TOTAL_STATES_PLUS_DF = 27

# Lista fixa de crops e cores para padronizar ordem e cor da legenda
CROP_ORDER = [
    "Coffee",
    "Corn",
    "Cotton",
    "Irrigated Rice",
    "Other summer crops",
    "Other winter crops",
    "Soybean",
    "Sugar cane",
]
CROP_COLOR_MAP = {
    "Coffee": "#8dd3c7",
    "Corn": "#bfa600",  # Amarelo escuro customizado
    "Cotton": "#bebada",
    "Irrigated Rice": "#fb8072",
    "Other summer crops": "#80b1d3",
    "Other winter crops": "#fdb462",
    "Soybean": "#b3de69",
    "Sugar cane": "#fccde5",
    "Sugar cane mill": "#808080",
}


def load_conab_detailed_data() -> dict[str, Any]:
    """Load CONAB detailed data from JSON file."""
    try:
        current_dir = Path(__file__).parent.parent.parent.parent
        file_path = current_dir / "data" / "conab_detailed_initiative.jsonc"

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

            # Clean the JSONC content
            lines = content.split("\n")
            cleaned_lines = []

            for line in lines:
                # Remove control characters and clean the line
                cleaned_line = "".join(
                    char for char in line if ord(char) >= 32 or char in "\t\n\r"
                )

                # Remove comments but keep the line if it has valid JSON
                if "//" in cleaned_line:
                    json_part = cleaned_line.split("//")[0].strip()
                    if json_part:
                        cleaned_lines.append(json_part)
                else:
                    if cleaned_line.strip():
                        cleaned_lines.append(cleaned_line)

            cleaned_content = "\n".join(cleaned_lines)

            # Additional cleanup for common JSON issues
            cleaned_content = cleaned_content.replace("\r", "").replace("\x00", "")

            return json.loads(cleaned_content)

    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        st.error(f"Error at line {e.lineno}, column {e.colno}")
        return {}
    except Exception as e:
        st.error(f"Error loading CONAB detailed data: {e}")
        return {}


def plot_conab_spatial_temporal_distribution(conab_data: dict[str, Any]) -> go.Figure:
    """
    Create a spatial and temporal distribution chart for CONAB mapping initiatives.
    Shows states/areas coverage over time in a timeline format.
    """
    if not conab_data:
        return go.Figure().update_layout()

    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})

    # Prepare data for timeline chart
    timeline_data = []
    all_states = set()
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        second_crop_years = crop_info.get("second_crop_years", {})

        # Process first safra data
        for state, years in first_crop_years.items():
            if state in regions:
                all_states.add(state)
                for year_range in years:
                    start_year = int(year_range.split("-")[0])
                    end_year = int(year_range.split("-")[1])
                    for year in range(start_year, end_year + 1):
                        timeline_data.append(
                            {
                                "State": state,
                                "Year": year,
                                "Crop": crop,
                                "Semester": "First",
                                "Coverage": 1,
                            }
                        )
        # Process second safra data
        for state, years in second_crop_years.items():
            if state in regions:
                all_states.add(state)
                for year_range in years:
                    start_year = int(year_range.split("-")[0])
                    end_year = int(year_range.split("-")[1])
                    for year in range(start_year, end_year + 1):
                        timeline_data.append(
                            {
                                "State": state,
                                "Year": year,
                                "Crop": crop,
                                "Semester": "Second",
                                "Coverage": 1,
                            }
                        )

    if not timeline_data:
        return go.Figure().update_layout()

    df = pd.DataFrame(timeline_data)

    # Cores - use CROP_COLOR_MAP instead of generating colors
    crop_types = [c for c in CROP_ORDER if c in df["Crop"].unique()]
    # Add any crops not in CROP_ORDER
    for crop in sorted(df["Crop"].unique()):
        if crop not in crop_types:
            crop_types.append(crop)

    states_list = sorted(all_states, reverse=True)
    states_list.append("Brazil")

    fig = go.Figure()
    legend_added = set()

    # Nova lógica: para cada (state, year), identificar todos os crops presentes e desenhar subdivisões
    state_year_crops = df.groupby(["State", "Year"])["Crop"].unique().reset_index()
    state_year_crops = state_year_crops.set_index(["State", "Year"])["Crop"].to_dict()

    # Para cada crop, desenhar todas as subdivisões referentes a ele
    for crop in crop_types:
        crop_data = df[df["Crop"] == crop]
        for state in states_list:
            if state == "Brazil":
                continue
            state_crop_data = crop_data[crop_data["State"] == state]
            if state_crop_data.empty:
                continue
            years = sorted(state_crop_data["Year"].unique())
            for year in years:
                crops_in_this = state_year_crops.get((state, year), [crop])
                total_crops = len(crops_in_this)
                if total_crops == 0:
                    continue
                crop_index = sorted(crops_in_this).index(crop)
                # Altura original
                original_bar_height = 0.4
                subdivided_bar_height = original_bar_height / total_crops
                state_index = states_list.index(state)
                # Centralizar subdivisões
                start_offset = -original_bar_height / 2
                bar_offset = (
                    start_offset
                    + (crop_index * subdivided_bar_height)
                    + (subdivided_bar_height / 2)
                )
                y_bottom = state_index + bar_offset - (subdivided_bar_height / 2)
                y_top = state_index + bar_offset + (subdivided_bar_height / 2)
                show_in_legend = crop not in legend_added
                if show_in_legend:
                    legend_added.add(crop)
                # Remove border lines for cleaner appearance
                fig.add_trace(
                    go.Scatter(
                        x=[year, year + 1.01, year + 1.01, year, year],
                        y=[y_bottom, y_bottom, y_top, y_top, y_bottom],
                        mode="lines",
                        fill="toself",
                        fillcolor=CROP_COLOR_MAP.get(crop, "#808080"),
                        line={"width": 0, "color": CROP_COLOR_MAP.get(crop, "#808080")},
                        name=crop,
                        legendgroup=crop,
                        showlegend=show_in_legend,
                        hovertemplate=f"<b>{state}</b><br>Crop: {crop}<br>Year: {year}<br><extra></extra>",
                    )
                )

    # Trace do Brasil
    if not df.empty:
        all_years = sorted(df["Year"].unique())
        if all_years:
            brazil_start = min(all_years)
            brazil_end = max(all_years)
            brazil_y_position = len(states_list) - 1
            fig.add_trace(
                go.Scatter(
                    x=[brazil_start, brazil_end + 1],
                    y=[brazil_y_position, brazil_y_position],
                    mode="lines",
                    line={"width": 15, "color": "#808080"},
                    name="Sugar cane mill",
                    showlegend=True,
                    hovertemplate=f"<b>Brazil</b><br>Overall Period: {brazil_start}-{brazil_end}<br><extra></extra>",
                )
            )

    from scripts.plotting.chart_core import (
        get_standard_bar_config,
        get_standard_legend_config,
    )

    tickvals = list(range(len(states_list)))
    ticktext = states_list
    layout_params = validate_plotly_params(
        title=" ",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Region</b>",
        height=600,
        showlegend=True,
        legend=get_standard_legend_config(title="Crop Type", position="right"),
        **get_standard_bar_config(),
        yaxis={
            "tickvals": tickvals,
            "ticktext": ticktext,
            "showgrid": False,
            "gridcolor": "#E5ECF6",
            "ticks": "outside",
            "ticklen": 8,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 0,
            "zeroline": False,
            "range": [-0.5, len(states_list) - 0.5],
        },
        xaxis={
            "dtick": 1,
            "showgrid": False,
            "gridcolor": "#E5ECF6",
            "ticks": "outside",
            "ticklen": 8,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 0,
            "zeroline": False,
            "tickangle": 45,
        },
    )
    fig.update_layout(**layout_params)
    apply_standard_layout(fig, "Year", "Region")
    # aplicar aqui um aumento no tamanho da fonte da legenda para 20
    fig.update_layout(legend={"font": {"size": 20}})
    # aumentar agora o tamanho da fonte do titulo da legenda para 22
    fig.update_layout(legend_title={"font": {"size": 22}})
    return fig


def plot_conab_temporal_coverage(conab_data: dict[str, Any]) -> go.Figure:
    """
    Create a temporal coverage chart showing percentage of states covered over time.
    """
    if not conab_data:
        return go.Figure().update_layout()

    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})

    # Count states per year
    year_coverage = {}
    for _crop, crop_info in crop_coverage.items():
        first_crop_years = crop_info.get("first_crop_years", {})
        second_crop_years = crop_info.get("second_crop_years", {})

        # Process first semester data
        for state, years in first_crop_years.items():
            for year_range in years:
                start_year = int(year_range.split("-")[0])
                end_year = int(year_range.split("-")[1])

                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)
        # Process second semester data
        for state, years in second_crop_years.items():
            for year_range in years:
                start_year = int(year_range.split("-")[0])
                end_year = int(year_range.split("-")[1])

                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)

    if not year_coverage:
        return go.Figure().update_layout()

    # Calculate percentage coverage
    years = sorted(year_coverage.keys())
    coverage_percentages = []

    for year in years:
        num_states = len(year_coverage[year])
        percentage = (num_states / TOTAL_STATES_PLUS_DF) * 100
        coverage_percentages.append(percentage)

    # Create figure
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=years,
            y=coverage_percentages,
            mode="lines+markers",
            line={"width": 3, "color": "#17a2b8"},
            marker={"size": 8, "color": "#17a2b8"},
            name="Coverage %",
            hovertemplate="<b>Year:</b> %{x}<br><b>Coverage:</b> %{y:.1f}%<br><extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(
        title="Temporal Coverage of CONAB Mapping Initiatives",
        xaxis_title="Year",
        yaxis_title="Pct States",
        height=500,
        yaxis={"range": [0, 100]},
        showlegend=False,
    )

    # Apply standard layout
    apply_standard_layout(fig, "Year", "Pct States")

    # Set X-axis tick angle for temporal data
    fig.update_xaxes(tickangle=45)

    return fig


def plot_conab_spatial_coverage(conab_data: dict[str, Any]) -> go.Figure:
    """
    Create a spatial coverage chart showing percentage coverage by state.
    """
    if not conab_data:
        return go.Figure().update_layout()

    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})

    # Count coverage by state
    state_coverage = {}
    for _crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        second_crop_years = crop_info.get("second_crop_years", {})

        # Count years of coverage for each state
        for state in regions:
            if state not in state_coverage:
                state_coverage[state] = set()

            # Add years from first semester
            if state in first_crop_years:
                for year_range in first_crop_years[state]:
                    start_year = int(year_range.split("-")[0])
                    end_year = int(year_range.split("-")[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)
            # Add years from second semester
            if state in second_crop_years:
                for year_range in second_crop_years[state]:
                    start_year = int(year_range.split("-")[0])
                    end_year = int(year_range.split("-")[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)

    if not state_coverage:
        return go.Figure().update_layout()

    # Calculate coverage percentages (considering 24 years from 2000-2023)
    total_years = 24
    states = []
    coverages = []

    for state, years in state_coverage.items():
        coverage_percent = (len(years) / total_years) * 100
        states.append(state)
        coverages.append(coverage_percent)

    # Sort by coverage percentage
    sorted_data = sorted(zip(states, coverages), key=lambda x: x[1])
    states, coverages = zip(*sorted_data)

    # Create figure
    fig = go.Figure()

    # Color gradient based on coverage
    colors = [
        (
            "#ffcccc"
            if c < 25
            else "#ffeb99" if c < 50 else "#ccffcc" if c < 75 else "#99ccff"
        )
        for c in coverages
    ]

    fig.add_trace(
        go.Bar(
            x=coverages,
            y=states,
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{c:.1f}%" for c in coverages],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<br><extra></extra>",
        )
    )
    # Update layout
    from scripts.plotting.chart_core import get_standard_bar_config

    fig.update_layout(
        title="Spatial Coverage of CONAB Mapping Initiatives (2000-2023)",
        showlegend=False,
        **get_standard_bar_config(),  # Apply standard bar configuration
    )

    # Apply standard layout with bar chart dimensions
    apply_standard_layout(
        fig, "Coverage (%)", "Region", chart_type="bar_chart", num_items=len(states)
    )

    return fig


def plot_conab_crop_diversity(conab_data: dict[str, Any]) -> go.Figure:
    """
    Create a crop type diversity chart showing crop types by state.
    """
    if not conab_data:
        return go.Figure().update_layout()

    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})

    # Count crop types by state
    state_crops = {}
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        for state in regions:
            if state not in state_crops:
                state_crops[state] = []
            state_crops[state].append(crop)

    if not state_crops:
        return go.Figure().update_layout()
    # Use the same ordering logic as spatial_temporal_distribution
    all_states = set(state_crops.keys())

    states_list = sorted(all_states, reverse=True)

    # Create figure
    fig = go.Figure()

    # Use CROP_ORDER and CROP_COLOR_MAP para padronizar ordem e cor da legenda
    crop_types = [
        c for c in CROP_ORDER if any(c in crops for crops in state_crops.values())
    ]
    legend_added = set()

    # Add traces for each crop first to maintain fixed legend order, similar to spatial_temporal_distribution
    for crop in crop_types:
        for state in states_list:
            if state == "Brazil":
                continue  # Skip Brazil, handle it separately
            if state in state_crops:
                count = (
                    state_crops[state].count(crop) if crop in state_crops[state] else 0
                )
                if count > 0:
                    show_in_legend = crop not in legend_added
                    if show_in_legend:
                        legend_added.add(crop)
                    fig.add_trace(
                        go.Bar(
                            x=[count],
                            y=[state],
                            orientation="h",
                            name=crop,
                            legendgroup=crop,
                            showlegend=show_in_legend,
                            marker={
                                "color": CROP_COLOR_MAP.get(crop, "#808080"),
                                "line": {"width": 0},
                            },
                            hovertemplate=f"<b>{crop}</b><br>State: {state}<br>Count: {count}<br><extra></extra>",
                        )
                    )

    # Add Brazil trace (Sugar cane mill) similar to spatial_temporal_distribution
    if crop_types:  # Only if there are crops to show
        fig.add_trace(
            go.Bar(
                x=[1],  # Fixed count of 1 for Brazil
                y=["Brazil"],
                orientation="h",
                name="Sugar cane mill",
                marker={
                    "color": CROP_COLOR_MAP.get("Sugar cane mill", "#808080"),
                    "line": {"width": 0},
                },
                showlegend=True,
                hovertemplate="<b>Brazil</b><br>Overall Coverage<br><extra></extra>",
            )
        )
    # Layout config (legend pattern from spatial_temporal_distribution)
    from scripts.plotting.chart_core import (
        get_standard_bar_config,
        get_standard_legend_config,
    )

    bar_config = get_standard_bar_config()
    bar_config["barmode"] = "stack"
    layout_params = validate_plotly_params(
        title=" ",
        xaxis_title="<b>Crop Type Count</b>",
        yaxis_title="<b>Region</b>",
        height=600,
        showlegend=True,
        legend=get_standard_legend_config(title="Crop Type", position="right"),
        **bar_config,
        yaxis={
            "categoryorder": "array",
            "categoryarray": states_list,
            "showgrid": False,
            "gridcolor": "#E5ECF6",
            "ticks": "outside",
            "ticklen": 8,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 0,
            "zeroline": False,
        },
        xaxis={
            "showgrid": False,
            "gridcolor": "#E5ECF6",
            "ticks": "outside",
            "ticklen": 8,
            "tickcolor": "black",
            "showline": True,
            "linewidth": 0,
            "zeroline": False,
        },
    )
    fig.update_layout(**layout_params)
    apply_standard_layout(fig, "Number of Crop Types", "Region")
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(tickangle=0)
    # aplicar aqui um aumento no tamanho da fonte da legenda para 20
    fig.update_layout(legend={"font": {"size": 20}})
    # aumentar agora o tamanho da fonte do titulo da legenda para 22
    fig.update_layout(legend_title={"font": {"size": 22}})
    # aumente um pouco a margem inferior do gráfico
    fig.update_layout(margin={"b": 85})
    return fig


# Map visualization functions for CONAB data

import folium
import geopandas as gpd


def load_brazil_shapefile() -> gpd.GeoDataFrame | None:
    """Load Brazil states shapefile."""
    try:
        current_dir = Path(__file__).parent.parent.parent.parent
        shapefile_path = (
            current_dir / "data" / "brazil-vector" / "BR_Municipios_2023.shp"
        )

        if not shapefile_path.exists():
            st.error(f"Shapefile not found at: {shapefile_path}")
            return None

        # Read the shapefile
        gdf = gpd.read_file(shapefile_path)

        # Check if we have state information
        state_columns = ["UF", "SIGLA_UF", "CD_UF", "NM_UF"]
        state_col = None
        for col in state_columns:
            if col in gdf.columns:
                state_col = col
                break

        if state_col is None:
            st.error("Could not find state column in shapefile")
            return None

        # Group by states to get state boundaries
        if "geometry" in gdf.columns:
            states_gdf = gdf.dissolve(by=state_col, as_index=False)
            return states_gdf
        else:
            st.error("No geometry column found in shapefile")
            return None

    except Exception as e:
        st.error(f"Error loading shapefile: {e}")
        return None


def create_conab_crop_map(
    conab_data: dict[str, Any], selected_crop: str = "Soybean"
) -> folium.Map:
    """
    Create an interactive map showing CONAB crop coverage by state.

    Args:
        conab_data: CONAB data dictionary
        selected_crop: Crop type to display

    Returns:
        Folium map object
    """
    # Center of Brazil
    brazil_center = [-14.235, -51.9253]

    # Create base map
    m = folium.Map(location=brazil_center, zoom_start=4, tiles="OpenStreetMap")

    # Load shapefile
    states_gdf = load_brazil_shapefile()
    if states_gdf is None:
        # Fallback to a simple map without shapefile
        folium.Marker(
            brazil_center,
            popup="Brazil - Shapefile not available",
            icon=folium.Icon(color="red"),
        ).add_to(m)
        return m

    # Get crop data
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_coverage = initiative_data.get("detailed_crop_coverage", {})
    crop_data = detailed_coverage.get(selected_crop, {})

    if not crop_data:
        folium.Marker(
            brazil_center,
            popup=f"No data available for {selected_crop}",
            icon=folium.Icon(color="orange"),
        ).add_to(m)
        return m

    # Get states with this crop
    covered_states = crop_data.get("regions", [])
    first_crop_years = crop_data.get("first_crop_years", {})

    # Prepare data for choropleth
    state_data = {}
    for state in covered_states:
        years = first_crop_years.get(state, [])
        if years:
            # Count years of coverage
            year_count = len(years)
            state_data[state] = year_count
        else:
            state_data[state] = 0

    # Map state abbreviations to full names for matching
    {v: k for k, v in BRAZILIAN_STATES.items()}

    # Try to match shapefile state column
    state_col = None
    for col in ["UF", "SIGLA_UF", "CD_UF", "NM_UF"]:
        if col in states_gdf.columns:
            state_col = col
            break

    if state_col:
        # Add coverage data to geodataframe
        states_gdf["crop_coverage"] = 0
        states_gdf["coverage_info"] = "No coverage"

        for idx, row in states_gdf.iterrows():
            state_code = row[state_col]

            # Try to match state code
            if state_code in state_data:
                coverage = state_data[state_code]
                states_gdf.loc[idx, "crop_coverage"] = coverage
                years_list = first_crop_years.get(state_code, [])
                years_str = ", ".join(years_list) if years_list else "No data"
                states_gdf.loc[idx, "coverage_info"] = (
                    f"{coverage} seasons: {years_str}"
                )

        # Create choropleth
        max_coverage = max(state_data.values()) if state_data.values() else 1

        for idx, row in states_gdf.iterrows():
            coverage = row["crop_coverage"]
            coverage_info = row["coverage_info"]

            # Color based on coverage
            if coverage == 0:
                color = "#lightgray"
                fillOpacity = 0.3
            else:
                # Green intensity based on coverage
                intensity = coverage / max_coverage
                green_value = int(100 + 155 * intensity)
                color = f"rgb(0, {green_value}, 0)"
                fillOpacity = 0.6

            # Add state to map
            folium.GeoJson(
                row["geometry"],
                style_function=lambda feature, color=color, fillOpacity=fillOpacity: {
                    "fillColor": color,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": fillOpacity,
                },
                popup=folium.Popup(
                    f"<b>{row[state_col]}</b><br>"
                    f"Crop: {selected_crop}<br>"
                    f"{coverage_info}",
                    max_width=300,
                ),
                tooltip=folium.Tooltip(f"{row[state_col]}: {coverage} seasons"),
            ).add_to(m)

    # Add a legend
    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 200px; height: 120px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
    <b>{selected_crop} Coverage</b><br>
    <i class="fa fa-square" style="color:#lightgray"></i> No coverage<br>
    <i class="fa fa-square" style="color:#64aa64"></i> Low coverage<br>
    <i class="fa fa-square" style="color:#00ff00"></i> High coverage<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def create_conab_all_crops_map(conab_data: dict[str, Any]) -> folium.Map:
    """
    Create an interactive map showing all CONAB crops with layer control.

    Args:
        conab_data: CONAB data dictionary

    Returns:
        Folium map object with layer control
    """
    # Center of Brazil
    brazil_center = [-14.235, -51.9253]

    # Create base map
    m = folium.Map(location=brazil_center, zoom_start=4, tiles="OpenStreetMap")

    # Get all crops
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_coverage = initiative_data.get("detailed_crop_coverage", {})

    if not detailed_coverage:
        folium.Marker(
            brazil_center, popup="No crop data available", icon=folium.Icon(color="red")
        ).add_to(m)
        return m

    # Create feature groups for each crop

    for crop_name, crop_data in detailed_coverage.items():
        if crop_name == "Sugar cane mill":  # Skip Brazil-wide entry
            continue

        # Create feature group for this crop
        fg = folium.FeatureGroup(name=crop_name)

        covered_states = crop_data.get("regions", [])
        first_crop_years = crop_data.get("first_crop_years", {})

        # Add markers for each state
        for state in covered_states:
            years = first_crop_years.get(state, [])
            if not years:
                continue

            # Get state coordinates (simplified - you might want to use actual state centroids)
            state_coords = get_state_coordinates(state)
            if state_coords:
                # Create popup content
                years_str = ", ".join(years) if years else "No data"
                popup_content = f"""
                <b>{BRAZILIAN_STATES.get(state, state)}</b><br>
                Crop: {crop_name}<br>
                Seasons: {len(years)}<br>
                Years: {years_str}
                """

                # Color based on crop type
                color = CROP_COLOR_MAP.get(crop_name, "#808080")

                folium.CircleMarker(
                    location=state_coords,
                    radius=8 + len(years),  # Size based on number of years
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{BRAZILIAN_STATES.get(state, state)}: {crop_name}",
                    color="black",
                    weight=1,
                    fillColor=color,
                    fillOpacity=0.7,
                ).add_to(fg)

        # Add feature group to map
        fg.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add legend for crop types
    legend_items = []
    for crop, color in CROP_COLOR_MAP.items():
        if crop in detailed_coverage and crop != "Sugar cane mill":
            legend_items.append(
                f'<i class="fa fa-circle" style="color:{color}"></i> {crop}'
            )

    legend_html = f"""
    <div style="position: fixed;
                top: 10px; right: 10px; width: 250px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:12px; padding: 10px; max-height: 400px; overflow-y: auto;">
    <b>CONAB Crop Types</b><br>
    {"<br>".join(legend_items)}
    <br><br>
    <small>Circle size = number of seasons</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def get_state_coordinates(state_code: str) -> list[float] | None:
    """
    Get approximate coordinates for Brazilian states.
    Returns [latitude, longitude] for the state center.
    """
    # Simplified state coordinates (approximate centers)
    state_coords = {
        "AC": [-8.77, -70.55],  # Acre
        "AL": [-9.71, -35.73],  # Alagoas
        "AP": [1.41, -51.77],  # Amapá
        "AM": [-3.07, -61.66],  # Amazonas
        "BA": [-12.96, -38.51],  # Bahia
        "CE": [-3.71, -38.54],  # Ceará
        "DF": [-15.83, -47.86],  # Distrito Federal
        "ES": [-19.19, -40.34],  # Espírito Santo
        "GO": [-16.64, -49.31],  # Goiás
        "MA": [-2.55, -44.30],  # Maranhão
        "MT": [-12.64, -55.42],  # Mato Grosso
        "MS": [-20.51, -54.54],  # Mato Grosso do Sul
        "MG": [-18.10, -44.38],  # Minas Gerais
        "PA": [-5.53, -52.29],  # Pará
        "PB": [-7.06, -35.55],  # Paraíba
        "PR": [-24.89, -51.55],  # Paraná
        "PE": [-8.28, -35.07],  # Pernambuco
        "PI": [-8.28, -43.68],  # Piauí
        "RJ": [-22.84, -43.15],  # Rio de Janeiro
        "RN": [-5.22, -36.52],  # Rio Grande do Norte
        "RS": [-30.01, -51.22],  # Rio Grande do Sul
        "RO": [-11.22, -62.80],  # Rondônia
        "RR": [1.89, -61.22],  # Roraima
        "SC": [-27.33, -49.44],  # Santa Catarina
        "SP": [-23.55, -46.64],  # São Paulo
        "SE": [-10.90, -37.07],  # Sergipe
        "TO": [-10.25, -48.25],  # Tocantins
    }

    return state_coords.get(state_code)
