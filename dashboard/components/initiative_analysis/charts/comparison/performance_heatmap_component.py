"""
Performance Heatmap Component - Comparison Analysis
==================================================

Advanced component for normalized performance analysis with comprehensive metrics visualization.
Features multi-dimensional performance heatmaps, comparative analysis, and interactive visualizations.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import numpy as np

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout


def _get_scalar_value(value) -> float:
    """Helper function to extract scalar value from pandas Series or other types."""
    if hasattr(value, 'item'):
        return float(value.item())
    elif hasattr(value, 'iloc'):
        return float(value.iloc[0])
    else:
        return float(value)


def render_performance_heatmap_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render comprehensive normalized performance analysis with interactive heatmaps.
    
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    st.markdown("#### 🔥 Normalized Performance Analysis")
    st.markdown("*Comparison of initiatives across normalized performance metrics (scaled 0–1).*")

    if filtered_df.empty:
        st.warning("⚠️ No data available for performance analysis.")
        return
    
    # Tab-based visualization for different performance views
    tab1, tab2, tab3 = st.tabs([
        "🔥 Performance Heatmap", 
        "📊 Metric Comparison", 
        "🎯 Performance Radar"
    ])
    
    with tab1:
        render_normalized_heatmap(filtered_df)
    
    with tab2:
        render_metric_comparison(filtered_df)
    
    with tab3:
        render_performance_radar(filtered_df)


def render_normalized_heatmap(filtered_df: pd.DataFrame) -> None:
    """Render normalized performance heatmap."""
    st.markdown("##### Multi-Dimensional Performance Heatmap")
    
    # Get performance metrics
    performance_data = extract_performance_metrics(filtered_df)
    
    if performance_data.empty:
        st.info("No performance metrics available for heatmap visualization.")
        return
    
    # Create normalized heatmap
    fig = create_performance_heatmap(performance_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance insights
        with st.expander("📊 Performance Insights"):
            render_performance_insights(performance_data)
    else:
        st.error("❌ Error generating performance heatmap.")


def render_metric_comparison(filtered_df: pd.DataFrame) -> None:
    """Render metric comparison charts."""
    st.markdown("##### Performance Metric Comparison")
    
    performance_data = extract_performance_metrics(filtered_df)
    
    if performance_data.empty:
        st.info("No performance metrics available for comparison.")
        return
    
    # Select metrics for comparison
    available_metrics = [col for col in performance_data.columns if col != 'Initiative']
    
    if not available_metrics:
        st.info("No numerical metrics available for comparison.")
        return
    
    selected_metrics = st.multiselect(
        "Select metrics to compare:",
        available_metrics,
        default=available_metrics[:min(4, len(available_metrics))],
        help="Choose up to 4 metrics for comparison"
    )
    
    if not selected_metrics:
        st.warning("Please select at least one metric.")
        return
    
    # Create comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart comparison
        if len(selected_metrics) >= 1:
            metric = selected_metrics[0]
            fig_bar = px.bar(
                performance_data,
                x="Initiative",
                y=metric,
                title=f"<b>{metric} Comparison</b>",
                color=metric,
                color_continuous_scale="RdYlBu_r"
            )
            fig_bar.update_layout(
                font=dict(family="Inter", size=12),
                title_font=dict(size=14, family="Inter", color="#1f2937"),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Scatter plot if multiple metrics
        if len(selected_metrics) >= 2:
            fig_scatter = px.scatter(
                performance_data,
                x=selected_metrics[0],
                y=selected_metrics[1],
                size=selected_metrics[2] if len(selected_metrics) > 2 else None,
                color=selected_metrics[3] if len(selected_metrics) > 3 else selected_metrics[0],
                hover_name="Initiative",
                title=f"<b>{selected_metrics[0]} vs {selected_metrics[1]}</b>",
                color_continuous_scale="Viridis"
            )
            fig_scatter.update_layout(
                font=dict(family="Inter", size=12),
                title_font=dict(size=14, family="Inter", color="#1f2937")
            )
            st.plotly_chart(fig_scatter, use_container_width=True)


def render_performance_radar(filtered_df: pd.DataFrame) -> None:
    """Render performance radar chart with customizable pillars."""
    st.markdown("##### Performance Radar Analysis")
    
    performance_data = extract_performance_metrics(filtered_df)
    
    if performance_data.empty:
        st.info("No performance metrics available for radar analysis.")
        return
    
    # Get available metrics for radar
    available_metrics = [col for col in performance_data.columns if col != 'Initiative']
    
    if len(available_metrics) < 3:
        st.info("Need at least 3 metrics for radar chart analysis.")
        return
    
    # Allow user to customize radar pillars
    st.markdown("**Customize Radar Chart Pillars:**")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_pillars = st.multiselect(
            "Select up to 6 performance pillars:",
            available_metrics,
            default=available_metrics[:min(6, len(available_metrics))],
            max_selections=6
        )
    
    with col2:
        selected_initiatives = st.multiselect(
            "Select initiatives to compare:",
            performance_data['Initiative'].tolist(),
            default=performance_data['Initiative'].tolist()[:min(5, len(performance_data))],
            max_selections=5
        )
    
    if not selected_pillars or not selected_initiatives:
        st.warning("Please select both pillars and initiatives.")
        return
    
    # Create radar chart
    fig_radar = create_performance_radar_chart(
        performance_data, selected_pillars, selected_initiatives
    )
    
    if fig_radar:
        st.plotly_chart(fig_radar, use_container_width=True)


def extract_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and normalize performance metrics from the dataframe."""
    # Common performance columns to look for
    performance_columns = [
        'Global_Accuracy', 'Spatial_Resolution_m', 'Update_Frequency_days',
        'Number_Classes', 'Agricultural_Classes', 'Start_Year', 'End_Year'
    ]
    
    # Find available performance columns
    available_columns = []
    for col in performance_columns:
        if col in df.columns:
            available_columns.append(col)
    
    if not available_columns:
        # Try with common column patterns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['accuracy', 'resolution', 'classes', 'year']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    available_columns.append(col)
    
    if not available_columns:
        return pd.DataFrame()
    
    # Get initiative names
    name_col = 'Display_Name' if 'Display_Name' in df.columns else 'Name'
    if name_col not in df.columns:
        name_col = df.columns[0]
    
    # Create performance dataframe
    performance_data = df[[name_col] + available_columns].copy()
    performance_data = performance_data.rename(columns={name_col: 'Initiative'})
    
    # Clean and normalize data
    for col in available_columns:
        # Handle missing values
        performance_data[col] = pd.to_numeric(performance_data[col], errors='coerce').fillna(0)
        
        # Invert resolution (smaller is better) for normalization
        if 'resolution' in col.lower() and performance_data[col].max() > 0:
            performance_data[col] = 1 / (performance_data[col] + 1)
        
        # Invert update frequency (smaller is better)
        if 'frequency' in col.lower() and performance_data[col].max() > 0:
            performance_data[col] = 1 / (performance_data[col] + 1)
    
    # Normalize all metrics to 0-1 scale
    scaler = MinMaxScaler()
    metrics_columns = [col for col in performance_data.columns if col != 'Initiative']
    
    if metrics_columns:
        performance_data[metrics_columns] = scaler.fit_transform(performance_data[metrics_columns])
    
    return performance_data


