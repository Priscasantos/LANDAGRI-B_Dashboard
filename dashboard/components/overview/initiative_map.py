"""
Initiative Map Component
=======================

Componente para visualização de mapa das iniciativas.

Author: LANDAGRI-B Project Team 
Date: 2025-07-23
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza mapa das iniciativas.

    Args:
        df: DataFrame com dados das iniciativas
    """
    st.subheader("🗺️ Mapa Global das Iniciativas")

    # Placeholder para o mapa - implementar com dados geográficos
    if "Country" in df.columns:
        countries = df["Country"].value_counts()

        fig = go.Figure(
            data=go.Scattergeo(
                lon=[0] * len(countries),  # Placeholder coordinates
                lat=[0] * len(countries),
                text=countries.index,
                mode="markers+text",
                marker=dict(size=countries.values * 5, color="blue", opacity=0.7),
            )
        )

        fig.update_layout(
            title="Distribuição Global das Iniciativas",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                showland=True,
                landcolor="lightgray",
            ),
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados geográficos não disponíveis para exibir o mapa.")
