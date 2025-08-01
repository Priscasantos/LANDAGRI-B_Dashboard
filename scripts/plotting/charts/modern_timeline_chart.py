#!/usr/bin/env python3
"""
Gráfico Timeline Moderno com Pontos e Linhas
============================================

Versão modernizada do timeline com pontos de início/fim e sombreamento.

Author: Dashboard Iniciativas LULC
Date: 2025-07-29
"""

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from scripts.data_processors.initiative_data_processor import (
    generate_timeline_data,
    process_all_initiatives_metadata,
)
from scripts.plotting.chart_core import add_display_names_to_df
from scripts.utilities.config import get_initiative_color_map
from scripts.utilities.modern_themes import apply_modern_theme, get_modern_colors


def plot_modern_timeline_chart(
    metadata: dict[str, Any],
    filtered_df: pd.DataFrame,
    chart_height: int = None,
    show_intervals: bool = True,
    show_shadows: bool = True,
    point_size: int = 12,
    line_width: int = 6,
    shadow_opacity: float = 0.25,
) -> go.Figure:
    """
    Cria um gráfico timeline moderno com pontos de início/fim e intervalos com sombreamento.

    Args:
        metadata: Metadados das iniciativas
        filtered_df: DataFrame filtrado
        chart_height: Altura do gráfico
        show_intervals: Mostrar intervalos entre pontos
        show_shadows: Mostrar sombreamento
        point_size: Tamanho dos pontos
        line_width: Largura das linhas
        shadow_opacity: Opacidade do sombreamento

    Returns:
        go.Figure: Figura Plotly modernizada
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        apply_modern_theme(fig, "Modern Timeline (No Data)", chart_type="timeline")
        return fig

    # Preparar dados usando o novo processador
    plot_df = filtered_df.copy()
    if "Name" not in plot_df.columns and "Nome" in plot_df.columns:
        plot_df.rename(columns={"Nome": "Name"}, inplace=True)
    if "Display_Name" not in plot_df.columns:
        plot_df = add_display_names_to_df(plot_df)

    # Processar metadados com o novo sistema
    processed_metadata = process_all_initiatives_metadata(metadata)
    timeline_data = generate_timeline_data(processed_metadata, plot_df)

    # Converter para formato esperado pelo gráfico
    initiatives_data = []
    for entry in timeline_data:
        initiatives_data.append(
            {
                "name": entry["name"],  # Nome da iniciativa
                "display_name": entry["display_name"],
                "acronym": entry["acronym"],
                "start_year": entry["start_year"],
                "end_year": entry["end_year"],
                "years": entry["years"],
                "type": entry["type"],  # Tipo de coverage traduzido
                "methodology": entry["methodology"],
            }
        )

    if not initiatives_data:
        fig = go.Figure()
        apply_modern_theme(fig, "Modern Timeline (No Data)", chart_type="timeline")
        return fig

    # Ordenar iniciativas (pode usar a ordem desejada)
    desired_order = [
        "CGLS",
        "GDW",
        "ESRI-10m LULC",
        "UMD-GLC",
        "GPW",
        "UMD-SASM",
        "ESA-WC",
        "WorldCereal",
        "PRODES",
        "DETER",
        "TerraClass Amazon",
        "TerraClass Cerrado",
        "MapBiomas",
        "IBGE-MLCU",
        "CONAB-AM",
    ]

    def get_order_index(acronym):
        try:
            return desired_order.index(acronym)
        except ValueError:
            return len(desired_order)

    initiatives_data.sort(key=lambda x: get_order_index(x["acronym"]), reverse=True)

    # Obter cores modernas
    modern_colors = get_modern_colors(len(initiatives_data))
    color_map = get_initiative_color_map([init["name"] for init in initiatives_data])

    # Criar figura
    fig = go.Figure()

    y_positions = list(range(len(initiatives_data)))
    y_labels = [init["acronym"] for init in initiatives_data]

    # Calcular range de anos
    all_years = []
    for init in initiatives_data:
        all_years.extend(init["years"])
    min_year = min(all_years) if all_years else 1985
    max_year = max(all_years) if all_years else 2024

    # Variáveis de controle para legendas únicas
    legend_start_added = False
    legend_end_added = False
    legend_data_added = False

    # Adicionar traces para cada iniciativa
    for i, init_data in enumerate(initiatives_data):
        y_pos = i
        color = color_map.get(init_data["name"], modern_colors[i % len(modern_colors)])

        # Sombreamento removido temporariamente para evitar sobreposições visuais

        # Trace removido: linha conectando início e fim (estava duplicando elementos visuais)

        # 3. Ponto de início (quadrado)
        fig.add_trace(
            go.Scatter(
                x=[init_data["start_year"]],
                y=[y_pos],
                mode="markers",
                marker={
                    "size": point_size + 2,  # Reduzido de +4 para +2
                    "color": color,
                    "symbol": "square",  # Quadrado para início
                    "opacity": 1.0,
                    "line": {"width": 2, "color": "white"},
                },
                name="■ Início da Iniciativa" if not legend_start_added else "",
                showlegend=not legend_start_added,
                legendgroup="starts",
                hovertemplate=f"<b>{init_data['acronym']} - INÍCIO</b><br>"
                + f"Ano: {init_data['start_year']}<br>"
                + f"Tipo: {init_data['type']}<br>"
                + f"Metodologia: {init_data['methodology']}<extra></extra>",
            )
        )
        legend_start_added = True

        # 4. Ponto de fim (retângulo, apenas se diferente do início)
        if init_data["start_year"] != init_data["end_year"]:
            fig.add_trace(
                go.Scatter(
                    x=[init_data["end_year"]],
                    y=[y_pos],
                    mode="markers",
                    marker={
                        "size": point_size + 3,  # Reduzido de +6 para +3
                        "color": color,
                        "symbol": "square-open",  # Retângulo aberto para fim
                        "opacity": 1.0,
                        "line": {"width": 3, "color": color},
                    },
                    name="□ Fim da Iniciativa" if not legend_end_added else "",
                    showlegend=not legend_end_added,
                    legendgroup="ends",
                    hovertemplate=f"<b>{init_data['acronym']} - FIM</b><br>"
                    + f"Ano: {init_data['end_year']}<br>"
                    + f"Tipo: {init_data['type']}<br>"
                    + f"Metodologia: {init_data['methodology']}<extra></extra>",
                )
            )
            legend_end_added = True

        # 5. Pontos para dados disponíveis (círculos)
        if len(init_data["years"]) > 2:  # Mostrar apenas se há mais que início/fim
            intermediate_years = [
                y
                for y in init_data["years"]
                if y != init_data["start_year"] and y != init_data["end_year"]
            ]
            if intermediate_years:
                fig.add_trace(
                    go.Scatter(
                        x=intermediate_years,
                        y=[y_pos] * len(intermediate_years),
                        mode="markers",
                        marker={
                            "size": point_size - 2,  # Círculos menores
                            "color": color,
                            "symbol": "circle",  # Círculo para dados
                            "opacity": 0.8,
                            "line": {"width": 1, "color": "white"},
                        },
                        name="● Dados Disponíveis" if not legend_data_added else "",
                        showlegend=not legend_data_added,
                        legendgroup="data_points",
                        hovertemplate=f"<b>{init_data['acronym']}</b><br>"
                        + "Dados disponíveis em: %{x}<br>"
                        + f"Tipo: {init_data['type']}<extra></extra>",
                    )
                )
                legend_data_added = True

    # Configurar layout moderno
    height = chart_height or max(400, len(initiatives_data) * 40)

    fig.update_layout(
        title={
            "text": "<b>Cronologia das Iniciativas de Monitoramento LULC</b>",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 26,
                "family": "Arial Black, sans-serif",
                "color": "#1e293b",
            },
        },
        height=height,
        margin={"l": 200, "r": 60, "t": 100, "b": 100},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        showlegend=True,
        legend={
            "orientation": "v",  # Legenda vertical
            "yanchor": "top",
            "y": 1.0,
            "xanchor": "left",
            "x": -0.35,  # Posicionada à esquerda, abaixo do eixo Y
            "bgcolor": "rgba(255,255,255,0.9)",
            "bordercolor": "rgba(0,0,0,0.2)",
            "borderwidth": 1,
            "font": {"size": 11, "color": "#1e293b", "family": "Arial, sans-serif"},
        },
    )

    # Configurar eixos
    fig.update_xaxes(
        title="<b>Período de Execução (Anos)</b>",
        title_font={"size": 16, "color": "#1e293b", "family": "Arial, sans-serif"},
        range=[min_year - 1, max_year + 1],
        showgrid=True,
        gridcolor="rgba(148, 163, 184, 0.4)",
        gridwidth=1,
        showline=True,
        linecolor="#94a3b8",
        linewidth=2,
        tickfont={"size": 13, "color": "#374151", "family": "Arial, sans-serif"},
        tickmode="linear",
        dtick=5,
    )

    fig.update_yaxes(
        title="<b>Iniciativas de Monitoramento LULC</b>",
        title_font={"size": 16, "color": "#1e293b", "family": "Arial, sans-serif"},
        tickmode="array",
        tickvals=y_positions,
        ticktext=y_labels,
        tickfont={"size": 12, "color": "#374151", "family": "Arial, sans-serif"},
        showgrid=False,
        showline=True,
        linecolor="#94a3b8",
        linewidth=2,
    )  # Aplicar tema moderno final
    apply_modern_theme(fig, chart_type="timeline")

    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Converte cor hex para rgba com alpha."""
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"({r}, {g}, {b}, {alpha})"
    except Exception:
        return f"(59, 130, 246, {alpha})"  # Default blue


