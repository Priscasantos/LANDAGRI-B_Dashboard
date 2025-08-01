"""
Componente modular para timeline moderno das iniciativas LULC.
Visualização interativa da evolução temporal com design moderno.
"""

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def timeline_with_modern_controls(metadata: dict[str, Any], filtered_df: pd.DataFrame) -> None:
    """
    Renderiza timeline moderno com controles interativos avançados.

    Args:
        metadata: Metadados das iniciativas
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("### 📅 Modern Timeline")
    st.markdown("*Interactive timeline with period shadows and modern design*")

    if not metadata or filtered_df is None or filtered_df.empty:
        st.warning("❌ No data available for timeline visualization.")
        return

    # Controles avançados
    col1, col2, col3 = st.columns(3)

    with col1:
        chart_height = st.slider(
            "Chart Height",
            min_value=400,
            max_value=1200,
            value=600,
            step=50,
            key="timeline_height"
        )

    with col2:
        item_spacing = st.slider(
            "Item Spacing",
            min_value=15,
            max_value=50,
            value=25,
            step=5,
            key="timeline_spacing"
        )

    with col3:
        line_width = st.slider(
            "Line Width",
            min_value=5,
            max_value=25,
            value=15,
            step=2,
            key="timeline_line_width"
        )

    # Configurações de margem
    with st.expander("🔧 Advanced Settings"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            margin_left = st.number_input("Left Margin", value=150, min_value=50, max_value=300)

        with col2:
            margin_right = st.number_input("Right Margin", value=50, min_value=20, max_value=200)

        with col3:
            margin_top = st.number_input("Top Margin", value=80, min_value=40, max_value=150)

        with col4:
            margin_bottom = st.number_input("Bottom Margin", value=100, min_value=50, max_value=200)

        margin_config = {
            "l": margin_left,
            "r": margin_right,
            "t": margin_top,
            "b": margin_bottom
        }

    # Gerar e exibir o timeline
    fig = plot_timeline_chart(
        metadata,
        filtered_df,
        chart_height=chart_height,
        item_spacing=item_spacing,
        line_width=line_width,
        margin_config=margin_config
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar configurações atual
    with st.sidebar.expander("📊 Current Timeline Settings"):
        st.write(f"**Height:** {chart_height}px")
        st.write(f"**Item Spacing:** {item_spacing}px")
        st.write(f"**Line Width:** {line_width}px")
        st.write(f"**Margins:** L:{margin_left} R:{margin_right} T:{margin_top} B:{margin_bottom}")


def plot_timeline_chart(
    metadata: dict[str, Any],
    filtered_df: pd.DataFrame,
    chart_height: int | None = None,
    chart_width: int | None = None,
    item_spacing: int = 25,
    line_width: int = 15,
    margin_config: dict | None = None
) -> go.Figure:
    """
    Cria gráfico de timeline moderno para as iniciativas LULC.

    Args:
        metadata: Metadados das iniciativas contendo anos disponíveis
        filtered_df: DataFrame filtrado com dados das iniciativas
        chart_height: Altura do gráfico em pixels
        chart_width: Largura do gráfico em pixels
        item_spacing: Espaçamento entre itens em pixels
        line_width: Largura das linhas do timeline
        margin_config: Configuração de margens

    Returns:
        go.Figure: Figura Plotly do timeline
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for timeline visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": "gray"}
        )
        fig.update_layout(
            title="Timeline - No Data Available",
            height=400
        )
        return fig

    # Preparar dados do timeline
    timeline_data = []
    nome_to_sigla = {}

    # Criar mapeamento nome para sigla
    if "Acronym" in filtered_df.columns and "Name" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    for nome, details in metadata.items():
        if isinstance(details, dict) and "available_years" in details:
            anos_lista = details["available_years"]
            if isinstance(anos_lista, list) and anos_lista:
                display_name = nome_to_sigla.get(nome, nome[:20])
                timeline_data.append({
                    "nome": nome,
                    "display_name": display_name,
                    "anos_lista": sorted(anos_lista),
                    "primeiro_ano": min(anos_lista),
                    "ultimo_ano": max(anos_lista),
                    "tipo": details.get("type", "Uncategorized"),
                    "total_anos": len(anos_lista)
                })

    if not timeline_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No timeline data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": "gray"}
        )
        fig.update_layout(
            title="Timeline - No Timeline Data",
            height=400
        )
        return fig

    # Ordenar por primeiro ano
    timeline_data.sort(key=lambda x: x["primeiro_ano"])

    # Definir cores por tipo
    color_map = {
        "Global": "rgba(76, 175, 80, 0.8)",
        "National": "rgba(33, 150, 243, 0.8)",
        "Regional": "rgba(255, 152, 0, 0.8)",
        "Local": "rgba(156, 39, 176, 0.8)",
        "Uncategorized": "rgba(158, 158, 158, 0.8)"
    }

    # Criar figura
    fig = go.Figure()

    # Adicionar traces para cada iniciativa
    for i, item in enumerate(timeline_data):
        y_position = i * item_spacing
        color = color_map.get(item["tipo"], color_map["Uncategorized"])

        # Adicionar sombra do período (background)
        fig.add_trace(go.Scatter(
            x=[item["primeiro_ano"], item["ultimo_ano"]],
            y=[y_position, y_position],
            mode='lines',
            line={
                "color": color.replace("0.8", "0.3"),
                "width": line_width + 4
            },
            showlegend=False,
            hoverinfo='skip',
            name=f"{item['display_name']}_shadow"
        ))

        # Controle simples para legenda baseado no índice
        show_in_legend = i == 0 or item["tipo"] != timeline_data[i-1]["tipo"]

        # Adicionar linha principal do período
        fig.add_trace(go.Scatter(
            x=[item["primeiro_ano"], item["ultimo_ano"]],
            y=[y_position, y_position],
            mode='lines+markers',
            line={
                "color": color,
                "width": line_width
            },
            marker={
                "size": 12,
                "color": color,
                "symbol": "circle",
                "line": {"width": 2, "color": "white"}
            },
            name=item["tipo"],
            legendgroup=item["tipo"],
            showlegend=show_in_legend,
            hovertemplate=(
                f"<b>{item['display_name']}</b><br>"
                f"Type: {item['tipo']}<br>"
                f"Period: {item['primeiro_ano']} - {item['ultimo_ano']}<br>"
                f"Duration: {item['ultimo_ano'] - item['primeiro_ano'] + 1} years<br>"
                f"Available Years: {item['total_anos']}<br>"
                "<extra></extra>"
            )
        ))

        # Adicionar marcadores para anos individuais (pontos pequenos)
        if len(item["anos_lista"]) > 2:  # Só mostrar pontos individuais se há mais de 2 anos
            for ano in item["anos_lista"][1:-1]:  # Excluir primeiro e último (já marcados)
                fig.add_trace(go.Scatter(
                    x=[ano],
                    y=[y_position],
                    mode='markers',
                    marker={
                        "size": 6,
                        "color": color,
                        "symbol": "circle"
                    },
                    showlegend=False,
                    hovertemplate=f"<b>{item['display_name']}</b><br>Year: {ano}<extra></extra>"
                ))

    # Calcular altura dinâmica
    if chart_height is None:
        chart_height = max(400, len(timeline_data) * item_spacing + 150)

    # Configurar layout
    layout_config = {
        "title": {
            "text": "LULC Initiatives Timeline",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2c3e50"}
        },
        "height": chart_height,
        "showlegend": True,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(255,255,255,0.8)",
            "bordercolor": "rgba(0,0,0,0.2)",
            "borderwidth": 1
        },
        "plot_bgcolor": "rgba(248,249,250,0.8)",
        "paper_bgcolor": "white",
        "xaxis": {
            "title": "Year",
            "showgrid": True,
            "gridcolor": "rgba(128,128,128,0.2)",
            "gridwidth": 1,
            "zeroline": False,
            "tickformat": "d",
            "dtick": 5,
            "range": [1985, 2025]
        },
        "yaxis": {
            "title": "Initiatives",
            "showgrid": False,
            "zeroline": False,
            "showticklabels": True,
            "tickmode": "array",
            "tickvals": [i * item_spacing for i in range(len(timeline_data))],
            "ticktext": [item["display_name"] for item in timeline_data],
            "automargin": True
        },
        "hovermode": "closest"
    }

    if chart_width is not None:
        layout_config["width"] = chart_width

    if margin_config is not None:
        layout_config["margin"] = margin_config
    else:
        layout_config["margin"] = {"l": 150, "r": 50, "t": 80, "b": 100}

    fig.update_layout(**layout_config)

    # Adicionar anotações para décadas
    for decade in range(1990, 2030, 10):
        fig.add_vline(
            x=decade,
            line_dash="dot",
            line_color="rgba(128,128,128,0.4)",
            line_width=1,
            annotation_text=f"{decade}s",
            annotation_position="top",
            annotation_font_size=10,
            annotation_font_color="rgba(100,100,100,0.8)"
        )

    return fig
