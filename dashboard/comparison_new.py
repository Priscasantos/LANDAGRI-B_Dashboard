"""
Comparison Dashboard - Orquestrador Principal
============================================

Orquestrador para a página de análise comparativa.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
Version: 2.0 - Modular
"""

import streamlit as st

from .components.comparison import (
    comparison_filters,
    country_comparison,
    sensor_comparison,
    temporal_comparison,
)
from .components.shared.base import DashboardBase


def run():
    """Executa o dashboard de análise comparativa."""
    # Validar dados
    if not DashboardBase.validate_data():
        return

    # Obter dados
    df = DashboardBase.get_data()

    # Mostrar informações dos dados na sidebar
    DashboardBase.show_data_info(df)

    # Layout principal
    st.title("📊 Análise Comparativa")
    st.markdown("---")

    # Filtros de comparação
    filters = comparison_filters.render(df)

    if not filters:
        st.info("Configure os filtros para visualizar as comparações.")
        return

    st.markdown("---")

    # Layout em abas
    tab1, tab2, tab3 = st.tabs(["Por País", "Por Sensor", "Temporal"])

    with tab1:
        country_comparison.render(df, filters)

    with tab2:
        sensor_comparison.render(df, filters)

    with tab3:
        temporal_comparison.render(df, filters)
