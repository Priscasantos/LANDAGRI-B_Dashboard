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
from ....shared.chart_core import HOVER_TEMPLATE_CROP, HOVER_TEMPLATE_REGION, calc_height, build_standard_layout

def plot_conab_crop_diversity_by_state(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Crop diversity chart showing presence/weight of each crop per state (acronym).
    Each crop is a separate trace so the legend shows crops (culturas), not regions.
    """
    if not conab_data:
        return go.Figure().update_layout(title="Crop Diversity by State (No data available)")

    # Extract crop data using a unified approach
    state_crop_weights = {}
    all_crops = set()

    # Data extraction strategies
    data_extractors = {
        "CONAB Crop Monitoring Initiative": lambda data: _extract_initiative_data(data, state_crop_weights, all_crops),
        'crop_calendar': lambda data: _extract_calendar_data(data, state_crop_weights, all_crops)
    }

    # Try each extractor until one succeeds
    extracted = False
    for key, extractor in data_extractors.items():
        if key in conab_data:
            extractor(conab_data[key])
            extracted = True
            break

    if not extracted:
        return go.Figure().update_layout(title="Crop Diversity by State (No compatible data format)")

    if not state_crop_weights:
        return go.Figure().update_layout(title="Crop Diversity by State (No crop data)")

    # Prepare data for visualization
    states = sorted(state_crop_weights.keys())
    all_crops = sorted(list(all_crops))

    # Filter crops with actual presence
    crop_series = {
        crop: [state_crop_weights.get(state, {}).get(crop, 0) for state in states]
        for crop in all_crops
    }
    crop_series = {crop: values for crop, values in crop_series.items() if any(v != 0 for v in values)}

    if not crop_series:
        return go.Figure().update_layout(title="Crop Diversity by State (No crop presence)")

    # Enhanced color palette with better visibility and distinction
    enhanced_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',  # Standard colors
        '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#7f7f7f',  # Additional colors
        '#8dd3c7', '#bebada', '#fb8072', '#80b1d3', '#fdb462',  # Pastel variants
        '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5'   # More variants
    ]

    # Assign colors to crops
    crop_color_map = {}
    for i, crop in enumerate(crop_series.keys()):
        explicit_color = get_crop_color(crop)
        crop_color_map[crop] = (
            explicit_color if explicit_color != '#808080' 
            else enhanced_palette[i % len(enhanced_palette)]
        )

    # Create visualization
    fig = go.Figure()
    for crop, values in crop_series.items():
        fig.add_trace(go.Bar(
            x=values,
            y=states,
            orientation='h',
            name=crop,
            marker=dict(
                color=crop_color_map[crop],
                line=dict(color='rgba(255,255,255,0.6)', width=0.5)
            ),
            hovertemplate=HOVER_TEMPLATE_CROP.format(crop)
        ))

    # Configure layout
    state_layout = build_standard_layout("Crop Diversity by State (legend: crops)", title_x=0.5,
                                         xaxis_title="Crop Presence / Intensity (weighted)",
                                         yaxis_title="State (Acronym)",
                                         height=calc_height(len(states), min_height=400, per_row=25),
                                         margin=dict(l=100, r=260, t=80, b=60),
                                         yaxis=dict(autorange='reversed', tickfont=dict(size=11)),
                                         legend={'title': {'text': 'Crops', 'font': {'size': 12}}}
                                         )

    fig.update_layout(**state_layout)

    return fig


def _extract_initiative_data(initiative_data: Dict[str, Any], state_crop_weights: Dict, all_crops: set) -> None:
    """Extract data from CONAB initiative format."""
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        all_crops.add(crop)
        for state in regions:
            state_acr = get_state_acronym(state)
            state_crop_weights.setdefault(state_acr, {}).setdefault(crop, 0)
            state_crop_weights[state_acr][crop] += 1


def _extract_calendar_data(crop_calendar: Dict[str, Any], state_crop_weights: Dict, all_crops: set) -> None:
    """Extract data from crop calendar format."""
    for crop_name, crop_data in crop_calendar.items():
        all_crops.add(crop_name)
        for state_info in crop_data:
            state = state_info.get('state_name', state_info.get('state', 'Unknown'))
            state_acr = get_state_acronym(state)
            calendar = state_info.get('calendar', {})
            active_months = sum(1 for _, activity in calendar.items() if activity and activity.strip())
            if active_months > 0:
                state_crop_weights.setdefault(state_acr, {}).setdefault(crop_name, 0)
                state_crop_weights[state_acr][crop_name] += active_months

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
            hovertemplate=HOVER_TEMPLATE_REGION.format(crop)
        ))
    
    # Update layout with modern styling and English labels
    region_layout = build_standard_layout("Crop Diversity Analysis by Region", title_x=0.065,
                                          xaxis_title="Crop Diversity Index",
                                          yaxis_title="Brazilian Region",
                                          height=500,
                                          legend={'title': {'text': 'Crop Types', 'font': {'size': 14}}, 'orientation': 'v', 'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 1.02},
                                          xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.3)', showline=True, linewidth=2, linecolor='#2C3E50', title_font=dict(size=14, color='#2C3E50', family='Arial, sans-serif')),
                                          yaxis=dict(showgrid=False, showline=True, linewidth=2, linecolor='#2C3E50', title_font=dict(size=14, color='#2C3E50', family='Arial, sans-serif'), tickfont=dict(size=12, color='#2C3E50', family='Arial, sans-serif')),
                                          margin=dict(l=60, r=120, t=80, b=60)
                                          )

    fig.update_layout(**region_layout)
    
    return fig