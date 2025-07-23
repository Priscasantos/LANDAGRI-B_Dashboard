"""
Detail Tables Component
======================

Componente para tabelas detalhadas das iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza tabelas detalhadas.

    Args:
        df: DataFrame com dados das iniciativas
    """
    st.subheader("📋 Detalhes das Iniciativas")

    # Seleção de colunas para exibir
    available_columns = df.columns.tolist()

    # Colunas essenciais para mostrar por padrão
    default_columns = []
    for col in ["Name", "Country", "Organization", "Start_Year", "End_Year"]:
        if col in available_columns:
            default_columns.append(col)

    if not default_columns:
        default_columns = available_columns[:5]  # Primeiras 5 colunas

    # Seletor de colunas
    selected_columns = st.multiselect(
        "Selecione as colunas para exibir:",
        options=available_columns,
        default=default_columns,
        key="detail_columns",
    )

    if not selected_columns:
        st.warning("Selecione pelo menos uma coluna para exibir.")
        return

    # Filtro de busca
    search_term = st.text_input(
        "🔍 Buscar iniciativas:",
        placeholder="Digite para filtrar...",
        key="detail_search",
    )

    # Aplicar filtro
    filtered_df = df[selected_columns].copy()

    if search_term:
        # Buscar em todas as colunas de texto
        mask = False
        for col in selected_columns:
            if filtered_df[col].dtype == "object":
                mask |= (
                    filtered_df[col]
                    .astype(str)
                    .str.contains(search_term, case=False, na=False)
                )
        filtered_df = filtered_df[mask]

    # Exibir tabela
    st.dataframe(filtered_df, use_container_width=True, height=400)

    # Informações da tabela
    st.info(f"Exibindo {len(filtered_df)} de {len(df)} iniciativas")
