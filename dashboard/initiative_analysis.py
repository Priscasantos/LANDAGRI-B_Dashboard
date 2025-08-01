"""
Initiative Analysis Dashboard - Versão Consolidada
=================================================

Dashboard completo consolidando toda funcionalidade dos arquivos legados:
- comparative_old.py: filtros avançados, múltiplos gráficos
- temporal_old.py: análise temporal completa
- detailed_old.py: seleção de iniciativas, radar charts

Funcionalidades:
- Menu lateral funcional com páginas separadas
- Filtros por tipo, metodologia, resolução, precisão
- Seleção múltipla de iniciativas para comparação
- Radar charts, dual bars, heatmaps, scatter plots
- Timeline completo com análise de gaps
- Análise temporal com evolução e cobertura

Autor: Dashboard Iniciativas LULC
Data: 2025-07-30
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

# Importar charts consolidados
try:
    from dashboard.components.initiative_analysis.charts.comparison_charts import (
        plot_accuracy_resolution_scatter,
    )
    from dashboard.components.initiative_analysis.charts.detailed_charts import (
        create_heatmap_chart,
    )
    from dashboard.components.initiative_analysis.charts.temporal_charts import (
        plot_coverage_gaps_chart,
        plot_temporal_availability_heatmap,
        plot_temporal_evolution_frequency,
        plot_timeline_chart,
    )

    CHARTS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Alguns charts não disponíveis: {e}")
    CHARTS_AVAILABLE = False

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
        # Fallback para análise temporal se a página não for reconhecida
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
            📊 Advanced Comparative Analysis
        </h2>
        <p style="color: #d1fae5; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Compare LULC initiatives with advanced filters and multiple visualizations
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🔎 Initiative Filters")

    # Filtros em colunas - similar ao comparative_old.py
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        # Filtro por tipo
        if "Type" in df.columns:
            tipos_disponiveis = df["Type"].dropna().unique().tolist()
            selected_types = st.multiselect(
                "📑 Initiative Types:",
                options=tipos_disponiveis,
                default=tipos_disponiveis,
                help="Filter by initiative types",
            )
        else:
            selected_types = []

        # Filtro por metodologia
        if "Methodology" in df.columns:
            metodologias_disponiveis = df["Methodology"].dropna().unique().tolist()
            selected_methods = st.multiselect(
                "🔬 Methodologies:",
                options=metodologias_disponiveis,
                default=metodologias_disponiveis[
                    : min(5, len(metodologias_disponiveis))
                ],
                help="Filter by methodologies",
            )
        else:
            selected_methods = []

    with filter_col2:
        # Filtro por resolução
        if "Resolution" in df.columns:
            res_min = float(df["Resolution"].min())
            res_max = float(df["Resolution"].max())
            selected_res_range = st.slider(
                "📐 Resolution Range (m):",
                min_value=res_min,
                max_value=res_max,
                value=(res_min, res_max),
                help="Filter by spatial resolution range",
            )
        else:
            selected_res_range = None

        # Filtro por precisão
        if "Accuracy (%)" in df.columns:
            acc_min = float(df["Accuracy (%)"].min())
            acc_max = float(df["Accuracy (%)"].max())
            selected_acc_range = st.slider(
                "🎯 Accuracy Range (%):",
                min_value=acc_min,
                max_value=acc_max,
                value=(acc_min, acc_max),
                help="Filter by accuracy range",
            )
        else:
            selected_acc_range = None

    # Aplicar filtros
    filtered_df = df.copy()

    if selected_types and "Type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

    if selected_methods and "Methodology" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]

    if selected_res_range and "Resolution" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["Resolution"] >= selected_res_range[0])
            & (filtered_df["Resolution"] <= selected_res_range[1])
        ]

    if selected_acc_range and "Accuracy (%)" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["Accuracy (%)"] >= selected_acc_range[0])
            & (filtered_df["Accuracy (%)"] <= selected_acc_range[1])
        ]

    if filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa encontrada com os filtros selecionados.")
        return

    st.markdown("---")
    st.markdown("### 📊 Comparison Charts")

    # Abas com diferentes tipos de análise
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🎯 Accuracy vs Resolution",
            "📊 Distributions",
            "🔥 Performance Heatmap",
            "📋 Detailed Table",
        ]
    )

    with tab1:
        st.markdown("#### 🎯 Accuracy vs Resolution Analysis")
        if (
            CHARTS_AVAILABLE
            and "Accuracy (%)" in filtered_df.columns
            and "Resolution" in filtered_df.columns
        ):
            try:
                fig_scatter = plot_accuracy_resolution_scatter(filtered_df)
                if hasattr(fig_scatter, "update_layout"):
                    fig_scatter.update_layout(title=None)
                st.plotly_chart(fig_scatter, use_container_width=True)
                setup_download_form(
                    fig_scatter, "precision_resolution_scatter", "scatter_comp"
                )
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de dispersão: {e}")
        else:
            st.warning("Dados insuficientes para gráfico de dispersão")

    with tab2:
        st.markdown("#### 📊 Distributions by Type and Methodology")

        col1, col2 = st.columns(2)

        with col1:
            if "Type" in filtered_df.columns:
                st.markdown("##### Distribution by Type")
                type_counts = filtered_df["Type"].value_counts()
                fig_pie_type = px.pie(
                    values=type_counts.values, names=type_counts.index
                )
                st.plotly_chart(fig_pie_type, use_container_width=True)

        with col2:
            if "Methodology" in filtered_df.columns:
                st.markdown("##### Distribution by Methodology")
                method_counts = filtered_df["Methodology"].value_counts()
                fig_pie_method = px.pie(
                    values=method_counts.values, names=method_counts.index
                )
                st.plotly_chart(fig_pie_method, use_container_width=True)

    with tab3:
        st.markdown("#### 🔥 Normalized Performance Heatmap")
        try:
            # Criar heatmap de performance com métricas disponíveis
            numeric_cols = filtered_df.select_dtypes(include=[int, float]).columns
            if len(numeric_cols) > 0:
                fig_heatmap = create_heatmap_chart(filtered_df)
                if fig_heatmap:
                    if hasattr(fig_heatmap, "update_layout"):
                        fig_heatmap.update_layout(title=None)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    setup_download_form(
                        fig_heatmap, "performance_heatmap", "heatmap_comp"
                    )
            else:
                st.warning("Nenhuma coluna numérica disponível para heatmap")
        except Exception as e:
            st.error(f"Erro ao gerar heatmap: {e}")

    with tab4:
        st.markdown("#### 📋 Filtered Data Table")
        st.dataframe(filtered_df, use_container_width=True)

        # Download CSV
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name="filtered_initiatives_comparison.csv",
                mime="text/csv",
                key="download-comparison-csv",
            )


def render_temporal_analysis(df: pd.DataFrame, metadata: dict) -> None:
    """
    Renderizar análise temporal completa baseada no temporal_old.py.
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

    # Preparar dados temporais
    temporal_data = prepare_temporal_data(metadata, df)

    if temporal_data.empty:
        st.warning("⚠️ Dados temporais insuficientes para análise.")
        return

    # Temporal controls
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
            )

    # Dropdown removido conforme solicitado

    # Abas de análise temporal
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Timeline", "📈 Evolution", "🔥 Coverage Heatmap", "⚠️ Gap Analysis"]
    )
    with tab1:
        st.markdown("#### 📊 Complete Initiatives Timeline")
        if CHARTS_AVAILABLE:
            try:
                fig_timeline = plot_timeline_chart(metadata, temporal_data)
                if hasattr(fig_timeline, "update_layout"):
                    fig_timeline.update_layout(title=None)
                st.plotly_chart(fig_timeline, use_container_width=True)
                setup_download_form(
                    fig_timeline, "timeline_initiatives", "timeline_temp"
                )
            except Exception as e:
                st.error(f"Error generating timeline: {e}")
        else:
            st.warning("Charts not available")
        # Temporal summary metrics
        if not temporal_data.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Active Initiatives", len(temporal_data))
            with col2:
                if "Cobertura_Percentual" in temporal_data.columns:
                    avg_coverage = temporal_data["Cobertura_Percentual"].mean()
                    st.metric("Average Coverage", f"{avg_coverage:.1f}%")
            with col3:
                if "Periodo_Total_Anos" in temporal_data.columns:
                    total_span = temporal_data["Periodo_Total_Anos"].sum()
                    st.metric("Total Span", f"{total_span} years")

    with tab2:
        st.markdown("#### 📈 Frequency Evolution")
        if CHARTS_AVAILABLE:
            try:
                fig_evolution = plot_temporal_evolution_frequency(df)
                if hasattr(fig_evolution, "update_layout"):
                    fig_evolution.update_layout(title=None)
                st.plotly_chart(fig_evolution, use_container_width=True)
                setup_download_form(
                    fig_evolution, "frequency_evolution", "evolution_temp"
                )
            except Exception as e:
                st.error(f"Error generating temporal evolution: {e}")

    with tab3:
        st.markdown("#### 🔥 Temporal Coverage Heatmap")
        if CHARTS_AVAILABLE:
            try:
                fig_heatmap = plot_temporal_availability_heatmap(df)
                if hasattr(fig_heatmap, "update_layout"):
                    fig_heatmap.update_layout(title=None)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                setup_download_form(fig_heatmap, "coverage_heatmap", "heatmap_temp")
            except Exception as e:
                st.error(f"Error generating temporal heatmap: {e}")

    with tab4:
        st.markdown("#### ⚠️ Temporal Gap Analysis")
        if CHARTS_AVAILABLE:
            try:
                fig_gaps = plot_coverage_gaps_chart(df)
                if hasattr(fig_gaps, "update_layout"):
                    fig_gaps.update_layout(title=None)
                st.plotly_chart(fig_gaps, use_container_width=True)
                setup_download_form(fig_gaps, "gap_analysis", "gaps_temp")
            except Exception as e:
                st.error(f"Error generating gap analysis: {e}")


