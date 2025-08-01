"""
Temporal Coverage Analysis Component
==================================

Advanced component for comprehensive temporal coverage analysis of LULC initiatives.
Features evolution trends, coverage heatmaps, and temporal statistics with modern visualizations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.components.shared.chart_core import get_chart_colors


def render_coverage_matrix_heatmap(temporal_data: pd.DataFrame, metadata: dict) -> None:
    """
    Render comprehensive temporal coverage analysis with modern visualizations.
    
    Args:
        temporal_data: DataFrame with processed temporal data
        metadata: Dictionary of initiative metadata
    """
    st.markdown("### 🗓️ Temporal Coverage Analysis")
    st.markdown("*Comprehensive analysis of data availability across time and initiatives*")
    
    # Tab-based navigation for different temporal views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Evolution Trends", 
        "🗓️ Coverage Matrix", 
        "📊 Coverage Statistics",
        "⏱️ Timeline Analysis"
    ])

    # --- Evolution Trends Tab ---
    with tab1:
        render_evolution_trends(metadata)

    # --- Coverage Matrix Tab ---
    with tab2:
        render_coverage_heatmap(metadata)
    
    # --- Coverage Statistics Tab ---
    with tab3:
        render_coverage_statistics(metadata)
    
    # --- Timeline Analysis Tab ---
    with tab4:
        render_timeline_analysis(metadata)


def render_evolution_trends(metadata: dict) -> None:
    """Render initiative evolution trends over time."""
    st.markdown("#### 📈 Initiative Evolution Over Time")
    
    # Extract all years and count initiatives per year
    all_years = set()
    initiative_years = {}
    
    for name, details in metadata.items():
        available_years = details.get("available_years", [])
        if available_years:
            years = [int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()]
        else:
            years_data = details.get("years", {})
            years = [int(y) for y in years_data.keys() if str(y).isdigit()]
        
        if years:
            all_years.update(years)
            initiative_years[name] = years
    
    if not all_years:
        st.info("No temporal data available for evolution analysis.")
        return
    
    years_sorted = sorted(all_years)
    
    # Count cumulative initiatives and new initiatives per year
    cumulative_count = []
    new_count = []
    active_count = []
    
    for year in years_sorted:
        # Cumulative: total initiatives that have data up to this year
        cumulative = sum(1 for years in initiative_years.values() if min(years) <= year)
        
        # New: initiatives that started in this year
        new = sum(1 for years in initiative_years.values() if min(years) == year)
        
        # Active: initiatives that have data for this specific year
        active = sum(1 for years in initiative_years.values() if year in years)
        
        cumulative_count.append(cumulative)
        new_count.append(new)
        active_count.append(active)
    
    # Create evolution chart
    fig = go.Figure()
    
    # Add cumulative line
    fig.add_trace(go.Scatter(
        x=years_sorted,
        y=cumulative_count,
        mode='lines+markers',
        name='Cumulative Initiatives',
        line=dict(color='#2563eb', width=3),
        marker=dict(size=8),
        fill='tonexty' if len(fig.data) > 0 else 'tozeroy',
        fillcolor='rgba(37, 99, 235, 0.1)'
    ))
    
    # Add active initiatives line
    fig.add_trace(go.Scatter(
        x=years_sorted,
        y=active_count,
        mode='lines+markers',
        name='Active Initiatives',
        line=dict(color='#10b981', width=3),
        marker=dict(size=6)
    ))
    
    # Add new initiatives bar
    fig.add_trace(go.Bar(
        x=years_sorted,
        y=new_count,
        name='New Initiatives',
        marker_color='#f59e0b',
        opacity=0.7,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>LULC Initiative Evolution (1984-2024)</b><br><span style='font-size:14px;color:#6b7280'>Growth and activity patterns over 40 years</span>",
            x=0.5,
            font=dict(size=18, family="Inter", color="#1f2937")
        ),
        xaxis=dict(
            title="<b>Year</b>",
            tickfont=dict(size=11, family="Inter", color="#6b7280"),
            showgrid=True,
            gridcolor='rgba(156,163,175,0.2)'
        ),
        yaxis=dict(
            title="<b>Cumulative & Active Initiatives</b>",
            side='left',
            tickfont=dict(size=11, family="Inter", color="#4b5563"),
            showgrid=True,
            gridcolor='rgba(156,163,175,0.2)'
        ),
        yaxis2=dict(
            title="<b>New Initiatives</b>",
            side='right',
            overlaying='y',
            tickfont=dict(size=11, family="Inter", color="#4b5563"),
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter", size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Evolution summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Years", len(years_sorted), f"{max(years_sorted) - min(years_sorted)} year span")
    with col2:
        peak_year = years_sorted[cumulative_count.index(max(cumulative_count))]
        st.metric("Peak Year", peak_year, f"{max(cumulative_count)} initiatives")
    with col3:
        avg_new = sum(new_count) / len(new_count)
        st.metric("Avg New/Year", f"{avg_new:.1f}", "initiatives")
    with col4:
        recent_growth = cumulative_count[-1] - cumulative_count[0] if len(cumulative_count) > 1 else 0
        st.metric("Total Growth", recent_growth, "initiatives")


def render_coverage_heatmap(metadata: dict) -> None:
    """Render modern coverage heatmap with proper scaling."""
    st.markdown("#### 🗓️ Temporal Coverage Matrix")
    
    # Extract temporal data
    all_years = set()
    for details in metadata.values():
        available_years = details.get("available_years", [])
        if available_years:
            all_years.update([int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()])
        else:
            years_data = details.get("years", {})
            if years_data:
                all_years.update([int(y) for y in years_data.keys() if str(y).isdigit()])
    
    if not all_years:
        st.info("No temporal data available for coverage matrix.")
        return
    
    years_sorted = sorted(all_years)
    initiatives = []
    matrix = []
    initiative_metadata = []
    
    # Build enhanced coverage matrix
    for name, details in metadata.items():
        display_name = details.get('display_name', name)
        available_years = details.get("available_years", [])
        if available_years:
            years_set = set(int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit())
        else:
            years_data = details.get("years", {})
            years_set = set(int(y) for y in years_data.keys() if str(y).isdigit())
        
        if years_set:  # Only include initiatives with temporal data
            row = []
            for year in years_sorted:
                row.append(1 if year in years_set else 0)
            
            initiatives.append(display_name[:35] + "..." if len(display_name) > 35 else display_name)
            matrix.append(row)
            initiative_metadata.append({
                'name': name,
                'start_year': min(years_set),
                'end_year': max(years_set),
                'coverage_years': len(years_set),
                'coverage_ratio': len(years_set) / len(years_sorted)
            })
    
    if not matrix:
        st.info("No coverage data available for visualization.")
        return
    
    # Create enhanced heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=years_sorted,
        y=initiatives,
        colorscale=[
            [0, '#f8fafc'],      # Light gray for no data
            [0.5, '#93c5fd'],    # Light blue for partial coverage
            [1, '#1d4ed8']       # Deep blue for full coverage
        ],
        showscale=True,
        colorbar=dict(
            title=dict(
                text="<b>Data<br>Available</b>",
                font=dict(size=12, family="Inter")
            ),
            tickvals=[0, 0.5, 1],
            ticktext=["No Data", "Partial", "Available"],
            tickfont=dict(size=10, family="Inter"),
            len=0.8
        ),
        hovertemplate="<b>%{y}</b><br>Year: <b>%{x}</b><br>Data: <b>%{customdata}</b><extra></extra>",
        customdata=[["Available" if cell == 1 else "Not Available" for cell in row] for row in matrix]
    ))
    
    fig.update_layout(
        height=max(600, len(initiatives) * 25),
        title=dict(
            text="<b>Temporal Coverage Matrix (1984-2024)</b><br><span style='font-size:14px;color:#6b7280'>40 years of LULC data availability</span>",
            x=0.5,
            font=dict(size=18, family="Inter", color="#1f2937")
        ),
        xaxis=dict(
            title="<b>Year</b>",
            tickfont=dict(size=10, family="Inter", color="#6b7280"),
            showgrid=False,
            dtick=5,  # Show every 5th year for clarity
            tickangle=-45
        ),
        yaxis=dict(
            title="<b>Initiative</b>",
            tickfont=dict(size=9, family="Inter", color="#4b5563"),
            showgrid=False,
            automargin=True
        ),
        margin=dict(l=250, r=100, t=100, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter", size=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_coverage_statistics(metadata: dict) -> None:
    """Render detailed coverage statistics."""
    st.markdown("#### 📊 Coverage Statistics Analysis")
    
    # Calculate coverage statistics
    stats_data = []
    all_years = set()
    
    for name, details in metadata.items():
        display_name = details.get('display_name', name)
        available_years = details.get("available_years", [])
        if available_years:
            years = [int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()]
        else:
            years_data = details.get("years", {})
            years = [int(y) for y in years_data.keys() if str(y).isdigit()]
        
        if years:
            all_years.update(years)
            stats_data.append({
                'Initiative': display_name,
                'Start Year': min(years),
                'End Year': max(years),
                'Duration': max(years) - min(years) + 1,
                'Coverage Years': len(years),
                'Coverage Ratio': len(years) / (max(years) - min(years) + 1) if len(years) > 0 else 0
            })
    
    if not stats_data:
        st.info("No statistics data available.")
        return
    
    stats_df = pd.DataFrame(stats_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Duration analysis
        fig_duration = px.histogram(
            stats_df,
            x="Duration",
            nbins=15,
            title="<b>Initiative Duration Distribution</b>",
            labels={"Duration": "Duration (Years)", "count": "Number of Initiatives"},
            color_discrete_sequence=['#3b82f6']
        )
        fig_duration.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            showlegend=False
        )
        st.plotly_chart(fig_duration, use_container_width=True)
    
    with col2:
        # Coverage ratio analysis
        fig_coverage = px.box(
            stats_df,
            y="Coverage Ratio",
            title="<b>Coverage Ratio Distribution</b>",
            labels={"Coverage Ratio": "Coverage Ratio (0-1)"},
            color_discrete_sequence=['#10b981']
        )
        fig_coverage.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            showlegend=False
        )
        st.plotly_chart(fig_coverage, use_container_width=True)
    
    # Detailed statistics table
    st.markdown("##### 📋 Detailed Coverage Statistics")
    
    # Sort by coverage years descending
    stats_df_display = stats_df.sort_values('Coverage Years', ascending=False)
    st.dataframe(stats_df_display, use_container_width=True, hide_index=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_duration = stats_df['Duration'].mean()
        st.metric("Avg Duration", f"{avg_duration:.1f} years")
    with col2:
        avg_coverage = stats_df['Coverage Ratio'].mean()
        st.metric("Avg Coverage", f"{avg_coverage:.1%}")
    with col3:
        longest_initiative = stats_df.loc[stats_df['Duration'].idxmax(), 'Initiative']
        st.metric("Longest Initiative", longest_initiative[:20] + "..." if len(longest_initiative) > 20 else longest_initiative)
    with col4:
        total_span = max(all_years) - min(all_years) + 1 if all_years else 0
        st.metric("Total Time Span", f"{total_span} years")


def render_timeline_analysis(metadata: dict) -> None:
    """Render timeline analysis with decades view."""
    st.markdown("#### ⏱️ Timeline Analysis by Decades")
    
    # Categorize initiatives by decades
    decade_data = {}
    
    for name, details in metadata.items():
        display_name = details.get('display_name', name)
        available_years = details.get("available_years", [])
        if available_years:
            years = [int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()]
        else:
            years_data = details.get("years", {})
            years = [int(y) for y in years_data.keys() if str(y).isdigit()]
        
        if years:
            start_year = min(years)
            decade = (start_year // 10) * 10
            decade_label = f"{decade}s"
            
            if decade_label not in decade_data:
                decade_data[decade_label] = []
            
            decade_data[decade_label].append({
                'Initiative': display_name,
                'Start Year': start_year,
                'Years Count': len(years)
            })
    
    if not decade_data:
        st.info("No timeline data available.")
        return
    
    # Create decade visualization
    decade_counts = {decade: len(initiatives) for decade, initiatives in decade_data.items()}
    
    fig = px.bar(
        x=list(decade_counts.keys()),
        y=list(decade_counts.values()),
        title="<b>Initiative Launches by Decade</b>",
        labels={"x": "Decade", "y": "Number of Initiatives Launched"},
        color=list(decade_counts.values()),
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=16, family="Inter", color="#1f2937"),
        showlegend=False,
        xaxis_title="<b>Decade</b>",
        yaxis_title="<b>Number of New Initiatives</b>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Decade breakdown
    for decade in sorted(decade_data.keys()):
        with st.expander(f"📅 {decade} Details ({len(decade_data[decade])} initiatives)"):
            decade_df = pd.DataFrame(decade_data[decade])
            decade_df = decade_df.sort_values('Start Year')
            st.dataframe(decade_df, use_container_width=True, hide_index=True)
