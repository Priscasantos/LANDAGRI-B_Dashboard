#!/usr/bin/env python3
"""
Agricultural Charts Module - CONAB Data Analysis
==============================================

Comprehensive charts for agricultural analysis based on CONAB data including
crop calendars, regional coverage, temporal     # Apply centralized theme
    apply_theme_to_figure(fig)
    
    fig.update_layout(
        title={
            'text': "🏘️ CONAB Agricultural Monitoring by State",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Brazilian States",
        yaxis_title="Number of Monitored Crops",
        height=get_dynamic_chart_height(len(states_data), 'bar'),
        xaxis_tickangle=-45
    )performance metrics.
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Import removed due to unused apply_standard_layout calls
# Note: modern_themes modules have been consolidated into chart_core
from scripts.plotting.chart_core import (
    apply_theme_to_figure,
    get_dynamic_chart_height,
    get_responsive_margin
)


def load_conab_data() -> Tuple[Dict, Dict]:
    """Load CONAB data from JSON files."""
    try:
        # Load detailed initiative data
        detailed_path = Path("data/json/conab_detailed_initiative.jsonc")
        calendar_path = Path("data/json/conab_crop_calendar_complete.jsonc")
        
        detailed_data = {}
        calendar_data = {}
        
        if detailed_path.exists():
            with open(detailed_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove JSONC comments
                lines = content.split('\n')
                clean_lines = []
                for line in lines:
                    # Remove comments starting with //
                    if '//' in line:
                        line = line[:line.index('//')]
                    clean_lines.append(line)
                clean_content = '\n'.join(clean_lines)
                detailed_data = json.loads(clean_content)
        
        if calendar_path.exists():
            with open(calendar_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove JSONC comments
                lines = content.split('\n')
                clean_lines = []
                for line in lines:
                    if '//' in line:
                        line = line[:line.index('//')]
                    clean_lines.append(line)
                clean_content = '\n'.join(clean_lines)
                calendar_data = json.loads(clean_content)
        
        return detailed_data, calendar_data
    except Exception as e:
        print(f"Error loading CONAB data: {e}")
        return {}, {}


def plot_crop_calendar_heatmap(calendar_data: Dict) -> go.Figure:
    """Create a heatmap showing crop planting/harvest calendar by state and month."""
    if not calendar_data or 'crop_calendar' not in calendar_data:
        fig = go.Figure()
        fig.add_annotation(
            text="CONAB crop calendar data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="State"
        )
        return fig
    
    # Prepare data for heatmap
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    # Get all states and crops
    all_states = set()
    crop_data = {}
    
    for crop_name, crop_entries in calendar_data['crop_calendar'].items():
        if crop_name not in crop_data:
            crop_data[crop_name] = {}
        
        for entry in crop_entries:
            if isinstance(entry, dict) and 'state_code' in entry and 'calendar' in entry:
                state = entry['state_code']
                all_states.add(state)
                
                if state not in crop_data[crop_name]:
                    crop_data[crop_name][state] = {}
                
                # Extract calendar data
                for month, activity in entry['calendar'].items():
                    crop_data[crop_name][state][month] = activity
    
    # Create subplots for each major crop
    major_crops = ['Soybean', 'Corn (1st harvest)', 'Cotton', 'Rice']
    available_crops = [crop for crop in major_crops if crop in crop_data]
    
    if not available_crops:
        available_crops = list(crop_data.keys())[:4]  # Take first 4 crops
    
    fig = make_subplots(
        rows=len(available_crops), cols=1,
        subplot_titles=[f"{crop} - Planting and Harvest Calendar" for crop in available_crops],
        vertical_spacing=0.08
    )
    
    # Activity encoding
    activity_map = {'': 0, 'P': 1, 'H': 2, 'PH': 3}
    activity_labels = ['No Activity', 'Planting', 'Harvest', 'Planting & Harvest']
    
    for i, crop in enumerate(available_crops):
        if crop in crop_data:
            # Prepare matrix
            states = sorted(list(all_states))
            z_matrix = []
            
            for state in states:
                row = []
                for month in months:
                    activity = crop_data[crop].get(state, {}).get(month, '')
                    row.append(activity_map.get(activity, 0))
                z_matrix.append(row)
            
            # Create heatmap
            fig.add_trace(
                go.Heatmap(
                    z=z_matrix,
                    x=months,
                    y=states,
                    colorscale=[[0, '#f0f0f0'], [0.33, '#90EE90'], [0.66, '#FFB347'], [1, '#FF6B6B']],
                    hovertemplate="<b>%{y}</b><br>Month: %{x}<br>Activity: " + 
                                 "%{customdata}<extra></extra>",
                    customdata=[[activity_labels[val] for val in row] for row in z_matrix],
                    showscale=i == 0,  # Show scale only for first subplot
                    colorbar=dict(
                        title="Activity Type",
                        tickvals=[0, 1, 2, 3],
                        ticktext=activity_labels,
                        x=1.02
                    ) if i == 0 else None
                ),
                row=i+1, col=1
            )
    
    
    # Remove unused apply_standard_layout call
    
    # Apply centralized theme
    apply_theme_to_figure(fig)
    
    fig.update_layout(
        title={
            'text': "🌾 Brazilian Crop Calendar - Planting and Harvest Periods",
            'x': 0.5,
            'xanchor': 'center'
        },
        height=get_dynamic_chart_height(len(available_crops), 'heatmap'),
        showlegend=False
    )
    
    return fig


def plot_regional_crop_coverage(detailed_data: Dict) -> go.Figure:
    """Create a chart showing crop coverage by region."""
    if not detailed_data:
        fig = go.Figure()
        fig.add_annotation(
            text="CONAB detailed data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        # apply_standard_layout(fig, "Region", "Number of Crops") - Commented for standardization
        return fig
    
    # Extract regional data
    initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Count crops by region
    region_crop_count = {}
    total_coverage = {}
    
    for crop, crop_info in detailed_crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        
        for region in regions:
            if region not in region_crop_count:
                region_crop_count[region] = 0
                total_coverage[region] = []
            
            region_crop_count[region] += 1
            
            # Get year coverage for this region
            years = first_crop_years.get(region, [])
            total_coverage[region].extend(years)
    
    # Create visualization
    regions = list(region_crop_count.keys())
    crop_counts = list(region_crop_count.values())
    
    # Calculate average coverage years
    avg_years = []
    for region in regions:
        years = total_coverage[region]
        if years:
            # Extract numeric years from year ranges
            numeric_years = []
            for year_range in years:
                if '-' in str(year_range):
                    start_year = int(str(year_range).split('-')[0])
                    numeric_years.append(start_year)
            avg_years.append(len(numeric_years) if numeric_years else 0)
        else:
            avg_years.append(0)
    
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=regions,
        y=crop_counts,
        name="Number of Crops",
        marker_color='#2E8B57',
        text=crop_counts,
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Crops: %{y}<br>Coverage: %{customdata} years<extra></extra>",
        customdata=avg_years
    ))
    
    
    # Apply modern styling
    # apply_standard_layout(fig, "", "", "") - Commented for standardization
    
    fig.update_layout(
        title={
            'text': "🗺️ Regional Crop Coverage Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Inter, Arial, sans-serif'}
        },
        xaxis_title="Brazilian States",
        yaxis_title="Number of Monitored Crops",
        height=500,
        xaxis_tickangle=-45
    )
    
    # Modern theme applied via chart_core
    return fig


def plot_temporal_crop_trends(detailed_data: Dict) -> go.Figure:
    """Create temporal trends chart showing crop monitoring over years."""
    if not detailed_data:
        fig = go.Figure()
        fig.add_annotation(
            text="CONAB detailed data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        # apply_standard_layout(fig, "Year", "Active Crops") - Commented for standardization
        return fig
    
    initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
    available_years = initiative_data.get("available_years", [])
    detailed_crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    if not available_years:
        fig = go.Figure()
        fig.add_annotation(
            text="No temporal data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        # apply_standard_layout(fig, "Year", "Active Crops") - Commented for standardization
        return fig
    
    # Calculate crop activity by year
    year_activity = {}
    
    for year in available_years:
        year_activity[year] = 0
        
        for crop, crop_info in detailed_crop_coverage.items():
            first_crop_years = crop_info.get("first_crop_years", {})
            
            for region, year_ranges in first_crop_years.items():
                for year_range in year_ranges:
                    if '-' in str(year_range):
                        start_year, end_year = str(year_range).split('-')
                        start_year = int(start_year)
                        end_year = int(end_year)
                        
                        if start_year <= year <= end_year:
                            year_activity[year] += 1
                            break
    
    years = sorted(year_activity.keys())
    activity_counts = [year_activity[year] for year in years]
    
    fig = go.Figure()
    
    # Add line chart
    fig.add_trace(go.Scatter(
        x=years,
        y=activity_counts,
        mode='lines+markers',
        name='Active Crops',
        line=dict(color='#4682B4', width=3),
        marker=dict(size=8, color='#4682B4'),
        hovertemplate="<b>Year: %{x}</b><br>Active Crops: %{y}<extra></extra>"
    ))
    
    # Add trend line
    if len(years) > 2:
        z = np.polyfit(years, activity_counts, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=years,
            y=p(years),
            mode='lines',
            name='Trend',
            line=dict(color='#FF6B6B', width=2, dash='dash'),
            hovertemplate="<b>Trend: %{y:.1f}</b><extra></extra>"
        ))
    
    
    # Apply modern styling
    # apply_standard_layout(fig, "", "", "") - Commented for standardization
    
    fig.update_layout(
        title={
            'text': "📈 Temporal Trends in Crop Monitoring (2000-2024)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Inter, Arial, sans-serif'}
        },
        xaxis_title="Year",
        yaxis_title="Number of Active Crop Monitoring Programs",
        height=500
    )
    
    return fig


def plot_crop_diversity_by_region(detailed_data: Dict) -> go.Figure:
    """Create a sunburst chart showing crop diversity by region."""
    if not detailed_data:
        fig = go.Figure()
        fig.add_annotation(
            text="CONAB detailed data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Prepare data for sunburst
    ids = []
    labels = []
    parents = []
    values = []
    
    # Add root
    ids.append("Brazil")
    labels.append("Brazil")
    parents.append("")
    values.append(0)
    
    # State mapping for regions
    state_to_region = {
        'RO': 'North', 'AC': 'North', 'AM': 'North', 'RR': 'North', 'PA': 'North', 'AP': 'North', 'TO': 'North',
        'MA': 'Northeast', 'PI': 'Northeast', 'CE': 'Northeast', 'RN': 'Northeast', 'PB': 'Northeast', 
        'PE': 'Northeast', 'AL': 'Northeast', 'SE': 'Northeast', 'BA': 'Northeast',
        'MT': 'Central-West', 'MS': 'Central-West', 'GO': 'Central-West', 'DF': 'Central-West',
        'MG': 'Southeast', 'ES': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
        'PR': 'South', 'SC': 'South', 'RS': 'South'
    }
    
    region_crop_count = {}
    state_crop_count = {}
    
    for crop, crop_info in detailed_crop_coverage.items():
        regions = crop_info.get("regions", [])
        
        for state in regions:
            region = state_to_region.get(state, 'Other')
            
            if region not in region_crop_count:
                region_crop_count[region] = 0
            if state not in state_crop_count:
                state_crop_count[state] = 0
            
            region_crop_count[region] += 1
            state_crop_count[state] += 1
    
    # Add regions
    for region, count in region_crop_count.items():
        ids.append(region)
        labels.append(f"{region} ({count} crops)")
        parents.append("Brazil")
        values.append(count)
    
    # Add states
    for state, count in state_crop_count.items():
        region = state_to_region.get(state, 'Other')
        ids.append(f"{region}-{state}")
        labels.append(f"{state} ({count})")
        parents.append(region)
        values.append(count)
    
    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>Value: %{value}<extra></extra>",
        maxdepth=3,
    ))
    
    
    # Apply modern styling
    # apply_standard_layout(fig, "", "", "") - Commented for standardization
    
    fig.update_layout(
        title={
            'text': "🌿 Crop Diversity Distribution by Region",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Inter, Arial, sans-serif'}
        },
        height=600
    )
    
    return fig


def plot_agricultural_performance_metrics(detailed_data: Dict) -> go.Figure:
    """Create performance metrics dashboard."""
    if not detailed_data:
        fig = go.Figure()
        fig.add_annotation(
            text="CONAB detailed data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
    
    # Extract key metrics
    overall_accuracy = initiative_data.get("overall_accuracy", 0)
    num_classes = initiative_data.get("number_of_classes", 0)
    num_agri_classes = initiative_data.get("number_of_agriculture_classes", 0)
    spatial_resolution = initiative_data.get("spatial_resolution", 0)
    coverage = initiative_data.get("coverage", "Unknown")
    years_span = len(initiative_data.get("available_years", []))
    
    # Create metrics visualization
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            "Overall Accuracy (%)", "Classification Classes", "Spatial Resolution (m)",
            "Temporal Coverage (years)", "Agricultural Focus (%)", "Regional Coverage"
        ],
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # Accuracy gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=overall_accuracy,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Accuracy"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#2E8B57"},
            'steps': [
                {'range': [0, 50], 'color': "#FFB347"},
                {'range': [50, 80], 'color': "#90EE90"},
                {'range': [80, 100], 'color': "#2E8B57"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ), row=1, col=1)
    
    # Classes indicator
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=num_classes,
        title={"text": "Total Classes"},
        number={'font': {'size': 40, 'color': '#4682B4'}},
        delta={'reference': 10, 'position': "top"}
    ), row=1, col=2)
    
    # Resolution indicator
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=spatial_resolution,
        title={"text": "Resolution (m)"},
        number={'font': {'size': 40, 'color': '#FF6B6B'}},
        delta={'reference': 50, 'position': "top", 'decreasing': {'color': 'green'}}
    ), row=1, col=3)
    
    # Temporal coverage
    fig.add_trace(go.Indicator(
        mode="number",
        value=years_span,
        title={"text": "Years Coverage"},
        number={'font': {'size': 40, 'color': '#DAA520'}}
    ), row=2, col=1)
    
    # Agricultural focus percentage
    agri_focus = (num_agri_classes / num_classes * 100) if num_classes > 0 else 0
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=agri_focus,
        title={"text": "Agri Focus"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#9370DB"},
            'steps': [
                {'range': [0, 33], 'color': "#f0f0f0"},
                {'range': [33, 66], 'color': "#d0d0d0"},
                {'range': [66, 100], 'color': "#9370DB"}
            ]
        }
    ), row=2, col=2)
    
    # Coverage indicator
    fig.add_trace(go.Indicator(
        mode="number",
        value=1,  # Brazil = 1 country
        title={"text": f"Coverage: {coverage}"},
        number={'font': {'size': 30, 'color': '#20B2AA'}}
    ), row=2, col=3)
    
    
    # Apply modern styling
    # apply_standard_layout(fig, "", "", "") - Commented for standardization
    
    fig.update_layout(
        title={
            'text': "📊 CONAB Agricultural Monitoring - Performance Metrics",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Inter, Arial, sans-serif'}
        },
        height=600
    )
    
    return fig


def create_agricultural_summary_stats(detailed_data: Dict, calendar_data: Dict) -> Dict:
    """Create summary statistics for agricultural data."""
    if not detailed_data and not calendar_data:
        return {
            'total_crops': 0,
            'total_regions': 0,
            'year_span': 0,
            'accuracy': 0,
            'main_crops': []
        }
    
    initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Calculate statistics
    total_crops = len(detailed_crop_coverage)
    
    all_regions = set()
    for crop_info in detailed_crop_coverage.values():
        regions = crop_info.get("regions", [])
        all_regions.update(regions)
    
    total_regions = len(all_regions)
    available_years = initiative_data.get("available_years", [])
    year_span = f"{min(available_years)}-{max(available_years)}" if available_years else "N/A"
    accuracy = initiative_data.get("overall_accuracy", 0)
    
    # Get main crops
    main_crops = list(detailed_crop_coverage.keys())[:5]
    
    return {
        'total_crops': total_crops,
        'total_regions': total_regions,
        'year_span': year_span,
        'accuracy': accuracy,
        'main_crops': main_crops
    }