def render_detailed_analysis(df: pd.DataFrame, metadata: dict) -> None:
    """
    Renderizar análise detalhada com seleção de iniciativas baseada no detailed_old.py.
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
        st.markdown("#### 📊 Dual Bars Comparison: Accuracy vs Resolution")
        if (
            "Accuracy (%)" in df_filtered.columns
            and "Resolution" in df_filtered.columns
        ):
            try:
                # Normalize resolution (inverse for better visualization)
                df_filtered = df_filtered.copy()
                df_filtered["resolution_norm"] = (1 / df_filtered["Resolution"]) / (
                    1 / df_filtered["Resolution"]
                ).max()

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        y=df_filtered["Display_Name"],
                        x=df_filtered["Accuracy (%)"],
                        name="Accuracy (%)",
                        orientation="h",
                        marker_color="royalblue",
                    )
                )
                fig.add_trace(
                    go.Bar(
                        y=df_filtered["Display_Name"],
                        x=df_filtered["resolution_norm"] * 100,
                        name="Resolution (Normalized)",
                        orientation="h",
                        marker_color="orange",
                    )
                )
                fig.update_layout(
                    barmode="group",
                    xaxis_title="Value (%)",
                    yaxis_title="Initiative",
                    title=None,
                    height=max(400, len(df_filtered) * 30 + 100),
                )
                st.plotly_chart(fig, use_container_width=True)
                setup_download_form(fig, "dual_bars_comparison", "dual_bars_det")

            except Exception as e:
                st.error(f"Error generating dual bars: {e}")
        else:
            st.warning("Required columns not available for dual bars")

    with tab2:
        st.markdown("#### 🎯 Multidimensional Radar Chart")
        try:
            # Numeric columns for radar chart
            radar_columns = []
            potential_cols = [
                "Accuracy (%)",
                "Resolution",
                "Classes",
                "Num_Agri_Classes",
            ]
            for col in potential_cols:
                if col in df_filtered.columns:
                    radar_columns.append(col)

            if len(radar_columns) >= 3:
                fig_radar = create_radar_chart_detailed(df_filtered, radar_columns)
                if fig_radar:
                    if hasattr(fig_radar, "update_layout"):
                        fig_radar.update_layout(title=None)
                    st.plotly_chart(fig_radar, use_container_width=True)
                    setup_download_form(fig_radar, "radar_chart", "radar_det")
            else:
                st.warning("Insufficient columns for radar chart")

        except Exception as e:
            st.error(f"Error generating radar chart: {e}")

    with tab3:
        st.markdown("#### 🔥 Correlation Heatmap")
        try:
            fig_heatmap = create_heatmap_chart(df_filtered)
            if fig_heatmap:
                if hasattr(fig_heatmap, "update_layout"):
                    fig_heatmap.update_layout(title=None)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                setup_download_form(fig_heatmap, "correlation_heatmap", "heatmap_det")
        except Exception as e:
            st.error(f"Error generating heatmap: {e}")

    with tab4:
        st.markdown("#### 📈 Detailed Data Table")
        st.dataframe(df_filtered, use_container_width=True)

        # Download CSV
        if not df_filtered.empty:
            csv = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Selected Data (CSV)",
                data=csv,
                file_name="selected_initiatives_detailed.csv",
                mime="text/csv",
                key="download-detailed-csv",
            )

    with tab5:
        st.markdown("#### 📅 Annual Coverage Analysis")
        if metadata:
            coverage_data = []
            for name in selected_initiatives:
                if name in metadata:
                    details = metadata[name]
                    if isinstance(details, dict) and "available_years" in details:
                        years = details["available_years"]
                        if isinstance(years, list):
                            for year in years:
                                coverage_data.append(
                                    {"Initiative": name, "Year": year, "Available": 1}
                                )

            if coverage_data:
                coverage_df = pd.DataFrame(coverage_data)
                pivot_table = coverage_df.pivot(
                    index="Initiative", columns="Year", values="Available"
                ).fillna(0)

                fig_coverage = px.imshow(
                    pivot_table,
                    title=None,
                    color_continuous_scale="Blues",
                    aspect="auto",
                )
                st.plotly_chart(fig_coverage, use_container_width=True)
            else:
                st.warning("Temporal coverage data not available")


def prepare_temporal_data(metadata: dict, df: pd.DataFrame) -> pd.DataFrame:
    """
    Preparar dados temporais baseado no metadata e DataFrame.
    """
    temporal_data = []

    # Build a mapping from initiative name to acronym if available
    acronym_map = {}
    if df is not None and not df.empty:
        if "Name" in df.columns and "Acronym" in df.columns:
            acronym_map = dict(zip(df["Name"], df["Acronym"]))

    for nome, details in metadata.items():
        if isinstance(details, dict) and "available_years" in details:
            years = details["available_years"]
            if isinstance(years, list) and years:
                # Use acronym if available, else use the name
                display_name = acronym_map.get(nome, nome)
                temporal_data.append(
                    {
                        "Nome": nome,
                        "Display_Name": display_name,
                        "Primeiro_Ano": min(years),
                        "Ultimo_Ano": max(years),
                        "Anos_Lista": years,
                        "Cobertura_Anos": len(years),
                        "Periodo_Total_Anos": max(years) - min(years) + 1,
                    }
                )

    if not temporal_data:
        return pd.DataFrame()

    temporal_df = pd.DataFrame(temporal_data)
    temporal_df["Cobertura_Percentual"] = (
        (
            temporal_df["Cobertura_Anos"]
            / temporal_df["Periodo_Total_Anos"].replace(0, 1)
        )
        * 100
    ).round(1)

    return temporal_df


def create_radar_chart_detailed(df: pd.DataFrame, columns: list[str]) -> go.Figure:
    """
    Criar radar chart detalhado para múltiplas iniciativas.
    """
    fig = go.Figure()

    # Normalizar dados para escala 0-1
    df_norm = df[columns].copy()
    for col in columns:
        if df_norm[col].max() > 0:
            df_norm[col] = df_norm[col] / df_norm[col].max()

    colors = px.colors.qualitative.Set1

    for i, (_, row) in enumerate(df.iterrows()):
        values = [df_norm.iloc[i, df_norm.columns.get_loc(col)] for col in columns]
        values.append(values[0])  # Fechar o radar

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=columns + [columns[0]],
                fill="toself",
                name=row["Display_Name"],
                line_color=colors[i % len(colors)],
            )
        )

    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 1]}},
        showlegend=True,
        title="Radar Chart: Comparação Multidimensional",
    )

    return fig


# Para compatibilidade com implementações legadas
def initiative_analysis(metadata=None, df_original=None):
    """Função legada - redireciona para run()."""
    run(metadata, df_original)


if __name__ == "__main__":
    run()
