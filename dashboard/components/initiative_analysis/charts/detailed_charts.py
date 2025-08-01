"""
Detailed Analysis Charts
=======================

Gráficos específicos para análise detalhada de iniciativas LULC.
Componentes para visualizações detalhadas e exploratórias.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

import pandas as pd
import plotly.graph_objects as go

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)


@smart_cache_data(ttl=300)
def create_dual_bars_chart(filtered_df: pd.DataFrame) -> go.Figure | None:
    """
    Cria gráfico de barras duplas para comparação de precisão vs resolução.

    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas

    Returns:
        Figura Plotly com barras duplas ou None se erro
    """
    try:
        if filtered_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível para análise detalhada",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        df_copy = filtered_df.copy()

        # Normalizar resolução (inverter para que menor seja melhor)
        if "Resolution" in df_copy.columns:
            resolution_series = pd.to_numeric(df_copy["Resolution"], errors="coerce")
            if resolution_series.notna().any():
                max_res = resolution_series.max()
                if max_res > 0:
                    df_copy["resolution_norm"] = (
                        (1 / resolution_series) / (1 / max_res) * 100
                    )
                else:
                    df_copy["resolution_norm"] = 0
            else:
                df_copy["resolution_norm"] = 0
        else:
            df_copy["resolution_norm"] = 0

        # Obter cores modernas
        colors = get_chart_colors()

        fig = go.Figure()

        # Barra de precisão
        accuracy_series = pd.to_numeric(
            df_copy.get("Accuracy (%)", pd.Series([0] * len(df_copy))), errors="coerce"
        ).fillna(0)
        fig.add_trace(
            go.Bar(
                y=df_copy.get("Display_Name", ["Unknown"] * len(df_copy)),
                x=accuracy_series,
                name="Precisão (%)",
                orientation="h",
                marker_color=colors[0] if colors else "#3b82f6",
            )
        )

        # Barra de resolução normalizada
        fig.add_trace(
            go.Bar(
                y=df_copy.get("Display_Name", ["Unknown"] * len(df_copy)),
                x=df_copy["resolution_norm"],
                name="Resolução (Normalizada)",
                orientation="h",
                marker_color=colors[1] if len(colors) > 1 else "#f59e0b",
            )
        )

        apply_standard_layout(
            fig,
            title="Comparação: Precisão vs Resolução",
            xaxis_title="Valor (%)",
            yaxis_title="Iniciativa",
        )

        fig.update_layout(
            barmode="group",
            height=max(400, len(df_copy) * 30 + 100),
        )

        return fig

    except Exception as e:
        print(f"Erro ao criar gráfico de barras duplas: {e}")
        return None


@smart_cache_data(ttl=300)
def create_radar_chart(filtered_df: pd.DataFrame) -> go.Figure | None:
    """
    Cria gráfico radar multidimensional.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com radar chart ou None se erro
    """
    try:
        if filtered_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível para radar chart",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Selecionar até 5 iniciativas para o radar
        radar_df = filtered_df.head(5).copy()

        # Definir métricas para o radar
        metrics = ["Accuracy (%)", "Resolution", "Total_Classes"]
        categories = ["Precisão", "Resolução (Inv.)", "Classes"]

        fig = go.Figure()
        colors = get_chart_colors()

        for i, (_, row) in enumerate(radar_df.iterrows()):
            values = []

            # Precisão (normalizada 0-1)
            accuracy = pd.to_numeric(row.get("Accuracy (%)", 0), errors="coerce")
            values.append(float(accuracy / 100) if pd.notna(accuracy) else 0)

            # Resolução (invertida e normalizada)
            resolution = pd.to_numeric(row.get("Resolution", 1), errors="coerce")
            if pd.notna(resolution) and resolution > 0:
                values.append(
                    float(1 / (resolution / 30))
                )  # Normalizar com referência de 30m
            else:
                values.append(0)

            # Classes (normalizada)
            classes = pd.to_numeric(row.get("Total_Classes", 0), errors="coerce")
            values.append(
                float(classes / 50) if pd.notna(classes) else 0
            )  # Normalizar até 50 classes

            # Fechar o polígono
            values_closed = values + [values[0]]
            theta_closed = categories + [categories[0]]

            fig.add_trace(
                go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill="toself",
                    name=row.get("Display_Name", "Unknown")[:20],
                    line_color=(
                        colors[i % len(colors)]
                        if colors
                        else f"hsl({i * 60}, 70%, 50%)"
                    ),
                    line_width=2,
                )
            )

        apply_standard_layout(fig, title="Análise Multidimensional (Radar)")

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
            )
        )

        return fig

    except Exception as e:
        print(f"Erro ao criar radar chart: {e}")
        return None


@smart_cache_data(ttl=300)
def create_heatmap_chart(filtered_df: pd.DataFrame) -> go.Figure | None:
    """
    Cria heatmap de correlação entre métricas.

    Args:
        filtered_df: DataFrame filtrado

    Returns:
        Figura Plotly com heatmap ou None se erro
    """
    try:
        if filtered_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dados disponível para heatmap",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Selecionar colunas numéricas para correlação
        numeric_cols = []
        correlation_data = pd.DataFrame()

        for col in [
            "Accuracy (%)",
            "Resolution",
            "Total_Classes",
            "Start_Year",
            "End_Year",
        ]:
            if col in filtered_df.columns:
                numeric_data = pd.to_numeric(filtered_df[col], errors="coerce")
                if numeric_data.notna().sum() > 1:  # Pelo menos 2 valores válidos
                    correlation_data[col] = numeric_data
                    numeric_cols.append(col)

        if len(numeric_cols) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="Dados numéricos insuficientes para correlação",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Calcular matriz de correlação
        corr_matrix = correlation_data.corr()

        # Criar heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale="RdBu",
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 12},
                hoverongaps=False,
            )
        )

        apply_standard_layout(fig, title="Matriz de Correlação - Métricas")

        fig.update_layout(width=500, height=500)

        return fig

    except Exception as e:
        print(f"Erro ao criar heatmap: {e}")
        return None


@smart_cache_data(ttl=300)
def create_distribution_plot(
    filtered_df: pd.DataFrame, metric: str = "Accuracy (%)"
) -> go.Figure | None:
    """
    Cria gráfico de distribuição para uma métrica específica.

    Args:
        filtered_df: DataFrame filtrado
        metric: Métrica para analisar distribuição

    Returns:
        Figura Plotly com distribuição ou None se erro
    """
    try:
        if filtered_df.empty or metric not in filtered_df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Dados insuficientes para distribuição de {metric}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Extrair dados da métrica
        metric_data = pd.to_numeric(filtered_df[metric], errors="coerce").dropna()

        if len(metric_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Nenhum valor válido para {metric}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Criar histograma
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=metric_data,
                nbinsx=min(20, len(metric_data)),
                name="Distribuição",
                marker_color=get_chart_colors()[0] if get_chart_colors() else "#3b82f6",
                opacity=0.7,
            )
        )

        # Adicionar linha de média
        mean_value = metric_data.mean()
        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {mean_value:.2f}",
        )

        apply_standard_layout(
            fig,
            title=f"Distribuição de {metric}",
            xaxis_title=metric,
            yaxis_title="Frequência",
        )

        return fig

    except Exception as e:
        print(f"Erro ao criar gráfico de distribuição: {e}")
        return None
