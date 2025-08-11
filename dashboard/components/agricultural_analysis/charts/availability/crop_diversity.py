"""
Crop Diversity Charts for CONAB Agricultural Data
===============================================

Creates visualizations showing crop diversity across states and regions
using CONAB crop calendar data. Includes both state and regional views.
"""

import plotly.graph_objects as go
from typing import Dict, Any
from .color_palettes import (
    get_state_color, 
    get_region_color, 
    get_crop_color,
    CROP_COLORS,
    get_state_acronym
)

def plot_conab_crop_diversity_by_state(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a crop type diversity chart showing crop types by state (with acronyms).
    """
    if not conab_data:
        return go.Figure().update_layout(title="Crop Diversity by State (No data available)")
    
    # Handle both data formats - CONAB initiative format and crop calendar format
    state_crops = {}
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        # Original CONAB initiative format
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        # Count crop types by state (original logic)
        for crop, crop_info in crop_coverage.items():
            regions = crop_info.get("regions", [])
            
            for state in regions:
                state_acronym = get_state_acronym(state)
                if state_acronym not in state_crops:
                    state_crops[state_acronym] = []
                state_crops[state_acronym].append(crop)
    
    elif 'crop_calendar' in conab_data:
        # Crop calendar format (like other availability charts)
        crop_calendar = conab_data['crop_calendar']
        
        # Count crop types by state from crop calendar
        for crop_name, crop_data in crop_calendar.items():
            for state_info in crop_data:
                # Get state name correctly - state_name or state, not region
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                state_acronym = get_state_acronym(state)
                calendar = state_info.get('calendar', {})
                
                # Only count if the crop has activities in this state
                active_months = sum(1 for month, activity in calendar.items() 
                                 if activity and activity.strip())
                
                if active_months > 0:
                    if state_acronym not in state_crops:
                        state_crops[state_acronym] = []
                    if crop_name not in state_crops[state_acronym]:
                        state_crops[state_acronym].append(crop_name)
    
    else:
        return go.Figure().update_layout(title="Crop Diversity by State (No compatible data format)")
    
    if not state_crops:
        return go.Figure().update_layout(title="Crop Diversity by State (No crop data)")
    
    # Prepare data for stacked bar chart
    states = sorted(list(state_crops.keys()))
    crop_types = list(set([crop for crops in state_crops.values() for crop in crops]))
    
    # Create figure with modern styling
    fig = go.Figure()
    
    # Count crops per state for each crop type
    for i, crop in enumerate(crop_types):
        crop_counts = []
        for state in states:
            count = state_crops[state].count(crop) if state in state_crops else 0
            crop_counts.append(count)
        
        color = get_crop_color(crop)
        
        fig.add_trace(go.Bar(
            x=crop_counts,
            y=states,
            orientation='h',
            name=crop,
            marker=dict(
                color=color,
                line=dict(color='rgba(255,255,255,0.6)', width=1),
                opacity=0.8
            ),
            hovertemplate=f"<b>{crop}</b><br>State: %{{y}}<br>Count: %{{x}}<br><extra></extra>",
            showlegend=True
        ))
    
    # Update layout with modern styling
    fig.update_layout(
        title={
            'text': "Crop Type Diversity by State",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2C3E50', 'family': 'Arial, sans-serif'}
        },
        xaxis_title="Number of Crop Types",
        yaxis_title="State",
        height=max(500, len(states) * 25),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial, sans-serif', size=12, color='#2C3E50'),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=False,
            zeroline=False
        ),
        margin=dict(l=80, r=180, t=60, b=60)
    )
    
    return fig

# Legacy function for backward compatibility
def plot_conab_crop_diversity(conab_data: Dict[str, Any]) -> go.Figure:
    """Legacy function - defaults to state view"""
    return plot_conab_crop_diversity_by_state(conab_data)


def plot_conab_crop_diversity_by_region(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a crop type diversity chart showing crop types by Brazilian region.
    Aggregates state data into regional patterns.
    """
    if not conab_data:
        return go.Figure().update_layout(title="Crop Diversity by Region (No data available)")
    
    # Region mapping for Brazilian states
    region_mapping = {
        # North (Norte)
        'AC': 'North', 'AP': 'North', 'AM': 'North', 'PA': 'North', 
        'RO': 'North', 'RR': 'North', 'TO': 'North',
        
        # Northeast (Nordeste)
        'AL': 'Northeast', 'BA': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast',
        'PB': 'Northeast', 'PE': 'Northeast', 'PI': 'Northeast', 'RN': 'Northeast', 'SE': 'Northeast',
        
        # Central-West (Centro-Oeste)
        'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
        
        # Southeast (Sudeste)
        'ES': 'Southeast', 'MG': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
        
        # South (Sul)
        'PR': 'South', 'RS': 'South', 'SC': 'South'
    }
    
    # Handle both data formats - CONAB initiative format and crop calendar format
    region_crops = {}
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        for crop, crop_info in crop_coverage.items():
            regions = crop_info.get("regions", [])
            
            for state in regions:
                state_acronym = get_state_acronym(state)
                region = region_mapping.get(state_acronym, 'Unknown')
                
                if region not in region_crops:
                    region_crops[region] = {}
                
                if crop not in region_crops[region]:
                    region_crops[region][crop] = 0
                
                region_crops[region][crop] += 1  # Count occurrences per region
    
    elif 'crop_calendar' in conab_data:
        crop_calendar = conab_data['crop_calendar']
        
        for crop_name, crop_data in crop_calendar.items():
            for state_info in crop_data:
                # Get state name correctly
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                state_acronym = get_state_acronym(state)
                region = region_mapping.get(state_acronym, 'Unknown')
                calendar = state_info.get('calendar', {})
                
                # Count active months as measure of crop presence
                active_months = sum(1 for month, activity in calendar.items() 
                                 if activity and activity.strip())
                
                if active_months > 0:
                    if region not in region_crops:
                        region_crops[region] = {}
                    
                    if crop_name not in region_crops[region]:
                        region_crops[region][crop_name] = 0
                    
                    # Weight by activity level
                    region_crops[region][crop_name] += active_months
    
    else:
        return go.Figure().update_layout(title="Crop Diversity by Region (No compatible data format)")
    
    if not region_crops:
        return go.Figure().update_layout(title="Crop Diversity by Region (No crop data)")
    
    # Prepare data for visualization
    regions = sorted(region_crops.keys())
    all_crops = set()
    for region_data in region_crops.values():
        all_crops.update(region_data.keys())
    all_crops = sorted(list(all_crops))
    
    # Create figure with regional color scheme
    fig = go.Figure()
    
    # Use crop colors from the palette, with fallback to regional colors
    from .color_palettes import get_crop_color, get_region_color
    
    for crop in all_crops:
        crop_counts = []
        colors_for_crop = []
        
        for region in regions:
            count = region_crops[region].get(crop, 0)
            crop_counts.append(count)
            # Use crop-specific color if available, otherwise use regional color
            crop_color = get_crop_color(crop)
            if crop_color == '#808080':  # Default color
                crop_color = get_region_color(region, use_dark=True)
            colors_for_crop.append(crop_color)
        
        fig.add_trace(go.Bar(
            x=crop_counts,
            y=regions,
            orientation='h',
            name=crop,
            marker=dict(
                color=get_crop_color(crop),
                line=dict(color='rgba(255,255,255,0.6)', width=1),
                opacity=0.8
            ),
            hovertemplate=f"<b>{crop}</b><br>Region: %{{y}}<br>Intensity: %{{x}}<br><extra></extra>"
        ))
    
    # Update layout with modern styling and English labels
    fig.update_layout(
        title={
            'text': "Crop Type Diversity by Brazilian Region",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2C3E50', 'family': 'Arial Black'}
        },
        xaxis_title="<b>Crop Diversity Index</b>",
        yaxis_title="<b>Brazilian Region</b>",
        height=500,
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title=dict(text="<b>Crop Types</b>", font=dict(size=14)),
            font=dict(size=12)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.3)',
            showline=True,
            linewidth=2,
            linecolor='#2C3E50',
            title_font=dict(size=14, color='#2C3E50', family='Arial Black')
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='#2C3E50',
            title_font=dict(size=14, color='#2C3E50', family='Arial Black'),
            tickfont=dict(size=12, color='#2C3E50', family='Arial')
        ),
        font=dict(family='Arial', size=12, color='#2C3E50'),
        margin=dict(l=60, r=120, t=80, b=60)
    )
    
    return fig