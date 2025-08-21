"""
Timeline Component - Temporal Analysis (Modern Implementation)
=============================================================

Modern component for rendering timeline with points, clean layout and year cap 1985-2024.
Based on advanced plot_timeline_chart function, adapted for modular structure.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


def render_timeline_tab(temporal_data: pd.DataFrame, metadata: dict) -> None:
    """
    Render timeline tab with complete temporal analysis and modern layout.
    
    Args:
        temporal_data: DataFrame with processed temporal data
        metadata: Dictionary of initiative metadata
    """
    st.markdown("#### 📊 LULC Initiatives Timeline")
    st.markdown("*Timeline overview of initiatives by year, showing temporal coverage and gaps for the 1985-2024 period.*")

    if temporal_data.empty or not metadata:
        st.warning("⚠️ No temporal data available for analysis.")
        return
    
    # Timeline controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_gaps = st.checkbox(
            "Show temporal gaps",
            value=True,
            help="Highlight years without data with red markers"
        )
    
    with col2:
        group_by_type = st.checkbox(
            "Group by methodology",
            value=False,
            help="Prefix initiatives with their methodology"
        )

    with col3:
        show_connections = st.checkbox(
            "Connect points",
            value=True,
            help="Show lines connecting years for each initiative"
        )
    
    # Generate modern timeline chart
    fig_timeline = plot_timeline_chart(metadata, temporal_data, show_gaps, group_by_type, show_connections)
    
    if fig_timeline:
        st.plotly_chart(fig_timeline, use_container_width=True, key="temporal_timeline_chart")
        
        # Timeline statistics
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        # Calculate statistics
        total_initiatives = len([name for name, details in metadata.items() 
                               if details.get("available_years", [])])
        
        all_years = set()
        for details in metadata.values():
            available_years = details.get("available_years", [])
            if available_years:
                all_years.update([y for y in available_years if 1985 <= y <= 2024])
        
        with stats_col1:
            st.metric("Initiatives with data", total_initiatives)
        
        with stats_col2:
            st.metric("Period covered", f"{min(all_years) if all_years else '-'} - {max(all_years) if all_years else '-'}")
        
        with stats_col3:
            st.metric("Unique years", len(all_years))
        
    else:
        st.error("❌ Error generating timeline chart.")


@smart_cache_data(ttl=300)
def plot_timeline_chart(
    metadata: dict, 
    temporal_data: pd.DataFrame, 
    show_gaps: bool = True,
    group_by_type: bool = False,
    show_connections: bool = True
) -> go.Figure:
    """
    Create modern timeline chart of LULC initiatives using points.
    
    Args:
        metadata: Dictionary of initiative metadata
        temporal_data: DataFrame with temporal data
        show_gaps: Whether to show temporal gaps
        group_by_type: Whether to group by type/methodology
        show_connections: Whether to connect points with lines
        
    Returns:
        Plotly Figure with modern timeline using points
    """
    if not metadata or temporal_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No temporal data available for timeline",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#6b7280", family="Inter, -apple-system, BlinkMacSystemFont, sans-serif")
        )
        return fig

    # Prepare timeline data
    timeline_data = []
    colors = get_chart_colors()
    
    # Year cap: 1985-2024
    MIN_YEAR, MAX_YEAR = 1985, 2024
    
    for i, (name, details) in enumerate(metadata.items()):
        try:
            # Extract temporal data - use 'available_years' which is the correct structure
            available_years = details.get("available_years", [])
            if not available_years:
                # Try other possible fields as fallback
                years_data = details.get("years", {})
                if years_data:
                    # If 'years' exists as dict, extract keys
                    all_years = []
                    for year in years_data.keys():
                        if isinstance(year, int):
                            all_years.append(year)
                        elif isinstance(year, str) and year.isdigit():
                            all_years.append(int(year))
                else:
                    continue  # No logs to avoid polluting interface
            else:
                # 'available_years' is a list of integers
                all_years = [int(year) for year in available_years if isinstance(year, (int, str)) and str(year).isdigit()]
            
            if not all_years:
                continue

            # Apply year cap (1985-2024)
            all_years = [year for year in all_years if MIN_YEAR <= year <= MAX_YEAR]
            if not all_years:
                continue

            start_year = min(all_years)
            end_year = max(all_years)

            # Determine type if available
            initiative_type = details.get("methodology", details.get("type", "Unknown"))
            coverage = details.get("coverage", "N/A")
            
            if group_by_type:
                display_name = f"[{initiative_type}] {name[:25]}"
            else:
                display_name = name[:35]
            
            timeline_data.append({
                "Initiative": display_name,
                "Start": start_year,
                "End": end_year,
                "Duration": end_year - start_year + 1,
                "Type": initiative_type,
                "Coverage": coverage,
                "Color": colors[i % len(colors)],
                "Years_Available": len(all_years),
                "All_Years": sorted(all_years),
                "Coverage_Text": f"{len(all_years)}/{end_year - start_year + 1} years"
            })
            
        except (ValueError, KeyError, AttributeError):
            continue
    
    if not timeline_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No initiatives with valid temporal data (1985-2024)",
            xref="paper",
            yref="paper", 
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#6b7280", family="Inter, -apple-system, BlinkMacSystemFont, sans-serif")
        )
        return fig
    
    # Sort by coverage and then by start date
    coverage_order = {'Global': 0, 'Regional': 1, 'National': 2, 'N/A': 3}
    timeline_data.sort(key=lambda x: (coverage_order.get(x["Coverage"], 3), x["Start"]))
    
    # Create figure with modern layout
    fig = go.Figure()
    
    # Add points for each available year
    for i, item in enumerate(timeline_data):
        # Add points for available years
        fig.add_trace(go.Scatter(
            x=item["All_Years"],
            y=[item["Initiative"]] * len(item["All_Years"]),
            mode='markers',
            marker=dict(
                color=item["Color"],
                size=12,
                symbol='circle',
                line=dict(width=2, color='white'),
                opacity=0.85
            ),
            name=item["Initiative"],
            hovertemplate=f"<b>{item['Initiative']}</b><br>" +
                         f"<b>Year:</b> %{{x}}<br>" +
                         f"<b>Period:</b> {item['Start']} - {item['End']}<br>" +
                         f"<b>Coverage:</b> {item['Coverage_Text']}<br>" +
                         f"<b>Methodology:</b> {item['Type']}<br>" +
                         f"<b>Scope:</b> {item['Coverage']}<extra></extra>",
            showlegend=False
        ))
        
        # Add connecting lines if requested
        if show_connections and len(item["All_Years"]) > 1:
            fig.add_trace(go.Scatter(
                x=[item["Start"], item["End"]],
                y=[item["Initiative"], item["Initiative"]],
                mode='lines',
                line=dict(
                    color=item["Color"],
                    width=3,
                    dash='solid'
                ),
                opacity=0.5,
                hoverinfo='skip',
                showlegend=False
            ))
        
        # Add gaps if requested
        if show_gaps and item["Years_Available"] < item["Duration"]:
            # Create list of missing years
            full_range = set(range(item["Start"], item["End"] + 1))
            missing_years = list(full_range - set(item["All_Years"]))
            
            if missing_years:
                fig.add_trace(go.Scatter(
                    x=missing_years,
                    y=[item["Initiative"]] * len(missing_years),
                    mode='markers',
                    marker=dict(
                        color='rgba(239,68,68,0.8)',
                        size=8,
                        symbol='x',
                        line=dict(width=2, color='#dc2626')
                    ),
                    name=f"Gaps - {item['Initiative']}",
                    hovertemplate=f"<b>Temporal Gap</b><br>" +
                                 f"<b>Missing year:</b> %{{x}}<br>" +
                                 f"<b>Initiative:</b> {item['Initiative']}<extra></extra>",
                    showlegend=False
                ))
    
    # Modern and responsive layout with improved typography
    fig.update_layout(
        title=dict(
            text=f"<b>LULC Initiatives Timeline</b><br><span style='font-size:14px;color:#6b7280'>{len(timeline_data)} initiatives • {MIN_YEAR}-{MAX_YEAR}</span>",
            x=0.5,
            font=dict(size=20, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#1f2937"),
            pad=dict(b=30)
        ),
        xaxis=dict(
            title=dict(
                text="<b>Year</b>",
                font=dict(size=14, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#374151")
            ),
            range=[MIN_YEAR - 1, MAX_YEAR + 1],
            tickmode='linear',
            tick0=MIN_YEAR,
            dtick=5,
            tickangle=-45,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(156,163,175,0.2)',
            showline=True,
            linewidth=2,
            linecolor='#d1d5db',
            tickfont=dict(size=11, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#6b7280"),
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="<b>Initiatives</b>",
                font=dict(size=14, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#374151")
            ),
            autorange="reversed",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(156,163,175,0.2)',
            showline=True,
            linewidth=2,
            linecolor='#d1d5db',
            tickfont=dict(size=10, family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#4b5563"),
            zeroline=False
        ),
        height=max(520, len(timeline_data) * 32),
        plot_bgcolor='rgba(249,250,251,0.9)',  # Light gray background
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(l=280, r=80, t=120, b=100),
        hovermode='closest',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=11, color="#374151")
    )
    
    # Add enhanced legend/annotation with better styling
    legend_text = f"<b>Legend:</b> ● Data points | ✕ Temporal gaps | Coverage: {MIN_YEAR}-{MAX_YEAR}"
    fig.add_annotation(
        text=legend_text,
        xref="paper",
        yref="paper",
        x=0.02,
        y=-0.08,
        showarrow=False,
        font=dict(size=12, color="#6b7280", family="Inter, -apple-system, BlinkMacSystemFont, sans-serif"),
        align="left",
        bgcolor="rgba(249,250,251,0.9)",
        bordercolor="#e5e7eb",
        borderwidth=1,
        borderpad=8
    )
    
    # Add coverage statistics annotation
    coverage_stats = {}
    for item in timeline_data:
        coverage = item["Coverage"]
        if coverage not in coverage_stats:
            coverage_stats[coverage] = 0
        coverage_stats[coverage] += 1
    
    coverage_text = " | ".join([f"{k}: {v}" for k, v in sorted(coverage_stats.items())])
    fig.add_annotation(
        text=f"<b>Coverage Distribution:</b> {coverage_text}",
        xref="paper",
        yref="paper",
        x=0.98,
        y=-0.08,
        showarrow=False,
        font=dict(size=12, color="#6b7280", family="Inter, -apple-system, BlinkMacSystemFont, sans-serif"),
        align="right",
        bgcolor="rgba(249,250,251,0.9)",
        bordercolor="#e5e7eb",
        borderwidth=1,
        borderpad=8
    )
    
    return fig
