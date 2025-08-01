#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Core Module - Centralized Chart Configuration and Theming
==============================================================

THE SINGLE SOURCE OF TRUTH for all chart styling, themes, colors, and layouts.
Eliminates hardcoded configurations and provides consistent theming across
all dashboard components with support for light/dark modes and accessibility.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List


# ==================== CORE THEME CONFIGURATION ====================

def detect_streamlit_theme() -> str:
    """
    Detects the current Streamlit theme mode.
    
    Returns:
        str: 'dark' if dark mode is detected, 'light' otherwise
    """
    try:
        # Check session state for theme preference if available
        if 'theme' in st.session_state:
            return st.session_state.theme
            
        # Default to light theme
        return 'light'
    except Exception:
        # Fallback to light theme if detection fails
        return 'light'


def get_theme_colors(theme: Optional[str] = None) -> Dict[str, str]:
    """
    Returns comprehensive color configuration for the specified theme.
    
    Args:
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict containing theme-appropriate colors for all UI elements
    """
    if theme is None:
        theme = detect_streamlit_theme()
    
    if theme == 'dark':
        return {
            # Background colors
            'background_color': '#0E1117',
            'paper_color': '#262730',
            'plot_bgcolor': '#1E1E1E',
            
            # Text colors
            'font_color': '#FAFAFA',
            'title_color': '#FFFFFF',
            'axis_color': '#E0E0E0', 
            'tick_color': '#CCCCCC',
            'annotation_color': '#B0B0B0',
            
            # Line and grid colors
            'grid_color': '#4A5568',
            'line_color': '#4A5568',
            'border_color': '#555555',
            
            # Interactive elements
            'hover_bgcolor': '#3A3A3A',
            'hover_bordercolor': '#666666',
        }
    else:  # light theme
        return {
            # Background colors
            'background_color': '#FFFFFF',
            'paper_color': '#FFFFFF', 
            'plot_bgcolor': '#FAFAFA',
            
            # Text colors
            'font_color': '#2D3748',
            'title_color': '#1A202C',
            'axis_color': '#4A5568',
            'tick_color': '#718096',
            'annotation_color': '#718096',
            
            # Line and grid colors
            'grid_color': '#E2E8F0',
            'line_color': '#CBD5E0',
            'border_color': '#E2E8F0',
            
            # Interactive elements
            'hover_bgcolor': '#F7FAFC',
            'hover_bordercolor': '#E2E8F0',
        }


# ==================== COLOR PALETTES ====================

