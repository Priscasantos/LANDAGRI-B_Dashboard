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
    across different seasons by state (horizontal layout).
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing seasonal agricultural patterns by state
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
    
    # Prepare data for visualization by state
    pattern_data = []
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_code = state_info.get('state_code', '')
            state_name = state_info.get('state_name', '')
            region = state_info.get('region', '')
            calendar = state_info.get('calendar', {})
            
            if not state_code:
                continue
            
            # Count activities by season for each state
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
                        'State': state_code,
                        'State_Name': state_name,
                        'Region': region,
                        'Season': season,
                        'Activities': count
                    })
    
    if not pattern_data:
        return go.Figure().update_layout(title="Seasonal Patterns (No activity data)")
    
    # Convert to DataFrame
    df = pd.DataFrame(pattern_data)
    
    # Aggregate data by state and season
    state_season_data = df.groupby(['State', 'Season'])['Activities'].sum().reset_index()
    
    # Color mapping for seasons
    season_colors = {
        'Spring': '#90EE90',  # Light green
        'Summer': '#FFD700',  # Gold
        'Autumn': '#DEB887',  # Burlywood
        'Winter': '#87CEEB'   # Sky blue
    }
    
    # Get all states and sort them
    all_states = sorted(state_season_data['State'].unique())
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Create separate traces for each season
    for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
        season_data = state_season_data[state_season_data['Season'] == season]
        
        # Create a complete list for all states (including zeros)
        activities_by_state = []
        for state in all_states:
            state_activities = season_data[season_data['State'] == state]['Activities'].sum()
            activities_by_state.append(state_activities)
        
        fig.add_trace(go.Bar(
            y=all_states,  # Y-axis for horizontal bars
            x=activities_by_state,  # X-axis for horizontal bars
            name=season,
            marker_color=season_colors[season],
            orientation='h',  # Horizontal orientation
            hovertemplate=f"<b>{season}</b><br>State: %{{y}}<br>Activities: %{{x}}<extra></extra>"
        ))
    
    # Update layout for horizontal display
    fig.update_layout(
        title="Seasonal Agricultural Activity Patterns by State",
        xaxis_title="Number of Activities",
        yaxis_title="State",
        barmode='stack',
        height=800,  # Increased height for better state visibility
        showlegend=True,
        legend=dict(
            title=dict(text="Seasons"),  # Título da legenda
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            tickfont=dict(size=10),  # Smaller font for better readability
            automargin=True
        )
    )
    
    return fig


def plot_crop_seasonal_distribution(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a heatmap showing crop distribution by state and month.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing crop distribution by state and month
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Crop Distribution by State and Month (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Month order for proper sorting
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    month_abbrev = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Prepare data matrix: states vs months with activity counts
    state_month_matrix = {}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_code = state_info.get('state_code', '')
            calendar = state_info.get('calendar', {})
            
            if not state_code:
                continue
                
            if state_code not in state_month_matrix:
                state_month_matrix[state_code] = {month_abbrev[i]: 0 for i in range(12)}
            
            # Count activities per month for this state
            for i, month in enumerate(month_order):
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    month_short = month_abbrev[i]
                    # Count each type of activity - PH counts for both P and H
                    if 'P' in activity:  # Includes both 'P' and 'PH'
                        state_month_matrix[state_code][month_short] += 1
                    if 'H' in activity:  # Includes both 'H' and 'PH'
                        state_month_matrix[state_code][month_short] += 1
    
    if not state_month_matrix:
        return go.Figure().update_layout(title="Crop Distribution by State and Month (No data)")
    
    # Convert to matrix format for heatmap
    states = sorted(state_month_matrix.keys())
    
    z_matrix = []
    for state in states:
        row = [state_month_matrix[state][month] for month in month_abbrev]
        z_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=month_abbrev,
        y=states,
        colorscale='Viridis',
        hovertemplate="State: %{y}<br>Month: %{x}<br>Activities: %{z}<extra></extra>",
        colorbar=dict(title="Number of Planting/Harvesting Activities")
    ))
    
    fig.update_layout(
        title="Crop Activity Distribution by State and Month",
        xaxis_title="Month",
        yaxis_title="State",
        height=max(600, len(states) * 25),  # Dynamic height based on number of states
        font=dict(size=10),
        xaxis=dict(tickangle=45),  # Rotate month names for better readability
        yaxis=dict(tickfont=dict(size=10))
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
            title=dict(text="Activities"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(tickangle=45)
    )
    
    return fig
