"""
Spatial Coverage Charts for CONAB Agricultural Data
==================================================

Creates visualizations showing spatial coverage of agricultural data
using CONAB crop calendar data. Includes both state         # Crop calendar format - IMPROVED CALCULATION  
        crop_calendar = conab_data['crop_calendar']
        
        for crop_name, crop_data in crop_calendar.items():
            for state_info in crop_data:
                # Get state name correctly
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                state_acronym = get_state_acronym(state)
                region = region_mapping.get(state_acronym, 'Unknown')
                calendar = state_info.get('calendar', {})
                
                if region not in region_coverage:
                    region_coverage[region] = {
                        'total_activities': 0,
                        'active_months': 0,
                        'crops': set(),
                        'states': set()
                    }
                
                # Count ALL activities (more precise calculation)
                active_months_this_crop = 0
                total_activities_this_crop = 0
                
                for month, activity in calendar.items():
                    if activity and activity.strip():
                        active_months_this_crop += 1
                        total_activities_this_crop += 1
                        # Count different activity types with different weights
                        if activity.strip() == 'PH':
                            total_activities_this_crop += 1  # Bonus for combined activities
                
                if total_activities_this_crop > 0:
                    region_coverage[region]['crops'].add(crop_name)
                    region_coverage[region]['states'].add(state_acronym)
                    region_coverage[region]['total_activities'] += total_activities_this_crop
                    region_coverage[region]['active_months'] += active_months_this_crop
"""

import plotly.graph_objects as go
from typing import Dict, Any
from .color_palettes import (
    get_state_color, 
    get_region_color, 
    get_coverage_color,
    MODERN_COLORS,
    REGIONAL_COLORS_DARK,
    get_state_acronym
)

