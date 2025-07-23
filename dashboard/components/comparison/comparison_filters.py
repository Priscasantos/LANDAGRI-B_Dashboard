"""
Comparison Filters Component
===========================

Componente de filtros para análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

from typing import Any

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame) -> dict[str, Any]:
    """
    Renderiza filtros para comparação.

    Args:
        df: DataFrame com dados das iniciativas

    Returns:
        Dict com os filtros selecionados
    """
    st.subheader("🔧 Configurar Comparação")

    # Filtros básicos
    with st.expander("Filtros de Dados", expanded=True):
        # Filtro por país
        countries = (
            ["Todos"] + sorted(df["Country"].unique().tolist())
            if "Country" in df.columns
            else ["Todos"]
        )
        selected_countries = st.multiselect(
            "Países:",
            options=countries[1:],  # Exclude 'Todos'
            default=countries[1:3] if len(countries) > 3 else countries[1:],
            key="comp_countries",
        )

        # Filtro por período
        year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]
        if year_columns:
            min_year, max_year = (
                min(map(int, year_columns)),
                max(map(int, year_columns)),
            )
            year_range = st.slider(
                "Período:",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                key="comp_years",
            )
        else:
            year_range = None

        # Tipo de comparação
        comparison_type = st.selectbox(
            "Tipo de Análise:",
            options=["Contagem de Iniciativas", "Uso de Sensores", "Evolução Temporal"],
            key="comp_type",
        )

    return {
        "countries": selected_countries,
        "year_range": year_range,
        "comparison_type": comparison_type,
        "available": bool(selected_countries),
    }