@smart_cache_data(ttl=300)
def create_performance_heatmap(performance_data: pd.DataFrame) -> go.Figure | None:
    """
    Create normalized performance heatmap.
    
    Args:
        performance_data: DataFrame with normalized performance metrics
        
    Returns:
        Plotly figure with performance heatmap or None if no data
    """
    if performance_data.empty:
        return None
    
    # Prepare data for heatmap
    metrics_cols = [col for col in performance_data.columns if col != 'Initiative']
    
    if not metrics_cols:
        return None
    
    # Create heatmap data
    z_data = performance_data[metrics_cols].values
    y_labels = performance_data['Initiative'].tolist()
    x_labels = metrics_cols
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, '#ef4444'],      # Red for low performance
            [0.25, '#f97316'],   # Orange for below average
            [0.5, '#eab308'],    # Yellow for average
            [0.75, '#22c55e'],   # Green for good
            [1, '#15803d']       # Dark green for excellent
        ],
        colorbar=dict(
            title=dict(
                text="<b>Normalized<br>Performance</b>",
                font=dict(size=12, family="Inter")
            ),
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["Low", "Below Avg", "Average", "Good", "Excellent"],
            tickfont=dict(size=10, family="Inter")
        ),
        hovertemplate="<b>Initiative:</b> %{y}<br><b>Metric:</b> %{x}<br><b>Score:</b> %{z:.2f}<extra></extra>",
        zmin=0,
        zmax=1
    ))
    
    fig.update_layout(
        title=dict(
            text="<b></b><br><span style='font-size:14px;color:#6b7280'></span>",
            x=0.5,
            font=dict(size=18, family="Inter", color="#1f2937")
        ),
        xaxis=dict(
            title="<b>Performance Metrics</b>",
            tickfont=dict(size=11, family="Inter", color="#6b7280"),
            tickangle=-45
        ),
        yaxis=dict(
            title="<b>Initiatives</b>",
            tickfont=dict(size=10, family="Inter", color="#4b5563")
        ),
        height=max(400, len(y_labels) * 40),
        font=dict(family="Inter", size=11),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_performance_radar_chart(performance_data: pd.DataFrame, pillars: list, initiatives: list) -> go.Figure | None:
    """Create customizable performance radar chart."""
    if performance_data.empty or not pillars or not initiatives:
        return None
    
    # Filter data
    radar_data = performance_data[performance_data['Initiative'].isin(initiatives)]
    
    fig = go.Figure()
    
    colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    for i, initiative in enumerate(initiatives):
        if initiative in radar_data['Initiative'].values:
            values = radar_data[radar_data['Initiative'] == initiative][pillars].values[0]
            # Close the radar by appending first value
            values = np.append(values, values[0])
            pillars_closed = pillars + [pillars[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=pillars_closed,
                fill='toself',
                name=initiative,
                line_color=colors[i % len(colors)],
                fillcolor=colors[i % len(colors)],
                opacity=0.3
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10, family="Inter")
            ),
            angularaxis=dict(
                tickfont=dict(size=11, family="Inter", color="#4b5563")
            )
        ),
        title=dict(
            text="<b>Performance Radar Comparison</b><br><span style='font-size:14px;color:#6b7280'>Multi-dimensional initiative analysis</span>",
            x=0.5,
            font=dict(size=16, family="Inter", color="#1f2937")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        height=600,
        font=dict(family="Inter", size=11)
    )
    
    return fig


