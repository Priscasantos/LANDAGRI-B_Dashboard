#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coverage Charts Module
======================

Generates various coverage-related charts for LULC initiatives,
including annual coverage multiselect, year overlap, and heatmap.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from scripts.utilities.config import get_initiative_color_map
from scripts.plotting.chart_core import get_display_name
from scripts.plotting.universal_cache import smart_cache_data

@smart_cache_data(ttl=300)
def plot_annual_coverage_multiselect(metadata: Dict[str, Any], filtered_df: pd.DataFrame, selected_initiatives: List[str]) -> go.Figure:
    """Plot annual coverage for selected initiatives using display names."""
    if not selected_initiatives or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Annual Coverage (No initiative selected or insufficient data)")
        return fig

    # Create name to display name mapping for selected initiatives
    nome_to_display_name = {row['Name']: get_display_name(row) 
                            for _, row in filtered_df[filtered_df['Name'].isin(selected_initiatives)].iterrows()}
    
    data = []
    for nome_original in selected_initiatives:
        if nome_original not in filtered_df['Name'].values: # Ensure initiative is in filtered_df to get metadata
            continue

        meta = metadata.get(nome_original, {})
        years_key = 'available_years' if 'available_years' in meta else 'anos_disponiveis'
        if years_key in meta and meta[years_key]:
            # Ensure years are integers and sorted
            anos = sorted([int(y) for y in meta[years_key] if pd.notna(y) and str(y).strip().isdigit()])
            if not anos: continue
            
            display_name = nome_to_display_name.get(nome_original, nome_original) # Fallback to original if not mapped by selection
            for ano in anos:
                data.append({'Name_original': nome_original, 'Display_Name': display_name, 'Ano': ano})
    
    if not data:
        fig = go.Figure()
        fig.update_layout(title="Annual Coverage (No temporal data available for selected initiatives)")
        return fig
        
    df_anos = pd.DataFrame(data)
    color_map = get_initiative_color_map(df_anos['Name_original'].unique().tolist())
    
    fig = go.Figure()
    unique_display_names_sorted = sorted(df_anos['Display_Name'].unique())

    for display_name_plot in unique_display_names_sorted:
        initiative_data_for_plot = df_anos[df_anos['Display_Name'] == display_name_plot]
        if not initiative_data_for_plot.empty:
            anos_plot = initiative_data_for_plot['Ano'].tolist()
            original_name_for_color = initiative_data_for_plot['Name_original'].iloc[0]
            
            fig.add_trace(go.Scatter(
                x=anos_plot,
                y=[display_name_plot] * len(anos_plot),
                mode='markers+lines',
                name=display_name_plot,
                marker=dict(
                    color=color_map.get(original_name_for_color, '#1f77b4'), 
                    size=12, 
                    line=dict(width=2, color=color_map.get(original_name_for_color, '#1f77b4'))
                ),
                line=dict(color=color_map.get(original_name_for_color, '#1f77b4'), width=3),
                showlegend=True
            ))
    
    if not df_anos.empty:
        min_year = int(df_anos['Ano'].min())
        max_year = int(df_anos['Ano'].max())
        fig.update_xaxes(
            tickmode='linear',
            tick0=min_year,
            dtick=1,
            range=[min_year - 0.5, max_year + 0.5],
            title='Year',
            showgrid=True,
            gridcolor="#E2E8F0",
            tickformat='d',
        )
    
    fig.update_layout(
        xaxis=dict(title="Year"),
        yaxis=dict(
            title="Initiative",
            type='category', 
            categoryorder='array', 
            categoryarray=unique_display_names_sorted
        ),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01, title="Initiative"),
        margin=dict(l=150, r=50, t=60, b=50) # Adjusted left margin for potentially longer display names
    )
    return fig

