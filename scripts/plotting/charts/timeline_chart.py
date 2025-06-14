#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timeline Chart Module
=====================

Generates the timeline chart for LULC initiatives.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from scripts.utilities.config import get_initiative_color_map
from scripts.plotting.chart_core import add_display_names_to_df, apply_standard_layout
from scripts.plotting.universal_cache import smart_cache_data

# If this function is also used by Streamlit pages, keep the cache decorator.
# Otherwise, if it's only for non-Streamlit generation, it can be removed.
@smart_cache_data(ttl=300) 
def plot_timeline(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """Plot an improved timeline using anos_disponiveis from metadata, with acronyms from DataFrame."""
    if not metadata or filtered_df is None or filtered_df.empty:
        return go.Figure().update_layout(title="Timeline of Initiatives (Insufficient data)")

    # Create a working copy and ensure Display_Name column exists, using the centralized function
    plot_df = filtered_df.copy()
    # Ensure 'Name' column exists for mapping with metadata keys
    if 'Name' not in plot_df.columns and 'Nome' in plot_df.columns: # Handle legacy 'Nome'
        plot_df.rename(columns={'Nome': 'Name'}, inplace=True)
    
    if 'Display_Name' not in plot_df.columns:
        plot_df = add_display_names_to_df(plot_df) # Add/overwrite Display_Name using chart_core

    timeline_data = []
    all_years = set()

    for nome_original_metadata, meta_content in metadata.items():
        initiative_row_series = plot_df[plot_df['Name'] == nome_original_metadata]
        
        if initiative_row_series.empty:
            continue
        
        initiative_row = initiative_row_series.iloc[0]
        display_name = initiative_row['Display_Name']
        metodologia = initiative_row.get('Methodology', 'N/A')

        years_key = 'available_years' if 'available_years' in meta_content else 'anos_disponiveis'
        if years_key in meta_content and meta_content[years_key]:
            # Ensure years are integers
            valid_years_for_initiative = [int(y) for y in meta_content[years_key] if pd.notna(y) and str(y).strip().isdigit()]
            if not valid_years_for_initiative:
                continue

            for ano in valid_years_for_initiative:
                timeline_data.append({
                    'produto': nome_original_metadata, 
                    'produto_display_name': display_name, 
                    'ano': int(ano), # Ensure ano is int
                    'disponivel': 1,
                    'metodologia': metodologia,
                })
                all_years.add(int(ano))

    if not timeline_data: # Simplified check, all_years would also be empty
        return go.Figure().update_layout(title="Timeline of Initiatives (No temporal data for selected initiatives)")

    timeline_df = pd.DataFrame(timeline_data)
    # min_year_data, max_year_data = (int(timeline_df['ano'].min()), int(timeline_df['ano'].max())) if not timeline_df.empty else (1985, 2024)
    
    # Define the fixed range for the chart
    chart_min_year, chart_max_year = 1985, 2024
    all_years_range = list(range(chart_min_year, chart_max_year + 1))
    
    produtos_unicos_df = timeline_df[['produto', 'produto_display_name']].drop_duplicates().sort_values(by='produto_display_name')
    
    display_names_unicos_sorted = produtos_unicos_df['produto_display_name'].tolist()
    if not display_names_unicos_sorted: # If no unique display names, means no valid data to plot
         return go.Figure().update_layout(title="Timeline of Initiatives (No unique initiatives to display)")


    matrix_data = []
    for display_name_iter in display_names_unicos_sorted:
        produto_data_for_matrix_rows = timeline_df[timeline_df['produto_display_name'] == display_name_iter]
        
        if produto_data_for_matrix_rows.empty:
            continue
            
        original_name_ref = produto_data_for_matrix_rows['produto'].iloc[0]
        produto_anos = produto_data_for_matrix_rows['ano'].tolist()
        produto_metodologia = produto_data_for_matrix_rows['metodologia'].iloc[0]

        for ano_iter in all_years_range:
            matrix_data.append({
                'produto': original_name_ref, 
                'produto_display_name': display_name_iter, 
                'ano': ano_iter,
                'disponivel': 1 if ano_iter in produto_anos else 0,
                'metodologia': produto_metodologia
            })

    if not matrix_data:
        return go.Figure().update_layout(title="Timeline of Initiatives (No data for matrix generation)")
        
    matrix_df = pd.DataFrame(matrix_data)
    fig_timeline = go.Figure()
    
    unique_original_names_for_colors = produtos_unicos_df['produto'].unique()
    color_map = get_initiative_color_map(unique_original_names_for_colors.tolist())
    
    legend_added = set()

    for current_display_name in display_names_unicos_sorted: # Iterate using sorted display names
        produto_data_plot = matrix_df[matrix_df['produto_display_name'] == current_display_name]
        
        if produto_data_plot.empty:
            continue
            
        anos_disponiveis = sorted(produto_data_plot[produto_data_plot['disponivel'] == 1]['ano'].tolist()) # Ensure sorted
        metodologia = produto_data_plot['metodologia'].iloc[0]
        original_name_for_color_key = produto_data_plot['produto'].iloc[0]
        cor = color_map.get(original_name_for_color_key, px.colors.qualitative.Set1[display_names_unicos_sorted.index(current_display_name) % len(px.colors.qualitative.Set1)])

        if anos_disponiveis:
            segments = []
            start_year_segment = anos_disponiveis[0]
            end_year_segment = anos_disponiveis[0]
            for j in range(1, len(anos_disponiveis)):
                if anos_disponiveis[j] == end_year_segment + 1:
                    end_year_segment = anos_disponiveis[j]
                else:
                    segments.append((start_year_segment, end_year_segment))
                    start_year_segment = anos_disponiveis[j]
                    end_year_segment = anos_disponiveis[j]
            segments.append((start_year_segment, end_year_segment))

            for seg_start, seg_end in segments:
                show_legend = current_display_name not in legend_added
                if show_legend:
                    legend_added.add(current_display_name)

                fig_timeline.add_trace(go.Scatter(
                    x=[seg_start, seg_end + 0.9], 
                    y=[current_display_name, current_display_name], 
                    mode='lines',
                    line=dict(color=cor, width=20), # Increased width for better visibility
                    name=current_display_name if show_legend else None,
                    showlegend=show_legend,
                    legendgroup=current_display_name,
                    hovertemplate=f"<b>{current_display_name}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>"
                ))
                
    apply_standard_layout(fig_timeline, "📅 Timeline of LULC Initiatives Availability (1985-2024)", "Year", "LULC Products", "timeline")
    
    fig_timeline.update_layout(
        height=max(600, len(display_names_unicos_sorted) * 40), # Increased per-initiative height
        margin=dict(l=220, r=30, t=100, b=80), # Adjusted left margin
        yaxis=dict(
            tickmode='array',
            tickvals=display_names_unicos_sorted, 
            ticktext=display_names_unicos_sorted, 
            type='category', 
            categoryorder='array', 
            categoryarray=display_names_unicos_sorted, 
            tickfont=dict(size=12) # Slightly smaller font if many items
        ),
        xaxis=dict(
            range=[chart_min_year - 0.5, chart_max_year + 0.5], 
            dtick=1, 
            tickformat='d',
            tickangle=-45,
            tickfont=dict(size=14), # Slightly smaller font
            gridwidth=1, # Thicker grid lines for clarity
            showgrid=True
        ),
        showlegend=True,
        legend=dict(traceorder='normal') # Ensure legend order matches y-axis if possible
    )
    return fig_timeline
