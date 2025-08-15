"""
Spatial Temporal Distribution Charts
===================================

Módulo para criação de gráficos de distribuição espacial e temporal dos dados CONAB.
Mostra a cobertura de estados/áreas ao longo do tempo em formato de timeline.

Autor: LANDAGRI-B Project Team 
Data: 2025-08-11
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, Any, List

# Import das funções auxiliares de type safety
from scripts.utilities.type_safety import validate_plotly_params, safe_bool_conversion


def plot_conab_spatial_temporal_distribution(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a spatial and temporal distribution chart for CONAB mapping initiatives.
    Shows states/areas coverage over time in a timeline format.
    Brazil is excluded from the visualization.
    """
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No data available)")
    
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
                    # Extract start year from range like "2018-2019"
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    
                    # Add data points for the year range
                    for year in range(start_year, end_year + 1):
                        timeline_data.append({
                            'State': state,
                            'Year': year,
                            'Crop': crop,
                            'Semester': 'First',
                            'Coverage': 1
                        })
        
        # Process second semester data
        for state, years in second_crop_years.items():
            if state in regions:
                all_states.add(state)
                for year_range in years:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    
                    for year in range(start_year, end_year + 1):
                        timeline_data.append({
                            'State': state,
                            'Year': year,
                            'Crop': crop,
                            'Semester': 'Second',
                            'Coverage': 1
                        })
    
    if not timeline_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No timeline data)")
    
    # Create DataFrame
    df = pd.DataFrame(timeline_data)
    
    # Create figure
    fig = go.Figure()
    
    # Get unique crop types and assign improved colors
    crop_types = sorted(df['Crop'].unique())
    # Enhanced color palette with better contrast and visibility
    improved_colors = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange  
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
        '#aec7e8',  # Light Blue
        '#ffbb78',  # Light Orange
        '#98df8a',  # Light Green
        '#ff9896',  # Light Red
        '#c5b0d5'   # Light Purple
    ]
    crop_colors = {crop: improved_colors[i % len(improved_colors)] for i, crop in enumerate(crop_types)}
    # Track which crops have already been added to legend
    legend_added = set()
    
    # Remove Brazil entirely from state processing and sort remaining states
    states_list = sorted([s for s in all_states if s != "Brazil"], reverse=True)  # Reverse order for top-to-bottom alphabetical

    # Add traces for each state, colored by crop type
    for state in states_list:
        state_data = df[df['State'] == state]
        if not state_data.empty:
            # Group by crop type for this state
            for crop in crop_types:
                crop_state_data = state_data[state_data['Crop'] == crop]
                if not crop_state_data.empty:
                    years = sorted(crop_state_data['Year'].unique())
                    
                    # Create continuous coverage periods
                    coverage_periods = []
                    if years:
                        start_year = years[0]
                        end_year = years[0]
                        
                        for year in years[1:]:
                            if year == end_year + 1:
                                end_year = year
                            else:
                                coverage_periods.append((start_year, end_year))
                                start_year = year
                                end_year = year
                        
                        coverage_periods.append((start_year, end_year))
                    
                    # Add traces for coverage periods
                    for j, (start, end) in enumerate(coverage_periods):
                        # Show legend only for the first trace of each crop type
                        show_in_legend = crop not in legend_added
                        if show_in_legend:
                            legend_added.add(crop)
                        
                        # Use type-safe parameters for Plotly
                        trace_params = validate_plotly_params(
                            x=[start, end],
                            y=[state, state],
                            mode='lines',
                            line=dict(width=15, color=crop_colors[crop]),
                            name=crop,
                            legendgroup=crop,
                            showlegend=safe_bool_conversion(show_in_legend),
                            hovertemplate=f"<b>{state}</b><br>Crop: {crop}<br>Period: {start}-{end}<br><extra></extra>"
                        )
                        fig.add_trace(go.Scatter(**trace_params))

    # Update layout with standardized font and presentation (matching seasonal distribution)
    layout_params = validate_plotly_params(
        title="CONAB Spatial and Temporal Distribution",
        xaxis_title="Year",
        yaxis_title="State",
        height=max(600, len(states_list) * 25),  # Dynamic height like seasonal distribution
        font=dict(size=10),  # Consistent font size
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=dict(text="Crop Type")
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=states_list,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            tickfont=dict(size=10),  # Consistent with seasonal distribution
            showline=True,
            linewidth=0,
            zeroline=False
        ),
        xaxis=dict(
            dtick=1,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            tickfont=dict(size=10),  # Consistent font size
            showline=True,
            linewidth=0,
            zeroline=False
        )
    )
    
    fig.update_layout(**layout_params)
    
    return fig
