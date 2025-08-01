"""
Detailed Table Component - Comparison Analysis
=============================================

Componente para renderizar a aba de tabela detalhada na análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_detailed_table_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de tabela detalhada para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📋 Tabela Detalhada das Iniciativas")
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado disponível para tabela detalhada.")
        return
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button(
        label="📥 Download Tabela",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="detailed_table.csv",
        mime="text/csv"
    )
