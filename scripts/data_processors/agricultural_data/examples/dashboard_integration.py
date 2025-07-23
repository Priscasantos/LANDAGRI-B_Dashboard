#!/usr/bin/env python3
"""
Exemplo - Integração com Dashboard Existente
============================================

Mostra como integrar os novos processadores com o dashboard
existente mantendo compatibilidade.
"""

import streamlit as st


def integrate_with_dashboard():
    """Integração com dashboard Streamlit existente."""

    # Importar dados agrícolas
    from scripts.data_processors.agricultural_data import get_agricultural_data

    # Cache para performance
    @st.cache_data
    def load_agricultural_data():
        agri_data = get_agricultural_data()
        return agri_data.get_dashboard_compatible_data("CONAB")

    # Carregar dados
    data = load_agricultural_data()

    # Interface do usuário
    st.title("Calendário Agrícola CONAB")

    if "calendar" in data:
        calendar_df = data["calendar"]

        # Filtros
        col1, col2 = st.columns(2)

        with col1:
            crops = st.multiselect(
                "Culturas:",
                calendar_df["crop"].unique(),
                default=calendar_df["crop"].unique()[:3],
            )

        with col2:
            regions = st.multiselect(
                "Regiões:",
                calendar_df["region"].unique(),
                default=calendar_df["region"].unique(),
            )

        # Filtrar dados
        filtered_df = calendar_df[
            (calendar_df["crop"].isin(crops)) & (calendar_df["region"].isin(regions))
        ]

        # Mostrar dados
        st.dataframe(filtered_df)

        # Mostrar resumo
        if "calendar_summary" in data:
            st.subheader("Resumo por Região")
            st.dataframe(data["calendar_summary"])


if __name__ == "__main__":
    integrate_with_dashboard()
