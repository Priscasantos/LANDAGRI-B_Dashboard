import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add scripts to path - This should be at the very top
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Importar componentes de gráficos
from dashboard.components.charts.modern_timeline_chart import (
    timeline_with_modern_controls,
)
from dashboard.components.temporal.coverage_heatmap_component import (
    render_coverage_heatmap,
)
from dashboard.components.temporal.evolution_analysis_component import (
    render_evolution_analysis,
)
from dashboard.components.temporal.gaps_analysis_component import render_gaps_analysis


def run(metadata=None, df_original=None):
    """
    Run temporal analysis with optional data parameters.
    If metadata and df_original are provided, use them directly.
    Otherwise, try to get from st.session_state for Streamlit compatibility.
    """

    st.header("⏳ Comprehensive Temporal Analysis of LULC Initiatives")

    # Get data from session or parameters
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
        st.error("❌ No data available for temporal analysis.")
        return

    # --- Prepare temporal_data DataFrame for modular components ---
    nome_to_sigla = {}
    if (
        df_for_analysis is not None
        and "Acronym" in df_for_analysis.columns
        and "Name" in df_for_analysis.columns
    ):
        for _, row in df_for_analysis.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    temporal_data = []
    for nome, details in meta_geral.items():
        if isinstance(details, dict) and "available_years" in details:
            anos_lista = (
                details["available_years"]
                if isinstance(details["available_years"], list)
                else []
            )
            if anos_lista:
                temporal_data.append(
                    {
                        "Nome": nome,
                        "Display_Name": nome_to_sigla.get(nome, nome[:15]),
                        "Anos_Lista": anos_lista,
                        "Primeiro_Ano": min(anos_lista),
                        "Ultimo_Ano": max(anos_lista),
                        "Tipo": details.get("type", "Uncategorized"),
                    }
                )

    temporal_df = pd.DataFrame(temporal_data)

    # Calculate missing years (gaps) for each initiative
    temporal_df["Anos_Faltando"] = temporal_df["Anos_Lista"].apply(
        calculate_largest_consecutive_gap
    )

    # --- Render all modular temporal charts in tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📅 Timeline", "⚠️ Gaps Analysis", "📈 Evolution", "🔥 Coverage Heatmap"]
    )

    with tab1:
        st.markdown("### 🌍 Modern Timeline of LULC Initiatives")
        st.markdown("*Featuring start/end points, period shadows, and modern design*")
        timeline_with_modern_controls(meta_geral, df_for_analysis)

    with tab2:
        render_gaps_analysis(temporal_df)

    with tab3:
        render_evolution_analysis(temporal_df)

    with tab4:
        render_coverage_heatmap(temporal_df)


def calculate_largest_consecutive_gap(anos_list):
    """Calculate the largest consecutive gap in a list of years"""
    if not isinstance(anos_list, list) or len(anos_list) < 2:
        return 0
    anos_list = sorted(set(anos_list))
    max_gap = 0
    for i in range(len(anos_list) - 1):
        gap = anos_list[i + 1] - anos_list[i] - 1
        if gap > max_gap:
            max_gap = gap
    return max_gap
