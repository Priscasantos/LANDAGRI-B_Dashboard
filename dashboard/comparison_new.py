"""
Comparison Dashboard - Orquestrador Principal
============================================

Orquestrador para a página de análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
Version: 2.0 - Modular
"""

import streamlit as st


from dashboard.components.comparison import (
    comparison_filters,
    sensor_comparison,
    temporal_comparison,
)
from dashboard.components.shared.base import DashboardBase


def run():
    """Executa o dashboard de análise comparativa."""
    # Validar dados
    if not DashboardBase.validate_data():
        st.error("❌ Dados não disponíveis. Verifique se os dados foram carregados corretamente.")
        return

    # Obter dados
    df = DashboardBase.get_data()
    
    if df is None or df.empty:
        st.error("❌ DataFrame está vazio ou não foi carregado.")
        return

    # Mostrar informações dos dados na sidebar
    DashboardBase.show_data_info(df)

    # Layout principal
    st.title("📊 Análise Comparativa")
    st.markdown("Compare iniciativas LULC por diferentes dimensões.")
    st.markdown("---")

    # Filtros de comparação
    filters = comparison_filters.render(df)

    # Always show tabs, even if no filters are applied
    st.markdown("---")

    # Layout em abas
    tab1, tab2 = st.tabs(["Por Sensor", "Temporal"])

    with tab1:
        st.subheader("🛰️ Análise por Sensor")
        sensor_comparison.render(df, filters)

    with tab2:
        st.subheader("📈 Análise Temporal")
        temporal_comparison.render(df, filters)
