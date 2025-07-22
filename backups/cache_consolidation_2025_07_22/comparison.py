"""
Comparative Analysis Dashboard Module
====================================

This module provides interactive comparative analysis tools for LULC initiatives.
Features filtering, visualization, and comparison capabilities across multiple
metrics and dimensions.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Type, Union

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ========================================
# 🚀 SISTEMA DE CACHE OTIMIZADO - COMPARISON
# ========================================
try:
    from utilities.cache_system import (
        load_optimized_data, 
        setup_performance_sidebar,
        get_filtered_data,
        calculate_statistics,
        prepare_chart_data
    )
    OPTIMIZATION_ENABLED = True
    st.sidebar.success("⚡ Sistema consolidado ativo - COMPARISON")
except ImportError:
    OPTIMIZATION_ENABLED = False
    # Funções dummy em caso de falha na importação
    def load_optimized_data(): return None, None, {'cache_hits': 0}
    def setup_performance_sidebar(): pass
    def get_filtered_data(*args): return None
    def calculate_statistics(*args): return {}
    def prepare_chart_data(*args): return None
    st.sidebar.warning("⚠️ Cache não disponível - COMPARISON")

from scripts.utilities.ui_elements import setup_download_form

# Setup paths for imports
current_dir = Path(__file__).parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import JSON interpreter
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata
except ImportError as e:
    st.error(f"❌ Error importing JSON interpreter: {e}")

    def interpret_initiatives_metadata(file_path=None):
        """Fallback function when JSON interpreter is not available."""
        st.warning("JSON interpreter could not be loaded. Using empty DataFrame.")
        return pd.DataFrame()


# Import plotting functions with comprehensive error handling
plotting_functions_loaded = False
plot_functions = {}

try:
    from scripts.plotting.generate_graphics import (
        plot_resolution_accuracy_scatter,
        plot_classes_frequency_boxplot,
        plot_spatial_resolution_comparison,
        plot_global_accuracy_comparison,
        plot_temporal_evolution_frequency,
        plot_class_diversity_focus,
        plot_classification_methodology,
        plot_resolution_vs_launch_year,
        plot_initiatives_by_resolution_category,
        plot_resolution_coverage_heatmap,
        plot_resolution_by_sensor_family,
        plot_resolution_slopegraph,
        plot_distribuicao_classes,
        plot_distribuicao_metodologias,
        plot_acuracia_por_metodologia,
        plot_normalized_performance_heatmap,
    )

    plotting_functions_loaded = True

    # Store functions in a dictionary for safe access
    plot_functions = {
        "spatial_resolution": plot_spatial_resolution_comparison,
        "global_accuracy": plot_global_accuracy_comparison,
        "temporal_evolution": plot_temporal_evolution_frequency,
        "class_diversity": plot_class_diversity_focus,
        "classification_methodology": plot_classification_methodology,
        "resolution_vs_launch": plot_resolution_vs_launch_year,
        "resolution_category": plot_initiatives_by_resolution_category,
        "resolution_heatmap": plot_resolution_coverage_heatmap,
        "resolution_sensor": plot_resolution_by_sensor_family,
        "resolution_slope": plot_resolution_slopegraph,
        "distribution_classes": plot_distribuicao_classes,
        "distribution_methods": plot_distribuicao_metodologias,
        "accuracy_method": plot_acuracia_por_metodologia,
        "normalized_performance": plot_normalized_performance_heatmap,
    }

except ImportError as e:
    plotting_functions_loaded = False
    st.error(f"⚠️ Plotting functions import error: {e}")

# Import table functions
try:
    from scripts.utilities.tables import gap_analysis
except ImportError:

    def gap_analysis(metadata: Dict, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """Fallback function for gap analysis when module is not available."""
        return pd.DataFrame()


def get_slider_range(
    series_min: pd.Series,
    series_max: pd.Series,
    default_min: Union[int, float],
    default_max: Union[int, float],
    data_type: Union[Type[int], Type[float]] = int,
) -> tuple:
    """
    Helper function to safely calculate slider ranges from pandas Series.

    Args:
        series_min: Series containing minimum values
        series_max: Series containing maximum values
        default_min: Default minimum value if calculation fails
        default_max: Default maximum value if calculation fails
        data_type: Type to cast the result to (int or float)

    Returns:
        Tuple containing (overall_min, overall_max, (overall_min, overall_max))
    """
    # Ensure series are not empty and contain valid numbers
    s_min_numeric = pd.to_numeric(series_min.dropna(), errors="coerce")
    s_max_numeric = pd.to_numeric(series_max.dropna(), errors="coerce")

    s_min_valid = s_min_numeric.dropna()
    s_max_valid = s_max_numeric.dropna()

    if s_min_valid.empty or s_max_valid.empty:
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    try:
        overall_min_val = s_min_valid.min()
        overall_max_val = s_max_valid.max()
    except Exception:
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    if pd.isna(overall_min_val) or pd.isna(overall_max_val):
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    overall_min = data_type(overall_min_val)
    overall_max = data_type(overall_max_val)

    # Fallback if data is inconsistent
    if overall_min > overall_max:
        overall_min, overall_max = data_type(default_min), data_type(default_max)

    return overall_min, overall_max, (overall_min, overall_max)


def safe_plot_call(plot_key: str, *args, **kwargs):
    """
    Safely call a plotting function with error handling.

    Args:
        plot_key: Key identifying the plotting function
        *args: Arguments to pass to the plotting function
        **kwargs: Keyword arguments to pass to the plotting function

    Returns:
        Plotly Figure object or None if function not available
    """
    if not plotting_functions_loaded or plot_key not in plot_functions:
        return None

    try:
        return plot_functions[plot_key](*args, **kwargs)
    except Exception as e:
        st.error(f"Error generating chart: {e}")
        return None


def run():
    # ========================================
    # 🚀 SISTEMA DE CACHE OTIMIZADO - COMPARISON
    # ========================================
    if OPTIMIZATION_ENABLED:
        # Setup performance sidebar
        setup_performance_sidebar()
        
        # Carrega dados otimizados
        metadata, df_original, cache_info = load_optimized_data()
        
        # Mostra informações de cache
        if cache_info.get('cache_hits', 0) > 0:
            st.sidebar.success(f"⚡ Cache hits: {cache_info['cache_hits']}")
    
    st.header("📊 Comparative Analysis Dashboard")
    st.markdown(
        "Use the filters below to select and compare LULC initiatives based on various criteria."
    )

    # Load data using the new JSON interpreter
    if "df_interpreted" not in st.session_state:
        if OPTIMIZATION_ENABLED and 'df_original' in locals():
            st.session_state.df_interpreted = df_original
        else:
            try:
                # Path to the metadata file
                metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
                df_interpreted = interpret_initiatives_metadata(metadata_file_path)
                if df_interpreted.empty:
                    st.error(
                        "❌ Data interpretation resulted in an empty DataFrame. Please check the interpreter and data file."
                    )
                    return
                st.session_state.df_interpreted = df_interpreted
            except Exception as e:
                st.error(f"❌ Error loading or interpreting data: {e}")
            # Fallback to an empty DataFrame in session state to prevent further errors
            st.session_state.df_interpreted = pd.DataFrame()
            return

    df = st.session_state.get("df_interpreted", pd.DataFrame())

    if df.empty:
        st.error("❌ Interpreted data is not loaded or is empty. Cannot proceed.")
        # Optionally, display a message about how to fix or where to check logs
        st.info(
            "Ensure `initiatives_metadata.jsonc` exists at the correct path and the `json_interpreter.py` is functioning correctly."
        )
        return

    # Ensure Display_Name exists, if not, it should have been created by the interpreter
    if "Display_Name" not in df.columns:
        st.warning(
            "⚠️ 'Display_Name' column is missing from the interpreted data. Charts might not display names correctly."
        )
        # As a fallback, create a simple display name if absolutely necessary, though interpreter should handle this
        if "Name" in df.columns:
            df["Display_Name"] = df["Name"].apply(
                lambda x: str(x)[:20]
            )  # Simple fallback
        else:
            df["Display_Name"] = "Unknown"

    st.markdown("### 🔎 Initiative Filters")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        tipos = (
            sorted(df["Type"].dropna().unique().tolist())
            if "Type" in df.columns
            else []
        )
        selected_types = st.multiselect(
            "Type", options=tipos, default=tipos, key="type_filter"
        )

    with filter_col2:
        metodologias = (
            sorted(df["Methodology"].dropna().unique().tolist())
            if "Methodology" in df.columns
            else []
        )
        selected_methods = st.multiselect(
            "Methodology",
            options=metodologias,
            default=metodologias,
            key="methodology_filter",
        )

    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        # Use the new min/max columns from the interpreter
        res_min_series = df.get("Resolution_min_val", pd.Series(dtype=float))
        res_max_series = df.get("Resolution_max_val", pd.Series(dtype=float))
        min_r, max_r, default_r_val = get_slider_range(
            res_min_series, res_max_series, 0, 1000, data_type=int
        )
        selected_res_range = st.slider(
            "Resolution (m)",
            min_value=min_r,
            max_value=max_r,
            value=default_r_val,
            help="Filters initiatives whose resolution range overlaps with the selected range.",
            key="resolution_filter",
        )

    with filter_col4:
        # Use the new min/max columns from the interpreter
        acc_min_series = df.get("Accuracy_min_val", pd.Series(dtype=float))
        acc_max_series = df.get("Accuracy_max_val", pd.Series(dtype=float))
        min_a, max_a, default_a_val = get_slider_range(
            acc_min_series, acc_max_series, 0.0, 100.0, data_type=float
        )
        selected_acc_range = st.slider(
            "Accuracy (%)",
            min_value=min_a,
            max_value=max_a,
            value=default_a_val,
            format="%.1f",
            help="Filters initiatives whose accuracy range overlaps with the selected range.",
            key="accuracy_filter",
        )

    # Row 3 for new filters - Reference System and Detailed Products
    filter_col5, filter_col6 = st.columns(2)
    with filter_col5:
        # Assuming Reference_System is a string or list of strings from the interpreter
        all_ref_systems = set()
        if "Reference_System" in df.columns:
            for item in df["Reference_System"].dropna():
                if isinstance(item, list):  # If interpreter returns a list
                    all_ref_systems.update(item)
                elif isinstance(item, str):  # If interpreter returns a string
                    all_ref_systems.update(
                        item.split(", ")
                    )  # Simple split if it's a comma-sep string
        selected_ref_systems = st.multiselect(
            "Reference System",
            options=sorted(list(all_ref_systems)),
            default=sorted(list(all_ref_systems)),
            key="ref_system_filter",
        )

    # Filter data based on selections
    filtered_df = df.copy()
    if selected_types:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    if selected_methods:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]

    # Resolution filtering: an initiative is included if its range [res_min, res_max] overlaps with selected_res_range [sel_min, sel_max]
    # Overlap condition: sel_min <= res_max AND sel_max >= res_min
    if (
        "Resolution_min_val" in filtered_df.columns
        and "Resolution_max_val" in filtered_df.columns
    ):
        sel_res_min, sel_res_max = selected_res_range
        filtered_df = filtered_df[
            (filtered_df["Resolution_max_val"] >= sel_res_min)
            & (filtered_df["Resolution_min_val"] <= sel_res_max)
        ]

    # Accuracy filtering (similar logic)
    if (
        "Accuracy_min_val" in filtered_df.columns
        and "Accuracy_max_val" in filtered_df.columns
    ):
        sel_acc_min, sel_acc_max = selected_acc_range
        filtered_df = filtered_df[
            (filtered_df["Accuracy_max_val"] >= sel_acc_min)
            & (filtered_df["Accuracy_min_val"] <= sel_acc_max)
        ]

    if selected_ref_systems and "Reference_System" in filtered_df.columns:
        # This filter needs to be robust if Reference_System can be a list or a string
        def check_ref_system(row_val):
            if isinstance(row_val, list):
                return any(rs in selected_ref_systems for rs in row_val)
            elif isinstance(row_val, str):
                return any(
                    rs in selected_ref_systems for rs in row_val.split(", ")
                )  # Simple split
            return False

        filtered_df = filtered_df[
            filtered_df["Reference_System"].apply(check_ref_system)
        ]

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the current filter criteria.")
        # Display tabs even if filtered_df is empty, charts will show their own "no data" messages

    st.markdown("---")
    st.markdown("### 📊 Comparison Charts")

    tab_titles = [
        "Spatial Resolution",
        "Global Accuracy",
        "Temporal Evolution",
        "Class Diversity",
        "Overall Methodology Dist.",
        "Resolution Analysis",
        "Class Details",
        "Methodology Deep Dive",
        "Normalized Performance",  # New Tab for Normalized Performance Heatmap
    ]
    (
        tab_spatial,
        tab_accuracy,
        tab_temporal,
        tab_diversity,
        tab_methodology_dist,
        tab_resolution_analysis,
        tab_class_details,
        tab_methodology_details,
        tab_normalized_performance,
    ) = st.tabs(tab_titles)

    # Renaming the original methodology tab variable for clarity
    # The original tab_methodology is now tab_methodology_dist
    with tab_methodology_dist:
        st.markdown("#### Overall Classification Methodology Distribution")
        st.write(
            "This chart shows the distribution of different classification methodologies used across ALL selected initiatives."
        )

        methodology_chart_type = st.radio(
            "Select Methodology Chart Type:",
            ("Pie Chart", "Bar Chart"),
            key="methodology_chart_type_comparison_tab",  # Unique key for radio in tab
        )
        chart_type_param = "pie" if methodology_chart_type == "Pie Chart" else "bar"

        if not filtered_df.empty:
            try:
                methodology_fig = safe_plot_call(
                    "classification_methodology",
                    filtered_df,
                    chart_type=chart_type_param,
                )
                if methodology_fig:
                    st.plotly_chart(
                        methodology_fig,
                        use_container_width=True,
                        key="overall_methodology_chart_comp",
                    )
                    setup_download_form(
                        methodology_fig,
                        default_filename="classification_methodology_comparison",
                        key_prefix="methodology_comp",
                    )
                else:
                    st.warning("❌ Could not generate methodology chart.")
            except Exception as e:
                st.error(
                    f"❌ Error generating overall classification methodology chart: {e}"
                )
        elif not plotting_functions_loaded:
            st.warning(
                "Overall classification methodology chart cannot be loaded because plotting functions failed to import."
            )
        else:
            st.info(
                "No data to display for overall methodology distribution based on current filters."
            )

    with tab_spatial:
        st.markdown("#### Spatial Resolution Overview")
        st.write(
            "This chart compares the spatial resolution (in meters) of the selected LULC initiatives. Lower values indicate finer (better) resolution."
        )
        if not plotting_functions_loaded:
            st.warning(
                "⚠️ Plotting functions not available. Please check import errors."
            )
        elif not filtered_df.empty:
            try:
                spatial_res_fig = safe_plot_call("spatial_resolution", filtered_df)
                if spatial_res_fig:
                    st.plotly_chart(
                        spatial_res_fig,
                        use_container_width=True,
                        key="spatial_res_chart_comp",
                    )

                # Add download functionality
                if spatial_res_fig:
                    setup_download_form(
                        spatial_res_fig,
                        default_filename="spatial_resolution_comparison",
                        key_prefix="spatial_res_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating spatial resolution chart: {e}")
        elif not plotting_functions_loaded:
            st.warning(
                "Spatial resolution chart cannot be loaded because plotting functions failed to import."
            )
        else:
            st.info("No data to display based on current filters.")

    with tab_accuracy:
        st.markdown("#### Global Accuracy Overview")
        st.write(
            "This chart compares the global accuracy (in %) of the selected LULC initiatives. Higher values indicate better accuracy."
        )
        if not filtered_df.empty:
            try:
                global_acc_fig = safe_plot_call("global_accuracy", filtered_df)
                if global_acc_fig:
                    st.plotly_chart(
                        global_acc_fig,
                        use_container_width=True,
                        key="global_acc_chart_comp",
                    )

                # Add download functionality
                if global_acc_fig:
                    setup_download_form(
                        global_acc_fig,
                        default_filename="global_accuracy_comparison",
                        key_prefix="global_acc_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating global accuracy chart: {e}")
        elif not plotting_functions_loaded:
            st.warning(
                "Global accuracy chart cannot be loaded because plotting functions failed to import."
            )
        else:
            st.info("No data to display based on current filters.")

    with tab_temporal:
        st.markdown("#### Temporal Evolution & Update Frequency")
        st.write(
            "This timeline chart shows the operational period (start to end year) of selected LULC initiatives, colored by their update frequency."
        )
        if not filtered_df.empty:
            try:
                temporal_evo_fig = safe_plot_call("temporal_evolution", filtered_df)
                if temporal_evo_fig:
                    st.plotly_chart(
                        temporal_evo_fig,
                        use_container_width=True,
                        key="temporal_evo_chart_comp",
                    )

                # Add download functionality
                if temporal_evo_fig:
                    setup_download_form(
                        temporal_evo_fig,
                        default_filename="temporal_evolution_frequency",
                        key_prefix="temporal_evo_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating temporal evolution chart: {e}")
        elif not plotting_functions_loaded:
            st.warning(
                "Temporal evolution chart cannot be loaded because plotting functions failed to import."
            )
        else:
            st.info("No data to display based on current filters.")

    with tab_diversity:
        st.markdown("#### Class Diversity and Agricultural Focus")
        st.write(
            "This chart compares the total number of classes versus the number of agricultural-specific classes for each initiative."
        )
        if not filtered_df.empty:
            try:
                class_diversity_fig = safe_plot_call("class_diversity", filtered_df)
                if class_diversity_fig:
                    st.plotly_chart(
                        class_diversity_fig,
                        use_container_width=True,
                        key="class_div_chart_comp",
                    )

                # Add download functionality
                if class_diversity_fig:
                    setup_download_form(
                        class_diversity_fig,
                        default_filename="class_diversity_focus",
                        key_prefix="class_div_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating class diversity chart: {e}")
        elif not plotting_functions_loaded:
            st.warning(
                "Class diversity chart cannot be loaded because plotting functions failed to import."
            )
        else:
            st.info("No data to display based on current filters.")

    with tab_resolution_analysis:  # Content for the new tab
        st.markdown("#### In-depth Resolution Analysis")
        st.write(
            "This section provides a deeper dive into spatial resolution characteristics, including its evolution, distribution by sensor, and relationship with other factors."
        )

        if not plotting_functions_loaded:
            st.warning(
                "Resolution analysis charts cannot be loaded because essential plotting functions failed to import."
            )
        elif filtered_df.empty:
            st.info(
                "No data to display for resolution analysis based on current filters."
            )
        else:
            # Load sensor metadata (once per session or if not already loaded)
            sensors_data_path = current_dir / "data" / "sensors_metadata.jsonc"
            if "sensors_meta" not in st.session_state:
                try:
                    with open(sensors_data_path, "r", encoding="utf-8") as f:
                        # Attempt to parse JSONC by removing comments first
                        content = f.read()
                        # Basic comment removal: lines starting with // and block comments /* ... */
                        import re

                        content_no_comments = re.sub(
                            r"//.*", "", content
                        )  # Remove single line comments
                        content_no_comments = re.sub(
                            r"/\*.*?\*/", "", content_no_comments, flags=re.DOTALL
                        )  # Remove block comments
                        st.session_state.sensors_meta = json.loads(content_no_comments)
                    st.success("Sensor metadata loaded successfully.")
                except Exception as e_sensor_load:
                    st.error(
                        f"❌ Error loading or parsing sensor metadata from {sensors_data_path}: {e_sensor_load}"
                    )
                    st.session_state.sensors_meta = {}  # Fallback to empty dict

            sensors_meta_data = st.session_state.get("sensors_meta", {})

            # Chart 1: Resolution vs. Launch Year
            st.markdown("##### Resolution vs. Launch Year")
            st.write(
                "Shows the relationship between spatial resolution and the year each initiative began. Lower resolution values (Y-axis) are generally better. Points are labeled by initiative."
            )
            try:
                fig_res_launch = safe_plot_call("resolution_vs_launch", filtered_df)
                if fig_res_launch:
                    st.plotly_chart(
                        fig_res_launch,
                        use_container_width=True,
                        key="res_vs_launch_comp",
                    )

                # Add download functionality
                if fig_res_launch:
                    setup_download_form(
                        fig_res_launch,
                        default_filename="resolution_vs_launch_year",
                        key_prefix="res_launch_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating 'Resolution vs. Launch Year' chart: {e}")

            # Chart 2: Initiatives by Resolution Category
            st.markdown("##### Initiatives by Resolution Category")
            st.write(
                "Summarizes how many initiatives fall into predefined spatial resolution categories, stacked by initiative type."
            )
            try:
                fig_res_cat = safe_plot_call("resolution_category", filtered_df)
                if fig_res_cat:
                    st.plotly_chart(
                        fig_res_cat, use_container_width=True, key="res_by_cat_comp"
                    )

                # Add download functionality
                if fig_res_cat:
                    setup_download_form(
                        fig_res_cat,
                        default_filename="initiatives_by_resolution_category",
                        key_prefix="res_cat_comp",
                    )
            except Exception as e:
                st.error(
                    f"❌ Error generating 'Initiatives by Resolution Category' chart: {e}"
                )

            # Chart 3: Resolution vs. Coverage Type Heatmap
            st.markdown("##### Resolution vs. Coverage Type Heatmap")
            st.write(
                "Visualizes the number of initiatives at the intersection of spatial resolution categories and geographic coverage types."
            )
            try:
                fig_res_heatmap = safe_plot_call("resolution_heatmap", filtered_df)
                if fig_res_heatmap:
                    st.plotly_chart(
                        fig_res_heatmap,
                        use_container_width=True,
                        key="res_cov_heatmap_comp",
                    )

                # Add download functionality
                if fig_res_heatmap:
                    setup_download_form(
                        fig_res_heatmap,
                        default_filename="resolution_coverage_heatmap",
                        key_prefix="res_heatmap_comp",
                    )
            except Exception as e:
                st.error(
                    f"❌ Error generating 'Resolution vs.Coverage Heatmap' chart: {e}"
                )

            # Charts requiring sensor metadata
            if not sensors_meta_data:
                st.warning(
                    "Sensor metadata (`sensors_metadata.jsonc`) could not be loaded or is empty. Skipping charts that depend on it (Resolution by Sensor Family, Resolution Slopegraph)."
                )
            else:
                # Chart 4: Resolution by Sensor Family
                st.markdown("##### Resolution Distribution by Sensor Family")
                st.write(
                    "Compares the spread (median, quartiles, outliers) of spatial resolutions for initiatives, grouped by the primary sensor families they utilize."
                )
                try:
                    fig_res_sensor = safe_plot_call(
                        "resolution_by_sensor", filtered_df, sensors_meta_data
                    )
                    if fig_res_sensor:
                        st.plotly_chart(
                            fig_res_sensor,
                            use_container_width=True,
                            key="res_by_sensor_comp",
                        )

                    # Add download functionality
                    if fig_res_sensor:
                        setup_download_form(
                            fig_res_sensor,
                            default_filename="resolution_by_sensor_family",
                            key_prefix="res_sensor_comp",
                        )
                except Exception as e:
                    st.error(
                        f"❌ Error generating 'Resolution by Sensor Family' chart: {e}"
                    )

                # Chart 5: Resolution Improvement Slopegraph
                st.markdown("##### Resolution Improvement Over Time (Slopegraph)")
                st.write(
                    "Shows how individual initiatives have changed their spatial resolution over time, based on changes in their referenced sensors and associated operational years."
                )
                try:
                    fig_res_slope = safe_plot_call(
                        "resolution_slope", filtered_df, sensors_meta_data
                    )
                    if fig_res_slope:
                        st.plotly_chart(
                            fig_res_slope,
                            use_container_width=True,
                            key="res_slope_comp",
                        )

                    # Add download functionality
                    if fig_res_slope:
                        setup_download_form(
                            fig_res_slope,
                            default_filename="resolution_slopegraph",
                            key_prefix="res_slope_comp",
                        )
                except Exception as e:
                    st.error(f"❌ Error generating 'Resolution Slopegraph' chart: {e}")

    with tab_class_details:  # Content for the new Class Details tab
        st.markdown("#### Distribution of Number of Classes")
        st.write(
            "This chart shows the distribution of the total number of classes identified by the selected LULC initiatives, colored by initiative type."
        )
        if not plotting_functions_loaded:
            st.warning(
                "Class details chart cannot be loaded because essential plotting functions failed to import."
            )
        elif filtered_df.empty:
            st.info("No data to display for class details based on current filters.")
        else:
            if "Classes" in filtered_df.columns and "Type" in filtered_df.columns:
                try:
                    # Ensure the 'Classes' column is numeric for the histogram
                    df_for_chart = filtered_df.copy()
                    df_for_chart["Classes"] = pd.to_numeric(
                        df_for_chart["Classes"], errors="coerce"
                    )
                    df_for_chart.dropna(
                        subset=["Classes"], inplace=True
                    )  # Remove rows where 'Classes' could not be converted

                    if not df_for_chart.empty:
                        fig_dist_classes = safe_plot_call(
                            "distribuicao_classes", df_for_chart
                        )
                        if fig_dist_classes:
                            st.plotly_chart(
                                fig_dist_classes,
                                use_container_width=True,
                                key="dist_classes_comp",
                            )

                        # Add download functionality
                        if fig_dist_classes:
                            setup_download_form(
                                fig_dist_classes,
                                default_filename="distribution_classes",
                                key_prefix="dist_classes_comp",
                            )
                    else:
                        st.info(
                            "No valid data for 'Classes' to display the chart after attempting conversion."
                        )
                except Exception as e:
                    st.error(
                        f"❌ Error generating 'Distribution of Classes' chart: {e}"
                    )
            else:
                missing_cols = []
                if "Classes" not in filtered_df.columns:
                    missing_cols.append("Classes")
                if "Type" not in filtered_df.columns:
                    missing_cols.append(
                        "Type"
                    )  # plot_distribuicao_classes uses 'Type' for color
                st.warning(
                    f"The column(s) {', '.join(missing_cols)} are not available in the filtered data, so the 'Distribution of Classes' chart cannot be generated."
                )

    with tab_methodology_details:  # Content for the new Methodology Details tab
        st.markdown("#### Methodology Deep Dive")
        st.write(
            "Explore the distribution of methodologies and their associated accuracies."
        )

        if not plotting_functions_loaded:
            st.warning(
                "Methodology details charts cannot be loaded because essential plotting functions failed to import."
            )
        elif filtered_df.empty:
            st.info(
                "No data to display for methodology details based on current filters."
            )
        else:
            # Chart 1: Distribution of Methodologies (Pie Chart)
            st.markdown("##### Distribution of Methodologies Used")
            if "Methodology" in filtered_df.columns:
                try:
                    method_counts = filtered_df["Methodology"].value_counts()
                    if not method_counts.empty:
                        fig_dist_meth = safe_plot_call(
                            "distribuicao_metodologias", method_counts
                        )
                        if fig_dist_meth:
                            st.plotly_chart(
                                fig_dist_meth,
                                use_container_width=True,
                                key="dist_meth_comp",
                            )

                        # Add download functionality
                        if fig_dist_meth:
                            setup_download_form(
                                fig_dist_meth,
                                default_filename="distribution_methodologies",
                                key_prefix="dist_meth_comp",
                            )
                    else:
                        st.info(
                            "No methodology data to display the distribution chart."
                        )
                except Exception as e:
                    st.error(
                        f"❌ Error generating 'Distribution of Methodologies' chart: {e}"
                    )
            else:
                st.warning(
                    "The 'Methodology' column is not available, so 'Distribution of Methodologies' chart cannot be generated."
                )

            st.markdown("---")  # Separator

            # Chart 2: Accuracy by Methodology (Box Plot)
            st.markdown("##### Accuracy by Methodology")
            if (
                "Methodology" in filtered_df.columns
                and "Accuracy (%)" in filtered_df.columns
                and "Type" in filtered_df.columns
            ):
                try:
                    # Ensure 'Accuracy (%)' is numeric
                    df_for_acc_chart = filtered_df.copy()
                    df_for_acc_chart["Accuracy (%)"] = pd.to_numeric(
                        df_for_acc_chart["Accuracy (%)"], errors="coerce"
                    )
                    df_for_acc_chart.dropna(
                        subset=["Accuracy (%)", "Methodology", "Type"], inplace=True
                    )

                    if not df_for_acc_chart.empty:
                        fig_acc_meth = safe_plot_call(
                            "acuracia_por_metodologia", df_for_acc_chart
                        )
                        if fig_acc_meth:
                            st.plotly_chart(
                                fig_acc_meth,
                                use_container_width=True,
                                key="acc_meth_comp",
                            )

                        # Add download functionality
                        if fig_acc_meth:
                            setup_download_form(
                                fig_acc_meth,
                                default_filename="accuracy_by_methodology",
                                key_prefix="acc_meth_comp",
                            )
                    else:
                        st.info(
                            "No valid data for 'Accuracy (%)' or 'Methodology' to display the accuracy chart after attempting conversion."
                        )
                except Exception as e:
                    st.error(
                        f"❌ Error generating 'Accuracy by Methodology' chart: {e}"
                    )
            else:
                missing_cols_acc = []
                if "Methodology" not in filtered_df.columns:
                    missing_cols_acc.append("Methodology")
                if "Accuracy (%)" not in filtered_df.columns:
                    missing_cols_acc.append("Accuracy (%)")
                if "Type" not in filtered_df.columns:
                    missing_cols_acc.append(
                        "Type"
                    )  # plot_acuracia_por_metodologia uses 'Type' for color
                st.warning(
                    f"The column(s) {', '.join(missing_cols_acc)} are not available, so 'Accuracy by Methodology' chart cannot be generated."
                )

    with (
        tab_normalized_performance
    ):  # Content for the new Normalized Performance Heatmap tab
        st.markdown("#### Normalized Performance Heatmap")
        st.write(
            "This heatmap displays a normalized view of various performance metrics across all selected initiatives. Values are scaled to highlight relative performance within each metric."
        )
        if not plotting_functions_loaded:
            st.warning(
                "Normalized Performance Heatmap cannot be loaded because essential plotting functions failed to import."
            )
        elif filtered_df.empty:
            st.info(
                "No data to display for the Normalized Performance Heatmap based on current filters."
            )
        else:
            try:
                fig_normalized_heatmap = safe_plot_call(
                    "normalized_performance_heatmap", filtered_df
                )
                if fig_normalized_heatmap:
                    st.plotly_chart(
                        fig_normalized_heatmap,
                        use_container_width=True,
                        key="normalized_perf_heatmap_comp",
                    )

                # Add download functionality
                if fig_normalized_heatmap:
                    setup_download_form(
                        fig_normalized_heatmap,
                        default_filename="normalized_performance_heatmap",
                        key_prefix="norm_heatmap_comp",
                    )
            except Exception as e:
                st.error(f"❌ Error generating Normalized Performance Heatmap: {e}")

    st.markdown("---")
    st.markdown("### 📋 Detailed Data Table")
    st.dataframe(filtered_df, use_container_width=True)

    # Correct way to download DataFrame as CSV
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_initiatives_comparison.csv",
            mime="text/csv",
            key="download-comparison-csv",
        )
    else:
        st.info("No data to download based on current filters.")


if __name__ == "__main__":
    run()
