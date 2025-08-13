#!/usr/bin/env python3
"""
Table Chart Utilities
=====================

Generates beautiful tables as Plotly figures for various data displays.

Author: LANDAGRI-B Project Team 
Date: 2024
"""

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from .modern_themes import get_modern_colors, apply_modern_theme

# Configurações de cores modernas para tabelas
modern_colors = {
    "text_primary": "#1f2937",
    "border": "#e5e7eb"
}

# Configuração padrão para tabelas modernas
modern_table_config = {
    "responsive": True,
    "displayModeBar": False
}


def create_brazilian_regions_table() -> go.Figure:
    """
    Creates a beautiful table showing Brazilian regions, states and their abbreviations.

    Returns:
        go.Figure: Plotly table figure with Brazilian geographic information
    """

    # Data for Brazilian regions, states and abbreviations
    brazilian_data = [
        # Norte
        ("Norte", "Acre", "AC"),
        ("Norte", "Amapá", "AP"),
        ("Norte", "Amazonas", "AM"),
        ("Norte", "Pará", "PA"),
        ("Norte", "Rondônia", "RO"),
        ("Norte", "Roraima", "RR"),
        ("Norte", "Tocantins", "TO"),
        # Nordeste
        ("Nordeste", "Alagoas", "AL"),
        ("Nordeste", "Bahia", "BA"),
        ("Nordeste", "Ceará", "CE"),
        ("Nordeste", "Maranhão", "MA"),
        ("Nordeste", "Paraíba", "PB"),
        ("Nordeste", "Pernambuco", "PE"),
        ("Nordeste", "Piauí", "PI"),
        ("Nordeste", "Rio Grande do Norte", "RN"),
        ("Nordeste", "Sergipe", "SE"),
        # Centro-Oeste
        ("Centro-Oeste", "Distrito Federal", "DF"),
        ("Centro-Oeste", "Goiás", "GO"),
        ("Centro-Oeste", "Mato Grosso", "MT"),
        ("Centro-Oeste", "Mato Grosso do Sul", "MS"),
        # Sudeste
        ("Sudeste", "Espírito Santo", "ES"),
        ("Sudeste", "Minas Gerais", "MG"),
        ("Sudeste", "Rio de Janeiro", "RJ"),
        ("Sudeste", "São Paulo", "SP"),
        # Sul
        ("Sul", "Paraná", "PR"),
        ("Sul", "Rio Grande do Sul", "RS"),
        ("Sul", "Santa Catarina", "SC"),
    ]

    # Create DataFrame
    df = pd.DataFrame(brazilian_data, columns=["Região", "Estado", "Sigla"])

    # Define colors for each region
    region_colors = {
        "Norte": "#2E8B57",  # Sea Green
        "Nordeste": "#FF6347",  # Tomato
        "Centro-Oeste": "#FFD700",  # Gold
        "Sudeste": "#4169E1",  # Royal Blue
        "Sul": "#9932CC",  # Dark Orchid
    }

    # Create color arrays for each cell
    fill_colors = []
    text_colors = []

    for _, row in df.iterrows():
        region = row["Região"]
        base_color = region_colors.get(region, "#F0F0F0")

        # Add colors for each column (Region, State, Abbreviation)
        fill_colors.append([base_color, "#FFFFFF", "#F8F9FA"])
        text_colors.append(["white", "black", "black"])

    # Transpose color arrays to match table structure
    fill_colors_transposed = list(map(list, zip(*fill_colors)))
    text_colors_transposed = list(map(list, zip(*text_colors)))

    # Create the table with modern styling
    config = modern_table_config

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[150, 200, 80],
                header={
                    "values": ["<b>Região</b>", "<b>Estado</b>", "<b>Sigla</b>"],
                    "fill_color": config["header"]["fill_color"],
                    "font": config["header"]["font"],
                    "align": config["header"]["align"],
                    "height": config["header"]["height"],
                    "line": {"width": 2, "color": "white"},
                },
                cells={
                    "values": [df["Região"], df["Estado"], df["Sigla"]],
                    "fill_color": fill_colors_transposed,
                    "font": {
                        "color": text_colors_transposed,
                        "size": 14,
                        "family": "Inter, system-ui, sans-serif",
                    },
                    "align": ["center", "left", "center"],
                    "height": config["cells"]["height"],
                    "line": {"width": 1, "color": "#ECF0F1"},
                },
            )
        ]
    )

    # Update layout for better appearance with modern styling
    fig.update_layout(
        title={
            "text": "<b>Estados e Regiões do Brasil</b>",
            "x": 0.5,
            "font": {
                "size": 20,
                "color": modern_colors["text_primary"],
                "family": "Inter, system-ui, sans-serif",
            },
        },
        width=600,
        height=800,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_custom_table(
    data: list[dict[str, Any]],
    title: str = "Data Table",
    column_widths: list[int] | None = None,
    color_scheme: str = "blue",
) -> go.Figure:
    """
    Creates a customizable table from data.

    Args:
        data: List of dictionaries containing table data
        title: Table title
        column_widths: Optional list of column widths
        color_scheme: Color scheme ('blue', 'green', 'red', 'purple', 'orange')

    Returns:
        go.Figure: Plotly table figure
    """

    if not data:
        return go.Figure().add_annotation(text="No data provided", showarrow=False)

    # Create DataFrame from data
    df = pd.DataFrame(data)

    # Color schemes
    color_schemes = {
        "blue": {"header": "#2C3E50", "even": "#ECF0F1", "odd": "#FFFFFF"},
        "green": {"header": "#27AE60", "even": "#E8F5E8", "odd": "#FFFFFF"},
        "red": {"header": "#E74C3C", "even": "#FDEDEC", "odd": "#FFFFFF"},
        "purple": {"header": "#8E44AD", "even": "#F4ECF7", "odd": "#FFFFFF"},
        "orange": {"header": "#E67E22", "even": "#FEF5E7", "odd": "#FFFFFF"},
    }

    scheme = color_schemes.get(color_scheme, color_schemes["blue"])

    # Create alternating row colors
    fill_colors = []
    for i in range(len(df)):
        if i % 2 == 0:
            fill_colors.append([scheme["even"]] * len(df.columns))
        else:
            fill_colors.append([scheme["odd"]] * len(df.columns))

    # Transpose for table format
    fill_colors_transposed = list(map(list, zip(*fill_colors)))

    # Set column widths
    if column_widths is None:
        column_widths = [150] * len(df.columns)

    # Create table with modern styling
    config = modern_table_config

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=column_widths,
                header={
                    "values": [f"<b>{col}</b>" for col in df.columns],
                    "fill_color": config["header"]["fill_color"],
                    "font": config["header"]["font"],
                    "align": config["header"]["align"],
                    "height": config["header"]["height"],
                    "line": {"width": 2, "color": "white"},
                },
                cells={
                    "values": [df[col] for col in df.columns],
                    "fill_color": fill_colors_transposed,
                    "font": {
                        "color": modern_colors["text_primary"],
                        "size": 12,
                        "family": "Inter, system-ui, sans-serif",
                    },
                    "align": "center",
                    "height": config["cells"]["height"],
                    "line": {"width": 1, "color": modern_colors["border"]},
                },
            )
        ]
    )

    # Update layout with modern styling
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.5,
            "font": {
                "size": 20,
                "color": modern_colors["text_primary"],
                "family": "Inter, system-ui, sans-serif",
            },
        },
        width=sum(column_widths) + 100,
        height=min(800, 100 + len(df) * 40),
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_mesoregions_table() -> go.Figure:
    """
    Creates a table showing some examples of Brazilian mesoregions by state.

    Returns:
        go.Figure: Plotly table figure with mesoregion information
    """

    # Sample mesoregions data (some examples from different states)
    mesoregions_data = [
        ("Triângulo Mineiro/Alto Paranaíba", "Minas Gerais", "MG"),
        ("Região Metropolitana de São Paulo", "São Paulo", "SP"),
        ("Norte Fluminense", "Rio de Janeiro", "RJ"),
        ("Norte Central Paranaense", "Paraná", "PR"),
        ("Região Metropolitana de Porto Alegre", "Rio Grande do Sul", "RS"),
        ("Grande Florianópolis", "Santa Catarina", "SC"),
        ("Centro Goiano", "Goiás", "GO"),
        ("Norte Matogrossense", "Mato Grosso", "MT"),
        ("Campo Grande", "Mato Grosso do Sul", "MS"),
        ("Distrito Federal", "Distrito Federal", "DF"),
        ("Recôncavo Baiano", "Bahia", "BA"),
        ("Mata Pernambucana", "Pernambuco", "PE"),
        ("Região Metropolitana do Ceará", "Ceará", "CE"),
        ("Norte Maranhense", "Maranhão", "MA"),
        ("Zona da Mata Paraibana", "Paraíba", "PB"),
        ("Agreste Potiguar", "Rio Grande do Norte", "RN"),
        ("Sertão Alagoano", "Alagoas", "AL"),
        ("Bacia do Rio Corrente", "Piauí", "PI"),
        ("Aracaju", "Sergipe", "SE"),
        ("Norte do Amapá", "Amapá", "AP"),
        ("Centro Amazonense", "Amazonas", "AM"),
        ("Baixo Amazonas", "Pará", "PA"),
        ("Vale do Rio Branco", "Roraima", "RR"),
        ("Leste Rondoniense", "Rondônia", "RO"),
        ("Vale do Rio dos Bois", "Acre", "AC"),
        ("Oriental do Tocantins", "Tocantins", "TO"),
        ("Norte Espírito-santense", "Espírito Santo", "ES"),
    ]

    # Create DataFrame
    df = pd.DataFrame(mesoregions_data, columns=["Mesorregião", "Estado", "Sigla"])

    # Sort by state name for better organization
    df = df.sort_values(["Estado", "Mesorregião"]).reset_index(drop=True)

    # Create alternating colors by state
    current_state = None
    state_colors = ["#E8F4FD", "#FFF2CC", "#E1F5FE", "#F3E5F5", "#E8F5E8", "#FFF3E0"]
    color_index = 0
    fill_colors = []

    for _, row in df.iterrows():
        if row["Estado"] != current_state:
            current_state = row["Estado"]
            color_index = (color_index + 1) % len(state_colors)

        base_color = state_colors[color_index]
        fill_colors.append([base_color, base_color, base_color])

    # Transpose for table format
    fill_colors_transposed = list(map(list, zip(*fill_colors)))

    # Create the table with modern styling
    config = modern_table_config

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[300, 180, 80],
                header={
                    "values": ["<b>Mesorregião</b>", "<b>Estado</b>", "<b>Sigla</b>"],
                    "fill_color": config["header"]["fill_color"],
                    "font": config["header"]["font"],
                    "align": config["header"]["align"],
                    "height": config["header"]["height"],
                    "line": {"width": 2, "color": "white"},
                },
                cells={
                    "values": [df["Mesorregião"], df["Estado"], df["Sigla"]],
                    "fill_color": fill_colors_transposed,
                    "font": {
                        "color": modern_colors["text_primary"],
                        "size": 12,
                        "family": "Inter, system-ui, sans-serif",
                    },
                    "align": ["left", "left", "center"],
                    "height": config["cells"]["height"],
                    "line": {"width": 1, "color": modern_colors["border"]},
                },
            )
        ]
    )

    # Update layout with modern styling
    fig.update_layout(
        title={
            "text": "<b>Exemplos de Mesorregiões Brasileiras</b>",
            "x": 0.5,
            "font": {
                "size": 20,
                "color": modern_colors["text_primary"],
                "family": "Inter, system-ui, sans-serif",
            },
        },
        width=700,
        height=900,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_summary_stats_table(
    data: pd.DataFrame, title: str = "Summary Statistics"
) -> go.Figure:
    """
    Creates a summary statistics table from a DataFrame.

    Args:
        data: DataFrame to summarize
        title: Table title

    Returns:
        go.Figure: Plotly table figure with summary statistics
    """

    if data.empty:
        return go.Figure().add_annotation(text="No data to summarize", showarrow=False)

    # Generate summary statistics
    numeric_cols = data.select_dtypes(include=["number"]).columns

    if len(numeric_cols) == 0:
        return go.Figure().add_annotation(
            text="No numeric columns to summarize", showarrow=False
        )

    summary_data = []
    for col in numeric_cols:
        summary_data.append(
            {
                "Column": col,
                "Count": data[col].count(),
                "Mean": (
                    f"{data[col].mean():.2f}" if not data[col].isna().all() else "N/A"
                ),
                "Std": (
                    f"{data[col].std():.2f}" if not data[col].isna().all() else "N/A"
                ),
                "Min": (
                    f"{data[col].min():.2f}" if not data[col].isna().all() else "N/A"
                ),
                "Max": (
                    f"{data[col].max():.2f}" if not data[col].isna().all() else "N/A"
                ),
            }
        )

    return create_custom_table(
        data=summary_data,
        title=title,
        column_widths=[150, 80, 100, 100, 100, 100],
        color_scheme="blue",  # Use consistent color scheme with modern theme
    )
