#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONAB Chart Module
==================

Generates specialized charts for CONAB (Companhia Nacional de Abastecimento) data analysis.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, Any
import json
from pathlib import Path
from scripts.plotting.chart_core import apply_standard_layout
from scripts.utilities.type_safety import safe_bool_conversion, validate_plotly_params

# Brazilian states and their abbreviations
BRAZILIAN_STATES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

# Total states + DF = 27 for 100% coverage
TOTAL_STATES_PLUS_DF = 27

def load_conab_detailed_data() -> Dict[str, Any]:
    """Load CONAB detailed data from JSON file."""
    try:
        current_dir = Path(__file__).parent.parent.parent.parent
        file_path = current_dir / "data" / "conab_detailed_initiative.jsonc"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Clean the JSONC content
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove control characters and clean the line
                cleaned_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t\n\r')
                
                # Remove comments but keep the line if it has valid JSON
                if '//' in cleaned_line:
                    json_part = cleaned_line.split('//')[0].strip()
                    if json_part:
                        cleaned_lines.append(json_part)
                else:
                    if cleaned_line.strip():
                        cleaned_lines.append(cleaned_line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # Additional cleanup for common JSON issues
            cleaned_content = cleaned_content.replace('\r', '').replace('\x00', '')
            
            return json.loads(cleaned_content)
            
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        st.error(f"Error at line {e.lineno}, column {e.colno}")
        return {}
    except Exception as e:
        st.error(f"Error loading CONAB detailed data: {e}")
        return {}

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
        first_semester = crop_info.get("first_semester_years", {})
        second_semester = crop_info.get("second_semester_years", {})
        
        # Process first semester data
        for state, years in first_semester.items():
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
        for state, years in second_semester.items():
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
    
    # Add traces for each state, colored by crop type
    states_list = sorted(list(all_states))
    
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
                        
                        coverage_periods.append((start_year, end_year))                    # Add traces for coverage periods
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
      # Update layout with type-safe parameters
    layout_params = validate_plotly_params(
        title="Spatial and Temporal Distribution of CONAB Mapping Initiatives (2000-2023)",
        xaxis_title="Year",
        yaxis_title="State/Area",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    fig.update_layout(**layout_params)
      # Apply standard layout
    apply_standard_layout(fig, "Spatial and Temporal Distribution of CONAB Mapping Initiatives (2000-2023)", "Year", "State/Area")
    
    return fig

def plot_conab_temporal_coverage(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a temporal coverage chart showing percentage of states covered over time.
    """
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No data available)")
    
    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Count states per year
    year_coverage = {}
    
    for crop, crop_info in crop_coverage.items():
        first_semester = crop_info.get("first_semester_years", {})
        second_semester = crop_info.get("second_semester_years", {})
        
        # Process first semester data
        for state, years in first_semester.items():
            for year_range in years:
                start_year = int(year_range.split('-')[0])
                end_year = int(year_range.split('-')[1])
                
                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)
        
        # Process second semester data
        for state, years in second_semester.items():
            for year_range in years:
                start_year = int(year_range.split('-')[0])
                end_year = int(year_range.split('-')[1])
                
                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)
    
    if not year_coverage:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No coverage data)")
    
    # Calculate percentage coverage
    years = sorted(year_coverage.keys())
    coverage_percentages = []
    
    for year in years:
        num_states = len(year_coverage[year])
        percentage = (num_states / TOTAL_STATES_PLUS_DF) * 100
        coverage_percentages.append(percentage)
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=coverage_percentages,
        mode='lines+markers',
        line=dict(width=3, color='#17a2b8'),
        marker=dict(size=8, color='#17a2b8'),
        name='Coverage %',
        hovertemplate="<b>Year:</b> %{x}<br><b>Coverage:</b> %{y:.1f}%<br><extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title="Temporal Coverage of CONAB Mapping Initiatives",
        xaxis_title="Year",
        yaxis_title="Pct States",
        height=500,
        yaxis=dict(range=[0, 100]),
        showlegend=False
    )
      # Apply standard layout
    apply_standard_layout(fig, "Temporal Coverage of CONAB Mapping Initiatives", "Year", "Pct States")
    
    return fig

def plot_conab_spatial_coverage(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a spatial coverage chart showing percentage coverage by state.
    """
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No data available)")
    
    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Count coverage by state
    state_coverage = {}
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_semester = crop_info.get("first_semester_years", {})
        second_semester = crop_info.get("second_semester_years", {})
        
        # Count years of coverage for each state
        for state in regions:
            if state not in state_coverage:
                state_coverage[state] = set()
            
            # Add years from first semester
            if state in first_semester:
                for year_range in first_semester[state]:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)
            
            # Add years from second semester
            if state in second_semester:
                for year_range in second_semester[state]:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)
    
    if not state_coverage:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No coverage data)")
    
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
    colors = ['#ffcccc' if c < 25 else '#ffeb99' if c < 50 else '#ccffcc' if c < 75 else '#99ccff' for c in coverages]
    
    fig.add_trace(go.Bar(
        x=coverages,
        y=states,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<br><extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title="Spatial Coverage of CONAB Mapping Initiatives (2000-2023)",
        xaxis_title="Coverage (%)",
        yaxis_title="State/Area",
        height=600,
        showlegend=False
    )
      # Apply standard layout
    apply_standard_layout(fig, "Spatial Coverage of CONAB Mapping Initiatives (2000-2023)", "Coverage (%)", "State/Area")
    
    return fig

def plot_conab_crop_diversity(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a crop type diversity chart showing crop types by state.
    """
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Crop Diversity (No data available)")
    
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
        return go.Figure().update_layout(title="CONAB Crop Diversity (No crop data)")
    
    # Prepare data for stacked bar chart
    states = sorted(state_crops.keys())
    crop_types = list(set([crop for crops in state_crops.values() for crop in crops]))
    
    # Create figure
    fig = go.Figure()
    
    # Color map for different crops
    color_map = {
        'Cotton': '#8B4513',
        'Irrigated Rice': '#4682B4',
        'Coffee': '#6B4423',
        'Sugar cane': '#32CD32',
        'Other winter crops': '#FFD700',
        'Other summer crops': '#FFA500',
        'Corn': '#FFFF00',
        'Soybean': '#8B0000',
        'Sugar cane mill': '#228B22'
    }
    
    # Count crops per state
    for crop in crop_types:
        crop_counts = []
        for state in states:
            count = state_crops[state].count(crop) if state in state_crops else 0
            crop_counts.append(count)
        
        fig.add_trace(go.Bar(
            x=crop_counts,
            y=states,
            orientation='h',
            name=crop,
            marker=dict(color=color_map.get(crop, '#808080')),
            hovertemplate=f"<b>{crop}</b><br>State: %{{y}}<br>Count: %{{x}}<br><extra></extra>"
        ))
      # Update layout with type-safe parameters
    layout_params = validate_plotly_params(
        title="Crop Type Diversity in CONAB Mapping by State (2000-2023)",
        xaxis_title="Crop Type Cnt",
        yaxis_title="State/Area",
        height=600,
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    fig.update_layout(**layout_params)
      # Apply standard layout
    apply_standard_layout(fig, "Crop Type Diversity in CONAB Mapping by State (2000-2023)", "Crop Type Cnt", "State/Area")
    
    return fig
