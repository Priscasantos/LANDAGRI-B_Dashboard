"""
Base Components for Dashboard
============================

Componentes base e utilitários compartilhados entre todas as páginas do dashboard.
Inclui funcionalidades comuns como validação de dados, formatação, e componentes UI.

Author: Dashboard Iniciativas LULC
Date: 2025-07-23
"""

from typing import Any

import pandas as pd
import streamlit as st


class DashboardBase:
    """Classe base para componentes do dashboard."""

    @staticmethod
    def validate_data() -> bool:
        """
        Valida se os dados estão carregados na sessão.

        Returns:
            bool: True se dados estão disponíveis, False caso contrário
        """
        if "df_interpreted" not in st.session_state:
            st.error(
                "❌ Dados não encontrados na sessão. Verifique se o app.py carregou os dados corretamente."
            )
            return False

        if (
            st.session_state.df_interpreted is None
            or st.session_state.df_interpreted.empty
        ):
            st.error(
                "❌ Nenhum dado disponível. Verifique o processo de carregamento de dados."
            )
            return False

        return True

    @staticmethod
    def get_data() -> pd.DataFrame | None:
        """
        Obtém os dados da sessão com validação.

        Returns:
            DataFrame ou None se dados não estão disponíveis
        """
        if not DashboardBase.validate_data():
            return None
        return st.session_state.df_interpreted

    @staticmethod
    def show_data_info(df: pd.DataFrame) -> None:
        """
        Mostra informações básicas sobre os dados carregados.

        Args:
            df: DataFrame com os dados
        """
        with st.sidebar:
            st.info(f"📊 **Dados carregados:** {len(df)} iniciativas")


class ChartComponent:
    """Classe base para componentes de gráficos."""

    def __init__(self, title: str, data: pd.DataFrame):
        self.title = title
        self.data = data

    def render(self) -> None:
        """Método base para renderizar o componente."""
        st.subheader(self.title)
        if self.data.empty:
            st.warning("Nenhum dado disponível para exibir.")
            return
        self._render_content()

    def _render_content(self) -> None:
        """Método a ser implementado pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar _render_content")


class FilterComponent:
    """Classe base para componentes de filtros."""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def render_filters(self) -> dict[str, Any]:
        """
        Renderiza filtros e retorna valores selecionados.

        Returns:
            Dict com os valores dos filtros selecionados
        """
        raise NotImplementedError("Subclasses devem implementar render_filters")
