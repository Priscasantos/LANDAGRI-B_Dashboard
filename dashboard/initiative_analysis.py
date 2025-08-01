"""
Initiative Analysis Dashboard - Consolidated Version
==================================================

Complete dashboard consolidating all functionality from legacy files:
- comparative_old.py: advanced filters, multiple charts
- temporal_old.py: complete temporal analysis
- detailed_old.py:    # Temporal analysis tabs with modular components
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Timeline", "📈 Evolution", "🕒 Temporal Coverage", "⚠️ Gap Analysis"]
    )tiative selection, radar charts

Features:
- Functional sidebar menu with separate pages
- Filters by type, methodology, resolution, accuracy
- Multiple initiative selection for comparison
- Radar charts, dual bars, heatmaps, scatter plots
- Complete timeline with gap analysis
- Temporal analysis with evolution and coverage

Author: LULC Initiatives Dashboard
Date: 2025-07-30
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# Importar componentes modulares consolidados (sempre disponíveis no escopo global)
# Componentes temporais
from dashboard.components.initiative_analysis.charts.temporal import (
    render_timeline_tab,
    render_evolution_analysis,
    render_coverage_matrix_heatmap,
    render_gaps_analysis,
)
# Componentes de comparação
from dashboard.components.initiative_analysis.charts.comparison import (
    render_accuracy_resolution_tab,
    render_distributions_tab,
    render_performance_heatmap_tab,
    render_detailed_table_tab,
    render_class_details_tab,
    render_methodology_deepdive_tab,
)
from dashboard.components.initiative_analysis.charts.comparison.bar_chart_component import render_bar_chart_tab
# Componentes detalhados
from dashboard.components.initiative_analysis.charts.detailed import (
    render_dual_bars_tab,
    render_radar_chart_tab,
    render_heatmap_tab,
    render_data_table_tab,
    render_annual_coverage_tab,
)
CHARTS_AVAILABLE = True

# Import para download de gráficos
try:
    from scripts.utilities.ui_elements import setup_download_form
except ImportError:

    def setup_download_form(fig, default_filename, key_prefix):
        st.warning("Download não disponível")


def run(metadata=None, df_original=None):
    """
    Executar análise abrangente das iniciativas LULC com menu lateral funcional.

    Args:
        metadata: Dicionário de metadados das iniciativas (opcional)
        df_original: DataFrame original com dados das iniciativas (opcional)
    """

    # Header visual padronizado
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🔬 Initiative Analysis
        </h1>
        <p style="color: #dbeafe; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Comprehensive analysis of LULC initiatives with full features
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Obter dados da sessão ou parâmetros
    df_for_analysis = None
    meta_geral = None

    if metadata is not None and df_original is not None:
        df_for_analysis = df_original
        meta_geral = metadata
    elif (
        "df_interpreted" in st.session_state
        and not st.session_state.df_interpreted.empty
    ):
        df_for_analysis = st.session_state.df_interpreted
        meta_geral = st.session_state.get("metadata", {})
        if not meta_geral:
            try:
                from scripts.utilities.json_interpreter import _load_jsonc_file

                metadata_file_path = (
                    _project_root / "data" / "initiatives_metadata.jsonc"
                )
                meta_geral = _load_jsonc_file(metadata_file_path)
            except Exception as e:
                st.error(f"Erro carregando metadata: {e}")
                return
    else:
        st.error("❌ Nenhum dado disponível para análise de iniciativas.")
        return

    # Verificar se temos dados suficientes
    if df_for_analysis is None or df_for_analysis.empty:
        st.warning("⚠️ Nenhum dado de iniciativas disponível para análise.")
        return

    # Adicionar Display_Name se não existir
    if "Display_Name" not in df_for_analysis.columns:
        df_for_analysis = df_for_analysis.copy()
        if "Acronym" in df_for_analysis.columns:
            df_for_analysis["Display_Name"] = df_for_analysis["Acronym"]
        else:
            df_for_analysis["Display_Name"] = df_for_analysis["Name"].str[:10]

    # Usar o sistema de navegação existente do app.py
    # A página atual é determinada pelo menu "Initiative Analysis" no sidebar principal
    current_page = st.session_state.get("current_page", "Temporal Analysis")

    # Renderizar a página baseada na seleção do menu principal
    if current_page == "Temporal Analysis":
        render_temporal_analysis(df_for_analysis, meta_geral)
    elif current_page == "Comparative Analysis":
        render_comparative_analysis(df_for_analysis, meta_geral)
    elif current_page == "Detailed Analysis":
        render_detailed_analysis(df_for_analysis, meta_geral)
    else:
        # Fallback to temporal analysis if page is not recognized
        render_temporal_analysis(df_for_analysis, meta_geral)


def render_comparative_analysis(df: pd.DataFrame, metadata: dict) -> None:
    """
    Renderizar análise comparativa com todos os filtros e gráficos dos arquivos legados.
    """

    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 600;">
            📊 Análise Comparativa Avançada
        </h2>
        <p style="color: #d1fae5; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Compare iniciativas LULC com filtros avançados e múltiplas visualizações
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


    # Filtros removidos conforme solicitado. Usar df diretamente.
    filtered_df = df.copy()

    st.markdown("---")
    st.markdown("### 📊 Gráficos de Comparação")

    # Abas de análise comparativa usando todos os componentes
    tab_labels = [
        "🎯 Precisão vs Resolução Espacial",
        "📏 Resolução Espacial",
        "⭐ Acurácia Global",
        "� Distribuição de Metodologias",
        "🏷️ Detalhes de Classes",
        "🔬 Metodologia - Deep Dive",
        "🔥 Normalized Performance",
        "📋 Detailed Table",
    ]
    (
        tab_acc_res,
        tab_res,
        tab_acc,
        tab_method_dist,
        tab_class_details,
        tab_method_deep,
        tab_perf_norm,
        tab_table,
    ) = st.tabs(tab_labels)

    with tab_acc_res:
        render_accuracy_resolution_tab(filtered_df)
    with tab_res:
        # Spatial resolution (distribution)
        render_distributions_tab(filtered_df)  # includes sub-tabs, can be adjusted
    with tab_acc:
        # Global accuracy (bar chart)
        from dashboard.components.initiative_analysis.charts.comparison.bar_chart_component import render_bar_chart_tab
        render_bar_chart_tab(filtered_df)
    with tab_method_dist:
        # Methodology distribution
        render_methodology_deepdive_tab(filtered_df)
    with tab_class_details:
        render_class_details_tab(filtered_df)
    with tab_method_deep:
        # Methodology deep dive (frequency table)
        render_methodology_deepdive_tab(filtered_df)
    with tab_perf_norm:
        render_performance_heatmap_tab(filtered_df)
    with tab_table:
        render_detailed_table_tab(filtered_df)


def render_temporal_analysis(df: pd.DataFrame, metadata: dict) -> None:
    """
    Render complete temporal analysis with consolidated modular components.
    Integrates all temporal components migrated from temporal_old.py.
    """
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.2);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 600;">
            ⏳ Complete Temporal Analysis
        </h2>
        <p style="color: #fef3c7; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Timeline, temporal evolution, and gap analysis of LULC initiatives
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Prepare temporal data
    temporal_data = prepare_temporal_data(metadata, df)

    if temporal_data.empty:
        st.warning("⚠️ Insufficient temporal data for analysis.")
        return

    # Use only standardized modular components

    # Global temporal controls
    col1, col2 = st.columns(2)

    with col1:
        # Extract unique years from data
        all_years = set()
        for _, row in df.iterrows():
            start_year = pd.to_numeric(row.get("Start_Year", 0), errors="coerce")
            end_year = pd.to_numeric(row.get("End_Year", 0), errors="coerce")
            if pd.notna(start_year) and start_year > 0:
                all_years.add(int(start_year))
            if pd.notna(end_year) and end_year > 0:
                all_years.add(int(end_year))
        if all_years:
            min_year = min(all_years)
            max_year = max(all_years)
            st.slider(
                "📅 Analysis period:",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                help="Select the period for temporal analysis",
                key="temporal_period_range"
            )

    with col2:
        st.markdown("### 📊 Quick Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Active Initiatives", len(temporal_data))
        with col_b:
            if "Coverage_Percentage" in temporal_data.columns:
                avg_coverage = temporal_data["Coverage_Percentage"].mean()
                st.metric("Average Coverage", f"{avg_coverage:.1f}%")

    # Abas de análise temporal com componentes modulares
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Timeline", "📈 Evolution", "�️ Cobertura Temporal", "⚠️ Gap Analysis"]
    )

    with tab1:
        render_timeline_tab(temporal_data, metadata)

    with tab2:
        render_evolution_analysis(temporal_data)

    with tab3:
        from dashboard.components.initiative_analysis.charts.temporal import render_coverage_matrix_heatmap
        render_coverage_matrix_heatmap(temporal_data, metadata)

    with tab4:
        render_gaps_analysis(temporal_data)


def render_detailed_analysis(df: pd.DataFrame, metadata: dict) -> None:
    """
    Render detailed analysis with initiative selection based on detailed_old.py.
    """
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 600;">
            🔍 Detailed Analysis
        </h2>
        <p style="color: #ede9fe; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Detailed comparison with multi-selection and radar charts
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    # Initiative selection for comparison
    st.markdown("### 🎯 Initiative Selection")
    selected_initiatives = st.multiselect(
        "Select initiatives for comparison:",
        options=df["Name"].tolist(),
        default=df["Name"].tolist()[: min(3, len(df))],
        help="Choose 2 or more initiatives for detailed comparative analysis",
    )
    if len(selected_initiatives) < 2:
        st.info(
            "👈 Select at least two initiatives in the menu above to start the analysis."
        )
        return
    # Filter data for selected initiatives
    df_filtered = df[df["Name"].isin(selected_initiatives)].copy()
    st.markdown("---")
    st.markdown("### 📊 Detailed Analyses")
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Dual Bars",
            "🎯 Radar Chart",
            "🔥 Heatmap",
            "📈 Data Table",
            "📅 Annual Coverage",
        ]
    )
    with tab1:
        render_dual_bars_tab(df_filtered)

    with tab2:
        render_radar_chart_tab(df_filtered)

    with tab3:
        render_heatmap_tab(df_filtered)

    with tab4:
        render_data_table_tab(df_filtered)

    with tab5:
        render_annual_coverage_tab(df_filtered)


def prepare_temporal_data(metadata: dict, df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare temporal data based on metadata and DataFrame.
    """
    temporal_data = []

    # Build a mapping from initiative name to acronym if available
    acronym_map = {}
    if df is not None and not df.empty:
        if "Name" in df.columns and "Acronym" in df.columns:
            acronym_map = dict(zip(df["Name"], df["Acronym"]))

    for name, details in metadata.items():
        if isinstance(details, dict) and "available_years" in details:
            years = details["available_years"]
            if isinstance(years, list) and years:
                # Use acronym if available, else use the name
                display_name = acronym_map.get(name, name)
                temporal_data.append(
                    {
                        "Name": name,
                        "Display_Name": display_name,
                        "First_Year": min(years),
                        "Last_Year": max(years),
                        "Years_List": years,
                        "Coverage_Years": len(years),
                        "Total_Period_Years": max(years) - min(years) + 1,
                    }
                )

    if not temporal_data:
        return pd.DataFrame()

    temporal_df = pd.DataFrame(temporal_data)
    temporal_df["Coverage_Percentage"] = (
        (
            temporal_df["Coverage_Years"]
            / temporal_df["Total_Period_Years"].replace(0, 1)
        )
        * 100
    ).round(1)

    return temporal_df


# For compatibility with legacy implementations
def initiative_analysis(metadata=None, df_original=None):
    """Legacy function - redirects to run()."""
    run(metadata, df_original)


if __name__ == "__main__":
    run()
