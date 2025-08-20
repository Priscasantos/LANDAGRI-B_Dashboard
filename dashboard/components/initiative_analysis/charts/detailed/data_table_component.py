"""
Data Table Component - Detailed Analysis
=======================================

Component for rendering detailed data table in detailed analysis.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

from dashboard.components.shared.nomenclature import clean_column_names


def render_data_table_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render detailed data table tab.
    O título da tabela é derivado do próprio DataFrame (parâmetro intrínseco):
      - procura por filtered_df.attrs['title']
      - ou por colunas comuns ('initiative', 'initiative_name', 'name', 'nome', 'titulo', 'title')
      - ou pelo nome do índice
      - senão usa um título padrão
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    if filtered_df.empty:
        st.warning("⚠️ No data available for detailed table.")
        return

    # Determina título a partir do DataFrame (atributos ou colunas conhecidas)
    title = None

    # 1) attrs['title'] se fornecido
    if isinstance(filtered_df, pd.DataFrame):
        title = filtered_df.attrs.get("title")

    # 2) colunas comuns que podem conter o nome da iniciativa
    if not title:
        for col in ("initiative", "initiative_name", "name", "nome", "titulo", "title"):
            if col in filtered_df.columns:
                vals = filtered_df[col].dropna().unique()
                if vals.size == 1:
                    title = f"Tabela: {str(vals[0])}"
                elif vals.size > 1:
                    title = "Tabela: múltiplas iniciativas"
                break

    # 3) nome do índice
    if not title and filtered_df.index.name:
        title = f"Tabela: {filtered_df.index.name}"

    # 4) fallback padrão
    if not title:
        title = "Detailed Initiatives Characteristics"

    # Apply friendly column names
    df_display = clean_column_names(filtered_df, use_friendly_names=True)

    # Exibe título e tabela
    st.markdown(f"<p style='font-size:18px;margin:0'><strong>{title}</strong></p>", unsafe_allow_html=True)
    st.dataframe(df_display, use_container_width=True)
