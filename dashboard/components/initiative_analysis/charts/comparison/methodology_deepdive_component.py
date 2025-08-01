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
    st.markdown("##### 📊 Methodology Distribution Analysis")
    
    # Get methodology frequency
    methodology_counts = df[methodology_col].value_counts().reset_index()
    methodology_counts.columns = ["Methodology", "Count"]
    
    if methodology_counts.empty:
        st.info("No methodology data available for distribution analysis.")
        return
    
    col1, col2 = st.columns(2)
    
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
        )
    st.plotly_chart(fig_pie, use_container_width=True, key=f"methodology_pie_{methodology_col}")
    
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
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Summary metrics
    st.markdown("##### 📋 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Methodologies", len(methodology_counts))
    with col2:
        most_common = methodology_counts.iloc[0]
        st.metric("Most Common", most_common["Methodology"][:15] + "..." if len(most_common["Methodology"]) > 15 else most_common["Methodology"])
    with col3:
        st.metric("Usage Count", most_common["Count"])
    with col4:
        coverage_pct = (most_common["Count"] / len(df)) * 100
        st.metric("Coverage", f"{coverage_pct:.1f}%")


def render_technique_comparison(df: pd.DataFrame, methodology_col: str) -> None:
    """Render technique comparison analysis."""
    st.markdown("##### 🔄 Methodology Technique Analysis")
    
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
        title_font=dict(size=16, family="Inter", color="#1f2937")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_methodology_trends(df: pd.DataFrame, methodology_col: str) -> None:
    """Render methodology trends over time if temporal data is available."""
    st.markdown("##### 📈 Methodology Evolution Trends")
    
    # Check if we have temporal data
    year_cols = [col for col in df.columns if 'year' in col.lower() or 'start' in col.lower()]
    
    if not year_cols:
        st.info("No temporal data available for trend analysis.")
        return
    
    year_col = year_cols[0]
    
    # Create methodology trends over time
    trend_df = df.groupby([year_col, methodology_col]).size().reset_index(name='count')
    
    fig = px.line(
        trend_df,
        x=year_col,
        y='count',
        color=methodology_col,
        title="<b>Methodology Usage Trends Over Time</b>",
        markers=True
    )
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=16, family="Inter", color="#1f2937"),
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Number of Initiatives</b>"
    )
    st.plotly_chart(fig, use_container_width=True)


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
