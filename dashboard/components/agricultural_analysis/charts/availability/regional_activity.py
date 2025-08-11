"""
Regional Activity Analysis Chart for CONAB Agricultural Data
==========================================================

Creates visualizations showing regional agricultural activity patterns
using CONAB crop calendar data.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd


def plot_regional_activity_comparison(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a comparison chart showing agricultural activity levels across regions.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure comparing regional activities
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Regional Activity Comparison (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare regional data
    regional_data = {}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            state_name = state_info.get('state_name', '')
            calendar = state_info.get('calendar', {})
            
            if region not in regional_data:
                regional_data[region] = {
                    'total_activities': 0,
                    'planting_activities': 0,
                    'harvest_activities': 0,
                    'states': set(),
                    'crops': set()
                }
            
            regional_data[region]['states'].add(state_name)
            regional_data[region]['crops'].add(crop_name)
            
            # Count activities
            for month, activity in calendar.items():
                if activity and activity.strip():
                    activity = activity.strip()
                    regional_data[region]['total_activities'] += 1
                    
                    if 'P' in activity:
                        regional_data[region]['planting_activities'] += 1
                    if 'H' in activity:
                        regional_data[region]['harvest_activities'] += 1
    
    if not regional_data:
        return go.Figure().update_layout(title="Regional Activity Comparison (No data)")
    
    # Prepare data for visualization
    regions = list(regional_data.keys())
    total_activities = [regional_data[region]['total_activities'] for region in regions]
    planting_activities = [regional_data[region]['planting_activities'] for region in regions]
    harvest_activities = [regional_data[region]['harvest_activities'] for region in regions]
    states_count = [len(regional_data[region]['states']) for region in regions]
    crops_count = [len(regional_data[region]['crops']) for region in regions]
    
    # Create subplot with secondary y-axis
    fig = go.Figure()
    
    # Add total activities bar
    fig.add_trace(go.Bar(
        x=regions,
        y=total_activities,
        name='Total Activities',
        marker_color='#1f77b4',
        yaxis='y',
        hovertemplate="Region: %{x}<br>Total Activities: %{y}<extra></extra>"
    ))
    
    # Add planting activities
    fig.add_trace(go.Scatter(
        x=regions,
        y=planting_activities,
        mode='lines+markers',
        name='Planting Activities',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8),
        yaxis='y2',
        hovertemplate="Region: %{x}<br>Planting: %{y}<extra></extra>"
    ))
    
    # Add harvest activities
    fig.add_trace(go.Scatter(
        x=regions,
        y=harvest_activities,
        mode='lines+markers',
        name='Harvest Activities',
        line=dict(color='#DAA520', width=3),
        marker=dict(size=8),
        yaxis='y2',
        hovertemplate="Region: %{x}<br>Harvest: %{y}<extra></extra>"
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title="Regional Agricultural Activity Comparison",
        xaxis_title="Region",
        yaxis=dict(
            title="Total Activities",
            side="left"
        ),
        yaxis2=dict(
            title="Specific Activities (P/H)",
            side="right",
            overlaying="y"
        ),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_state_activity_heatmap(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a heatmap showing activity intensity by state and crop type.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing state-crop activity heatmap
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="State Activity Heatmap (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare state-crop matrix
    state_crop_matrix = {}
    all_states = set()
    all_crops = set()
    
    for crop_name, crop_data in crop_calendar.items():
        all_crops.add(crop_name)
        
        for state_info in crop_data:
            state_code = state_info.get('state_code', '')
            calendar = state_info.get('calendar', {})
            
            if state_code:
                all_states.add(state_code)
                
                if state_code not in state_crop_matrix:
                    state_crop_matrix[state_code] = {}
                
                # Count activities for this state-crop combination
                activity_count = sum(1 for activity in calendar.values() if activity and activity.strip())
                state_crop_matrix[state_code][crop_name] = activity_count
    
    if not state_crop_matrix:
        return go.Figure().update_layout(title="State Activity Heatmap (No data)")
    
    # Convert to matrix format
    states = sorted(list(all_states))
    crops = sorted(list(all_crops))
    
    z_matrix = []
    for state in states:
        row = []
        for crop in crops:
            value = state_crop_matrix.get(state, {}).get(crop, 0)
            row.append(value)
        z_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=crops,
        y=states,
        colorscale='YlOrRd',
        hovertemplate="State: %{y}<br>Crop: %{x}<br>Activities: %{z}<extra></extra>",
        colorbar=dict(title="Activity Count")
    ))
    
    fig.update_layout(
        title="Agricultural Activity Intensity by State and Crop Type",
        xaxis_title="Crop Type",
        yaxis_title="State",
        height=max(600, len(states) * 20),
        font=dict(size=10),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_regional_crop_specialization(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a chart showing crop specialization patterns by region.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing regional crop specialization
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Regional Crop Specialization (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Calculate regional crop specialization
    regional_crops = {}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            calendar = state_info.get('calendar', {})
            
            if region not in regional_crops:
                regional_crops[region] = {}
            
            if crop_name not in regional_crops[region]:
                regional_crops[region][crop_name] = 0
            
            # Count non-empty activities
            activity_count = sum(1 for activity in calendar.values() if activity and activity.strip())
            regional_crops[region][crop_name] += activity_count
    
    if not regional_crops:
        return go.Figure().update_layout(title="Regional Crop Specialization (No data)")
    
    # Create stacked bar chart
    fig = go.Figure()
    
    # Get all crops for consistent coloring
    all_crops = set()
    for region_data in regional_crops.values():
        all_crops.update(region_data.keys())
    
    crop_colors = px.colors.qualitative.Set3[:len(all_crops)]
    color_map = dict(zip(sorted(all_crops), crop_colors))
    
    regions = sorted(regional_crops.keys())
    
    for crop in sorted(all_crops):
        values = []
        for region in regions:
            value = regional_crops[region].get(crop, 0)
            values.append(value)
        
        fig.add_trace(go.Bar(
            x=regions,
            y=values,
            name=crop,
            marker_color=color_map[crop],
            hovertemplate=f"<b>{crop}</b><br>Region: %{{x}}<br>Activities: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Regional Crop Specialization Patterns",
        xaxis_title="Region",
        yaxis_title="Activity Count",
        barmode='stack',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig


def plot_activity_timeline_by_region(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a timeline showing when agricultural activities occur by region.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing regional activity timeline
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Regional Activity Timeline (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Prepare regional monthly data
    regional_monthly = {}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            calendar = state_info.get('calendar', {})
            
            if region not in regional_monthly:
                regional_monthly[region] = {month: 0 for month in month_order}
            
            for month, activity in calendar.items():
                if month in regional_monthly[region] and activity and activity.strip():
                    regional_monthly[region][month] += 1
    
    if not regional_monthly:
        return go.Figure().update_layout(title="Regional Activity Timeline (No data)")
    
    # Create line chart for each region
    fig = go.Figure()
    
    region_colors = px.colors.qualitative.Set2[:len(regional_monthly)]
    
    for i, (region, monthly_data) in enumerate(sorted(regional_monthly.items())):
        values = [monthly_data[month] for month in month_order]
        
        fig.add_trace(go.Scatter(
            x=month_order,
            y=values,
            mode='lines+markers',
            name=region,
            line=dict(color=region_colors[i % len(region_colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>{region}</b><br>Month: %{{x}}<br>Activities: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Agricultural Activity Timeline by Region",
        xaxis_title="Month",
        yaxis_title="Number of Activities",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        xaxis=dict(tickangle=45)
    )
    
    return fig
