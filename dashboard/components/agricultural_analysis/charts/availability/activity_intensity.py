"""
Activity Intensity Analysis Chart for CONAB Agricultural Data
===========================================================

Creates visualizations showing agricultural activity intensity patterns
using CONAB crop calendar data.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def plot_activity_intensity_matrix(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a matrix showing activity intensity across months and crops.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing activity intensity matrix
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Activity Intensity Matrix (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Prepare crop-month intensity matrix
    crop_month_intensity = {}
    
    for crop_name, crop_data in crop_calendar.items():
        crop_month_intensity[crop_name] = {month: 0 for month in month_order}
        
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            
            for month, activity in calendar.items():
                if month in crop_month_intensity[crop_name] and activity and activity.strip():
                    crop_month_intensity[crop_name][month] += 1
    
    if not crop_month_intensity:
        return go.Figure().update_layout(title="Activity Intensity Matrix (No data)")
    
    # Convert to matrix format
    crops = sorted(list(crop_month_intensity.keys()))
    
    z_matrix = []
    for crop in crops:
        row = [crop_month_intensity[crop][month] for month in month_order]
        z_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=month_order,
        y=crops,
        colorscale='Viridis',
        hovertemplate="Crop: %{y}<br>Month: %{x}<br>Intensity: %{z}<extra></extra>",
        colorbar=dict(title="Activity Intensity")
    ))
    
    fig.update_layout(
        title="Agricultural Activity Intensity Matrix (Crops vs Months)",
        xaxis_title="Month",
        yaxis_title="Crop Type",
        height=max(400, len(crops) * 30),
        font=dict(size=10),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_peak_activity_analysis(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a chart analyzing peak activity periods throughout the year.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing peak activity analysis
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Peak Activity Analysis (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Count different types of activities by month
    monthly_activities = {
        month: {'Planting': 0, 'Harvest': 0, 'Both': 0, 'Total': 0} 
        for month in month_order
    }
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            
            for month, activity in calendar.items():
                if month in monthly_activities and activity:
                    activity = activity.strip()
                    monthly_activities[month]['Total'] += 1
                    
                    if activity == 'P':
                        monthly_activities[month]['Planting'] += 1
                    elif activity == 'H':
                        monthly_activities[month]['Harvest'] += 1
                    elif activity == 'PH':
                        monthly_activities[month]['Both'] += 1
    
    # Create subplot with multiple traces
    fig = go.Figure()
    
    # Add total activities area
    total_values = [monthly_activities[month]['Total'] for month in month_order]
    fig.add_trace(go.Scatter(
        x=month_order,
        y=total_values,
        fill='tonexty',
        mode='lines',
        name='Total Activities',
        line=dict(color='rgba(255, 165, 0, 0.3)', width=0),
        fillcolor='rgba(255, 165, 0, 0.1)',
        hovertemplate="Month: %{x}<br>Total: %{y}<extra></extra>"
    ))
    
    # Add planting activities
    planting_values = [monthly_activities[month]['Planting'] for month in month_order]
    fig.add_trace(go.Scatter(
        x=month_order,
        y=planting_values,
        mode='lines+markers',
        name='Planting Peak',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, symbol='triangle-up'),
        hovertemplate="Month: %{x}<br>Planting: %{y}<extra></extra>"
    ))
    
    # Add harvest activities
    harvest_values = [monthly_activities[month]['Harvest'] for month in month_order]
    fig.add_trace(go.Scatter(
        x=month_order,
        y=harvest_values,
        mode='lines+markers',
        name='Harvest Peak',
        line=dict(color='#DAA520', width=3),
        marker=dict(size=8, symbol='triangle-down'),
        hovertemplate="Month: %{x}<br>Harvest: %{y}<extra></extra>"
    ))
    
    # Add combined activities
    both_values = [monthly_activities[month]['Both'] for month in month_order]
    fig.add_trace(go.Scatter(
        x=month_order,
        y=both_values,
        mode='lines+markers',
        name='Combined Peak',
        line=dict(color='#8B0000', width=3),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate="Month: %{x}<br>Combined: %{y}<extra></extra>"
    ))
    
    # Find and annotate peak months
    max_total_idx = total_values.index(max(total_values))
    max_planting_idx = planting_values.index(max(planting_values))
    max_harvest_idx = harvest_values.index(max(harvest_values))
    
    annotations = [
        dict(
            x=month_order[max_total_idx],
            y=max(total_values),
            text=f"Peak Total<br>{max(total_values)} activities",
            showarrow=True,
            arrowhead=2,
            arrowcolor='orange',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='orange'
        ),
        dict(
            x=month_order[max_planting_idx],
            y=max(planting_values),
            text=f"Peak Planting<br>{max(planting_values)} activities",
            showarrow=True,
            arrowhead=2,
            arrowcolor='green',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='green'
        ),
        dict(
            x=month_order[max_harvest_idx],
            y=max(harvest_values),
            text=f"Peak Harvest<br>{max(harvest_values)} activities",
            showarrow=True,
            arrowhead=2,
            arrowcolor='goldenrod',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='goldenrod'
        )
    ]
    
    fig.update_layout(
        title="Peak Agricultural Activity Analysis Throughout the Year",
        xaxis_title="Month",
        yaxis_title="Activity Count",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=annotations,
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_activity_density_map(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a density map showing activity concentration across regions and months.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing activity density map
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Activity Density Map (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Prepare region-month density data
    region_month_density = {}
    all_regions = set()
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            calendar = state_info.get('calendar', {})
            
            all_regions.add(region)
            
            if region not in region_month_density:
                region_month_density[region] = {month: 0 for month in month_order}
            
            for month, activity in calendar.items():
                if month in region_month_density[region] and activity and activity.strip():
                    region_month_density[region][month] += 1
    
    if not region_month_density:
        return go.Figure().update_layout(title="Activity Density Map (No data)")
    
    # Convert to matrix format
    regions = sorted(list(all_regions))
    
    z_matrix = []
    for region in regions:
        row = [region_month_density[region][month] for month in month_order]
        z_matrix.append(row)
    
    # Create heatmap with custom colorscale
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=month_order,
        y=regions,
        colorscale='Hot',
        hovertemplate="Region: %{y}<br>Month: %{x}<br>Density: %{z}<extra></extra>",
        colorbar=dict(title="Activity Density"),
        showscale=True
    ))
    
    fig.update_layout(
        title="Agricultural Activity Density Map (Regions vs Months)",
        xaxis_title="Month",
        yaxis_title="Region",
        height=max(400, len(regions) * 50),
        font=dict(size=12),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_activity_concentration_index(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a chart showing activity concentration index by crop and region.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing activity concentration index
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Activity Concentration Index (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Calculate concentration index (Herfindahl-Hirschman Index adapted for temporal concentration)
    crop_concentration = {}
    
    for crop_name, crop_data in crop_calendar.items():
        monthly_counts = {}
        total_activities = 0
        
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            
            for month, activity in calendar.items():
                if activity and activity.strip():
                    monthly_counts[month] = monthly_counts.get(month, 0) + 1
                    total_activities += 1
        
        if total_activities > 0:
            # Calculate concentration index (0 = evenly distributed, 1 = highly concentrated)
            concentration = sum((count / total_activities) ** 2 for count in monthly_counts.values())
            crop_concentration[crop_name] = {
                'concentration_index': concentration,
                'total_activities': total_activities,
                'active_months': len(monthly_counts)
            }
    
    if not crop_concentration:
        return go.Figure().update_layout(title="Activity Concentration Index (No data)")
    
    # Prepare data for visualization
    crops = list(crop_concentration.keys())
    concentration_indices = [crop_concentration[crop]['concentration_index'] for crop in crops]
    total_activities = [crop_concentration[crop]['total_activities'] for crop in crops]
    active_months = [crop_concentration[crop]['active_months'] for crop in crops]
    
    # Create bubble chart
    fig = go.Figure()
    
    # Color scale based on concentration index
    colors = ['#FF6B6B' if ci > 0.5 else '#4ECDC4' if ci > 0.25 else '#95E1D3' for ci in concentration_indices]
    
    fig.add_trace(go.Scatter(
        x=concentration_indices,
        y=active_months,
        mode='markers',
        marker=dict(
            size=[max(10, min(50, ta / 5)) for ta in total_activities],  # Size based on total activities
            color=colors,
            opacity=0.7,
            line=dict(width=2, color='white')
        ),
        text=crops,
        textposition="middle center",
        hovertemplate="<b>%{text}</b><br>Concentration Index: %{x:.3f}<br>Active Months: %{y}<br>Total Activities: %{marker.size}<extra></extra>"
    ))
    
    # Add concentration level zones
    fig.add_vrect(
        x0=0, x1=0.25,
        fillcolor="lightgreen", opacity=0.1,
        annotation_text="Low Concentration", annotation_position="top left"
    )
    fig.add_vrect(
        x0=0.25, x1=0.5,
        fillcolor="yellow", opacity=0.1,
        annotation_text="Medium Concentration", annotation_position="top"
    )
    fig.add_vrect(
        x0=0.5, x1=1,
        fillcolor="lightcoral", opacity=0.1,
        annotation_text="High Concentration", annotation_position="top right"
    )
    
    fig.update_layout(
        title="Agricultural Activity Concentration Index by Crop",
        xaxis_title="Concentration Index (0 = evenly distributed, 1 = highly concentrated)",
        yaxis_title="Number of Active Months",
        height=500,
        showlegend=False,
        font=dict(size=12)
    )
    
    return fig
