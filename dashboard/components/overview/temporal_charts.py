"""
Temporal Charts Component
========================

Componente para gráficos temporais das iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza gráficos temporais.

    Args:
        df: DataFrame com dados das iniciativas
    """
    st.subheader("📈 Evolução Temporal das Iniciativas")

    # Encontrar colunas de anos
    year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]

    if not year_columns:
        st.info("Dados temporais não encontrados.")
        return

    # Contar iniciativas por ano
    yearly_data = {}
    for year in sorted(year_columns):
        count = df[year].notna().sum()
        yearly_data[int(year)] = count

    if not yearly_data:
        st.info("Nenhum dado temporal disponível.")
        return

    # Gráfico de linha temporal
    fig = px.line(
        x=list(yearly_data.keys()),
        y=list(yearly_data.values()),
        title="Evolução das Iniciativas ao Longo do Tempo",
        labels={"x": "Ano", "y": "Número de Iniciativas Ativas"},
    )

    fig.update_traces(mode="lines+markers", marker={"size": 8})

    fig.update_layout(height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
