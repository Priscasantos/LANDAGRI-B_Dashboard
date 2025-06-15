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
def plot_resolution_accuracy_scatter(filtered_df: pd.DataFrame) -> go.Figure:
    """Create an enhanced scatter plot of Resolution vs. Accuracy with display names.
       Handles variations in input column names for resolution, accuracy, and classes."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Resolution vs. Accuracy Comparison (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Standardize column names internally
    rename_map = {}
    if 'Resolution' in plot_df.columns and 'Resolution (m)' not in plot_df.columns:
        rename_map['Resolution'] = 'Resolution (m)'
    if 'Accuracy' in plot_df.columns and 'Accuracy (%)' not in plot_df.columns:
        rename_map['Accuracy'] = 'Accuracy (%)'
    if 'Number_of_Classes' in plot_df.columns and 'Classes' not in plot_df.columns:
        rename_map['Number_of_Classes'] = 'Classes'
    if rename_map:
        plot_df.rename(columns=rename_map, inplace=True)

    # Ensure required columns are present after potential rename
    required_cols = ['Resolution (m)', 'Accuracy (%)']
    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Resolution vs. Accuracy (Missing columns: {', '.join(missing_cols)})")
        return fig

    # Ensure Display_Name exists, using get_display_name from chart_core
    if 'Display_Name' not in plot_df.columns or plot_df['Display_Name'].isnull().any():
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
def plot_spatial_resolution_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart comparing spatial resolutions of initiatives."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Spatial Resolution Comparison (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Ensure 'Resolution_max_val' and 'Display_Name' columns exist
    # 'Resolution_max_val' is preferred as it represents the finest resolution if a range is given.
    # If only 'Resolution (m)' exists, use that.
    resolution_col = None
    if 'Resolution_max_val' in plot_df.columns and plot_df['Resolution_max_val'].notna().any():
        resolution_col = 'Resolution_max_val'
    elif 'Resolution (m)' in plot_df.columns and plot_df['Resolution (m)'].notna().any():
        resolution_col = 'Resolution (m)'
    
    if not resolution_col:
        fig = go.Figure()
        fig.update_layout(title="Spatial Resolution Comparison (Missing Resolution Data)")
        return fig

    if 'Display_Name' not in plot_df.columns or plot_df['Display_Name'].isnull().any():
        plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)

    # Sort by resolution for better visualization (lower is better)
    plot_df = plot_df.sort_values(by=resolution_col, ascending=True)

    fig = px.bar(
        plot_df,
        x='Display_Name',
        y=resolution_col,
        color='Type' if 'Type' in plot_df.columns else None,
        labels={resolution_col: 'Resolution (m)', 'Display_Name': 'Initiative'},
        hover_name='Display_Name',
        hover_data={
            resolution_col: True,
            'Type': True if 'Type' in plot_df.columns else False,
            # Corrected to use 'Acronym' or 'Source' if 'Acronym' is not available
            'Acronym': True if 'Acronym' in plot_df.columns else (
                'Source' if 'Source' in plot_df.columns else False
            )
        },
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    
    apply_standard_layout(fig, 'Spatial Resolution Comparison', 'Initiative', 'Resolution (m)')
    fig.update_layout(xaxis_tickangle=-45) # Angle initiative names for readability
    return fig


@smart_cache_data(ttl=300)
def plot_global_accuracy_comparison(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart comparing global accuracy of initiatives."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Global Accuracy Comparison (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Ensure 'Accuracy_max_val' and 'Display_Name' columns exist
    # 'Accuracy_max_val' is preferred as it represents the best reported accuracy.
    # If only 'Accuracy (%)' exists, use that.
    accuracy_col = None
    if 'Accuracy_max_val' in plot_df.columns and plot_df['Accuracy_max_val'].notna().any():
        accuracy_col = 'Accuracy_max_val'
    elif 'Accuracy (%)' in plot_df.columns and plot_df['Accuracy (%)'].notna().any():
        accuracy_col = 'Accuracy (%)'
    
    if not accuracy_col:
        fig = go.Figure()
        fig.update_layout(title="Global Accuracy Comparison (Missing Accuracy Data)")
        return fig

    if 'Display_Name' not in plot_df.columns or plot_df['Display_Name'].isnull().any():
        plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)

    # Sort by accuracy for better visualization (higher is better)
    plot_df = plot_df.sort_values(by=accuracy_col, ascending=True) # Ascending for horizontal bar, highest at top

    fig = px.bar(
        plot_df,
        x=accuracy_col,
        y='Display_Name',
        orientation='h', # Horizontal bar chart
        color='Type' if 'Type' in plot_df.columns else None,
        labels={accuracy_col: 'Global Accuracy (%)', 'Display_Name': 'Initiative'},
        hover_name='Display_Name',
        hover_data={
            accuracy_col: ':.1f%', # Format hover accuracy to one decimal place
            'Type': True if 'Type' in plot_df.columns else False,
            # Corrected to use 'Acronym' or 'Source' if 'Acronym' is not available
            'Acronym': True if 'Acronym' in plot_df.columns else (
                'Source' if 'Source' in plot_df.columns else False
            )
        },
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    
    apply_standard_layout(fig, 'Global Accuracy Comparison', 'Global Accuracy (%)', 'Initiative')
    fig.update_layout(
        yaxis=dict(autorange="reversed"), # Ensure highest accuracy is at the top
        height=max(400, len(plot_df) * 25) # Adjust height based on number of initiatives
    )
    return fig


@smart_cache_data(ttl=300)
def plot_temporal_evolution_frequency(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a timeline or stacked bar chart for temporal coverage and update frequency."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Temporal Evolution & Update Frequency (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Required columns for this chart
    required_cols = ['Start_Year', 'End_Year', 'Temporal_Frequency']
    if 'Display_Name' not in plot_df.columns or plot_df['Display_Name'].isnull().any():
        plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)
    
    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Temporal Evolution (Missing: {', '.join(missing_cols)})")
        return fig

    # Convert year columns to numeric, coercing errors
    plot_df['Start_Year'] = pd.to_numeric(plot_df['Start_Year'], errors='coerce')
    plot_df['End_Year'] = pd.to_numeric(plot_df['End_Year'], errors='coerce')

    # Drop rows where start or end year could not be converted or are missing
    plot_df.dropna(subset=['Start_Year', 'End_Year'], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Temporal Evolution (No valid year data)")
        return fig

    # Sort by Start_Year for timeline view
    plot_df = plot_df.sort_values(by='Start_Year', ascending=True)

    # Create the timeline chart using px.timeline
    # For px.timeline, we need 'start', 'end', and 'y' (resource/initiative)
    # We can use 'Display_Name' for y, 'Start_Year' for start, and 'End_Year' for end.
    # Color can be by 'Temporal_Frequency' or 'Type'. Let's use 'Temporal_Frequency' for this specific chart.

    # Simpler custom_data construction
    custom_data_cols = []
    if 'Temporal_Frequency' in plot_df.columns:
        custom_data_cols.append('Temporal_Frequency')
    if 'Type' in plot_df.columns:
        custom_data_cols.append('Type')
    if 'Acronym' in plot_df.columns:
        custom_data_cols.append('Acronym')
    elif 'Source' in plot_df.columns: # Fallback if Acronym is not there
        custom_data_cols.append('Source')

    fig = px.timeline(
        plot_df,
        x_start='Start_Year',
        x_end='End_Year',
        y='Display_Name',
        color='Temporal_Frequency' if 'Temporal_Frequency' in plot_df.columns else None,
        hover_name='Display_Name',
        labels={
            'Display_Name': 'Initiative',
            'Start_Year': 'Start Year',
            'End_Year': 'End Year',
            'Temporal_Frequency': 'Update Frequency'
        },
        custom_data=custom_data_cols if custom_data_cols else None
    )

    # Improve hover information - adjust customdata indices based on what's available
    hover_template_parts = ["<b>%{y}</b><br>Period: %{base|%Y} - %{xEnd|%Y}"]
    # custom_data_mapping = [] # This was used to build customdata, now custom_data_cols serves this
    
    # Rebuild hovertemplate based on the actual order in custom_data_cols
    for i, col_name in enumerate(custom_data_cols):
        display_label = col_name.replace("_", " ").title()
        if col_name == 'Acronym' and 'Acronym' not in plot_df.columns and 'Source' in plot_df.columns:
            display_label = 'Source' # Adjust label if we fell back to Source
        hover_template_parts.append(f"{display_label}: %{{customdata[{i}]}}")
    
    if custom_data_cols: # Only update custom_data if we have something to map
        # fig.update_traces(customdata=plot_df[custom_data_cols].values) # custom_data is now directly passed to px.timeline
        hover_template_parts.append("<extra></extra>")
        fig.update_traces(hovertemplate="<br>".join(hover_template_parts))

    apply_standard_layout(fig, 'Temporal Coverage and Update Frequency', 'Year', 'Initiative')
    fig.update_layout(
        height=max(400, len(plot_df) * 30), # Adjust height
        xaxis_type='linear' # Ensure years are treated linearly
    )
    # Ensure y-axis categories are sorted as per the sorted DataFrame for consistent display
    fig.update_yaxes(categoryorder='array', categoryarray=plot_df['Display_Name'].unique())

    return fig


@smart_cache_data(ttl=300)
def plot_class_diversity_focus(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart for number of agricultural classes vs. total classes."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Class Diversity & Agricultural Focus (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Required columns
    # Assuming 'Number_of_Classes' is total classes and 'Number_of_Agricultural_Classes' for agricultural ones.
    # These names might need to be adjusted based on the actual DataFrame columns.
    required_cols = ['Number_of_Classes', 'Number_of_Agricultural_Classes']
    if 'Display_Name' not in plot_df.columns or plot_df['Display_Name'].isnull().any():
        plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)

    missing_cols = [col for col in required_cols if col not in plot_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Class Diversity (Missing: {', '.join(missing_cols)})")
        return fig

    # Convert class count columns to numeric, coercing errors
    plot_df['Number_of_Classes'] = pd.to_numeric(plot_df['Number_of_Classes'], errors='coerce')
    plot_df['Number_of_Agricultural_Classes'] = pd.to_numeric(plot_df['Number_of_Agricultural_Classes'], errors='coerce')

    # Drop rows where class counts are missing or invalid
    plot_df.dropna(subset=['Number_of_Classes', 'Number_of_Agricultural_Classes'], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Class Diversity (No valid class count data)")
        return fig

    # Sort by total number of classes for better visualization
    plot_df = plot_df.sort_values(by='Number_of_Classes', ascending=False)

    # Prepare data for grouped bar chart
    # We need to melt the DataFrame to have 'variable' (Total Classes, Agri Classes) and 'value' columns
    plot_df_melted = plot_df.melt(
        id_vars=['Display_Name', 'Type'] if 'Type' in plot_df.columns else ['Display_Name'],
        value_vars=['Number_of_Classes', 'Number_of_Agricultural_Classes'],
        var_name='Class Category',
        value_name='Number of Classes'
    )
    # Make Class Category more readable
    plot_df_melted['Class Category'] = plot_df_melted['Class Category'].replace({
        'Number_of_Classes': 'Total Classes',
        'Number_of_Agricultural_Classes': 'Agricultural Classes'
    })

    fig = px.bar(
        plot_df_melted,
        x='Display_Name',
        y='Number of Classes',
        color='Class Category',
        barmode='group', # Grouped bar chart
        hover_name='Display_Name',
        labels={'Display_Name': 'Initiative', 'Number of Classes': 'Count', 'Class Category': 'Category'},
        color_discrete_map={
            'Total Classes': '#1f77b4',  # Muted blue
            'Agricultural Classes': '#2ca02c'  # Cooked asparagus green
        }
    )

    apply_standard_layout(fig, 'Class Diversity and Agricultural Focus', 'Initiative', 'Number of Classes')
    fig.update_layout(
        xaxis_tickangle=-45,
        height=max(500, len(plot_df) * 35) # Adjust height
    )
    return fig


@smart_cache_data(ttl=300)
def plot_classification_methodology(filtered_df: pd.DataFrame, chart_type: str = 'pie') -> go.Figure:
    """Create a pie or bar chart showing the distribution of classification methodologies."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Classification Methodology Distribution (Insufficient data)")
        return fig

    plot_df = filtered_df.copy()

    # Required column
    methodology_col = 'Methodology' # Assuming this is the column name
    if methodology_col not in plot_df.columns:
        fig = go.Figure()
        fig.update_layout(title=f"Methodology Distribution (Missing column: {methodology_col})")
        return fig

    # Drop rows where methodology is missing
    plot_df.dropna(subset=[methodology_col], inplace=True)
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Methodology Distribution (No valid methodology data)")
        return fig

    # Count occurrences of each methodology
    methodology_counts = plot_df[methodology_col].value_counts().reset_index()
    methodology_counts.columns = [methodology_col, 'Count']

    if chart_type == 'pie':
        fig = px.pie(
            methodology_counts,
            names=methodology_col,
            values='Count',
            hover_name=methodology_col,
            hole=.3 # Donut-like pie chart
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        title = "Classification Methodology Distribution (Pie Chart)"
        apply_standard_layout(fig, title, "", "") # Pass empty strings for axis titles for pie
    elif chart_type == 'bar':
        # Sort by count for bar chart
        methodology_counts = methodology_counts.sort_values(by='Count', ascending=False)
        fig = px.bar(
            methodology_counts,
            x=methodology_col,
            y='Count',
            color=methodology_col, # Color by methodology
            labels={methodology_col: 'Methodology', 'Count': 'Number of Initiatives'},
            hover_name=methodology_col
        )
        title = "Classification Methodology Distribution (Bar Chart)"
        apply_standard_layout(fig, title, "Methodology", "Number of Initiatives")
        fig.update_layout(xaxis_tickangle=-45)
    else:
        fig = go.Figure()
        fig.update_layout(title=f"Invalid chart type: {chart_type}. Choose 'pie' or 'bar'.")
        return fig

    fig.update_layout(showlegend=(chart_type == 'bar')) # Show legend for bar, pie has labels
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
            # Ensure max and min are different to avoid division by zero if all values are the same
            min_val, max_val = col_values.min(), col_values.max()
            if max_val == min_val:
                normalized = pd.Series(50, index=col_values.index) # Assign a neutral 50 if all values are same
            elif weight > 0:  # Higher values are better
                normalized = (col_values - min_val) / (max_val - min_val) * 100
            else:  # Lower values are better (like resolution)
                normalized = (max_val - col_values) / (max_val - min_val) * 100
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


@smart_cache_data(ttl=300)
def plot_classes_frequency_boxplot(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a box plot of Number of Classes by Temporal Frequency."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Classes vs. Temporal Frequency (Insufficient data)")
        return fig

    required_cols = ['Number_of_Classes', 'Temporal_Frequency']
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Classes vs. Temporal Frequency (Missing: {', '.join(missing_cols)})")
        return fig

    plot_df = filtered_df.dropna(subset=required_cols).copy()
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Classes vs. Temporal Frequency (No valid data after NaN drop)")
        return fig
        
    # Ensure Temporal_Frequency is treated as a category (string)
    plot_df['Temporal_Frequency'] = plot_df['Temporal_Frequency'].astype(str)
    # Sort by a natural order if possible (e.g., if frequencies are like 'Annual', 'Biannual')
    # This might need a more sophisticated sorting if a specific order is required.
    # For now, default alphanumeric sort of unique string values will apply.

    fig = px.box(
        plot_df,
        x='Temporal_Frequency',
        y='Number_of_Classes',
        color='Type' if 'Type' in plot_df.columns else None,
        hover_name='Display_Name' if 'Display_Name' in plot_df.columns else None,
        points="all", # Show all data points
        notched=True, # Add notches for median comparison
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )

    apply_standard_layout(
        fig, 
        "Number of Classes by Temporal Frequency", 
        "Temporal Frequency", 
        "Number of Classes"
    )
    fig.update_layout(xaxis_categoryorder='category ascending') # Ensure consistent ordering
    return fig


@smart_cache_data(ttl=300)
def plot_methodology_type_barchart(filtered_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of Methodology Breakdown by Initiative Type."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Methodology Breakdown by Type (Insufficient data)")
        return fig

    required_cols = ['Methodology', 'Type']
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    if missing_cols:
        fig = go.Figure()
        fig.update_layout(title=f"Methodology Breakdown by Type (Missing: {', '.join(missing_cols)})")
        return fig

    plot_df = filtered_df.groupby(['Type', 'Methodology'], observed=False).size().reset_index(name='Count')
    
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Methodology Breakdown by Type (No data after grouping)")
        return fig

    fig = px.bar(
        plot_df,
        x='Type',
        y='Count',
        color='Methodology',
        barmode='group',
        hover_name='Methodology', # Shows methodology on hover for the bar segment
        hover_data={'Type': True, 'Count': True, 'Methodology': False} # Customize hover data
    )

    apply_standard_layout(
        fig, 
        "Methodology Breakdown by Initiative Type", 
        "Initiative Type", 
        "Number of Initiatives"
    )
    fig.update_layout(xaxis_categoryorder='category ascending')
    return fig
