"""
Spatial Temporal Distribution Charts
===================================

Módulo para criação de gráficos de distribuição espacial e temporal dos dados CONAB.
Mostra a cobertura de estados/áreas ao longo do tempo em formato de timeline.

Autor: Dashboard Iniciativas LULC
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
    
    # Get unique crop types and assign colors
    crop_types = sorted(df['Crop'].unique())
    colors = px.colors.qualitative.Set3
    crop_colors = {crop: colors[i % len(colors)] for i, crop in enumerate(crop_types)}
    # Track which crops have already been added to legend
    legend_added = set()
    
    # Filter out Brazil from state processing and sort remaining states
    states_without_brazil = [s for s in all_states if s != "Brazil"]
    states_list = sorted(states_without_brazil, reverse=True)  # Reverse order for top-to-bottom alphabetical
    # Add Brazil at the end (bottom) of the list
    states_list.append("Brazil")


    
    # Add traces for each state, colored by crop type (skip Brazil for now)
    for state in states_list:
        if state == "Brazil":
            continue  # Skip Brazil, handle it separately
        
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
    
    # Add Brazil trace at the bottom showing the overall temporal coverage
    if timeline_data:
        # Get the overall time range for Brazil
        all_years = sorted(df['Year'].unique())
        if all_years:
            brazil_start = min(all_years)
            brazil_end = max(all_years)
            
            # Add a trace for Brazil spanning the entire period
            trace_params = validate_plotly_params(
                x=[brazil_start, brazil_end],
                y=["Brazil", "Brazil"],
                mode='lines',
                line=dict(width=15, color='#808080'),  # Gray color for Brazil
                name='Sugar cane mill',
                showlegend=True,
                hovertemplate=f"<b>Brazil</b><br>Overall Period: {brazil_start}-{brazil_end}<br><extra></extra>"
            )
            fig.add_trace(go.Scatter(**trace_params)) 

    # Possível implementação futura para cores por mesorregião:
    # Seria necessário carregar o dicionário de mesorregiões e mapear cores por estado
    # Exemplo:
    # state_color_map = load_mesoregion_colors()
    # ticktext_colored = create_colored_tick_labels(states_list, state_color_map)
    
    # Update layout with type-safe parameters
    layout_params = validate_plotly_params(
        title="",
        xaxis_title="<b>Ano</b>",
        yaxis_title="<b>Região</b>",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title=dict(text="<b>Crop Type</b>")
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=states_list,
            showgrid=False,      # Remove o grid do eixo y
            gridcolor='#E5ECF6',  # Cor do grid do eixo y
            ticks='outside',     # Adiciona ticks externos no eixo y
            ticklen=8,            # Tamanho dos ticks (opcional)
            tickcolor='black',  # Cor dos ticks do eixo y
            tickfont=dict(size=14),  # Ajuste o tamanho se quiser
            showline=True,      # Remove a linha externa do eixo y
            linewidth=0,         # Define espessura da linha como 0
            zeroline=False
        ),
        xaxis=dict(
            dtick=1,  # Define o espaçamento entre os ticks do eixo x
            showgrid=False,      # Remove o grid do eixo x
            gridcolor='#E5ECF6',  # Cor do grid do eixo x
            ticks='outside',     # Adiciona ticks externos no eixo x
            ticklen=8,            # Tamanho dos ticks (opcional)
            tickcolor='black',  # Cor dos ticks do eixo x
            showline=True,      # Remove a linha externa do eixo x
            linewidth=0,         # Define espessura da linha como 0
            zeroline=False
        )
    )
    
    fig.update_layout(**layout_params)
    
    return fig