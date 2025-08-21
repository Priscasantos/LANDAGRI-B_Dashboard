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



def render_coverage_matrix_heatmap(temporal_data: pd.DataFrame, metadata: dict) -> None:
    """
    Render comprehensive temporal coverage analysis with modern visualizations.
    
    Args:
        temporal_data: DataFrame with processed temporal data
        metadata: Dictionary of initiative metadata
    """
    st.markdown("### 🗓️ Temporal Coverage Analysis")
    st.markdown("*Comprehensive analysis of data availability across time and initiatives.*")
    
    # Tab-based navigation for different temporal views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Evolution Trends", 
        "🗓️ Coverage Availability", 
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
    """Simplified temporal coverage view: horizontal timeline per initiative with gaps preserved.
    Keeps a consistent (larger) height and a clean visual — not a matrix."""
    st.markdown("#### 🗓️ Temporal Coverage Availability")


    # Collect years and initiatives
    all_years = set()
    initiatives_raw = []

    for name, details in metadata.items():
        display_name = details.get('display_name', name)
        available_years = details.get("available_years", [])
        if available_years:
            years_set = {int(y) for y in available_years if isinstance(y, (int, str)) and str(y).isdigit()}
        else:
            years_data = details.get("years", {})
            years_set = {int(y) for y in years_data.keys() if str(y).isdigit()}

        if not years_set:
            continue

        all_years.update(years_set)
        initiatives_raw.append({
            "name": display_name,
            "short_name": display_name if len(display_name) <= 60 else display_name[:57] + "...",
            "years": years_set,
            "start": min(years_set),
            "coverage": len(years_set)
        })

    if not all_years or not initiatives_raw:
        st.info("No temporal data available for coverage view.")
        return

    years_sorted = sorted(all_years)

    # Sort initiatives: newest start first, then by coverage desc
    initiatives_sorted = sorted(initiatives_raw, key=lambda i: (i["start"], -i["coverage"]), reverse=True)
    initiative_names = [i["short_name"] for i in initiatives_sorted]

    # Build traces: one horizontal trace per initiative using full year axis with None for gaps
    fig = go.Figure()
    color = "#2563eb"
    for idx, inst in enumerate(initiatives_sorted):
        x_vals = []
        y_vals = []
        hover_texts = []
        for y in years_sorted:
            if y in inst["years"]:
                x_vals.append(y)
                y_vals.append(idx)
                hover_texts.append(f"<b>{inst['short_name']}</b><br>Year: {y}")
            else:
                # None breaks the line (preserves gaps/continuity)
                x_vals.append(None)
                y_vals.append(None)
                hover_texts.append(None)

        fig.add_trace(go.Scattergl(
            x=x_vals,
            y=y_vals,
            mode='lines+markers',
            name=inst['short_name'],
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            hoverinfo='text',
            hovertext=hover_texts,
            connectgaps=False,
            showlegend=False
        ))

    # Fixed larger height (consistent)
    fixed_height = 900

    fig.update_xaxes(
        title_text="<b>Year</b>",
        tickmode="array",
        tickvals=years_sorted,
        ticktext=[str(y) for y in years_sorted],
        tickangle=45,
        tickfont=dict(size=11, family="Inter", color="#374151"),
        showgrid=True,
        gridcolor='rgba(203,213,225,0.3)'
    )

    fig.update_yaxes(
        title_text="<b>Initiative</b>",
        tickmode="array",
        tickvals=list(range(len(initiative_names))),
        ticktext=initiative_names,
        tickfont=dict(size=11, family="Inter", color="#111827"),
        autorange="reversed",
        automargin=True,
        showgrid=False
    )

    fig.update_layout(
        title=dict(
        text="<b>Year-by-Year Availability (Simplified Line View)</b><br><span style='font-size:12px;color:#6b7280'>Lines show continuity; gaps interrupt the line</span>",
            x=0.5,
            font=dict(family="Inter", size=14, color="#111827")
        ),
        template="plotly_white",
        margin=dict(l=260, r=80, t=100, b=120),
        height=fixed_height,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
        font=dict(family="Inter", size=11, color="#111827")
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
    
    # Create decade visualization using a tidy DataFrame (ensures stable ordering and proper colorbar)
    decade_counts = {decade: len(initiatives) for decade, initiatives in decade_data.items()}

    # Build a DataFrame and sort decades numerically (e.g., '1990s' -> 1990)
    def _decade_key(label: str) -> int:
        try:
            return int(str(label).rstrip('s'))
        except Exception:
            return 0

    decade_items = sorted(decade_counts.items(), key=lambda kv: _decade_key(kv[0]))
    decade_df = pd.DataFrame(decade_items, columns=["Decade", "Count"])
    category_order = decade_df["Decade"].tolist()

    fig = px.bar(
        decade_df,
        x="Decade",
        y="Count",
        title="<b>Initiative Launches by Decade</b>",
        labels={"Decade": "Decade", "Count": "Number of Initiatives Launched"},
        color="Count",
        color_continuous_scale="Viridis",
        category_orders={"Decade": category_order}
    )

    fig.update_layout(
        font={"family": "Inter", "size": 12},
        title_font={"size": 16, "family": "Inter", "color": "#1f2937"},
        xaxis_title="<b>Decade</b>",
        yaxis_title="<b>Number of New Initiatives</b>",
        margin={"t": 100},
        # Configure colorbar directly in layout to avoid update_traces conflicts
        coloraxis_colorbar={
            "title": {"text": "Quantity of Initiatives", "side": "top"},
            "tickmode": "linear",
            "showticklabels": True
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Decade breakdown
    for decade in sorted(decade_data.keys()):
        with st.expander(f"📅 {decade} Details ({len(decade_data[decade])} initiatives)"):
            decade_df = pd.DataFrame(decade_data[decade])
            decade_df = decade_df.sort_values('Start Year')
            st.dataframe(decade_df, use_container_width=True, hide_index=True)
