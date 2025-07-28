"""
Comparison Dashboard - Orquestrador Principal Modular
====================================================

Orquestrador principal para análise comparativa de iniciativas LULC.
Integra todos os componentes modulares de comparação.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
Version: 3.0 - Modular Completo
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from typing import Union, Type

# Add scripts to path for imports
current_dir = Path(__file__).parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import the JSON interpreter
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata
except ImportError as e:
    st.error(f"❌ Error importing JSON interpreter: {e}")
    def interpret_initiatives_metadata(file_path=None):
        st.warning("JSON interpreter could not be loaded. Using empty DataFrame.")
        return pd.DataFrame()

# Import comparison components
from dashboard.components.comparison import (
    comparison_filters,
    sensor_comparison,
    temporal_comparison,
    class_analysis,
    methodology_analysis,
    performance_analysis,
)
from dashboard.components.shared.base import DashboardBase


def get_slider_range(series_min: pd.Series, series_max: pd.Series, 
                     default_min: Union[int, float], default_max: Union[int, float], 
                     data_type: Union[Type[int], Type[float]] = int):
    """Helper function to safely get min/max for sliders"""
    
    # Ensure series are not empty and contain valid numbers
    s_min_numeric = pd.to_numeric(series_min.dropna(), errors='coerce')
    s_max_numeric = pd.to_numeric(series_max.dropna(), errors='coerce')

    s_min_valid = s_min_numeric.dropna()
    s_max_valid = s_max_numeric.dropna()
    
    if s_min_valid.empty or s_max_valid.empty:
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))
    
    try:
        overall_min_val = s_min_valid.min()
        overall_max_val = s_max_valid.max()
    except Exception:
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    if pd.isna(overall_min_val) or pd.isna(overall_max_val):
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    overall_min = data_type(overall_min_val)
    overall_max = data_type(overall_max_val)
    
    if overall_min > overall_max:
        overall_min, overall_max = data_type(default_min), data_type(default_max)

    return overall_min, overall_max, (overall_min, overall_max)


def run():
    """Executa o dashboard de análise comparativa."""
    st.header("📊 Comparative Analysis Dashboard")
    st.markdown("Use os filtros abaixo para selecionar e comparar iniciativas LULC baseado em vários critérios.")

    # Load data using session state or JSON interpreter
    if 'df_interpreted' not in st.session_state:
        try:
            metadata_file_path = current_dir / "data" / "json" / "initiatives_metadata.jsonc"
            df_interpreted = interpret_initiatives_metadata(metadata_file_path)
            if df_interpreted.empty:
                st.error("❌ A interpretação dos dados resultou em um DataFrame vazio. Verifique o interpretador e o arquivo de dados.")
                return
            st.session_state.df_interpreted = df_interpreted
        except Exception as e:
            st.error(f"❌ Erro ao carregar ou interpretar dados: {e}")
            st.session_state.df_interpreted = pd.DataFrame()
            return

    df = st.session_state.get('df_interpreted', pd.DataFrame())

    if df.empty:
        st.error("❌ Os dados interpretados não foram carregados ou estão vazios. Não é possível prosseguir.")
        st.info("Certifique-se de que `initiatives_metadata.jsonc` existe no caminho correto e que `json_interpreter.py` está funcionando corretamente.")
        return

    # Ensure Display_Name exists
    if 'Display_Name' not in df.columns:
        st.warning("⚠️ Coluna 'Display_Name' está faltando nos dados interpretados. Os gráficos podem não exibir nomes corretamente.")
        if 'Name' in df.columns:
            df['Display_Name'] = df['Name'].apply(lambda x: str(x)[:20])
        else:
            df['Display_Name'] = "Unknown"

    # Advanced Filters Section
    st.markdown("### 🔎 Filtros de Iniciativas")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        tipos = sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else []
        selected_types = st.multiselect("Tipo", options=tipos, default=tipos, key="type_filter")
    
    with filter_col2:
        metodologias = sorted(df["Methodology"].dropna().unique().tolist()) if "Methodology" in df.columns else []
        selected_methods = st.multiselect("Metodologia", options=metodologias, default=metodologias, key="methodology_filter")

    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        # Use the new min/max columns from the interpreter
        res_min_series = df.get('Resolution_min_val', pd.Series(dtype=float))
        res_max_series = df.get('Resolution_max_val', pd.Series(dtype=float))
        min_r, max_r, default_r_val = get_slider_range(res_min_series, res_max_series, 0, 1000, data_type=int)
        selected_res_range = st.slider("Resolução (m)", 
                                       min_value=min_r, 
                                       max_value=max_r, 
                                       value=default_r_val,
                                       help="Filtra iniciativas cuja faixa de resolução se sobrepõe à faixa selecionada.",
                                       key="resolution_filter")
    
    with filter_col4:
        # Use the new min/max columns from the interpreter
        acc_min_series = df.get('Accuracy_min_val', pd.Series(dtype=float))
        acc_max_series = df.get('Accuracy_max_val', pd.Series(dtype=float))
        min_a, max_a, default_a_val = get_slider_range(acc_min_series, acc_max_series, 0.0, 100.0, data_type=float)
        selected_acc_range = st.slider("Precisão (%)", 
                                       min_value=min_a, 
                                       max_value=max_a, 
                                       value=default_a_val,
                                       format="%.1f",
                                       help="Filtra iniciativas cuja faixa de precisão se sobrepõe à faixa selecionada.",
                                       key="accuracy_filter")

    # Reference System filter
    filter_col5, filter_col6 = st.columns(2)
    with filter_col5:
        all_ref_systems = set()
        if 'Reference_System' in df.columns:
            for item in df['Reference_System'].dropna():
                if isinstance(item, list):
                    all_ref_systems.update(item)
                elif isinstance(item, str):
                    all_ref_systems.update(item.split(', '))
        selected_ref_systems = st.multiselect("Sistema de Referência", 
                                              options=sorted(list(all_ref_systems)), 
                                              default=sorted(list(all_ref_systems)), 
                                              key="ref_system_filter")

    # Filter data based on selections
    filtered_df = df.copy()
    if selected_types:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    if selected_methods:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]
    
    # Resolution filtering: overlap condition
    if 'Resolution_min_val' in filtered_df.columns and 'Resolution_max_val' in filtered_df.columns:
        sel_res_min, sel_res_max = selected_res_range
        filtered_df = filtered_df[
            (filtered_df['Resolution_max_val'] >= sel_res_min) & 
            (filtered_df['Resolution_min_val'] <= sel_res_max)
        ]

    # Accuracy filtering
    if 'Accuracy_min_val' in filtered_df.columns and 'Accuracy_max_val' in filtered_df.columns:
        sel_acc_min, sel_acc_max = selected_acc_range
        filtered_df = filtered_df[
            (filtered_df['Accuracy_max_val'] >= sel_acc_min) & 
            (filtered_df['Accuracy_min_val'] <= sel_acc_max)
        ]
        
    if selected_ref_systems and 'Reference_System' in filtered_df.columns:
        def check_ref_system(row_val):
            if isinstance(row_val, list):
                return any(rs in selected_ref_systems for rs in row_val)
            elif isinstance(row_val, str):
                return any(rs in selected_ref_systems for rs in row_val.split(', '))
            return False
        filtered_df = filtered_df[filtered_df['Reference_System'].apply(check_ref_system)]

    if filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa corresponde aos critérios de filtro atuais.")
    
    # Create filters dict for components
    filters = {
        "countries": [],  # Countries will be handled by country_comparison component
        "types": selected_types,
        "methodologies": selected_methods,
        "resolution_range": selected_res_range,
        "accuracy_range": selected_acc_range,
        "ref_systems": selected_ref_systems
    }

    st.markdown("---")
    st.markdown("### 📊 Análises Comparativas")

    # Main analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛰️ Por Sensor", 
        "📈 Temporal",
        "🎯 Classes",
        "🔬 Metodologias",
        "⚡ Performance"
    ])

    with tab1:
        sensor_comparison.render(filtered_df, filters)

    with tab2:
        temporal_comparison.render(filtered_df, filters)
    
    with tab3:
        class_analysis.render(filtered_df, filters)
    
    with tab4:
        methodology_analysis.render(filtered_df, filters)
    
    with tab5:
        performance_analysis.render(filtered_df, filters)

    # Data table section removed per user request
    # User: "nao precisa ter tabela d edados detalhada em todos os menus compariosn"
    
    # Download functionality removed per user request
    # User: "remova donwlaod dados filtrados como CSV de todos os lugares tbm"


if __name__ == '__main__':
    run()
