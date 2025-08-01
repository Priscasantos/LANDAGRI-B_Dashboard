#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distribution Charts Module
==========================

Generates various distribution-related charts for LULC initiatives,
including class distribution, methodology distribution, and accuracy analysis.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scripts.plotting.chart_core import (
    get_display_name, 
    get_scope_colors
)
from scripts.plotting.universal_cache import smart_cache_data


@smart_cache_data(ttl=300)
def plot_distribuicao_classes(filtered_df):
    """Plot histogram distribution of number of classes with improved error handling."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Number of Classes Distribution (Insufficient data)")
        return fig
    
    # Verificar se a coluna 'Classes' existe e tem dados válidos
    if 'Classes' not in filtered_df.columns:
        fig = go.Figure()
        fig.update_layout(title="Number of Classes Distribution ('Classes' column not found)")
        return fig
    
    # Filtrar dados válidos (não nulos e numéricos)
    valid_data = filtered_df.dropna(subset=['Classes'])
    
    if valid_data.empty:
        fig = go.Figure()
        fig.update_layout(title="Number of Classes Distribution (No valid data)")
        return fig
    
    # Determinar cor baseada na coluna Type se existir
    color_column = 'Type' if 'Type' in valid_data.columns else None
    color_map = get_scope_colors() if color_column else None
    
    fig = px.histogram(
        valid_data,
        x='Classes',
        color=color_column,
        nbins=10,
        color_discrete_map=color_map
    )
    return fig


@smart_cache_data(ttl=300)
def plot_classes_por_iniciativa(filtered_df):
    """Plot number of classes per initiative using display names for y-axis labels."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Number of Classes per Initiative (Insufficient data)")
        return fig
    
    # Create a copy of the dataframe and add display names using the helper
    plot_df = filtered_df.copy()
    plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)
    
    fig = px.bar(
        plot_df.sort_values('Classes', ascending=True),
        x='Classes',
        y='Display_Name', # Use the new Display_Name column
        color='Type',
        orientation='h',
        color_discrete_map=get_scope_colors()
    )
    fig.update_layout(
        height=max(400, len(plot_df) * 25), # Adjust height dynamically
        yaxis=dict(type='category') # Ensure y-axis is treated as categorical
    )
    return fig


@smart_cache_data(ttl=300)
def plot_distribuicao_metodologias(method_counts):
    """Plot pie chart distribution of methodologies used."""
    if method_counts is None or method_counts.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribution of Methodologies Used (Insufficient data)")
        return fig
    
    fig = px.pie(
        values=method_counts.values,
        names=method_counts.index
    )
    
    return fig


def plot_acuracia_por_metodologia(filtered_df):
    """Plot accuracy distribution by methodology using box plot."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Accuracy by Methodology (Insufficient data)")
        return fig
    
    fig = px.box(
        filtered_df,
        x='Methodology',
        y='Accuracy (%)',
        color='Type',
        color_discrete_map=get_scope_colors()
    )
    fig.update_xaxes(tickangle=45)
    
    return fig


@smart_cache_data(ttl=300) 
def plot_resolution_accuracy(filtered_df: pd.DataFrame) -> go.Figure:
    """Plots a scatter plot of Resolution vs. Accuracy using display names."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Resolution vs. Accuracy (Insufficient data)")
        return fig

    # Ensure required columns are present
    if 'Resolution (m)' not in filtered_df.columns or 'Accuracy (%)' not in filtered_df.columns:
        fig = go.Figure()
        fig.update_layout(title="Resolution vs. Accuracy (Missing required columns)")
        return fig

    plot_df = filtered_df.copy()
    plot_df['Display_Name'] = plot_df.apply(get_display_name, axis=1)

    fig = px.scatter(
        plot_df,
        x='Resolution (m)',
        y='Accuracy (%)',
        color='Type', # Optional: color by Type or another category
        size='Classes', # Optional: size by number of Classes
        hover_name='Display_Name',
        color_discrete_map=get_scope_colors()
    )
    
    return fig
