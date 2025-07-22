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


# Centralized Visual Configuration - Simplified
CHART_CONFIG = {
    'font_family': 'Times New Roman',
    'font_color': '#2D3748',
    'axis': {
        'title_font_size': 22,    # Títulos dos eixos: tamanho 25, negrito
        'tick_font_size': 20,     # Conteúdo dos eixos: tamanho 20
    },
    'layout': {
        'showgrid': False,        # Remove o grid dos eixos
        'gridcolor': '#E5ECF6',   # Cor do grid (quando ativado)
        'ticks': 'outside',       # Ticks externos
        'ticklen': 8,             # Tamanho dos ticks
        'tickcolor': 'black',     # Cor dos ticks
        'tickangle': 45,          # Ângulo de 45 graus para os rótulos dos eixos
        'showline': True,         # Mostra linha dos eixos
        'linewidth': 0,           # Espessura da linha dos eixos
        'zeroline': False         # Remove linha do zero
    },
    'margins': {
        'bottom': 80,            # Margem inferior - espaço para título do eixo X
        'left': 80,              # Margem esquerda - espaço para título do eixo Y
        'right': 120,             # Margem direita aumentada para colorbar e título
        'top': 40                 # Margem superior
    },
    'legend': {
        'font_size': 16,          # Tamanho da fonte dos itens da legenda
        'title_font_size': 18,    # Tamanho da fonte do título da legenda
        'item_spacing': 5,        # Espaçamento entre itens da legenda
        'title_spacing': 10,      # Espaçamento entre título e itens da legenda
        'symbol_width': 30,       # Largura dos símbolos da legenda
        'indentation': 0          # Indentação dos itens em relação ao título
    },
    'colorbar': {
        'title_font_size': 22,    # Tamanho da fonte do título da colorbar (mesmo da legenda)
        'tick_font_size': 20,     # Tamanho da fonte dos ticks da colorbar (mesmo dos itens da legenda)
        'thickness': 20,          # Espessura da colorbar
        'len': 0.8,               # Comprimento da colorbar (80% da altura do gráfico)
        'x_position': 1.02,       # Posição X da colorbar (similar à legenda direita)
        'y_position': 0.5,        # Posição Y da colorbar (centro)
        'title_side': 'top',      # Título sempre acima da colorbar
        'x_anchor': 'left',       # Ancoragem X
        'y_anchor': 'middle'      # Ancoragem Y
    },
    'dimensions': {
        # Dimensões padrão para diferentes tipos de gráfico
        'default': {'width': 800, 'height': 600},      # Padrão retangular
        'square': {'width': 600, 'height': 600},       # Quadrado
        'tall': {'width': 600, 'height': 800},         # Retangular alto
        'wide': {'width': 1000, 'height': 500},        # Retangular largo
        
        # Configurações específicas por tipo de gráfico
        'bar_chart': {
            'base': {'width': 1400, 'height': 600},
            'min_height': 400,
            'height_per_item': 40,  # Altura adicional por item (para muitos itens)
            'max_size': 1200,
        },
        'line_chart': {
            'base': {'width': 1400, 'height': 600},
            'min_width': 600,
            'max_width': 1400
        },
        'heatmap': {
            'base': {'width': 1200, 'height': 800},
            'min_size': 400,
            'size_per_item': 50,    # Tamanho adicional por item na matriz
            'max_size': 1400,
            'aspect_ratio': 1.0     # Mantém proporção quadrada
        },
        'correlation_matrix': {
            'base': {'width': 600, 'height': 600},  # Sempre quadrado
            'min_size': 400,
            'size_per_item': 60,
            'max_size': 1400,
            'aspect_ratio': 1.0
        },
        'radar_chart': {
            'base': {'width': 600, 'height': 600},  # Sempre quadrado
            'min_size': 500,
            'max_size': 1400
        },
        'scatter_plot': {
            'base': {'width': 800, 'height': 600},
            'max_size': 1400
        }
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


def apply_standard_layout(fig, xaxis_title: str = "", yaxis_title: str = "", xaxis_tickangle: Optional[int] = None, 
                         legend_title: str = "", legend_position: str = "right", show_legend: bool = True,
                         chart_type: str = "default", num_items: Optional[int] = None, 
                         aspect_override: Optional[str] = None, 
                         custom_margins: Optional[Dict[str, int]] = None) -> None:
    """
    Applies standardized layout configuration to a Plotly figure.
    
    Configurações padronizadas:
    - Fonte: Times New Roman para todo o gráfico
    - Sem título na figura
    - Títulos dos eixos: negrito, tamanho 16
    - Conteúdo dos eixos: tamanho 14
    - Layout visual padrão: grid, ticks, linhas dos eixos, etc.
    - Margem inferior aumentada para acomodar título do eixo X
    - Ângulo padrão de 45 graus para rótulos do eixo X
    - Legenda padronizada com tamanho e espaçamento consistentes
    - Dimensões padronizadas baseadas no tipo de gráfico e número de itens
    
    Args:
        fig: Plotly figure object
        xaxis_title: X-axis title
        yaxis_title: Y-axis title
        xaxis_tickangle: Override for x-axis tick angle (default: uses standard 45 degrees)
        legend_title: Legend title (optional)
        legend_position: Legend position ("right", "top", "bottom", "left")
        show_legend: Whether to show the legend
        chart_type: Type of chart for dimension calculation ("bar_chart", "heatmap", etc.)
        num_items: Number of data items for dynamic sizing
        aspect_override: Override aspect ratio ("square", "tall", "wide", "default")
        custom_margins: Custom margins dict to override defaults (e.g., {"right": 200})
    """
    config = CHART_CONFIG    # Configuração global da fonte e margens
    
    # Get standardized dimensions
    dimensions = get_standard_dimensions(
        chart_type=chart_type,
        num_items=num_items,
        aspect_override=aspect_override
    )
    
    # Prepare margins - use custom margins if provided, otherwise use defaults
    if custom_margins:
        margins = {
            'b': custom_margins.get('bottom', config['margins']['bottom']),
            'l': custom_margins.get('left', config['margins']['left']),
            'r': custom_margins.get('right', config['margins']['right']),
            't': custom_margins.get('top', config['margins']['top'])
        }
    else:
        margins = {
            'b': config['margins']['bottom'],
            'l': config['margins']['left'],
            'r': config['margins']['right'],
            't': config['margins']['top']
        }
    
    fig.update_layout(
        font=dict(
            family=config['font_family'],
            color=config['font_color']
        ),
        margin=margins,                     # Use prepared margins
        width=dimensions['width'],          # Largura padronizada
        height=dimensions['height']         # Altura padronizada
    )

    # Aplicar configuração padronizada da legenda
    if show_legend:
        legend_config = get_standard_legend_config(
            title=legend_title,
            position=legend_position
        )
        fig.update_layout(
            showlegend=True,
            legend=legend_config
        )
    else:
        fig.update_layout(showlegend=False)

    # Configuração padrão dos eixos (layout visual)
    layout_config = config['layout']
    
    # Aplicar configurações do eixo X
    xaxis_config = dict(
        showgrid=layout_config['showgrid'],
        gridcolor=layout_config['gridcolor'],
        ticks=layout_config['ticks'],
        ticklen=layout_config['ticklen'],
        tickcolor=layout_config['tickcolor'],
        tickangle=xaxis_tickangle if xaxis_tickangle is not None else layout_config['tickangle'],  # Use override or standard 45 degrees
        showline=layout_config['showline'],
        linewidth=layout_config['linewidth'],
        zeroline=layout_config['zeroline'],
        tickfont=dict(
            size=config['axis']['tick_font_size'],
            family=config['font_family'],
            color=config['font_color']
        )
    )
    
    # Adicionar título do eixo X se fornecido
    if xaxis_title:
        xaxis_config['title'] = dict(
            text=xaxis_title,
            font=dict(
                size=config['axis']['title_font_size'],
                family=config['font_family'],
                color=config['font_color'],
                weight='bold'
            ),
            standoff=25  # Espaçamento entre título e ticks
        )
    
    fig.update_xaxes(**xaxis_config)

    # Aplicar configurações do eixo Y
    yaxis_config = dict(
        showgrid=layout_config['showgrid'],
        gridcolor=layout_config['gridcolor'],
        ticks=layout_config['ticks'],
        ticklen=layout_config['ticklen'],
        tickcolor=layout_config['tickcolor'],
        showline=layout_config['showline'],
        linewidth=layout_config['linewidth'],
        zeroline=layout_config['zeroline'],
        tickfont=dict(
            size=config['axis']['tick_font_size'],
            family=config['font_family'],
            color=config['font_color']
        )
    )
    
    # Adicionar título do eixo Y se fornecido
    if yaxis_title:
        yaxis_config['title'] = dict(
            text=yaxis_title,
            font=dict(
                size=config['axis']['title_font_size'],
                family=config['font_family'],
                color=config['font_color'],
                weight='bold'
            ),
            standoff=25  # Espaçamento entre título e ticks
        )
    
    fig.update_yaxes(**yaxis_config)



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


def get_standard_legend_config(title: str = "", orientation: str = "v", position: str = "right") -> Dict[str, Any]:
    """
    Gets standardized legend configuration for charts.
    
    Args:
        title: Legend title text
        orientation: "v" for vertical, "h" for horizontal
        position: "right", "top", "bottom", "left"
        
    Returns:
        Dict with legend configuration
    """
    config = CHART_CONFIG
    
    # Base legend configuration using standardized values
    legend_config = {
        "orientation": orientation,
        "bgcolor": "rgba(255,255,255,0)",  # Transparent background - no frame
        "borderwidth": 0,  # Remove border completely
        "font": {
            "family": config['font_family'],
            "size": config['legend']['font_size'],
            "color": config['font_color']
        },
        "itemsizing": "constant",  # Ensures consistent symbol sizes
        "itemwidth": config['legend']['symbol_width'],  # Width of legend symbols
        "tracegroupgap": config['legend']['item_spacing'],  # Spacing between legend items
        "indentation": config['legend']['indentation']  # Indentation from title
    }
    
    # Add title if provided
    if title:
        legend_config["title"] = {
            "text": f"<b>{title}</b>",
            "font": {
                "family": config['font_family'],
                "size": config['legend']['title_font_size'],
                "color": config['font_color']
            },
            "side": "top"
        }
        # Add spacing between title and items
        legend_config["tracegroupgap"] = config['legend']['title_spacing']
    
    # Position-specific settings
    if position == "right":
        legend_config.update({
            "yanchor": "top",
            "y": 1,
            "xanchor": "left", 
            "x": 1.02
        })
    elif position == "top":
        legend_config.update({
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5
        })
    elif position == "bottom":
        legend_config.update({
            "orientation": "h",
            "yanchor": "top",
            "y": -0.1,
            "xanchor": "center",
            "x": 0.5
        })
    elif position == "left":
        legend_config.update({
            "yanchor": "top",
            "y": 1,
            "xanchor": "right",
            "x": -0.02
        })
    
    return legend_config


def get_standard_colorbar_config(title: str = "Values", 
                               custom_tickvals: Optional[list] = None,
                               custom_ticktext: Optional[list] = None,
                               position: str = "right") -> Dict[str, Any]:
    """
    Gets standardized colorbar configuration for heatmaps, following the same pattern as legend config.
    
    Args:
        title: Título da colorbar
        custom_tickvals: Valores customizados para os ticks
        custom_ticktext: Textos customizados para os ticks
        position: Posição da colorbar ('right', 'top', 'bottom', 'left')
        
    Returns:
        Dict with colorbar configuration following the same standards as legend
    """
    config = CHART_CONFIG
    
    # Base colorbar configuration using the same font standards as legend
    colorbar_config = {
        'title': {
            'text': f"<b>{title}</b><br><br><br><br><br><br><br><br><br><br>",  # Adiciona espaçamento com quebras de linha
            'side': config['colorbar']['title_side'],
            'font': {
                'size': config['colorbar']['title_font_size'],  # Mesmo tamanho do título da legenda
                'family': config['font_family'],                # Mesma fonte global
                'color': config['font_color']                   # Mesma cor global
            }
        },
        'tickfont': {
            'size': config['colorbar']['tick_font_size'],       # Mesmo tamanho dos itens da legenda
            'family': config['font_family'],                    # Mesma fonte global
            'color': config['font_color']                       # Mesma cor global
        },
        'thickness': config['colorbar']['thickness'],
        'len': config['colorbar']['len'],
        'xanchor': config['colorbar']['x_anchor'],
        'x': config['colorbar']['x_position'],
        'yanchor': config['colorbar']['y_anchor'],
        'y': config['colorbar']['y_position']
    }
    
    # Adicionar ticks customizados se fornecidos
    if custom_tickvals is not None:
        colorbar_config['tickvals'] = custom_tickvals
    if custom_ticktext is not None:
        colorbar_config['ticktext'] = custom_ticktext
    
    # Position-specific settings (similar to legend positioning)
    if position == "top":
        colorbar_config.update({
            'orientation': 'h',
            'xanchor': 'center',
            'x': 0.5,
            'yanchor': 'bottom',
            'y': 1.02,
            'title': {
                **colorbar_config['title'],
                'side': 'top'
            }
        })
    elif position == "bottom":
        colorbar_config.update({
            'orientation': 'h',
            'xanchor': 'center',
            'x': 0.5,
            'yanchor': 'top',
            'y': -0.1,
            'title': {
                **colorbar_config['title'],
                'side': 'bottom'
            }
        })
    elif position == "left":
        colorbar_config.update({
            'xanchor': 'right',
            'x': -0.02,
            'yanchor': 'middle',
            'y': 0.5,
            'title': {
                **colorbar_config['title'],
                'side': 'left'
            }
        })
    # position == "right" é o padrão, já configurado acima
        
    return colorbar_config


def apply_standard_colorbar(fig, title: str = "Values",
                          custom_tickvals: Optional[list] = None,
                          custom_ticktext: Optional[list] = None,
                          position: str = "right") -> None:
    """
    Applies standardized colorbar configuration to a Plotly figure.
    
    Args:
        fig: Figura Plotly
        title: Título da colorbar
        custom_tickvals: Valores customizados para os ticks
        custom_ticktext: Textos customizados para os ticks
        position: Posição da colorbar
    """
    colorbar_config = get_standard_colorbar_config(title, custom_tickvals, custom_ticktext, position)
    
    # Atualizar colorbar se existir
    for trace in fig.data:
        if hasattr(trace, 'colorbar') and trace.colorbar is not None:
            trace.update(colorbar=colorbar_config)
        elif hasattr(trace, 'marker') and hasattr(trace.marker, 'colorbar'):
            trace.marker.update(colorbar=colorbar_config)


def get_standard_bar_config() -> Dict[str, Any]:
    """
    Gets standardized bar chart configuration.
    
    Returns:
        Dict with bar chart configuration
    """
    return {
        "bargap": 0.3,      # Gap between bars (30% of bar width)
        "bargroupgap": 0.1, # Gap between bar groups (10% of bar width)
        "barmode": "group"  # Default bar mode (can be overridden)
    }


def apply_standard_legend(fig, title: str = "", position: str = "right", show_legend: bool = True) -> None:
    """
    Applies standardized legend configuration to a Plotly figure.
    
    Args:
        fig: Plotly figure object
        title: Legend title (optional)
        position: Legend position ("right", "top", "bottom", "left")
        show_legend: Whether to show the legend
    """
    if show_legend:
        legend_config = get_standard_legend_config(title=title, position=position)
        fig.update_layout(
            showlegend=True,
            legend=legend_config
        )
    else:
        fig.update_layout(showlegend=False)


def get_standard_dimensions(chart_type: str = "default", num_items: Optional[int] = None, 
                          aspect_override: Optional[str] = None) -> Dict[str, int]:
    """
    Gets standardized dimensions for different chart types with dynamic sizing based on data.
    
    Args:
        chart_type: Type of chart ("bar_chart", "heatmap", "correlation_matrix", "line_chart", 
                   "radar_chart", "scatter_plot", or "default")
        num_items: Number of data items (for dynamic sizing)
        aspect_override: Override aspect ratio ("square", "tall", "wide", "default")
        
    Returns:
        Dict with 'width' and 'height' keys containing pixel dimensions
    """
    config = CHART_CONFIG['dimensions']
    
    # Handle aspect ratio overrides first
    if aspect_override in ['square', 'tall', 'wide', 'default']:
        return config[aspect_override].copy()
    
    # Get chart-specific configuration
    if chart_type in config and isinstance(config[chart_type], dict) and 'base' in config[chart_type]:
        chart_config = config[chart_type]
        base_dims = chart_config['base'].copy()
        
        # Apply dynamic sizing based on chart type and number of items
        if num_items is not None and num_items > 0:
            
            if chart_type == "bar_chart":
                # Dynamic height for bar charts based on number of bars
                min_height = chart_config.get('min_height', 400)
                max_height = chart_config.get('max_height', 1200)
                height_per_item = chart_config.get('height_per_item', 40)
                
                # Calculate dynamic height: base + additional per item
                dynamic_height = base_dims['height'] + (num_items - 5) * height_per_item
                base_dims['height'] = max(min_height, min(dynamic_height, max_height))
            
            elif chart_type in ["heatmap", "correlation_matrix"]:
                # Square sizing for matrices based on number of items
                min_size = chart_config.get('min_size', 400)
                max_size = chart_config.get('max_size', 1000)
                size_per_item = chart_config.get('size_per_item', 50)
                
                # Calculate square dimensions
                dynamic_size = min_size + num_items * size_per_item
                final_size = max(min_size, min(dynamic_size, max_size))
                
                # Maintain aspect ratio if specified
                if chart_config.get('aspect_ratio') == 1.0:
                    base_dims['width'] = final_size
                    base_dims['height'] = final_size
            
            elif chart_type == "line_chart":
                # Dynamic width for line charts with many series/time points
                min_width = chart_config.get('min_width', 600)
                max_width = chart_config.get('max_width', 1400)
                
                if num_items > 10:  # Many time points or series
                    dynamic_width = base_dims['width'] + (num_items - 10) * 20
                    base_dims['width'] = max(min_width, min(dynamic_width, max_width))
        
        return base_dims
    
    # Fallback to default dimensions
    return config['default'].copy()


def apply_standard_dimensions(fig, chart_type: str = "default", num_items: Optional[int] = None, 
                            aspect_override: Optional[str] = None) -> None:
    """
    Applies standardized dimensions to a Plotly figure.
    
    Args:
        fig: Plotly figure object
        chart_type: Type of chart for dimension calculation ("bar_chart", "heatmap", etc.)
        num_items: Number of data items for dynamic sizing
        aspect_override: Override aspect ratio ("square", "tall", "wide", "default")
    """
    dimensions = get_standard_dimensions(
        chart_type=chart_type,
        num_items=num_items,
        aspect_override=aspect_override
    )
    
    fig.update_layout(
        width=dimensions['width'],
        height=dimensions['height']
    )


def apply_heatmap_with_performance_title(fig, 
                                        custom_tickvals: Optional[list] = None,
                                        custom_ticktext: Optional[list] = None,
                                        xaxis_title: str = "Metrics", 
                                        yaxis_title: str = "Initiative",
                                        num_items: Optional[int] = None,
                                        title_x: float = 1.04,
                                        title_y: float = 0.9) -> None:
    """
    Função unificada para heatmap com título "Performance Score" customizável.
    
    Args:
        fig: Figura Plotly
        custom_tickvals: Valores customizados para os ticks
        custom_ticktext: Textos customizados para os ticks
        xaxis_title: Título do eixo X
        yaxis_title: Título do eixo Y
        num_items: Número de itens para dimensionamento dinâmico
        title_x: Posição horizontal do título (1.0 = borda direita do gráfico)
        title_y: Posição vertical do título (1.0 = topo, 0.0 = base)
    """
    config = CHART_CONFIG
    
    # 1. Configurar colorbar sem título
    colorbar_config = {
        'tickfont': {
            'size': config['colorbar']['tick_font_size'],
            'family': config['font_family'],
            'color': config['font_color']
        },
        'thickness': config['colorbar']['thickness'],
        'len': config['colorbar']['len'],
        'xanchor': config['colorbar']['x_anchor'],
        'x': config['colorbar']['x_position'],
        'yanchor': config['colorbar']['y_anchor'],
        'y': config['colorbar']['y_position']
    }
    
    if custom_tickvals is not None:
        colorbar_config['tickvals'] = custom_tickvals
    if custom_ticktext is not None:
        colorbar_config['ticktext'] = custom_ticktext
    
    # Aplicar colorbar nas traces
    for trace in fig.data:
        if hasattr(trace, 'colorbar'):
            trace.update(colorbar=colorbar_config)
        elif hasattr(trace, 'marker') and hasattr(trace.marker, 'colorbar'):
            trace.marker.update(colorbar=colorbar_config)
    
    # 2. Adicionar título "Performance Score" na posição especificada
    fig.add_annotation(
        text="<b>Performance Score</b>",
        x=title_x,
        y=title_y,
        xref="paper", 
        yref="paper",
        xanchor="left",
        yanchor="top",
        showarrow=False,
        font=dict(
            size=config['colorbar']['title_font_size'],
            family=config['font_family'],
            color=config['font_color']
        )
    )
    
    # 3. Aplicar layout otimizado para heatmap
    colorbar_margins = {
        'bottom': 80,
        'left': 200,
        'right': 200,
        'top': 60
    }
    
    apply_standard_layout(
        fig, 
        xaxis_title=xaxis_title, 
        yaxis_title=yaxis_title, 
        xaxis_tickangle=0,
        legend_title="", 
        show_legend=False,
        chart_type="heatmap", 
        num_items=num_items,
        custom_margins=colorbar_margins
    )
    
    # 4. Configurações específicas do heatmap
    fig.update_layout(
        xaxis=dict(tickangle=0, side='bottom'), 
        yaxis=dict(type='category', autorange='reversed', side='left')
    )
