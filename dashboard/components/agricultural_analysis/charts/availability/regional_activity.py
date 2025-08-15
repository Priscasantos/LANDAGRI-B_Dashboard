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
    Create a heatmap showing agricultural activity intensity across states and activity types.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing state activity heatmap by activity type
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Activity Heatmap (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare state activity data by activity type
    state_activity_data = {}
    activity_types = ['Planting Only', 'Harvesting Only', 'Planting & Harvesting', 'Total Activities']
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_abbrev = state_info.get('state_code', '')
            calendar = state_info.get('calendar', {})
            
            if not state_abbrev:
                continue
                
            if state_abbrev not in state_activity_data:
                state_activity_data[state_abbrev] = {
                    'Planting Only': 0,
                    'Harvesting Only': 0, 
                    'Planting & Harvesting': 0,
                    'Total Activities': 0
                }
            
            # Count activities by type
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            
            for month in months:
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    state_activity_data[state_abbrev]['Total Activities'] += 1
                    
                    if activity == 'P':
                        state_activity_data[state_abbrev]['Planting Only'] += 1
                    elif activity == 'H':
                        state_activity_data[state_abbrev]['Harvesting Only'] += 1
                    elif activity == 'PH':
                        state_activity_data[state_abbrev]['Planting & Harvesting'] += 1
    
    if not state_activity_data:
        return go.Figure().update_layout(title="Activity Heatmap (No data)")
    
    # Get all states sorted alphabetically for better organization
    sorted_states = sorted(state_activity_data.keys())
    
    # Create matrix for heatmap
    matrix = []
    for state in sorted_states:
        row = [state_activity_data[state][activity_type] for activity_type in activity_types]
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=activity_types,
        y=sorted_states,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Activity Count"),
        hovertemplate="State: %{y}<br>Activity Type: %{x}<br>Count: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Agricultural Activity Intensity by State and Activity Type",
        xaxis_title="Activity Type",
        yaxis_title="State",
        height=800,  # Increased height to accommodate all states
        xaxis=dict(tickangle=45),
        yaxis=dict(tickfont=dict(size=10))  # Smaller font for better readability
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


def plot_state_activity_comparison(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a comparison chart showing agricultural activity levels by individual states.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure comparing state activities
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="State Activity Comparison (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare state data
    state_data = {}
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_abbrev = state_info.get('state_code', '')
            calendar = state_info.get('calendar', {})
            
            if not state_abbrev:
                continue
                
            if state_abbrev not in state_data:
                state_data[state_abbrev] = {
                    'total_activities': 0,
                    'planting_activities': 0,
                    'harvest_activities': 0,
                    'crops': set()
                }
            
            state_data[state_abbrev]['crops'].add(crop_name)
            
            # Count activities using correct month names - handle PH (simultaneous)
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            
            for month in months:
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    if 'P' in activity:  # Includes both 'P' and 'PH'
                        state_data[state_abbrev]['planting_activities'] += 1
                        state_data[state_abbrev]['total_activities'] += 1
                    if 'H' in activity:  # Includes both 'H' and 'PH'
                        state_data[state_abbrev]['harvest_activities'] += 1
                        # Only add to total if it's not PH (to avoid double counting)
                        if activity != 'PH':
                            state_data[state_abbrev]['total_activities'] += 1
    
    if not state_data:
        return go.Figure().update_layout(title="State Activity Comparison (No data)")
    
    # Sort states by total activities and show ALL states (remove top 15 limit)
    sorted_states = sorted(state_data.keys(), 
                          key=lambda s: state_data[s]['total_activities'], 
                          reverse=True)
    
    # Prepare data for visualization - show all states
    states = sorted_states
    total_activities = [state_data[state]['total_activities'] for state in states]
    planting_activities = [state_data[state]['planting_activities'] for state in states]
    harvest_activities = [state_data[state]['harvest_activities'] for state in states]
    crops_count = [len(state_data[state]['crops']) for state in states]
    
    # Create figure
    fig = go.Figure()
    
    # Add planting activities bar
    fig.add_trace(go.Bar(
        x=states,
        y=planting_activities,
        name='Planting Activities',
        marker_color='#2E8B57',
        hovertemplate="State: %{x}<br>Planting Activities: %{y}<br><extra></extra>"
    ))
    
    # Add harvest activities bar
    fig.add_trace(go.Bar(
        x=states,
        y=harvest_activities,
        name='Harvest Activities',
        marker_color='#DAA520',
        hovertemplate="State: %{x}<br>Harvest Activities: %{y}<br><extra></extra>"
    ))
    
    fig.update_layout(
        title="Agricultural Activity Comparison (Planting and Harvesting Activities)",
        xaxis_title="State",
        yaxis_title="Number of Activities",
        height=600,  # Increased height for more states
        barmode='stack',
        showlegend=True,
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_state_crop_distribution(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a chart showing crop distribution by individual states.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing crop distribution by state
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="State Crop Distribution (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare state-crop matrix
    state_crops = {}
    all_crops = set()
    
    for crop_name, crop_data in crop_calendar.items():
        all_crops.add(crop_name)
        for state_info in crop_data:
            state_abbrev = state_info.get('state', '')
            
            if not state_abbrev:
                continue
                
            if state_abbrev not in state_crops:
                state_crops[state_abbrev] = set()
            
            state_crops[state_abbrev].add(crop_name)
    
    if not state_crops:
        return go.Figure().update_layout(title="State Crop Distribution (No data)")
    
    # Create matrix for heatmap
    states = sorted(state_crops.keys())
    crops = sorted(all_crops)
    
    # Create binary matrix (1 if state has crop, 0 otherwise)
    matrix = []
    for crop in crops:
        row = []
        for state in states:
            if state in state_crops and crop in state_crops[state]:
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=states,
        y=crops,
        colorscale='Viridis',
        showscale=True,
        hovertemplate="State: %{x}<br>Crop: %{y}<br>Present: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Crop Distribution and Activities by State",
        xaxis_title="State",
        yaxis_title="Crop Type",
        height=600,
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_state_activity_timeline(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a timeline showing agricultural activities by individual states.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing activity timeline by state
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="State Activity Timeline (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Prepare monthly data by state
    state_monthly_data = {}
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    month_abbrev = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            state_abbrev = state_info.get('state_code', '')
            calendar = state_info.get('calendar', {})
            
            if not state_abbrev:
                continue
                
            if state_abbrev not in state_monthly_data:
                state_monthly_data[state_abbrev] = {month_abbrev[i]: 0 for i in range(12)}
            
            # Count activities per month - handle PH (simultaneous planting and harvest)
            for i, month in enumerate(months):
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    month_short = month_abbrev[i]
                    # Count each type of activity - PH counts for both P and H
                    if 'P' in activity:  # Includes both 'P' and 'PH'
                        state_monthly_data[state_abbrev][month_short] += 1
                    if 'H' in activity:  # Includes both 'H' and 'PH'
                        state_monthly_data[state_abbrev][month_short] += 1
    
    if not state_monthly_data:
        return go.Figure().update_layout(title="State Activity Timeline (No data)")
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for all states with highest activity first
    sorted_states = sorted(state_monthly_data.keys(), 
                          key=lambda s: sum(state_monthly_data[s].values()), 
                          reverse=True)
    
    colors = px.colors.qualitative.Set3
    
    for i, state in enumerate(sorted_states):
        activities = [state_monthly_data[state][month] for month in month_abbrev]
        
        fig.add_trace(go.Scatter(
            x=month_abbrev,
            y=activities,
            mode='lines+markers',
            name=state,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6),
            hovertemplate=f"State: {state}<br>Month: %{{x}}<br>Activities: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Planting and Harvesting Activity Timeline by State",
        xaxis_title="Month",
        yaxis_title="Number of Planting/Harvesting Activities",
        height=600,  # Increased height for better visibility
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


def plot_regional_activity_heatmap(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a heatmap showing agricultural activity intensity by Brazilian regions and months.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing regional activity heatmap
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Regional Activity Heatmap (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Brazilian regions
    regions = ['North', 'Northeast', 'Central-West', 'Southeast', 'South']
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    month_abbrev = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Initialize regional monthly data
    regional_monthly_data = {}
    for region in regions:
        regional_monthly_data[region] = {month_abbrev[i]: 0 for i in range(12)}
    
    # Aggregate data by region
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            calendar = state_info.get('calendar', {})
            
            if region not in regions:
                continue
            
            # Count activities per month - handle PH (simultaneous planting and harvest)
            for i, month in enumerate(months):
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    month_short = month_abbrev[i]
                    # Count each type of activity - PH counts for both P and H
                    if 'P' in activity:  # Includes both 'P' and 'PH'
                        regional_monthly_data[region][month_short] += 1
                    if 'H' in activity:  # Includes both 'H' and 'PH'
                        regional_monthly_data[region][month_short] += 1
    
    # Create matrix for heatmap
    matrix = []
    for region in regions:
        row = [regional_monthly_data[region][month] for month in month_abbrev]
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=month_abbrev,
        y=regions,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Activity Count"),
        hovertemplate="Region: %{y}<br>Month: %{x}<br>Activities: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Agricultural Activity Intensity by Brazilian Regions",
        xaxis_title="Month",
        yaxis_title="Brazilian Region",
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return fig


def plot_regional_activity_timeline(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a timeline showing agricultural activities aggregated by Brazilian regions.
    
    Args:
        conab_data: Dictionary containing CONAB crop calendar data
        
    Returns:
        Plotly figure showing regional activity timeline
    """
    if not conab_data or 'crop_calendar' not in conab_data:
        return go.Figure().update_layout(title="Regional Activity Timeline (No data available)")
    
    crop_calendar = conab_data['crop_calendar']
    
    # Brazilian regions
    regions = ['North', 'Northeast', 'Central-West', 'Southeast', 'South']
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    month_abbrev = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Initialize regional monthly data by activity type
    regional_planting_data = {}
    regional_harvest_data = {}
    
    for region in regions:
        regional_planting_data[region] = {month_abbrev[i]: 0 for i in range(12)}
        regional_harvest_data[region] = {month_abbrev[i]: 0 for i in range(12)}
    
    # Aggregate data by region
    for crop_name, crop_data in crop_calendar.items():
        for state_info in crop_data:
            region = state_info.get('region', 'Unknown')
            calendar = state_info.get('calendar', {})
            
            if region not in regions:
                continue
            
            # Count activities per month - handle PH (simultaneous planting and harvest)
            for i, month in enumerate(months):
                activity = calendar.get(month, '')
                if activity and activity.strip():
                    activity = activity.strip()
                    month_short = month_abbrev[i]
                    
                    if 'P' in activity:  # Includes both 'P' and 'PH'
                        regional_planting_data[region][month_short] += 1
                    if 'H' in activity:  # Includes both 'H' and 'PH'
                        regional_harvest_data[region][month_short] += 1
    
    # Create figure
    fig = go.Figure()
    
    # Regional colors
    region_colors = {
        'North': '#2E8B57',
        'Northeast': '#FF6347', 
        'Central-West': '#DAA520',
        'Southeast': '#4682B4',
        'South': '#9370DB'
    }
    
    # Add planting traces
    for region in regions:
        planting_activities = [regional_planting_data[region][month] for month in month_abbrev]
        
        fig.add_trace(go.Scatter(
            x=month_abbrev,
            y=planting_activities,
            mode='lines+markers',
            name=f'{region} - Planting',
            line=dict(color=region_colors.get(region, '#808080'), width=3, dash='solid'),
            marker=dict(size=8, symbol='circle'),
            hovertemplate=f"Region: {region}<br>Month: %{{x}}<br>Planting Activities: %{{y}}<extra></extra>"
        ))
    
    # Add harvest traces
    for region in regions:
        harvest_activities = [regional_harvest_data[region][month] for month in month_abbrev]
        
        fig.add_trace(go.Scatter(
            x=month_abbrev,
            y=harvest_activities,
            mode='lines+markers',
            name=f'{region} - Harvest',
            line=dict(color=region_colors.get(region, '#808080'), width=3, dash='dash'),
            marker=dict(size=8, symbol='square'),
            hovertemplate=f"Region: {region}<br>Month: %{{x}}<br>Harvest Activities: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Agricultural Activity Timeline by Brazilian Regions",
        xaxis_title="Month",
        yaxis_title="Number of Activities",
        height=600,
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
