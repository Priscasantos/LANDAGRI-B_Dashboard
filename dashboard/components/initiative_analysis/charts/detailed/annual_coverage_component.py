"""
Annual Coverage Component - Detailed Analysis
============================================

Componente para renderizar cobertura anual das iniciativas na análise detalhada.

Author: Dashboard Iniciativas LULC
Date: 2025-08-01
"""

import pandas as pd
import streamlit as st

def render_annual_coverage_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de cobertura anual das iniciativas.
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas
    """
    st.markdown("#### 📅 Cobertura Anual das Iniciativas")
    if filtered_df.empty or "available_years" not in filtered_df.columns:
        st.warning("⚠️ Nenhum dado de cobertura anual disponível.")
        return
    for idx, row in filtered_df.iterrows():
        st.markdown(f"**{row.get('Display_Name', row.get('Name', 'Iniciativa'))}:**")
        years = row.get("available_years", [])
        if isinstance(years, list) and years:
            st.write(pd.DataFrame({"Ano": years}))
        else:
            st.info("Sem dados de anos disponíveis.")
