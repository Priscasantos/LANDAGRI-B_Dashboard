#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparison Charts Module
========================

Generates various comparison-related charts for LULC initiatives,
including scatter plots, correlation matrices, and ranking charts.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from scripts.plotting.chart_core import get_display_name, apply_standard_layout
from scripts.plotting.universal_cache import smart_cache_data


@smart_cache_data(ttl=300)
def plot_scatter_resolution_accuracy(filtered_df: pd.DataFrame) -> go.Figure:
    """Create an enhanced scatter plot of Resolution vs. Accuracy with display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Resolution vs. Accuracy Comparison (Insufficient data)")
        return fig

    # Ensure required columns are present
    required_cols = ['Resolution (m)', 'Accuracy (%)']
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Resolution vs. Accuracy (Missing columns: {', '.join(missing_cols)})")
        return fig

    plot_df = filtered_df.copy()
    plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)

    fig = px.scatter(
        plot_df,
        x='Resolution (m)',
        y='Accuracy (%)',
        color='Type' if 'Type' in plot_df.columns else None,
        size='Classes' if 'Classes' in plot_df.columns else None,
        hover_name='Display_Name',
        hover_data=['Classes', 'Type'] if all(col in plot_df.columns for col in ['Classes', 'Type']) else None,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    
    # Apply standardized layout
    apply_standard_layout(fig, 'Resolution vs. Accuracy Comparison', 'Resolution (m)', 'Accuracy (%)')
    
    return fig


@smart_cache_data(ttl=300)
def plot_comparison_matrix(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a comparison matrix heatmap for multiple numeric metrics."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (Insufficient data)")
        return fig

    # Select numeric columns for comparison
    numeric_columns = []
    for col in filtered_df.columns:
        if filtered_df[col].dtype in ['int64', 'float64'] and col not in ['Name']:
            # Check if column has sufficient non-null values
            if filtered_df[col].notna().sum() > 0:
                numeric_columns.append(col)
    
    if len(numeric_columns) < 2:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (Insufficient numeric data)")
        return fig

    # Create a subset with numeric data and add display names
    plot_df = filtered_df[['Name'] + numeric_columns].copy()
    plot_df = plot_df.dropna(subset=numeric_columns, how='all')
    
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Comparison Matrix (No valid data)")
        return fig
    
    # Add display names
    plot_df['Display_Name'] = plot_df.apply(lambda row: get_display_name(row), axis=1)
    
    # Normalize the data for better visualization
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    
    # Fill NaN values with column means before scaling
    numeric_df = plot_df[numeric_columns].fillna(plot_df[numeric_columns].mean())
    normalized_data = scaler.fit_transform(numeric_df)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=normalized_data,
        x=numeric_columns,
        y=plot_df['Display_Name'].values,
        colorscale='RdYlBu_r',
        hoverongaps=False,
        showscale=True,
        colorbar=dict(title="Normalized Value")
    ))
    
    # Apply standardized layout
    apply_standard_layout(fig, "Initiative Comparison Matrix", "Metrics", "Initiative")
    
    fig.update_layout(
        height=max(400, len(plot_df) * 25),
        xaxis=dict(tickangle=45),
        yaxis=dict(type='category')
    )
    
    return fig


@smart_cache_data(ttl=300)
def plot_initiative_ranking(filtered_df: pd.DataFrame, ranking_criteria: Dict[str, float] | None = None) -> go.Figure:
    """Create a ranking chart based on multiple criteria with display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Initiative Ranking (Insufficient data)")
        return fig

    # Default ranking criteria if not provided
    if ranking_criteria is None:
        ranking_criteria = {
            'Accuracy (%)': 0.4,
            'Classes': 0.3,
            'Resolution (m)': -0.3  # Negative because lower resolution is better
        }

    # Check if required columns exist
    available_criteria = {k: v for k, v in ranking_criteria.items() if k in filtered_df.columns}
    
    if not available_criteria:
        fig = go.Figure()
        fig.update_layout(title="Initiative Ranking (Missing ranking criteria columns)")
        return fig

    plot_df = filtered_df.copy()
    plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)
    
    # Calculate composite score
    plot_df['Composite_Score'] = 0
    for column, weight in available_criteria.items():
        # Normalize column values to 0-100 scale
        col_values = plot_df[column].dropna()
        if len(col_values) > 0:
            if weight > 0:  # Higher values are better
                normalized = (col_values - col_values.min()) / (col_values.max() - col_values.min()) * 100
            else:  # Lower values are better (like resolution)
                normalized = (col_values.max() - col_values) / (col_values.max() - col_values.min()) * 100
            plot_df.loc[col_values.index, 'Composite_Score'] += normalized * abs(weight)
    
    # Sort by composite score
    plot_df = plot_df.sort_values('Composite_Score', ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        plot_df,
        x='Composite_Score',
        y='Display_Name',
        color='Type' if 'Type' in plot_df.columns else None,
        orientation='h',
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'},
        hover_data=[col for col in available_criteria.keys() if col in plot_df.columns]
    )
    
    # Apply standardized layout
    apply_standard_layout(fig, "Initiative Ranking (Composite Score)", "Composite Score", "Initiative")
    
    fig.update_layout(
        height=max(400, len(plot_df) * 25),
        yaxis=dict(type='category')
    )
    
    return fig


