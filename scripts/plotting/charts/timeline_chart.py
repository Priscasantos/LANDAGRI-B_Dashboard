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
import streamlit as st
from typing import Dict, Any, Optional
from scripts.utilities.config import get_initiative_color_map
from scripts.plotting.chart_core import add_display_names_to_df, apply_standard_layout
from scripts.plotting.universal_cache import smart_cache_data

# If this function is also used by Streamlit pages, keep the cache decorator.
# Otherwise, if it's only for non-Streamlit generation, it can be removed.
def plot_timeline(metadata: Dict[str, Any], filtered_df: pd.DataFrame, 
                 chart_height: Optional[int] = None, chart_width: Optional[int] = None,
                 item_spacing: int = 25, line_width: int = 15, 
                 margin_config: Optional[Dict] = None) -> go.Figure:    
    """
    Plot an improved timeline using anos_disponiveis from metadata, with acronyms from DataFrame.
    
    Args:
        metadata: Initiative metadata
        filtered_df: Filtered DataFrame
        chart_height: Custom chart height (None for auto)
        chart_width: Custom chart width (None for auto)
        item_spacing: Vertical spacing between items (pixels)
        line_width: Width of timeline bars
        margin_config: Custom margins dict
    """
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
        
        # Get coverage information from metadata
        coverage = meta_content.get('coverage', 'N/A')

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
                    'coverage': coverage,
                })
                all_years.add(int(ano))

    if not timeline_data: # Simplified check, all_years would also be empty
        return go.Figure().update_layout(title="Timeline of Initiatives (No temporal data for selected initiatives)")    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Calculate dynamic range based on actual data
    min_year_data = int(timeline_df['ano'].min()) if not timeline_df.empty else 1985
    max_year_data = int(timeline_df['ano'].max()) if not timeline_df.empty else 2024
    
    # Use dynamic range: start at first year, end at last year + 1
    chart_min_year, chart_max_year = min_year_data, max_year_data + 1
    all_years_range = list(range(min_year_data, max_year_data + 1))

    # Define the desired order for 'coverage'
    coverage_order = ['Global', 'Regional', 'National', 'N/A']
    timeline_df['coverage'] = pd.Categorical(timeline_df['coverage'], categories=coverage_order, ordered=True)

    # Sort by coverage and then by product_display_name in reverse alphabetical order
    produtos_unicos_df = timeline_df[['produto', 'produto_display_name', 'coverage']].drop_duplicates().sort_values(
        by=['coverage', 'produto_display_name'],
        ascending=[True, False]  # Ascending for coverage, Descending for product_display_name
    )
    
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
                # Add a line segment for each continuous range of years
                fig_timeline.add_trace(go.Scatter(
                    x=[seg_start, seg_end + 1], # Use seg_end + 1 to extend the line to the next year
                    y=[current_display_name, current_display_name], 
                    mode='lines',
                    line=dict(color=cor, width=line_width),  # Use parametrized width 
                    name=current_display_name if current_display_name else original_name_for_color_key,
                    showlegend=False,  # Remove legend
                    legendgroup=current_display_name,
                    hovertemplate=f"<b>{current_display_name}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>"
                ))                
    apply_standard_layout(fig_timeline, "", "Year", "Initiatives", "timeline")
    
    # Default margins
    default_margins = dict(l=220, r=30, t=60, b=40)
    margins = margin_config if margin_config else default_margins

    # Calculate height
    if chart_height is None:
        calculated_height = max(300, len(display_names_unicos_sorted) * item_spacing)
    else:
        calculated_height = chart_height

    # Padronizar espessura dos ticks
    tick_width_standard = 0.8

    fig_timeline.update_layout(
        height=calculated_height,
        margin=margins,
        yaxis=dict(
            tickmode='array',
            tickvals=display_names_unicos_sorted, 
            ticktext=display_names_unicos_sorted, 
            type='category', 
            categoryorder='array', 
            categoryarray=display_names_unicos_sorted, 
            tickfont=dict(size=11),
            showgrid=False,
            ticks="outside",
            ticklen=8,
            tickwidth=tick_width_standard,
            tickcolor="black",
            showline=True,
            linewidth=1,
            linecolor="black",
        ),
        xaxis=dict(
            range=[chart_min_year - 0.5, chart_max_year + 0.5], 
            tickmode='array',
            tickvals=list(range(chart_min_year, chart_max_year + 2)),
            ticktext=[str(year) for year in range(chart_min_year, chart_max_year + 2)],
            tickformat='d',
            tickangle=-45,
            tickfont=dict(size=12),
            ticks="outside",
            ticklen=8,
            tickwidth=tick_width_standard,
            tickcolor="black",
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor="black",
            type="linear",
            autorange=False,
            fixedrange=False
        ),
        showlegend=True,
        legend=dict(traceorder='normal')
    )
    return fig_timeline


def timeline_with_controls(metadata: Dict[str, Any], filtered_df: pd.DataFrame):
    """Timeline chart with interactive controls for Streamlit."""
    
    st.sidebar.subheader("📐 Timeline Dimensions")
    
    # Controles de dimensão
    chart_height = st.sidebar.slider(
        "Chart Height", 
        min_value=200, 
        max_value=1200, 
        value=600, 
        step=50,
        help="Total height of the chart in pixels"
    )
    
    item_spacing = st.sidebar.slider(
        "Item Spacing", 
        min_value=15, 
        max_value=50, 
        value=25, 
        step=5,
        help="Vertical spacing between timeline items"
    )
    
    line_width = st.sidebar.slider(
        "Line Width", 
        min_value=5, 
        max_value=30, 
        value=15, 
        step=2,
        help="Width of the timeline bars"
    )
    
    # Controles de margem
    with st.sidebar.expander("🔧 Advanced Margins"):
        margin_left = st.number_input(
            "Left Margin", 
            value=220, 
            min_value=50, 
            max_value=400,
            help="Space for initiative names on the left"
        )
        margin_right = st.number_input(
            "Right Margin", 
            value=30, 
            min_value=10, 
            max_value=100
        )
        margin_top = st.number_input(
            "Top Margin", 
            value=60, 
            min_value=20, 
            max_value=150,
            help="Space for title at the top"
        )
        margin_bottom = st.number_input(
            "Bottom Margin", 
            value=40, 
            min_value=20, 
            max_value=100,
            help="Space for year labels at the bottom"
        )
    
    margin_config = {
        'l': margin_left,
        'r': margin_right, 
        't': margin_top,
        'b': margin_bottom
    }
    
    # Gerar gráfico com configurações
    fig = plot_timeline(
        metadata, 
        filtered_df,
        chart_height=chart_height,
        item_spacing=item_spacing,
        line_width=line_width,
        margin_config=margin_config
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Show current settings
    with st.sidebar.expander("📊 Current Settings"):
        st.json({
            "chart_height": chart_height,
            "item_spacing": item_spacing,
            "line_width": line_width,
            "margins": margin_config
        })
