"""
Class Details Component - Comparison Analysis
============================================

Componente para renderizar detalhes de classes das iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_class_details_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de detalhes de classes para análise comparativa.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 🏷️ Detalhes das Classes das Iniciativas")
    if filtered_df.empty or "Classes" not in filtered_df.columns:
        st.warning("⚠️ Nenhum dado de classes disponível.")
        return
    # Exibir tabela expandida de classes
    for idx, row in filtered_df.iterrows():
        st.markdown(f"**{row.get('Display_Name', row.get('Name', 'Iniciativa'))}:**")
        classes = row.get("Classes", [])
        if isinstance(classes, list) and classes:
            st.write(pd.DataFrame(classes))
        else:
            st.info("Sem detalhes de classes disponíveis.")
