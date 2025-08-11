"""
Seasonal Patterns Chart for CONAB Agricultural Data
==================================================

Creates visualizations showing seasonal agricultural patterns across Brazil
using CONAB crop calendar data.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd


def plot_seasonal_patterns(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a seasonal patterns chart showing planting and harvest periods
    across different seasons and regions.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing seasonal agricultural patterns
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Seasonal Patterns (No data available)")
    
    # Extract crop calendar data
    crop_calendar = conab_data['crop_calendar']
    
    # Define seasons and their months
    seasons = {
        'Spring': ['September', 'October', 'November'],
        'Summer': ['December', 'January', 'February'],
        'Autumn': ['March', 'April', 'May'],
        'Winter': ['June', 'July', 'August']
    }
    
    # Prepare data for visualization
    pattern_data = []
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_code = state_info.get('state_code', '')
            state_name = state_info.get('state_name', '')
            region = state_info.get('region', '')
            calendar = state_info.get('calendar', {})
            
            # Count activities by season
            season_activities = {'Spring': 0, 'Summer': 0, 'Autumn': 0, 'Winter': 0}
            
            for month, activity in calendar.items():
                if activity and activity.strip():  # Has some activity
                    for season, months in seasons.items():
                        if month in months:
                            season_activities[season] += 1
                            break
            
            # Add to pattern data
            for season, count in season_activities.items():
                if count > 0:
                    pattern_data.append({
                        'Crop': crop_name,
                        'State': state_name,
                        'Region': region,
                        'Season': season,
                        'Activities': count
                    })
    
    if not pattern_data:
        return go.Figure().update_layout(title="Seasonal Patterns (No activity data)")
    
    # Convert to DataFrame
    df = pd.DataFrame(pattern_data)
    
    # Create sunburst chart for hierarchical view
    fig = go.Figure()
    
    # Aggregate data by region and season
    region_season_data = df.groupby(['Region', 'Season'])['Activities'].sum().reset_index()
    
    # Color mapping for seasons
    season_colors = {
        'Spring': '#90EE90',  # Light green
        'Summer': '#FFD700',  # Gold
        'Autumn': '#DEB887',  # Burlywood
        'Winter': '#87CEEB'   # Sky blue
    }
    
    # Create separate traces for each season
    for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
        season_data = region_season_data[region_season_data['Season'] == season]
        
        if not season_data.empty:
            fig.add_trace(go.Bar(
                x=season_data['Region'],
                y=season_data['Activities'],
                name=season,
                marker_color=season_colors[season],
                hovertemplate=f"<b>{season}</b><br>Region: %{{x}}<br>Activities: %{{y}}<extra></extra>"
            ))
    
    # Update layout
    fig.update_layout(
        title="Seasonal Agricultural Activity Patterns by Region",
        xaxis_title="Region",
        yaxis_title="Number of Activities",
        barmode='stack',
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


def plot_crop_seasonal_distribution(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a heatmap showing crop distribution across seasons and regions.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing crop seasonal distribution
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Crop Seasonal Distribution (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Define seasons and their months
    seasons = {
        'Spring': ['September', 'October', 'November'],
        'Summer': ['December', 'January', 'February'],
        'Autumn': ['March', 'April', 'May'],
        'Winter': ['June', 'July', 'August']
    }
    
    # Prepare data matrix: crops vs seasons
    crop_season_matrix = {}
    
    for crop_name, crop_data in crop_calendar.items():
        crop_season_matrix[crop_name] = {'Spring': 0, 'Summer': 0, 'Autumn': 0, 'Winter': 0}
        
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            
            for month, activity in calendar.items():
                if activity and activity.strip():
                    for season, months in seasons.items():
                        if month in months:
                            crop_season_matrix[crop_name][season] += 1
                            break
    
    if not crop_season_matrix:
        return go.Figure().update_layout(title="Crop Seasonal Distribution (No data)")
    
    # Convert to matrix format for heatmap
    crops = list(crop_season_matrix.keys())
    seasons_list = ['Spring', 'Summer', 'Autumn', 'Winter']
    
    z_matrix = []
    for crop in crops:
        row = [crop_season_matrix[crop][season] for season in seasons_list]
        z_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=seasons_list,
        y=crops,
        colorscale='Viridis',
        hovertemplate="Crop: %{y}<br>Season: %{x}<br>Activities: %{z}<extra></extra>",
        colorbar=dict(title="Number of Activities")
    ))
    
    fig.update_layout(
        title="Crop Activity Distribution Across Seasons",
        xaxis_title="Season",
        yaxis_title="Crop Type",
        height=max(400, len(crops) * 30),
        font=dict(size=10)
    )
    
    return fig


def plot_monthly_activity_intensity(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a line chart showing monthly activity intensity across the year.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing monthly activity intensity
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Monthly Activity Intensity (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Count activities by month and type
    monthly_activities = {month: {'Planting': 0, 'Harvest': 0, 'Both': 0} for month in month_order}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            
            for month, activity in calendar.items():
                if month in monthly_activities and activity:
                    activity = activity.strip()
                    if activity == 'P':
                        monthly_activities[month]['Planting'] += 1
                    elif activity == 'H':
                        monthly_activities[month]['Harvest'] += 1
                    elif activity == 'PH':
                        monthly_activities[month]['Both'] += 1
    
    # Create line chart
    fig = go.Figure()
    
    # Add traces for each activity type
    activity_colors = {
        'Planting': '#2E8B57',    # Sea green
        'Harvest': '#DAA520',     # Goldenrod
        'Both': '#8B0000'         # Dark red
    }
    
    for activity_type, color in activity_colors.items():
        values = [monthly_activities[month][activity_type] for month in month_order]
        
        fig.add_trace(go.Scatter(
            x=month_order,
            y=values,
            mode='lines+markers',
            name=activity_type,
            line=dict(color=color, width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>{activity_type}</b><br>Month: %{{x}}<br>Activities: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Monthly Agricultural Activity Intensity Throughout the Year",
        xaxis_title="Month",
        yaxis_title="Number of Activities",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(tickangle=45)
    )
    
    return fig
