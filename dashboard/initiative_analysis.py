
"""
Initiative Analysis Dashboard - Consolidated Version
==================================================

Complete dashboard consolidating all functionality from legacy files:
- comparative_old.py: advanced filters, multiple charts
- temporal_old.py: complete temporal analysis
- detailed_old.py: initiative selection, radar charts

Features:
- Functional sidebar menu with separate pages
- Filters by type, methodology, resolution, accuracy
- Multiple initiative selection for comparison
- Radar charts, dual bars, heatmaps, scatter plots
- Complete timeline with gap analysis
- Temporal analysis with evolution and coverage

Author: LANDAGRI-B Project Team 
Date: 2025-07-30
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.components.initiative_analysis.charts.comparison import (
    render_accuracy_resolution_tab,
    render_class_details_tab,
    render_detailed_table_tab,
    render_distributions_tab,
    render_methodology_deepdive_tab,
    render_performance_heatmap_tab,
)
from dashboard.components.initiative_analysis.charts.comparison.distributions_component import render_methodology_distribution
from dashboard.components.initiative_analysis.charts.comparison.bar_chart_component import render_bar_chart_tab
from dashboard.components.initiative_analysis.charts.detailed import (
    render_annual_coverage_tab,
    render_data_table_tab,
    render_dual_bars_tab,
    render_heatmap_tab,
    render_radar_chart_tab,
)
from dashboard.components.initiative_analysis.charts.temporal import (
    render_coverage_matrix_heatmap,
    render_evolution_analysis,
    render_gaps_analysis,
    render_timeline_tab,
)

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def run(metadata=None, df_original=None):
    """
    Execute comprehensive analysis of LULC initiatives with sidebar menu.

    Args:
        metadata: Dictionary of initiative metadata (optional)
        df_original: Original DataFrame with initiative data (optional)
    """
    # Standard visual header
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

    # Get session data or parameters
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
                st.error(f"Error loading metadata: {e}")
                return
    else:
        st.error("❌ No data available for initiative analysis.")
        return

    # Check if we have enough data
    if df_for_analysis is None or df_for_analysis.empty:
        st.warning("⚠️ No initiative data available for analysis.")
        return

    # Add Display_Name if not present
    if "Display_Name" not in df_for_analysis.columns:
        df_for_analysis = df_for_analysis.copy()
        if "Acronym" in df_for_analysis.columns:
            df_for_analysis["Display_Name"] = df_for_analysis["Acronym"]
        else:
            df_for_analysis["Display_Name"] = df_for_analysis["Name"].str[:10]

    # Use navigation system from app.py
    current_page = st.session_state.get("current_page", "Temporal Analysis")

    # Render page based on main menu selection
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
            📊 Advanced Comparative Analysis
        </h2>
        <p style="color: #d1fae5; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Compare LULC initiatives with advanced filters and multiple visualizations
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


    # Filtros removidos conforme solicitado. Usar df diretamente.
    filtered_df = df.copy()

    st.markdown("---")
    st.markdown("### 📊 Comparison Charts")

    # Abas de análise comparativa usando todos os componentes
    tab_labels = [
        "🎯 Accuracy vs Spatial Resolution",
        "📏 Spatial Resolution",
        "⭐ Global Accuracy",
        "🧮 Methodology Distribution",
        "🏷️ Class Details",
        "🔬 Methodology - Deep Dive",
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
        render_bar_chart_tab(filtered_df)
    with tab_method_dist:
        # Methodology distribution
        render_methodology_distribution(filtered_df)
    with tab_class_details:
        render_class_details_tab(filtered_df)
    # Check for required columns
    methodology_cols = [col for col in filtered_df.columns if 'methodology' in col.lower() or 'method' in col.lower()]
    performance_cols = [col for col in filtered_df.columns if filtered_df[col].dtype in ['float64', 'int64'] and col.lower() != 'initiative']
    # For detailed table, just need any columns

    with tab_method_deep:
        if not methodology_cols:
            st.warning("⚠️ No methodology column found in the data. Please check your input file.")
        else:
            render_methodology_deepdive_tab(filtered_df)
    with tab_perf_norm:
        if not performance_cols:
            st.warning("⚠️ No numerical performance columns found in the data. Please check your input file.")
        else:
            render_performance_heatmap_tab(filtered_df)
    with tab_table:
        if filtered_df.empty:
            st.warning("⚠️ No data available for detailed table.")
        else:
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


    # Abas de análise temporal com componentes modulares
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Timeline", "📈 Evolution", "⌚Temporal Coverage", "⚠️ Gap Analysis"]
    )

    with tab1:
        render_timeline_tab(temporal_data, metadata)

    with tab2:
        render_evolution_analysis(temporal_data)

    with tab3:
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
    # Merge available_years from metadata
    if "available_years" not in df_filtered.columns:
        df_filtered["available_years"] = df_filtered["Name"].map(lambda n: metadata.get(n, {}).get("available_years", []))
    st.markdown("---")
    st.markdown("### 📊 Detailed Analyses")
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Bar Chart",
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
    if df is not None and not df.empty and "Name" in df.columns and "Acronym" in df.columns:
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
