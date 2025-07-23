"""
Sensor Charts Component
======================

Componente para gráficos de sensores utilizados nas iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza gráficos de sensores.

    Args:
        df: DataFrame com dados das iniciativas
    """
    st.subheader("📡 Sensores Utilizados")

    # Encontrar colunas de sensores
    sensor_columns = [col for col in df.columns if "sensor" in col.lower()]

    if not sensor_columns:
        st.info("Dados de sensores não encontrados.")
        return

    # Contar uso de sensores
    sensor_usage = {}
    for col in sensor_columns:
        if col in df.columns:
            count = df[col].notna().sum()
            if count > 0:
                sensor_usage[col.replace("_", " ").title()] = count

    if not sensor_usage:
        st.info("Nenhum sensor em uso nas iniciativas.")
        return

    # Gráfico de barras
    fig = px.bar(
        x=list(sensor_usage.keys()),
        y=list(sensor_usage.values()),
        title="Uso de Sensores por Iniciativa",
        labels={"x": "Tipo de Sensor", "y": "Número de Iniciativas"},
    )

    fig.update_layout(height=300, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
