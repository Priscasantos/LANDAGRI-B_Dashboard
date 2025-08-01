"""
Methodology Deep Dive Component - Comparison Analysis
====================================================

Componente para análise aprofundada de metodologias das iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_methodology_deepdive_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de análise aprofundada de metodologias.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🔬 Análise Aprofundada de Metodologias")
    if filtered_df.empty or "Methodology" not in filtered_df.columns:
        st.warning("⚠️ Nenhum dado de metodologia disponível.")
        return
    # Exemplo: tabela de frequência de metodologias
    freq = filtered_df["Methodology"].value_counts().reset_index()
    freq.columns = ["Metodologia", "Contagem"]
    st.dataframe(freq, use_container_width=True)
    st.download_button(
        label="📥 Download Frequência de Metodologias",
        data=freq.to_csv(index=False).encode('utf-8'),
        file_name="methodology_deepdive.csv",
        mime="text/csv"
    )
