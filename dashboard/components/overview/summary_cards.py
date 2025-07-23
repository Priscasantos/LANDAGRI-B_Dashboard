"""
Summary Cards Component
======================

Componente para cards de resumo da página de visão geral.
Mostra métricas principais das iniciativas LULC.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza cards de resumo com métricas principais.

    Args:
        df: DataFrame com dados das iniciativas
    """
    # Calcular métricas
    total_initiatives = len(df)

    # Sensores únicos
    sensor_columns = [col for col in df.columns if "sensor" in col.lower()]
    total_sensors = 0
    for col in sensor_columns:
        if col in df.columns:
            total_sensors += df[col].notna().sum()

    # Países únicos
    countries = df["Country"].nunique() if "Country" in df.columns else 0

    # Período temporal
    year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]
    years_range = (
        f"{min(year_columns)} - {max(year_columns)}" if year_columns else "N/A"
    )

    # Layout dos cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🎯 Total de Iniciativas",
            value=total_initiatives,
            help="Número total de iniciativas LULC cadastradas",
        )

    with col2:
        st.metric(
            label="🛰️ Sensores Utilizados",
            value=total_sensors,
            help="Total de sensores utilizados nas iniciativas",
        )

    with col3:
        st.metric(
            label="🌍 Países",
            value=countries,
            help="Número de países com iniciativas LULC",
        )

    with col4:
        st.metric(
            label="📅 Período",
            value=years_range,
            help="Período temporal das iniciativas",
        )
