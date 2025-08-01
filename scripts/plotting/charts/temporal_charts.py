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
from scripts.plotting.chart_core import (
    add_display_names_to_df, 
    get_initiative_color_map,
    get_font_config,
    get_resolution_colors
)

# Renamed from plot_timeline to plot_timeline_chart
def plot_timeline_chart(metadata: Dict[str, Any], filtered_df: pd.DataFrame, 
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
            tickfont=get_font_config('tick_small'),
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
            tickfont=get_font_config('tick'),
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
    # Updated to call the renamed function
    fig = plot_timeline_chart(
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

# Placeholder functions for missing charts

def plot_coverage_heatmap_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """Generates the Plotly figure for the coverage heatmap."""
    fig = go.Figure()
    fig.add_annotation(text="plot_coverage_heatmap_chart - Not Implemented", showarrow=False)
    if temporal_data.empty: # Basic check to use the parameter and avoid unused warning
        pass
    return fig

def plot_gaps_bar_chart(gaps_data: pd.DataFrame) -> go.Figure:
    """Generates the Plotly bar chart for temporal gaps analysis."""
    fig = go.Figure()
    fig.add_annotation(text="Temporal Gaps (Not Implemented)", showarrow=False)
    fig.add_annotation(text="plot_gaps_bar_chart - Not Implemented", showarrow=False)
    if gaps_data.empty: # Basic check
        pass
    return fig

def plot_evolution_line_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """
    Generates the Plotly line chart for evolution analysis showing how data availability
    evolves over time across all initiatives.
    
    Args:
        temporal_data: DataFrame with temporal data containing 'Anos_Lista' and 'Tipo' columns
        
    Returns:
        go.Figure: Plotly figure showing evolution of data availability
    """
    if temporal_data.empty or 'Anos_Lista' not in temporal_data.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No temporal data available for evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=get_font_config('annotation')
        )
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title="Number of Active Initiatives")
        )
        return fig
    
    # Process data to count initiatives per year
    all_years = []
    for _, row in temporal_data.iterrows():
        if isinstance(row['Anos_Lista'], list):
            all_years.extend(row['Anos_Lista'])
    
    if not all_years:
        fig = go.Figure()
        fig.add_annotation(
            text="No year data available for evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=get_font_config('annotation')
        )
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title="Number of Active Initiatives")
        )
        return fig
    
    # Count initiatives per year
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Year': year_counts.index,
        'Number_Initiatives': year_counts.values
    })
    
    # Create the figure
    fig = go.Figure()
    
    # Add the main evolution line with area fill
    fig.add_trace(go.Scatter(
        x=years_df['Year'],
        y=years_df['Number_Initiatives'],
        mode='lines+markers',
        name='Active Initiatives',
        line=dict(color='rgba(0, 150, 136, 1)', width=3),
        marker=dict(
            size=8, 
            color='rgba(0, 150, 136, 0.8)',
            line=dict(width=2, color='rgba(0, 150, 136, 1)')
        ),
        fill='tonexty',
        fillcolor='rgba(0, 150, 136, 0.2)',
        hovertemplate='<b>Year: %{x}</b><br>Active Initiatives: %{y}<extra></extra>'
    ))
      # Add trend markers for key points
    max_initiatives_year = years_df.loc[years_df['Number_Initiatives'].idxmax()]
    
    # Mark peak year
    fig.add_trace(go.Scatter(
        x=[max_initiatives_year['Year']],
        y=[max_initiatives_year['Number_Initiatives']],
        mode='markers',
        name='Peak Year',
        marker=dict(
            size=12,
            color='rgba(255, 193, 7, 1)',
            symbol='star',
            line=dict(width=2, color='rgba(255, 152, 0, 1)')
        ),
        hovertemplate=f'<b>Peak Year: {max_initiatives_year["Year"]}</b><br>Initiatives: {max_initiatives_year["Number_Initiatives"]}<extra></extra>',
        showlegend=True
    ))
    
    # Enhanced layout specific to evolution chart
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="Year",
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            dtick=2,  # Show every 2 years for better readability
            tickangle=-45 if len(years_df) > 15 else 0  # Rotate labels if many years
        ),
        yaxis=dict(
            title="Number of Active Initiatives",
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            zeroline=True,
            zerolinecolor='rgba(128,128,128,0.4)',
            zerolinewidth=1
        ),
        hovermode='x unified'
    )
    
    # Add annotations for context
    avg_initiatives = years_df['Number_Initiatives'].mean()
    fig.add_hline(
        y=avg_initiatives,
        line_dash="dash",
        line_color="rgba(128,128,128,0.6)",
        annotation_text=f"Average: {avg_initiatives:.1f}",
        annotation_position="bottom right"
    )
    
    return fig

