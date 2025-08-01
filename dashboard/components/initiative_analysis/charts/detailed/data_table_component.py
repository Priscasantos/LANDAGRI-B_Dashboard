"""
Data Table Component - Detailed Analysis
=======================================

Componente para renderizar tabela de dados detalhada na análise detalhada.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_data_table_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de tabela de dados detalhada.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📈 Tabela de Dados Detalhada")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para tabela detalhada.")
        return
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button(
        label="📥 Download Tabela Detalhada",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="detailed_data_table.csv",
        mime="text/csv"
    )
