"""
Country Comparison Component
===========================

Componente para comparação por país.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza comparação por país.

    Args:
        df: DataFrame com dados das iniciativas
        filters: Filtros aplicados
    """
    st.subheader("🌍 Comparação por País")

    if "Country" not in df.columns:
        st.info("Dados de país não disponíveis.")
        return

    # Filtrar dados se necessário
    filtered_df = df.copy()
    if filters.get("countries"):
        filtered_df = filtered_df[filtered_df["Country"].isin(filters["countries"])]

    # Contar iniciativas por país
    country_counts = filtered_df["Country"].value_counts()

    # Gráfico de barras
    fig = px.bar(
        x=country_counts.index,
        y=country_counts.values,
        title="Número de Iniciativas por País",
        labels={"x": "País", "y": "Número de Iniciativas"},
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela resumo
    st.write("**Resumo por País:**")
    summary_df = pd.DataFrame(
        {"País": country_counts.index, "Iniciativas": country_counts.values}
    )
    st.dataframe(summary_df, use_container_width=True)
