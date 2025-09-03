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

def plot_conab_spatial_coverage_by_state(
    conab_data: Dict[str, Any],
    region_mapping: Dict[str, str] | None = None,
    total_years: int = 24,
    weights: Dict[str, int] | None = None
) -> go.Figure:
    """
    Simplified state-level spatial coverage chart.
    - Keeps legend (one entry per region).
    - Colors states by region.
    - Avoids hardcoded layout details by exposing mapping, weights and total_years.
    - Legend and Y axis are sorted alphabetically.
    """
    if not conab_data:
        return go.Figure().update_layout(title="Spatial Coverage by State (No data available)")

    # Default region mapping (can be overridden by caller)
    if region_mapping is None:
        region_mapping = {
            'AC': 'North', 'AP': 'North', 'AM': 'North', 'PA': 'North', 'RO': 'North', 'RR': 'North', 'TO': 'North',
            'AL': 'Northeast', 'BA': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast', 'PB': 'Northeast',
            'PE': 'Northeast', 'PI': 'Northeast', 'RN': 'Northeast', 'SE': 'Northeast',
            'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
            'ES': 'Southeast', 'MG': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
            'PR': 'South', 'RS': 'South', 'SC': 'South'
        }

    # Default weights (activity, crop count, active months)
    if weights is None:
        weights = {'activity': 60, 'crop': 30, 'density': 10}

    state_coverage: Dict[str, Any] = {}

    # Normalize both supported input formats into state_coverage
    if "CONAB Crop Monitoring Initiative" in conab_data:
        initiative = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crops_info = initiative.get("detailed_crop_coverage", {})
        for crop, info in crops_info.items():
            regions = info.get("regions", [])
            for sem in ("first_crop_years", "second_crop_years"):
                sem_dict = info.get(sem, {})
                for state in regions:
                    st = get_state_acronym(state)
                    state_coverage.setdefault(st, set())
                    if state in sem_dict:
                        for yr_range in sem_dict[state]:
                            start, end = (int(x) for x in yr_range.split('-'))
                            state_coverage[st].update(range(start, end + 1))
    elif 'crop_calendar' in conab_data:
        crop_calendar = conab_data['crop_calendar']
        for crop_name, crop_states in crop_calendar.items():
            for state_info in crop_states:
                state = state_info.get('state_name', state_info.get('state', 'Unknown'))
                st = get_state_acronym(state)
                cal = state_info.get('calendar', {})
                entry = state_coverage.setdefault(st, {'total_activities': 0, 'active_months': 0, 'crops': set()})
                active_months_this = 0
                total_acts_this = 0
                for _, activity in cal.items():
                    if activity and activity.strip():
                        active_months_this += 1
                        total_acts_this += 1
                        if activity.strip() == 'PH':
                            total_acts_this += 1
                if total_acts_this > 0:
                    entry['crops'].add(crop_name)
                    entry['total_activities'] += total_acts_this
    else:
        return go.Figure().update_layout(title="Spatial Coverage by State (No compatible data format)")

    if not state_coverage:
        return go.Figure().update_layout(title="Spatial Coverage by State (No coverage data)")

    # Compute coverage percentages
    states: list[str] = []
    coverages: list[float] = []

    if "CONAB Crop Monitoring Initiative" in conab_data:
        for st, years in state_coverage.items():
            pct = (len(years) / total_years) * 100 if total_years > 0 else 0
            states.append(st)
            coverages.append(pct)
    else:
        max_acts = max((v['total_activities'] for v in state_coverage.values()), default=1)
        max_crops = max((len(v['crops']) for v in state_coverage.values()), default=1)
        max_months = max((v['active_months'] for v in state_coverage.values()), default=1)

        for st, v in state_coverage.items():
            a = (v['total_activities'] / max_acts) * weights['activity'] if max_acts else 0
            c = (len(v['crops']) / max_crops) * weights['crop'] if max_crops else 0
            d = (v['active_months'] / max_months) * weights['density'] if max_months else 0
            states.append(st)
            coverages.append(a + c + d)

    # Sort descending
    sorted_pairs = sorted(zip(states, coverages), key=lambda x: x[1], reverse=True)
    states, coverages = zip(*sorted_pairs)

    # Colors per state by region, and collect region-to-color map
    colors = []
    region_colors: Dict[str, str] = {}
    for st in states:
        region = region_mapping.get(st, 'Unknown')
        color = get_region_color(region, use_dark=True)
        colors.append(color)
        region_colors.setdefault(region, color)

    # Build figure: one bar trace with per-bar colors + simple legend entries per region
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(coverages),
        y=list(states),
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<extra></extra>",
        showlegend=False
    ))

    # Add one minimal legend item per region (legendonly traces)
    for region_name, color in region_colors.items():
        fig.add_trace(go.Bar(
            x=[0],
            y=[''],
            marker=dict(color=color),
            name=region_name,
            showlegend=True,
            hoverinfo='none',
            visible='legendonly'
        ))

    # Minimal, non-hardcoded layout — include Y axis title with acronyms
    # Sort region_colors by region name (alphabetical order) for legend
    sorted_region_colors = dict(sorted(region_colors.items(), key=lambda x: x[0]))

    # Remove previous legendonly traces and add them in alphabetical order
    # (Remove all traces except the main bar)
    fig.data = fig.data[:1]
    for region_name, color in sorted_region_colors.items():
        fig.add_trace(go.Bar(
            x=[0],
            y=[''],
            marker=dict(color=color),
            name=region_name,
            showlegend=True,
            hoverinfo='none',
            visible='legendonly'
        ))

    fig.update_layout(
        title="Agricultural data availability by Brazilian States (colored by region)",
        xaxis_title="Coverage (%)",
        yaxis_title="Brazilian States (Acronym)",
        height=min(700, 40 * len(states) + 120),
        showlegend=True,
        legend=dict(title='Region'),
        margin=dict(l=80, r=140, t=80, b=60)
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