def plot_evolution_heatmap_chart(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """
    Generates an area chart showing the evolution of spatial resolution in LULC initiatives over time.
    Uses three resolution categories: Coarse (≥100m), Medium (30-99m), and High (<30m).
    
    Args:
        metadata: Initiative metadata containing spatial resolution and available years
        filtered_df: Filtered DataFrame with initiative data
        
    Returns:
        go.Figure: Plotly figure showing stacked area chart of resolution evolution
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for resolution evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=get_font_config('annotation')
        )
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title="Initiatives")
        )
        return fig
    
    # Process metadata to extract resolution and years data
    resolution_data = []
    
    for initiative_name, meta_info in metadata.items():
        if not isinstance(meta_info, dict):
            continue
            
        # Get available years
        years_key = 'available_years' if 'available_years' in meta_info else 'anos_disponiveis'
        if years_key not in meta_info or not meta_info[years_key]:
            continue
            
        years = meta_info[years_key]
        if not isinstance(years, list):
            continue
            
        # Get spatial resolution
        spatial_res = meta_info.get('spatial_resolution')
        if spatial_res is None:
            continue
            
        # Parse resolution to get a single representative value
        resolution_value = _parse_resolution_for_categorization(spatial_res)
        if resolution_value is None:
            continue
            
        # Categorize resolution
        if resolution_value >= 100:
            category = "Coarse (≥100m)"
        elif resolution_value >= 30:
            category = "Medium (30-99m)"
        else:
            category = "High (<30m)"
            
        # Add data for each year
        for year in years:
            if isinstance(year, (int, float)) and 1985 <= year <= 2024:
                resolution_data.append({
                    'initiative': initiative_name,
                    'year': int(year),
                    'resolution_value': resolution_value,
                    'category': category
                })
    
    if not resolution_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No resolution data available for the selected initiatives",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=get_font_config('annotation')
        )
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title="Initiatives")
        )
        return fig
    
    # Create DataFrame and aggregate by year and category
    df_resolution = pd.DataFrame(resolution_data)
    
    # Count initiatives by year and category
    yearly_counts = df_resolution.groupby(['year', 'category']).size().reset_index(name='count')
    
    # Pivot to get categories as columns
    pivot_df = yearly_counts.pivot(index='year', columns='category', values='count').fillna(0)
    
    # Ensure we have all years from 1985 to 2024
    all_years = list(range(1985, 2025))
    pivot_df = pivot_df.reindex(all_years, fill_value=0)
    
    # Define category order and colors using centralized theme
    category_order = ["High (<30m)", "Medium (30-99m)", "Coarse (≥100m)"]
    colors = get_resolution_colors()
    
    # Ensure all categories exist in the DataFrame
    for category in category_order:
        if category not in pivot_df.columns:
            pivot_df[category] = 0
    
    # Create the figure
    fig = go.Figure()
    
    # Add stacked area traces
    for i, category in enumerate(category_order):
        if category in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[category],
                mode='lines',
                name=category,
                fill='tonexty' if i > 0 else 'tozeroy',
                fillcolor=colors[category],
                line=dict(color=colors[category], width=2),
                hovertemplate=f'<b>{category}</b><br>Year: %{{x}}<br>Initiatives: %{{y}}<extra></extra>',
                stackgroup='one'  # This creates the stacked area effect
            ))    # Add milestone annotations for key years
    milestones = {
        2000: "Milestone 2000",
        2020: "Milestone 2020"
    }
    
    for year, label in milestones.items():
        if year in pivot_df.index:
            fig.add_vline(
                x=year,
                line_dash="dash",
                line_color="rgba(128,128,128,0.6)",
                line_width=1,
                annotation_text=label,
                annotation_position="top",
                annotation_font_size=10,
                annotation_font_color="rgba(139,69,19,0.8)"
            )
    
    # Chart specific layout
    fig.update_layout(
        xaxis=dict(title="Year"),
        yaxis=dict(title="Initiatives")
    )
    
    # Customize layout for area chart
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            range=[1985, 2024],
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            dtick=5,  # Show every 5 years
            tickangle=0,
            tickfont=get_font_config('tick')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            zeroline=True,
            zerolinecolor='rgba(128,128,128,0.4)',
            zerolinewidth=1,
            title_font=get_font_config('axis_title')
        ),
        hovermode='x unified'
    )
    
    # Add subtitle with resolution categories explanation
    fig.add_annotation(
        text="High: <30m | Medium: 30-99m | Coarse: ≥100m",
        xref="paper", yref="paper",
        x=0.5, y=-0.12,
        showarrow=False,
        font=get_font_config('annotation_small'),
        align="center"
    )
    
    return fig


def _parse_resolution_for_categorization(spatial_res: Any) -> Optional[float]:
    """
    Helper function to parse spatial resolution for categorization.
    Returns a single representative resolution value in meters.
    """
    if spatial_res is None:
        return None
        
    # Handle direct numeric values
    if isinstance(spatial_res, (int, float)):
        return float(spatial_res)
    
    # Handle string values
    if isinstance(spatial_res, str):
        # Extract numeric value from string like "30m", "100", etc.
        import re
        res_str = re.sub(r'[^\d.]', '', spatial_res)
        if res_str:
            return float(res_str)
        return None
    
    # Handle list of values or objects
    if isinstance(spatial_res, list):
        values = []
        
        # Look for 'current' resolution first
        for item in spatial_res:
            if isinstance(item, dict) and item.get('current', False):
                val = item.get('resolution')
                if val is not None:
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, str):
                        import re
                        res_str = re.sub(r'[^\d.]', '', val)
                        if res_str:
                            return float(res_str)
        
        # If no 'current' found, collect all values
        for item in spatial_res:
            if isinstance(item, dict):
                val = item.get('resolution')
            else:
                val = item
                
            if val is not None:
                if isinstance(val, (int, float)):
                    values.append(float(val))
                elif isinstance(val, str):
                    import re
                    res_str = re.sub(r'[^\d.]', '', val)
                    if res_str:
                        values.append(float(res_str))
        
        # Return the minimum resolution (highest detail) if multiple values
        if values:
            return min(values)
    
    return None


