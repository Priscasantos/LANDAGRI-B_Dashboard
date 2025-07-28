"""
Comparison Filters Component
============================

Componente para filtros de análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame) -> dict:
    """
    Renderiza filtros para análise comparativa.
    
    Args:
        df: DataFrame com dados das iniciativas
        
    Returns:
        dict: Filtros selecionados
    """
    st.sidebar.subheader("🔍 Filtros de Comparação")
    
    # Show data info for debugging
    if st.sidebar.checkbox("🔍 Debug - Mostrar Info dos Dados", key="debug_data"):
        st.sidebar.write(f"Linhas: {len(df)}")
        st.sidebar.write(f"Colunas: {len(df.columns)}")
        st.sidebar.write("Colunas disponíveis:")
        st.sidebar.write(list(df.columns))
    
    filters = {}
    
    # Filtro por país
    if "Country" in df.columns:
        countries = df["Country"].dropna().unique()
        if len(countries) > 0:
            filters["countries"] = st.sidebar.multiselect(
                "Países",
                options=sorted(countries),
                default=list(sorted(countries)[:3]) if len(countries) >= 3 else list(sorted(countries)),  # Default to first 3 or all
                key="comp_countries"
            )
        else:
            st.sidebar.warning("Nenhum país encontrado nos dados.")
    else:
        st.sidebar.warning("Coluna 'Country' não encontrada.")
    
    # Filtro por tipo
    if "Type" in df.columns:
        types = df["Type"].dropna().unique()
        if len(types) > 0:
            filters["types"] = st.sidebar.multiselect(
                "Tipos",
                options=sorted(types),
                default=list(sorted(types)),  # Default to all types
                key="comp_types"
            )
        else:
            st.sidebar.warning("Nenhum tipo encontrado nos dados.")
    else:
        st.sidebar.warning("Coluna 'Type' não encontrada.")
    
    # Filtro por período
    year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]
    if year_columns:
        min_year = int(min(year_columns))
        max_year = int(max(year_columns))
        filters["year_range"] = st.sidebar.slider(
            "Período",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="comp_years"
        )
    else:
        st.sidebar.warning("Nenhuma coluna de ano encontrada.")
    
    # Show selected filters for debugging
    if st.sidebar.checkbox("🔍 Debug - Mostrar Filtros", key="debug_filters"):
        st.sidebar.write("Filtros selecionados:")
        st.sidebar.json(filters)
    
    # Return filters even if some are empty - let individual components handle the logic
    return filters
