#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Core Module - Centralized Chart Configuration and Display Names
=====================================================================

Centralizes chart configuration, display name logic, and styling 
to ensure consistency across all charts (Streamlit and non-Streamlit).

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import pandas as pd
from typing import Dict, Any, Optional
from scripts.utilities.config import get_initiative_color_map


# Centralized Visual Configuration
CHART_CONFIG = {
    'theme': {
        'background_color': '#FFFFFF',
        'paper_color': '#FFFFFF',
        'font_family': 'Arial',
        'font_color': '#2D3748',
        'grid_color': '#E2E8F0',
        'grid_width': 0.5,
        'line_color': '#E2E8F0',
    },
    'title': {
        'font_size': 18,
        'font_family': 'Arial Black',
        'font_color': '#2D3748',
        'x_position': 0.02,
        'y_position': 0.95,
    },
    'axis': {
        'title_font_size': 14,
        'tick_font_size': 12,
        'tick_font_size_small': 11,
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
        'timeline_width': 1000,
        'small_chart_width': 800,
        'small_chart_height': 600,
    }
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
                         chart_type: str = 'default') -> None:
    """
    Applies standardized layout configuration to a Plotly figure.
    
    Args:
        fig: Plotly figure object
        title: Chart title
        xaxis_title: X-axis title
        yaxis_title: Y-axis title
        chart_type: Type of chart ('timeline', 'small', 'default')
    """
    config = CHART_CONFIG
    
    # Determine dimensions
    width = config['dimensions']['default_width']
    height = config['dimensions']['default_height']
    
    if chart_type == 'timeline':
        width = config['dimensions']['timeline_width']
    elif chart_type == 'small':
        width = config['dimensions']['small_chart_width']
        height = config['dimensions']['small_chart_height']
    
    fig.update_layout(
        title={
            'text': title,
            'x': config['title']['x_position'],
            'y': config['title']['y_position'],
            'font': {
                'size': config['title']['font_size'],
                'color': config['title']['font_color'],
                'family': config['title']['font_family']
            }
        },
        plot_bgcolor=config['theme']['background_color'],
        paper_bgcolor=config['theme']['paper_color'],
        font=dict(
            color=config['theme']['font_color'],
            family=config['theme']['font_family']
        ),
        height=height,
        width=width,
        margin=dict(
            l=config['margins']['left'],
            r=config['margins']['right'],
            t=config['margins']['top'],
            b=config['margins']['bottom']
        ),
        hovermode='closest'
    )
    
    # Apply axis styling
    if xaxis_title or yaxis_title:
        fig.update_xaxes(
            title=dict(
                text=xaxis_title,
                font=dict(
                    size=config['axis']['title_font_size'],
                    color=config['theme']['font_color']
                )
            ),
            gridcolor=config['theme']['grid_color'],
            gridwidth=config['theme']['grid_width'],
            tickfont=dict(
                size=config['axis']['tick_font_size'],
                color=config['theme']['font_color']
            ),
            showgrid=True,
            zeroline=False,
            linecolor=config['theme']['line_color']
        )
        
        fig.update_yaxes(
            title=dict(
                text=yaxis_title,
                font=dict(
                    size=config['axis']['title_font_size'],
                    color=config['theme']['font_color']
                )
            ),
            gridcolor=config['theme']['grid_color'],
            gridwidth=config['theme']['grid_width'],
            tickfont=dict(
                size=config['axis']['tick_font_size_small'],
                color=config['theme']['font_color']
            ),
            showgrid=True,
            zeroline=False,
            linecolor=config['theme']['line_color']
        )


def get_color_mapping(names_list: list) -> Dict[str, str]:
    """
    Gets consistent color mapping for initiative names.
    
    Args:
        names_list: List of initiative names
        
    Returns:
        Dict mapping names to colors
    """
    return get_initiative_color_map(names_list)


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