@smart_cache_data(ttl=300)
def plot_correlation_matrix(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a correlation matrix for numeric variables."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Correlation Matrix (Insufficient data)")
        return fig

    # Select numeric columns
    numeric_columns = []
    for col in filtered_df.columns:
        if filtered_df[col].dtype in ['int64', 'float64'] and col not in ['Name']:
            if filtered_df[col].notna().sum() > 1:  # Need at least 2 values for correlation
                numeric_columns.append(col)
    
    if len(numeric_columns) < 2:
        fig = go.Figure()
        fig.update_layout(title="Correlation Matrix (Need at least 2 numeric columns)")
        return fig

    # Calculate correlation matrix
    corr_matrix = filtered_df[numeric_columns].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        showscale=True,
        colorbar=dict(title="Correlation")
    ))
    
    # Apply standardized layout
    apply_standard_layout(fig, "Variable Correlation Matrix", "Variables", "Variables")
    
    fig.update_layout(
        height=max(400, len(numeric_columns) * 40),
        xaxis=dict(tickangle=45),
        yaxis=dict(tickangle=0)
    )
    
    return fig


@smart_cache_data(ttl=300)
def plot_radar_comparison(data1: Dict[str, Any], data2: Dict[str, Any], filtered_df: pd.DataFrame, 
                         init1: str, init2: str) -> go.Figure:
    """Create a radar chart comparing two initiatives with standardized display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Radar Comparison (Insufficient data)")
        return fig
      # Available categories for comparison
    categories = ['Accuracy (%)', 'Resolution (m)', 'Classes']
    available_categories = [cat for cat in categories if cat in filtered_df.columns]
    
    if len(available_categories) < 2:
        fig = go.Figure()
        fig.update_layout(title="Radar Comparison (Insufficient data columns)")
        return fig
    
    def normalize_for_radar(value, column, df):
        """Normalize values for radar chart (0-100 scale)"""
        if pd.isna(value) or df[column].isna().all():
            return 50  # Default middle value
        
        min_val, max_val = df[column].min(), df[column].max()
        if max_val == min_val:
            return 50  # All values are the same
        
        if column == 'Resolution (m)':
            # For resolution, lower is better, so invert the scale
            return (max_val - value) / (max_val - min_val) * 100
        else:
            # For accuracy and classes, higher is better
            return (value - min_val) / (max_val - min_val) * 100
    
    # Get display names for the initiatives
    display_name_1 = init1
    display_name_2 = init2
    
    # Try to get acronyms if available
    for _, row in filtered_df.iterrows():
        name_col = 'Name' if 'Name' in row else 'Nome' if 'Nome' in row else None
        if name_col and row[name_col] == init1:
            display_name_1 = get_display_name(row)
        elif name_col and row[name_col] == init2:
            display_name_2 = get_display_name(row)
    
    # Calculate normalized values
    values1 = [normalize_for_radar(data1.get(cat, 0), cat, filtered_df) for cat in available_categories]
    values2 = [normalize_for_radar(data2.get(cat, 0), cat, filtered_df) for cat in available_categories]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values1 + [values1[0]],
        theta=available_categories + [available_categories[0]],
        fill='toself',
        name=display_name_1,
        line_color='#ff6b6b'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=values2 + [values2[0]],
        theta=available_categories + [available_categories[0]],
        fill='toself',
        name=display_name_2,
        line_color='#4dabf7'
    ))
    
    # Apply standardized layout
    apply_standard_layout(fig, "Initiative Comparison (Radar Chart)", "", "")
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500
    )
    
    return fig
