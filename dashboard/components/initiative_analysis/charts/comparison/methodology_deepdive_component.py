"""
Methodology Deep Dive Component - Comparison Analysis
====================================================

Component for comprehensive methodology analysis with interactive visualizations.
Features methodology distribution charts, technique analysis, and comparative insights.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import hashlib
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_methodology_deepdive_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render comprehensive methodology deep dive analysis with interactive charts.
    
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    st.markdown("#### 🔬 Methodology Deep Dive Analysis")
    st.markdown("*Comparative analysis of methodology performance and accuracy across initiatives.*")
    
    if filtered_df.empty:
        st.warning("⚠️ No initiative data available for methodology analysis.")
        return
    
    # Check for methodology data
    methodology_cols = [col for col in filtered_df.columns if 'methodology' in col.lower() or 'method' in col.lower()]
    if not methodology_cols:
        st.warning("⚠️ No methodology information available in the data.")
        return
    
    methodology_col = methodology_cols[0]  # Use first methodology column found
    
    # Tab-based visualization
    tab1, tab2, tab3 = st.tabs([
        "📊 Methodology Distribution", 
        "🔄 Technique Comparison", 
        "📈 Methodology Trends"
    ])
    
    with tab1:
        render_methodology_distribution(filtered_df, methodology_col)
    
    with tab2:
        render_technique_comparison(filtered_df, methodology_col)
    
    with tab3:
        render_methodology_trends(filtered_df, methodology_col)


def render_methodology_distribution(df: pd.DataFrame, methodology_col: str) -> None:
    """Render methodology distribution charts."""
    
    # Get methodology frequency
    methodology_counts = df[methodology_col].value_counts().reset_index()
    methodology_counts.columns = ["Methodology", "Count"]
    
    if methodology_counts.empty:
        st.info("No methodology data available for distribution analysis.")
        return
    
    # criar duas colunas e rotear chamadas de st.plotly_chart por key para garantir exibição lado a lado
    col1, col2 = st.columns(2)
    _original_plotly_chart = st.plotly_chart

    def _routed_plotly_chart(fig, use_container_width=True, key=None, **kwargs):
        if key == "methodology_pie_chart":
            return col1.plotly_chart(fig, use_container_width=use_container_width, key=key, **kwargs)
        if key == "methodology_bar_chart":
            return col2.plotly_chart(fig, use_container_width=use_container_width, key=key, **kwargs)
        return _original_plotly_chart(fig, use_container_width=use_container_width, key=key, **kwargs)

    st.plotly_chart = _routed_plotly_chart
    
    with col1:
        # Pie chart
        fig_pie = px.pie(
            methodology_counts,
            values="Count",
            names="Methodology",
            title="<b>Methodology Distribution</b>",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=16, family="Inter", color="#1f2937"),
            legend_title_text="Methodology (Algorithm)"
        )
    st.plotly_chart(fig_pie, use_container_width=True, key="methodology_pie_chart")
    
    with col2:
        # Bar chart
        fig_bar = px.bar(
            methodology_counts,
            x="Count",
            y="Methodology",
            orientation="h",
            title="<b>Methodology Frequency</b>",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=16, family="Inter", color="#1f2937"),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="methodology_bar_chart")
    
    # Summary metrics
    st.markdown("##### Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Methodologies", len(methodology_counts))
    with col2:
        most_common = methodology_counts.iloc[0]
        st.metric("Most Common", most_common["Methodology"][:25] + "..." if len(most_common["Methodology"]) > 25 else most_common["Methodology"])
    with col3:
        st.metric("Usage Count", most_common["Count"])
    with col4:
        coverage_pct = (most_common["Count"] / len(df)) * 100
        st.metric("Coverage", f"{coverage_pct:.1f}%")


def render_technique_comparison(df: pd.DataFrame, methodology_col: str) -> None:
    """Render technique comparison analysis."""
    
    # Try to categorize methodologies into techniques
    techniques = categorize_methodologies(df[methodology_col].tolist())
    
    if not techniques:
        st.info("No technique categorization available.")
        return
    
    # Create technique comparison chart
    technique_df = pd.DataFrame(list(techniques.items()), columns=["Technique", "Count"])
    
    fig = px.treemap(
        technique_df,
        path=["Technique"],
        values="Count",
        title="<b>Methodology Techniques Breakdown</b>",
        color="Count",
        color_continuous_scale="RdYlBu_r"
    )
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=14, family="Inter", color="#1f2937")
    )
    st.plotly_chart(fig, use_container_width=True, key="methodology_accuracy_heatmap")


def render_methodology_trends(df: pd.DataFrame, methodology_col: str) -> None:
    """
    Render methodology usage trends over time.

    Detects a temporal column (year/start/date), coerces it to a year
    integer when possible, drops invalid rows, groups by year and
    methodology, and renders a Plotly line chart.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe containing temporal and methodology columns.
    methodology_col : str
        Column name for methodology/categories to color the lines.
    """
    # Validate input column
    if methodology_col not in df.columns:
        st.warning(f"Column '{methodology_col}' not found.")
        return

    # Heuristic search for temporal columns
    temporal_keys = ("year", "start", "date", "timestamp")
    year_cols = [
        col for col in df.columns
        if any(k in col.lower() for k in temporal_keys)
    ]
    if not year_cols:
        st.info("No temporal data available for trend analysis.")
        return

    # Prefer an explicit 'year' column if present
    year_col = next((c for c in year_cols if c.lower() == "year"), year_cols[0])

    # Work on a small copy to avoid SettingWithCopyWarning
    tmp = df[[year_col, methodology_col]].copy()

    # Drop rows missing methodology (they cannot be grouped)
    tmp = tmp.dropna(subset=[methodology_col])

    # Try to coerce the temporal column to a year integer:
    # - If datetime-like, extract year
    # - Otherwise try numeric conversion
    try:
        # First attempt: parse as datetimes (avoid deprecated/unsupported kwargs)
        parsed = pd.to_datetime(tmp[year_col], errors="coerce")
        if parsed.notna().any():
            tmp[year_col] = parsed.dt.year
        else:
            # Fallback: numeric conversion (e.g., "2020", 2020.0)
            tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce")
    except Exception:
        # On unexpected parsing errors, fallback to numeric conversion
        tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce")

    # Drop rows where year parsing failed
    tmp = tmp.dropna(subset=[year_col])
    if tmp.empty:
        st.info("No valid temporal data available for trend analysis.")
        return

    # Ensure integer year type for consistent grouping/sorting
    tmp[year_col] = tmp[year_col].astype(int)

    # Group and count occurrences. use observed=True if methodology is categorical
    trend_df = (
        tmp.groupby([year_col, methodology_col])
        .size()
        .reset_index(name="count")
        .sort_values(by=year_col)
    )

    # Build and render the chart
    fig = px.line(
        trend_df,
        x=year_col,
        y="count",
        color=methodology_col,
        title="<b>Methodology Usage Trends Over Time</b>",
        markers=True,
    )
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=16, family="Inter", color="#1f2937"),
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Number of Initiatives</b>",
    )
    st.plotly_chart(fig, use_container_width=True, key="methodology_trends_chart")


def categorize_methodologies(methodologies: list[str]) -> dict[str, int]:
    """
    Categorize methodologies into technique groups.
    
    Args:
        methodologies: List of methodology strings
        
    Returns:
        Dictionary with technique categories and counts
    """
    technique_keywords = {
        "Machine Learning": ["machine learning", "ml", "random forest", "svm", "neural", "deep learning"],
        "Remote Sensing": ["remote sensing", "satellite", "landsat", "modis", "sentinel"],
        "Classification": ["classification", "supervised", "unsupervised", "pixel-based"],
        "Object-Based": ["object-based", "obia", "segmentation"],
        "Time Series": ["time series", "temporal", "phenology"],
        "Statistical": ["statistical", "regression", "bayesian"],
        "Hybrid": ["hybrid", "ensemble", "combination"],
        "Other": []
    }
    
    technique_counts = {technique: 0 for technique in technique_keywords.keys()}
    
    for methodology in methodologies:
        if not methodology or pd.isna(methodology):
            continue
            
        methodology_lower = str(methodology).lower()
        categorized = False
        
        for technique, keywords in technique_keywords.items():
            if technique == "Other":
                continue
            if any(keyword in methodology_lower for keyword in keywords):
                technique_counts[technique] += 1
                categorized = True
                break
        
        if not categorized:
            technique_counts["Other"] += 1
    
    # Remove empty categories
    return {k: v for k, v in technique_counts.items() if v > 0}