def plot_conab_spatial_coverage_by_state(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a spatial coverage chart showing percentage coverage by state (with acronyms).
    """
    if not conab_data:
        return go.Figure().update_layout(title="Spatial Coverage by State (No data available)")
    
    # Handle both data formats - CONAB initiative format and crop calendar format
    state_coverage = {}
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        # Original CONAB initiative format
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        for crop, crop_info in crop_coverage.items():
            regions = crop_info.get("regions", [])
            first_crop_years = crop_info.get("first_crop_years", {})
            second_crop_years = crop_info.get("second_crop_years", {})
            
            for state in regions:
                state_acronym = get_state_acronym(state)
                if state_acronym not in state_coverage:
                    state_coverage[state_acronym] = set()
                
                # Add years from first semester
                if state in first_crop_years:
                    for year_range in first_crop_years[state]:
                        start_year = int(year_range.split('-')[0])
                        end_year = int(year_range.split('-')[1])
                        for year in range(start_year, end_year + 1):
                            state_coverage[state_acronym].add(year)
                
                # Add years from second semester
                if state in second_crop_years:
                    for year_range in second_crop_years[state]:
                        start_year = int(year_range.split('-')[0])
                        end_year = int(year_range.split('-')[1])
                        for year in range(start_year, end_year + 1):
                            state_coverage[state_acronym].add(year)
    
    elif 'crop_calendar' in conab_data:
        # Crop calendar format - IMPROVED CALCULATION
        crop_calendar = conab_data['crop_calendar']
        
        for crop_name, crop_data in crop_calendar.items():
            for state_info in crop_data:
                # Get state name correctly
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                state_acronym = get_state_acronym(state)
                calendar = state_info.get('calendar', {})
                
                if state_acronym not in state_coverage:
                    state_coverage[state_acronym] = {
                        'total_activities': 0,
                        'active_months': 0,
                        'crops': set()
                    }
                
                # Count ALL activities (more precise than just crop count)
                active_months_this_crop = 0
                total_activities_this_crop = 0
                
                for month, activity in calendar.items():
                    if activity and activity.strip():
                        active_months_this_crop += 1
                        total_activities_this_crop += 1
                        # Count different activity types (P, H, PH) with different weights
                        if activity.strip() == 'PH':
                            total_activities_this_crop += 1  # Bonus for combined activities
                
                if total_activities_this_crop > 0:
                    state_coverage[state_acronym]['crops'].add(crop_name)
                    state_coverage[state_acronym]['total_activities'] += total_activities_this_crop
                    state_coverage[state_acronym]['active_months'] += active_months_this_crop
    
    else:
        return go.Figure().update_layout(title="Spatial Coverage by State (No compatible data format)")
    
    if not state_coverage:
        return go.Figure().update_layout(title="Spatial Coverage by State (No coverage data)")
    
    # IMPROVED: Calculate coverage percentages using activity density
    states = []
    coverages = []
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        # For CONAB initiative, use temporal coverage
        total_years = 24
        for state, years in state_coverage.items():
            coverage_percent = (len(years) / total_years) * 100
            states.append(state)
            coverages.append(coverage_percent)
    else:
        # For crop calendar, use improved activity-based calculation
        max_total_activities = max(data['total_activities'] for data in state_coverage.values()) if state_coverage else 1
        max_crops = max(len(data['crops']) for data in state_coverage.values()) if state_coverage else 1
        max_active_months = max(data['active_months'] for data in state_coverage.values()) if state_coverage else 1
        
        for state, data in state_coverage.items():
            # Combine multiple factors for more nuanced coverage calculation
            activity_factor = (data['total_activities'] / max_total_activities) * 60  # 60% weight
            crop_factor = (len(data['crops']) / max_crops) * 30  # 30% weight
            density_factor = (data['active_months'] / max_active_months) * 10  # 10% weight
            
            coverage_percent = activity_factor + crop_factor + density_factor
            states.append(state)
            coverages.append(coverage_percent)
    
    # Sort by coverage percentage
    sorted_data = sorted(zip(states, coverages), key=lambda x: x[1], reverse=True)
    states, coverages = zip(*sorted_data)
    
    # Apply regional colors to states
    colors = []
    for state in states:
        colors.append(get_state_color(state, use_dark=True))
    
    # Create figure with modern styling and regional colors
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=coverages,
        y=states,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.8)', width=1.5),
            pattern=dict(shape='', size=8)
        ),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        textfont=dict(size=12, color='#2C3E50', family='Arial, sans-serif'),
        hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<br><extra></extra>",
        name="Coverage"
    ))
    
    # Update layout with modern styling
    fig.update_layout(
        title=dict(
            text="Agricultural data availability by Brazilian States Coverage (states colored by region)",
            font=dict(size=15, color='#2C3E50', family='Arial, sans-serif'),
            x=0.0
        ),
        xaxis_title="Coverage (%)",
        yaxis_title="State",
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=12, color='#2C3E50'),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(176,196,222,0.3)',
            range=[0, max(coverages) * 1.15] if coverages else [0, 100],
            tickfont=dict(size=12, color='#2C3E50'),
            title_font=dict(size=15, color='#2C3E50', family='Arial, sans-serif')
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, color='#2C3E50'),
            title_font=dict(size=15, color='#2C3E50', family='Arial, sans-serif')
        ),
        margin=dict(l=80, r=120, t=80, b=60)
    )
    
    return fig


def plot_conab_spatial_coverage_by_region(conab_data: Dict[str, Any]) -> go.Figure:
    """
    Create a spatial coverage chart showing percentage coverage by region.
    """
    if not conab_data:
        return go.Figure().update_layout(title="Spatial Coverage by Region (No data available)")
    
    # Define Brazilian regions
    region_mapping = {
        'AC': 'North', 'AP': 'North', 'AM': 'North', 'PA': 'North', 'RO': 'North', 'RR': 'North', 'TO': 'North',
        'AL': 'Northeast', 'BA': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast', 'PB': 'Northeast', 
        'PE': 'Northeast', 'PI': 'Northeast', 'RN': 'Northeast', 'SE': 'Northeast',
        'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
        'ES': 'Southeast', 'MG': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
        'PR': 'South', 'RS': 'South', 'SC': 'South'
    }
    
    # Handle both data formats with consistent data structure
    region_coverage = {}
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        for crop, crop_info in crop_coverage.items():
            regions = crop_info.get("regions", [])
            first_crop_years = crop_info.get("first_crop_years", {})
            second_crop_years = crop_info.get("second_crop_years", {})
            
            for state in regions:
                state_acronym = get_state_acronym(state)
                region = region_mapping.get(state_acronym, 'Unknown')
                
                if region not in region_coverage:
                    region_coverage[region] = {'years': set(), 'crops': set(), 'states': set()}
                
                region_coverage[region]['states'].add(state_acronym)
                region_coverage[region]['crops'].add(crop)
                
                # Add years from both semesters
                for year_dict in [first_crop_years, second_crop_years]:
                    if state in year_dict:
                        for year_range in year_dict[state]:
                            start_year = int(year_range.split('-')[0])
                            end_year = int(year_range.split('-')[1])
                            for year in range(start_year, end_year + 1):
                                region_coverage[region]['years'].add(year)
    
    elif 'crop_calendar' in conab_data:
        crop_calendar = conab_data['crop_calendar']
        
        for crop_name, crop_data in crop_calendar.items():
            for state_info in crop_data:
                # Get state name correctly - state_name or state, not region
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                state_acronym = get_state_acronym(state)
                region = region_mapping.get(state_acronym, 'Unknown')
                calendar = state_info.get('calendar', {})
                
                if region not in region_coverage:
                    region_coverage[region] = {'total_activities': 0, 'crops': set(), 'states': set()}
                
                region_coverage[region]['states'].add(state_acronym)
                region_coverage[region]['crops'].add(crop_name)
                
                active_months = sum(1 for month, activity in calendar.items() 
                                 if activity and activity.strip())
                
                region_coverage[region]['total_activities'] += active_months
    
    else:
        return go.Figure().update_layout(title="Spatial Coverage by Region (No compatible data format)")
    
    if not region_coverage:
        return go.Figure().update_layout(title="Spatial Coverage by Region (No coverage data)")
    
    # IMPROVED: Calculate coverage percentages using consistent data structure
    regions = []
    coverages = []
    
    if "CONAB Crop Monitoring Initiative" in conab_data:
        # For CONAB initiative, use temporal coverage
        total_years = 24
        for region, data in region_coverage.items():
            coverage_percent = (len(data['years']) / total_years) * 100
            regions.append(region)
            coverages.append(coverage_percent)
    else:
        # For crop calendar, use improved activity-based calculation
        if region_coverage:
            max_total_activities = max(data['total_activities'] for data in region_coverage.values()) if region_coverage else 1
            max_crops = max(len(data['crops']) for data in region_coverage.values()) if region_coverage else 1
            max_states = max(len(data['states']) for data in region_coverage.values()) if region_coverage else 1
            
            for region, data in region_coverage.items():
                # Combine multiple factors for more nuanced coverage calculation
                activity_factor = (data['total_activities'] / max_total_activities) * 50 if max_total_activities > 0 else 0  # 50% weight
                crop_factor = (len(data['crops']) / max_crops) * 30 if max_crops > 0 else 0  # 30% weight  
                state_factor = (len(data['states']) / max_states) * 20 if max_states > 0 else 0  # 20% weight
                
                coverage_percent = activity_factor + crop_factor + state_factor
                regions.append(region)
                coverages.append(coverage_percent)
    
    # Sort by coverage percentage
    sorted_data = sorted(zip(regions, coverages), key=lambda x: x[1], reverse=True)
    regions, coverages = zip(*sorted_data)
    
    # Apply regional colors
    colors = []
    for region in regions:
        colors.append(get_region_color(region, use_dark=True))
    
    # Create figure with modern styling and regional colors
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=coverages,
        y=regions,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.8)', width=2),
            opacity=0.8
        ),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        textfont=dict(size=14, color='#2C3E50', family='Arial, sans-serif'),
        hovertemplate="<b>%{y} Region</b><br>Coverage: %{x:.1f}%<br><extra></extra>",
        name="Coverage"
    ))
    
    # Update layout with modern styling
    fig.update_layout(
        title=dict(
            text="Agricultural data availability by Brazilian Regions Coverage",
            font=dict(size=15, color='#2C3E50', family='Arial, sans-serif'),
            x=0.0
        ),
        xaxis_title="Coverage (%)",
        yaxis_title="Region",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial, sans-serif', size=12, color='#2C3E50'),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            zeroline=False,
            range=[0, max(coverages) * 1.1] if coverages else [0, 100]
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=False,
            zeroline=False
        ),
        margin=dict(l=120, r=100, t=80, b=60)
    )
    
    return fig


# Legacy function for backward compatibility
def plot_conab_spatial_coverage(conab_data: Dict[str, Any]) -> go.Figure:
    """Legacy function - defaults to state view"""
    return plot_conab_spatial_coverage_by_state(conab_data)