def timeline_with_modern_controls(metadata: dict[str, Any], filtered_df: pd.DataFrame):
    """Interface Streamlit para timeline moderno com controles."""
    import streamlit as st

    st.sidebar.subheader("🎨 Controles do Timeline Moderno")

    # Controles visuais
    show_intervals = st.sidebar.checkbox(
        "Mostrar Intervalos",
        value=True,
        help="Mostrar linhas conectando pontos de início e fim",
    )

    show_shadows = st.sidebar.checkbox(
        "Mostrar Sombreamento",
        value=True,
        help="Mostrar áreas sombreadas para períodos das iniciativas",
    )

    point_size = st.sidebar.slider(
        "Tamanho dos Pontos", min_value=8, max_value=20, value=12, step=2
    )

    line_width = st.sidebar.slider(
        "Largura das Linhas", min_value=3, max_value=15, value=8, step=1
    )

    shadow_opacity = st.sidebar.slider(
        "Opacidade do Sombreamento", min_value=0.1, max_value=0.5, value=0.25, step=0.05
    )

    chart_height = st.sidebar.slider(
        "Altura do Gráfico", min_value=400, max_value=1200, value=600, step=50
    )  # Gerar gráfico
    fig = plot_modern_timeline_chart(
        metadata=metadata,
        filtered_df=filtered_df,
        chart_height=chart_height,
        show_intervals=show_intervals,
        show_shadows=show_shadows,
        point_size=point_size,
        line_width=line_width,
        shadow_opacity=shadow_opacity,
    )

    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar configurações atuais
    with st.sidebar.expander("📊 Configurações Atuais"):
        st.json(
            {
                "mostrar_intervalos": show_intervals,
                "mostrar_sombreamento": show_shadows,
                "tamanho_pontos": point_size,
                "largura_linhas": line_width,
                "opacidade_sombreamento": shadow_opacity,
                "altura_grafico": chart_height,
            }
        )