def get_color_palette(category: str, count: int, theme: Optional[str] = None) -> List[str]:
    """
    Returns theme-appropriate color palette for different data categories.
    
    Args:
        category: Type of data ('initiatives', 'scopes', 'resolutions', 'general')
        count: Number of colors needed
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        List of hex color codes
    """
    if theme is None:
        theme = detect_streamlit_theme()
    
    # Predefined palettes optimized for accessibility and theme compatibility
    palettes = {
        'initiatives': {
            'light': [
                "#2563EB", "#DC2626", "#059669", "#D97706", "#7C3AED", 
                "#DB2777", "#0891B2", "#65A30D", "#C2410C", "#9333EA",
                "#BE185D", "#0E7490", "#84CC16", "#EA580C", "#A21CAF"
            ],
            'dark': [
                "#60A5FA", "#F87171", "#34D399", "#FBBF24", "#A78BFA",
                "#F472B6", "#22D3EE", "#A3E635", "#FB923C", "#C084FC", 
                "#EC4899", "#06B6D4", "#BFDB38", "#F97316", "#D946EF"
            ]
        },
        'scopes': {
            'light': {"Global": "#DC2626", "Nacional": "#2563EB", "Regional": "#059669"},
            'dark': {"Global": "#F87171", "Nacional": "#60A5FA", "Regional": "#34D399"}
        },
        'resolutions': {
            'light': {
                "High (<30m)": "#059669",      # Green for high resolution
                "Medium (30-99m)": "#D97706",  # Orange for medium  
                "Coarse (≥100m)": "#DC2626"   # Red for coarse
            },
            'dark': {
                "High (<30m)": "#34D399",      # Light green for high resolution
                "Medium (30-99m)": "#FBBF24",  # Light orange for medium
                "Coarse (≥100m)": "#F87171"   # Light red for coarse
            }
        },
        'general': {
            'light': [
                "#1F2937", "#374151", "#4B5563", "#6B7280", "#9CA3AF", 
                "#D1D5DB", "#E5E7EB", "#F3F4F6", "#F9FAFB"
            ],
            'dark': [
                "#F9FAFB", "#F3F4F6", "#E5E7EB", "#D1D5DB", "#9CA3AF", 
                "#6B7280", "#4B5563", "#374151", "#1F2937"
            ]
        }
    }
    
    if category in palettes:
        theme_palette = palettes[category][theme]
        if isinstance(theme_palette, dict):
            return list(theme_palette.values())[:count]
        else:
            # Extend palette if needed
            colors = (theme_palette * ((count // len(theme_palette)) + 1))[:count]
            return colors
    
    # Fallback to general palette
    general_colors = palettes['general'][theme]
    return (general_colors * ((count // len(general_colors)) + 1))[:count]


def get_scope_colors(theme: Optional[str] = None) -> Dict[str, str]:
    """Returns color mapping for scope categories."""
    if theme is None:
        theme = detect_streamlit_theme()
    
    if theme == 'light':
        return {"Global": "#DC2626", "Nacional": "#2563EB", "Regional": "#059669"}
    else:
        return {"Global": "#F87171", "Nacional": "#60A5FA", "Regional": "#34D399"}


def get_resolution_colors(theme: Optional[str] = None) -> Dict[str, str]:
    """Returns color mapping for resolution categories.""" 
    if theme is None:
        theme = detect_streamlit_theme()
    
    if theme == 'light':
        return {
            "High (<30m)": "#059669",
            "Medium (30-99m)": "#D97706", 
            "Coarse (≥100m)": "#DC2626"
        }
    else:
        return {
            "High (<30m)": "#34D399",
            "Medium (30-99m)": "#FBBF24",
            "Coarse (≥100m)": "#F87171"
        }


def get_initiative_color_map(initiative_names: List[str], theme: Optional[str] = None) -> Dict[str, str]:
    """
    Returns color mapping for initiative names.
    
    Args:
        initiative_names: List of initiative names
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict mapping initiative names to colors
    """
    colors = get_color_palette('initiatives', len(initiative_names), theme)
    return dict(zip(initiative_names, colors))


# ==================== FONT CONFIGURATION ====================

def get_font_config(element_type: str, theme: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns font configuration for different UI elements.
    
    Args:
        element_type: Type of element ('title', 'axis_title', 'tick', 'legend', 'annotation')
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict containing font configuration
    """
    if theme is None:
        theme = detect_streamlit_theme()
    
    theme_colors = get_theme_colors(theme)
    
    font_configs = {
        'title': {
            'family': 'Arial Black, Arial, sans-serif',
            'size': 20,
            'color': theme_colors['title_color']
        },
        'axis_title': {
            'family': 'Arial, sans-serif',
            'size': 16,
            'color': theme_colors['axis_color']
        },
        'tick': {
            'family': 'Arial, sans-serif', 
            'size': 14,
            'color': theme_colors['tick_color']
        },
        'tick_small': {
            'family': 'Arial, sans-serif',
            'size': 12,
            'color': theme_colors['tick_color']
        },
        'legend': {
            'family': 'Arial, sans-serif',
            'size': 13,
            'color': theme_colors['font_color']
        },
        'annotation': {
            'family': 'Arial, sans-serif',
            'size': 14,
            'color': theme_colors['annotation_color']
        },
        'annotation_small': {
            'family': 'Arial, sans-serif',
            'size': 12,
            'color': theme_colors['annotation_color']
        }
    }
    
    return font_configs.get(element_type, font_configs['tick'])


# ==================== LAYOUT CONFIGURATION ====================


# Centralized Visual Configuration with Dynamic Theme Support
def get_chart_config(theme: Optional[str] = None) -> Dict[str, Any]:
    """
    Gets the complete chart configuration with theme-appropriate colors.
    
    Args:
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict containing complete chart configuration
    """
    if theme is None:
        theme = detect_streamlit_theme()
        
    theme_colors = get_theme_colors(theme)
    
    return {
        'theme': theme_colors,
        'fonts': {
            'title': get_font_config('title', theme),
            'axis_title': get_font_config('axis_title', theme),
            'tick': get_font_config('tick', theme),
            'tick_small': get_font_config('tick_small', theme),
            'legend': get_font_config('legend', theme),
            'annotation': get_font_config('annotation', theme),
            'annotation_small': get_font_config('annotation_small', theme),
        },
        'margins': {
            'left': 180,
            'right': 50, 
            'top': 80,
            'bottom': 60,
        },
        'dimensions': {
            'default_width': 1000,
            'default_height': 600,
            'timeline_width': 1200,
            'small_chart_width': 800,
            'small_chart_height': 500,
        },
        'grid': {
            'width': 0.5,
            'show': True,
        }
    }


# ==================== THEME APPLICATION FUNCTIONS ====================

def apply_theme_to_figure(fig, theme: Optional[str] = None) -> None:
    """
    Applies complete theme styling to any Plotly figure.
    
    Args:
        fig: Plotly figure object
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
    """
    config = get_chart_config(theme)
    theme_colors = config['theme']
    
    fig.update_layout(
        plot_bgcolor=theme_colors['plot_bgcolor'],
        paper_bgcolor=theme_colors['paper_color'],
        font=dict(
            color=theme_colors['font_color'],
            family=config['fonts']['tick']['family']
        ),
        hoverlabel=dict(
            bgcolor=theme_colors['hover_bgcolor'],
            bordercolor=theme_colors['hover_bordercolor'],
            font=dict(color=theme_colors['font_color'])
        ),
        legend=dict(
            font=config['fonts']['legend'],
            bgcolor=theme_colors['paper_color'],
            bordercolor=theme_colors['border_color'],
            borderwidth=1
        )
    )
    
    # Apply grid and axis styling
    fig.update_xaxes(
        gridcolor=theme_colors['grid_color'],
        gridwidth=config['grid']['width'],
        showgrid=config['grid']['show'],
        showline=True,
        linewidth=1,
        linecolor=theme_colors['line_color'],
        mirror=True,
        tickfont=config['fonts']['tick']
    )
    
    fig.update_yaxes(
        gridcolor=theme_colors['grid_color'],
        gridwidth=config['grid']['width'],
        showgrid=config['grid']['show'],
        showline=True,
        linewidth=1,
        linecolor=theme_colors['line_color'],
        mirror=True,
        tickfont=config['fonts']['tick']
    )


def get_annotation_config(theme: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns configuration for chart annotations.
    
    Args:
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict containing annotation configuration
    """
    font_config = get_font_config('annotation', theme)
    
    return {
        'font': font_config,
        'showarrow': False,
        'xref': 'paper',
        'yref': 'paper',
        'x': 0.5,
        'y': 0.5,
        'xanchor': 'center',
        'yanchor': 'middle'
    }


def get_display_name(row: pd.Series, default_truncate_length: int = 10) -> str:
    """
    Gets the standardized display name for an initiative.
    
    Priority order: Acronym > Sigla > Name (truncated)
    
    Args:
        row: DataFrame row containing initiative data
        default_truncate_length: Length to truncate Name if no Acronym/Sigla
        
    Returns:
        str: Display name for the initiative
    """
    # Priority 1: Acronym (English standard)
    if 'Acronym' in row and pd.notna(row['Acronym']) and str(row['Acronym']).strip():
        return str(row['Acronym']).strip()
    
    # Priority 2: Sigla (Portuguese legacy)
    if 'Sigla' in row and pd.notna(row['Sigla']) and str(row['Sigla']).strip():
        return str(row['Sigla']).strip()
    
    # Priority 3: Name (fallback)
    name_col = None
    if 'Name' in row and pd.notna(row['Name']):
        name_col = 'Name'
    elif 'Nome' in row and pd.notna(row['Nome']):
        name_col = 'Nome'
    
    if name_col:
        full_name = str(row[name_col]).strip()
        return full_name[:default_truncate_length] if len(full_name) > default_truncate_length else full_name
    
    # Ultimate fallback
    return f"Initiative_{row.name if hasattr(row, 'name') else 'Unknown'}"


def create_display_name_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    Creates a mapping from full names to display names (acronyms).
    
    Args:
        df: DataFrame containing initiative data
        
    Returns:
        Dict mapping full names to display names
    """
    mapping = {}
    
    # Determine name column (English preferred)
    name_col = 'Name' if 'Name' in df.columns else 'Nome' if 'Nome' in df.columns else None
    
    if name_col is None:
        return mapping
    
    for _, row in df.iterrows():
        full_name = row[name_col]
        if pd.notna(full_name):
            display_name = get_display_name(row)
            mapping[str(full_name)] = display_name
    
    return mapping


def add_display_names_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a standardized 'Display_Name' column to the DataFrame.
    
    Args:
        df: DataFrame to process
        
    Returns:
        DataFrame with Display_Name column added
    """
    df = df.copy()
    df['Display_Name'] = df.apply(get_display_name, axis=1)
    return df


def apply_standard_layout(fig, title: str, xaxis_title: str = "", yaxis_title: str = "", 
                         chart_type: str = 'default', theme: Optional[str] = None) -> None:
    """
    Applies standardized layout configuration to a Plotly figure.
    
    Args:
        fig: Plotly figure object
        title: Chart title
        xaxis_title: X-axis title
        yaxis_title: Y-axis title
        chart_type: Type of chart ('timeline', 'small', 'default')
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
    """
    config = get_chart_config(theme)
    theme_colors = config['theme']
    
    # Determine dimensions
    width = config['dimensions']['default_width']
    height = config['dimensions']['default_height']
    
    if chart_type == 'timeline':
        width = config['dimensions']['timeline_width']
    elif chart_type == 'small':
        width = config['dimensions']['small_chart_width']
        height = config['dimensions']['small_chart_height']
    
    # Apply title and layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.02,
            'y': 0.95,
            'font': config['fonts']['title']
        },
        plot_bgcolor=theme_colors['plot_bgcolor'],
        paper_bgcolor=theme_colors['paper_color'],
        font=dict(
            color=theme_colors['font_color'],
            family=config['fonts']['tick']['family']
        ),
        height=height,
        width=width,
        margin=dict(
            l=config['margins']['left'],
            r=config['margins']['right'],
            t=config['margins']['top'],
            b=config['margins']['bottom']
        ),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor=theme_colors['hover_bgcolor'],
            bordercolor=theme_colors['hover_bordercolor'],
            font=dict(color=theme_colors['font_color'])
        ),
        legend=dict(
            font=config['fonts']['legend'],
            bgcolor=theme_colors['paper_color'],
            bordercolor=theme_colors['border_color'],
            borderwidth=1
        )
    )
    
    # Apply axis styling with titles
    if xaxis_title:
        fig.update_xaxes(
            title=dict(
                text=xaxis_title,
                font=config['fonts']['axis_title']
            )
        )
        
    if yaxis_title:
        fig.update_yaxes(
            title=dict(
                text=yaxis_title,
                font=config['fonts']['axis_title']
            )
        )
    
    # Apply grid and line styling  
    fig.update_xaxes(
        gridcolor=theme_colors['grid_color'],
        gridwidth=config['grid']['width'],
        showgrid=config['grid']['show'],
        showline=True,
        linewidth=1,
        linecolor=theme_colors['line_color'],
        mirror=True,
        tickfont=config['fonts']['tick']
    )
    
    fig.update_yaxes(
        gridcolor=theme_colors['grid_color'],
        gridwidth=config['grid']['width'],
        showgrid=config['grid']['show'],
        showline=True,
        linewidth=1,
        linecolor=theme_colors['line_color'],
        mirror=True,
        tickfont=config['fonts']['tick']
    )

    # Chart-specific adjustments
    if chart_type == 'timeline':
        fig.update_yaxes(tickfont=config['fonts']['tick_small'])
    elif chart_type == 'small':
        fig.update_xaxes(tickfont=config['fonts']['tick_small'])
        fig.update_yaxes(tickfont=config['fonts']['tick_small'])



def get_color_mapping(names_list: List[str], theme: Optional[str] = None) -> Dict[str, str]:
    """
    Gets consistent color mapping for initiative names.
    
    Args:
        names_list: List of initiative names
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Dict mapping names to colors
    """
    return get_initiative_color_map(names_list, theme)


def set_theme_preference(theme: str) -> None:
    """
    Sets the theme preference in Streamlit session state.
    
    Args:
        theme: 'light' or 'dark'
    """
    try:
        st.session_state.theme = theme
    except Exception:
        # If not in Streamlit context, silently ignore
        pass


# ==================== UTILITY FUNCTIONS ====================

def add_no_data_annotation(fig, message: str = "No data available for the selected filters.", 
                          theme: Optional[str] = None) -> None:
    """
    Adds a 'no data' annotation to a figure with theme-appropriate styling.
    
    Args:
        fig: Plotly figure object
        message: Message to display
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
    """
    annotation_config = get_annotation_config(theme)
    annotation_config['text'] = message
    fig.add_annotation(**annotation_config)


def create_empty_figure(title: str = "No Data", message: str = "No data available", 
                       theme: Optional[str] = None):
    """
    Creates an empty figure with consistent theming for no-data scenarios.
    
    Args:
        title: Chart title
        message: No-data message  
        theme: Theme name ('light' or 'dark'). Auto-detects if None.
        
    Returns:
        Configured Plotly figure
    """
    fig = go.Figure()
    apply_standard_layout(fig, title=title, theme=theme)
    add_no_data_annotation(fig, message, theme)
    return fig


def prepare_temporal_display_data(metadata: Dict[str, Any], df_original: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Prepares temporal data with standardized display names.
    
    Args:
        metadata: Initiative metadata dictionary
        df_original: Original DataFrame (optional, for acronym mapping)
        
    Returns:
        DataFrame with temporal data and display names
    """
    # Create name to acronym mapping from DataFrame if available
    name_to_display = {}
    if df_original is not None and not df_original.empty:
        name_to_display = create_display_name_mapping(df_original)
    
    data_list = []
    
    for nome, meta_data in metadata.items():
        anos_disponiveis = meta_data.get('anos_disponiveis', meta_data.get('available_years', []))
        
        if not anos_disponiveis:
            continue
            
        # Convert to list of integers
        anos_int = []
        for ano in anos_disponiveis:
            if isinstance(ano, (int, float)) and pd.notna(ano):
                anos_int.append(int(ano))
        
        if not anos_int:
            continue
            
        anos_int = sorted(anos_int)
        
        # Calculate temporal statistics
        primeiro_ano = min(anos_int)
        ultimo_ano = max(anos_int)
        span_total = ultimo_ano - primeiro_ano + 1
        anos_com_dados = len(anos_int)
        
        # Calculate gaps
        anos_esperados = set(range(primeiro_ano, ultimo_ano + 1))
        anos_faltando = anos_esperados - set(anos_int)
        maior_lacuna = _calculate_largest_gap(anos_int) if len(anos_int) > 1 else 0
        
        # Get display name (acronym preferred)
        display_name = name_to_display.get(nome, nome[:10])
        
        data_list.append({
            'Nome': nome,
            'Display_Name': display_name,
            'Primeiro_Ano': primeiro_ano,
            'Ultimo_Ano': ultimo_ano,
            'Span_Total': span_total,
            'Anos_Com_Dados': anos_com_dados,
            'Anos_Faltando': len(anos_faltando),
            'Cobertura_Percentual': (anos_com_dados / span_total) * 100,
            'Maior_Lacuna': maior_lacuna,
            'Anos_Lista': anos_int,
            'Tipo': meta_data.get('type', meta_data.get('tipo', 'Not specified'))
        })
    
    return pd.DataFrame(data_list)


def _calculate_largest_gap(anos_list: list) -> int:
    """Calculate the largest consecutive gap in a list of years"""
    if len(anos_list) <= 1:
        return 0
    
    anos_sorted = sorted(anos_list)
    gaps = []
    
    for i in range(len(anos_sorted) - 1):
        gap = anos_sorted[i + 1] - anos_sorted[i] - 1
        if gap > 0:
            gaps.append(gap)
    
    return max(gaps) if gaps else 0
