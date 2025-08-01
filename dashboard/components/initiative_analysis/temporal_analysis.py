"""
Temporal Analysis Module
=======================

Módulo para análise temporal das iniciativas LULC.
Fornece interface e lógica para análise da evolução temporal dos dados.

Funcionalidades:
- Análise de evolução temporal
- Gráficos de tendências
- Métricas temporais
- Interface interativa

Autor: Dashboard Iniciativas LULC
Data: 2025-07-30
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Importar funções de charts
from dashboard.components.initiative_analysis.charts.temporal_charts import (
    plot_coverage_gaps_chart,
    plot_temporal_coverage_heatmap,
    plot_temporal_evolution_frequency,
    plot_temporal_gaps_analysis,
    plot_yearly_distribution,
)

# Importar utils de dados
from scripts.data_processing import load_initiatives_json
from scripts.utils import create_initiative_filter, get_available_initiatives


def run(metadata=None, df_original=None):
    """
    Executar análise temporal das iniciativas.

    Args:
        metadata: Dicionário de metadados das iniciativas (opcional)
        df_original: DataFrame original com dados das iniciativas (opcional)
    """

    st.markdown("## 📈 Análise Temporal")
    st.markdown(
        """
    Explore a evolução temporal das iniciativas LULC e identifique padrões de cobertura temporal.
    """
    )

    # Carregar dados se não fornecidos
    if metadata is None or df_original is None:
        try:
            metadata = load_initiatives_json()
            df_original = pd.json_normalize(metadata)
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return

    # Filtros interativos
    st.markdown("### 🔧 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        # Filtro de iniciativas
        available_initiatives = get_available_initiatives(metadata)
        selected_initiatives = st.multiselect(
            "Selecione as iniciativas:",
            available_initiatives,
            default=(
                available_initiatives[:5]
                if len(available_initiatives) > 5
                else available_initiatives
            ),
            help="Selecione as iniciativas para análise temporal",
        )

    with col2:
        # Filtro de período
        if "temporal_coverage" in df_original.columns:
            # Extrair anos únicos dos dados temporais
            all_years = []
            for coverage in df_original["temporal_coverage"].dropna():
                if isinstance(coverage, list):
                    for period in coverage:
                        if isinstance(period, dict) and "start_year" in period:
                            all_years.append(period["start_year"])
                        if isinstance(period, dict) and "end_year" in period:
                            all_years.append(period["end_year"])

            if all_years:
                min_year = min(all_years)
                max_year = max(all_years)

                year_range = st.slider(
                    "Período de análise:",
                    min_value=min_year,
                    max_value=max_year,
                    value=(min_year, max_year),
                    help="Selecione o período para análise",
                )
            else:
                st.warning("Não foi possível extrair informações temporais dos dados")
                year_range = (2000, 2025)
        else:
            year_range = (2000, 2025)

    # Filtrar dados
    filtered_df = create_initiative_filter(df_original, selected_initiatives)

    if filtered_df.empty:
        st.warning("Nenhuma iniciativa selecionada ou dados disponíveis.")
        return

    # Abas de análise temporal
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Evolução Temporal",
            "🗓️ Cobertura Temporal",
            "📅 Distribuição Anual",
            "🔍 Análise de Lacunas",
        ]
    )

    with tab1:
        st.markdown("#### 📈 Evolução da Frequência de Iniciativas")

        try:
            fig_evolution = plot_temporal_evolution_frequency(filtered_df)
            st.plotly_chart(fig_evolution, use_container_width=True)

            st.markdown(
                """
            **Interpretação:**
            - Visualiza como o número de iniciativas evolui ao longo do tempo
            - Identifica períodos de maior atividade
            - Mostra tendências temporais no desenvolvimento de iniciativas
            """
            )
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de evolução temporal: {e}")

    with tab2:
        st.markdown("#### 🗓️ Mapa de Calor da Cobertura Temporal")

        try:
            fig_heatmap = plot_temporal_coverage_heatmap(filtered_df)
            st.plotly_chart(fig_heatmap, use_container_width=True)

            st.markdown(
                """
            **Interpretação:**
            - Mostra a intensidade da cobertura temporal por período
            - Identifica anos com maior concentração de dados
            - Facilita a identificação de padrões sazonais
            """
            )
        except Exception as e:
            st.error(f"Erro ao gerar mapa de calor temporal: {e}")

    with tab3:
        st.markdown("#### 📅 Distribuição Anual de Iniciativas")

        try:
            fig_yearly = plot_yearly_distribution(filtered_df)
            st.plotly_chart(fig_yearly, use_container_width=True)

            st.markdown(
                """
            **Interpretação:**
            - Distribui as iniciativas por ano
            - Mostra a evolução histórica do desenvolvimento de iniciativas
            - Identifica períodos de maior crescimento
            """
            )
        except Exception as e:
            st.error(f"Erro ao gerar distribuição anual: {e}")

    with tab4:
        st.markdown("#### 🔍 Análise de Lacunas Temporais")

        try:
            # Gráfico de análise de lacunas
            fig_gaps = plot_temporal_gaps_analysis(filtered_df)
            st.plotly_chart(fig_gaps, use_container_width=True)

            # Gráfico de lacunas de cobertura
            fig_coverage_gaps = plot_coverage_gaps_chart(filtered_df)
            st.plotly_chart(fig_coverage_gaps, use_container_width=True)

            st.markdown(
                """
            **Interpretação:**
            - Identifica períodos sem cobertura de dados
            - Mostra lacunas na continuidade temporal
            - Ajuda no planejamento de novas coletas de dados
            """
            )
        except Exception as e:
            st.error(f"Erro ao gerar análise de lacunas: {e}")

    # Métricas resumo
    st.markdown("### 📊 Métricas Temporais")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_initiatives = len(filtered_df)
        st.metric("Total de Iniciativas", total_initiatives)

    with col2:
        # Calcular período coberto
        if "temporal_coverage" in filtered_df.columns:
            years_covered = []
            for coverage in filtered_df["temporal_coverage"].dropna():
                if isinstance(coverage, list):
                    for period in coverage:
                        if isinstance(period, dict):
                            if "start_year" in period:
                                years_covered.append(period["start_year"])
                            if "end_year" in period:
                                years_covered.append(period["end_year"])

            if years_covered:
                period_span = max(years_covered) - min(years_covered) + 1
                st.metric("Período Coberto", f"{period_span} anos")
            else:
                st.metric("Período Coberto", "N/A")
        else:
            st.metric("Período Coberto", "N/A")

    with col3:
        # Calcular média de anos por iniciativa
        if "temporal_coverage" in filtered_df.columns:
            years_per_initiative = []
            for coverage in filtered_df["temporal_coverage"].dropna():
                if isinstance(coverage, list):
                    years_count = 0
                    for period in coverage:
                        if (
                            isinstance(period, dict)
                            and "start_year" in period
                            and "end_year" in period
                        ):
                            years_count += period["end_year"] - period["start_year"] + 1
                    if years_count > 0:
                        years_per_initiative.append(years_count)

            if years_per_initiative:
                avg_years = sum(years_per_initiative) / len(years_per_initiative)
                st.metric("Média Anos/Iniciativa", f"{avg_years:.1f}")
            else:
                st.metric("Média Anos/Iniciativa", "N/A")
        else:
            st.metric("Média Anos/Iniciativa", "N/A")

    with col4:
        # Calcular densidade temporal
        if year_range and total_initiatives > 0:
            density = total_initiatives / (year_range[1] - year_range[0] + 1)
            st.metric("Densidade Temporal", f"{density:.2f} init/ano")
        else:
            st.metric("Densidade Temporal", "N/A")


if __name__ == "__main__":
    run()
