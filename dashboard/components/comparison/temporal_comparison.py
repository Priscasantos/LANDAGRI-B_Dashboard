"""
Temporal Comparison Component
============================

Componente para comparação temporal.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza comparação temporal.

    Args:
        df: DataFrame com dados das iniciativas
        filters: Filtros aplicados
    """
    st.subheader("⏰ Comparação Temporal")
    st.info("Componente de comparação temporal em desenvolvimento.")

    # Placeholder - implementar lógica específica
    year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]

    if year_columns:
        st.write(f"Período disponível: {min(year_columns)} - {max(year_columns)}")
        st.write(f"Anos com dados: {len(year_columns)}")
    else:
        st.write("Nenhum dado temporal encontrado.")