@smart_cache_data(ttl=300)
def plot_ano_overlap(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """Plots the number of initiatives available per year."""
    all_anos_data = []
    # Ensure 'Name' column exists for mapping with metadata keys
    df_copy = filtered_df.copy()
    if 'Name' not in df_copy.columns and 'Nome' in df_copy.columns:
        df_copy.rename(columns={'Nome': 'Name'}, inplace=True)

    for nome_original_metadata, meta_content in metadata.items():
        # Check if initiative is in the filtered DataFrame
        initiative_details = df_copy[df_copy['Name'] == nome_original_metadata]
        if initiative_details.empty:
            continue
        
        tipo = initiative_details['Type'].iloc[0] # Assuming 'Type' column exists
        
        years_key = 'available_years' if 'available_years' in meta_content else 'anos_disponiveis'
        if years_key in meta_content and meta_content[years_key]:
            # Ensure years are integers
            valid_years = [int(y) for y in meta_content[years_key] if pd.notna(y) and str(y).strip().isdigit()]
            if not valid_years: continue

            for ano in valid_years:
                all_anos_data.append({'Ano': ano, 'Name': nome_original_metadata, 'Type': tipo})
    
    if not all_anos_data:
        return go.Figure().update_layout(title="Number of Initiatives Overlap (No temporal data)")
        
    all_anos_df = pd.DataFrame(all_anos_data)
    count_ano = all_anos_df.groupby('Ano').size().reset_index(name='N_iniciativas')
    
    fig = px.bar(
        count_ano,
        x='Ano',
        y='N_iniciativas',
        color='N_iniciativas',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis=dict(title="Year", tickformat='d'), # Ensure year is displayed as integer
        yaxis=dict(title="Number of Initiatives")
    )
    return fig


def plot_heatmap(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """Plot heatmap of annual coverage using display names for y-axis."""
    if filtered_df is None or filtered_df.empty or not metadata:
        return go.Figure().update_layout(title="Annual Coverage Heatmap (Insufficient data)")

    # Create a working copy and ensure Display_Name column exists
    plot_df = filtered_df.copy()
    if 'Name' not in plot_df.columns and 'Nome' in plot_df.columns:
        plot_df.rename(columns={'Nome': 'Name'}, inplace=True)
    if 'Display_Name' not in plot_df.columns:
        from scripts.plotting.chart_core import add_display_names_to_df
        plot_df = add_display_names_to_df(plot_df)

    all_anos_data = []
    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df['Name'] == nome_original_metadata]
        if initiative_row_series.empty:
            continue
        
        display_name = initiative_row_series.iloc[0]['Display_Name']
            
        years_key = 'available_years' if 'available_years' in meta_content else 'anos_disponiveis'
        if years_key in meta_content and meta_content[years_key]:
            valid_years = [int(y) for y in meta_content[years_key] if pd.notna(y) and str(y).strip().isdigit()]
            if not valid_years: continue
            for ano in valid_years:
                all_anos_data.append({'Ano': ano, 'Display_Name': display_name, 'Value': 1})
    
    if not all_anos_data:
        return go.Figure().update_layout(title="Annual Coverage Heatmap (No temporal data)")
        
    all_anos_df = pd.DataFrame(all_anos_data)
    pivot = all_anos_df.pivot_table(index='Display_Name', columns='Ano', values='Value', aggfunc='count', fill_value=0)
    
    if pivot.empty:
        return go.Figure().update_layout(title="Annual Coverage Heatmap (Pivot table is empty)")

    pivot = pivot.sort_index() # Sort y-axis (Display_Name)
    # Ensure all years from 1985-2024 are present in columns, even if no data
    chart_min_year, chart_max_year = 1985, 2024
    all_heatmap_years = list(range(chart_min_year, chart_max_year + 1))
    pivot = pivot.reindex(columns=all_heatmap_years, fill_value=0)

    fig = px.imshow(
        pivot,
        aspect='auto',
        color_continuous_scale='Blues',
        labels=dict(color='Coverage')
    )
    
    fig.update_layout(
        xaxis=dict(title="Year"),
        yaxis=dict(title="Initiative")
    )
    fig.update_layout(
        height=max(400, 25 * len(pivot.index)),
        xaxis=dict(tickformat='d', dtick=2, range=[chart_min_year - 0.5, chart_max_year + 0.5]), # Ensure integer years, tick every 2 years
        yaxis=dict(type='category'),
        coloraxis_colorbar=dict(title="Available")
    )
    return fig
