"""
Sensor Comparison Component
==========================

Componente para comparação por sensor.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza comparação por sensor.

    Args:
        df: DataFrame com dados das iniciativas
        filters: Filtros aplicados
    """
    st.subheader("📡 Comparação por Sensor")
    st.info("Componente de comparação por sensor em desenvolvimento.")

    # Placeholder - implementar lógica específica
    sensor_columns = [col for col in df.columns if "sensor" in col.lower()]

    if sensor_columns:
        st.write(f"Sensores disponíveis: {len(sensor_columns)}")
        for col in sensor_columns[:5]:  # Mostrar primeiros 5
            count = df[col].notna().sum()
            st.write(f"- {col}: {count} iniciativas")
    else:
        st.write("Nenhum dado de sensor encontrado.")