def render_performance_insights(performance_data: pd.DataFrame) -> None:
    """Render performance insights and statistics."""
    if performance_data.empty:
        st.info("No data available for insights.")
        return
    
    metrics_cols = [col for col in performance_data.columns if col != 'Initiative']
    
    if not metrics_cols:
        st.info("No metrics available for insights.")
        return
    
    # Calculate overall performance score
    performance_data['Overall_Score'] = performance_data[metrics_cols].mean(axis=1)
    
    # Top and bottom performers
    top_performer = performance_data.loc[performance_data['Overall_Score'].idxmax()]
    bottom_performer = performance_data.loc[performance_data['Overall_Score'].idxmin()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        top_name = str(top_performer['Initiative'])
        display_name = top_name[:20] + "..." if len(top_name) > 20 else top_name
        # Convert Series value to scalar using helper function
        score_value = _get_scalar_value(top_performer['Overall_Score'])
        st.metric("Top Performer", display_name, f"{score_value:.3f}")
    
    with col2:
        bottom_name = str(bottom_performer['Initiative'])
        display_name = bottom_name[:20] + "..." if len(bottom_name) > 20 else bottom_name
        # Convert Series value to scalar using helper function
        score_value = _get_scalar_value(bottom_performer['Overall_Score'])
        st.metric("Bottom Performer", display_name, f"{score_value:.3f}")
    
    with col3:
        avg_score = performance_data['Overall_Score'].mean()
        st.metric("Average Score", f"{float(avg_score):.3f}")
    
    # Best and worst metrics
    metric_averages = performance_data[metrics_cols].mean().sort_values(ascending=False)
    
    st.markdown("**Metric Performance Summary:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("🏆 **Strongest Metrics:**")
        for metric in metric_averages.head(3).index:
            st.write(f"• {metric}: {metric_averages[metric]:.3f}")
    
    with col2:
        st.markdown("⚠️ **Areas for Improvement:**")
        for metric in metric_averages.tail(3).index:
            st.write(f"• {metric}: {metric_averages[metric]:.3f}")
