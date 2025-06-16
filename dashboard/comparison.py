import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# import plotly.express as px # This line can be removed if px is not directly used in this file
import sys
import json # Added json import
from pathlib import Path
from typing import Type, Union

# Original sys.path logic
current_dir = Path(__file__).parent.parent # Should be dashboard-iniciativas
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import the new JSON interpreter
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata
except ImportError as e:
    st.error(f"❌ Error importing JSON interpreter: {e}")
    # Define a placeholder if import fails, to allow app to run with a warning
    def interpret_initiatives_metadata(file_path=None):
        st.warning("JSON interpreter could not be loaded. Using empty DataFrame.")
        return pd.DataFrame()

# --- Attempt to import plotting functions with detailed error reporting ---
st.write("Attempting to import plotting functions...") # Debug message
plotting_functions_loaded = False
try:
    from scripts.plotting.generate_graphics import (
        plot_resolution_accuracy_scatter, 
        plot_classes_frequency_boxplot,
        plot_spatial_resolution_comparison,
        plot_global_accuracy_comparison,
        plot_temporal_evolution_frequency,
        plot_class_diversity_focus,
        plot_classification_methodology,
        # New resolution chart imports
        plot_resolution_vs_launch_year,
        plot_initiatives_by_resolution_category,
        plot_resolution_coverage_heatmap,
        plot_resolution_by_sensor_family,
        plot_resolution_slopegraph,
        # Distribution charts for new tabs
        plot_distribuicao_classes,
        plot_distribuicao_metodologias,
        plot_acuracia_por_metodologia
    )
    st.success("SUCCESS: Plotting functions imported from scripts.plotting.generate_graphics!")
    plotting_functions_loaded = True
except ImportError as e_graphics_detail:
    st.error("CRITICAL IMPORT ERROR: Failed to import from scripts.plotting.generate_graphics.")
    st.exception(e_graphics_detail) # Display the full exception
    # Define placeholders if import fails
    def plot_resolution_accuracy_scatter(_filtered_df):
        st.warning("Placeholder: plot_resolution_accuracy_scatter not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_resolution_accuracy_scatter not available", showarrow=False)
    def plot_classes_frequency_boxplot(_filtered_df):
        st.warning("Placeholder: plot_classes_frequency_boxplot not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_classes_frequency_boxplot not available", showarrow=False)
    def plot_spatial_resolution_comparison(_filtered_df): # Added placeholder
        st.warning("Placeholder: plot_spatial_resolution_comparison not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_spatial_resolution_comparison not available", showarrow=False)
    def plot_global_accuracy_comparison(_filtered_df): # Added placeholder
        st.warning("Placeholder: plot_global_accuracy_comparison not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_global_accuracy_comparison not available", showarrow=False)
    def plot_temporal_evolution_frequency(_filtered_df): # Added placeholder
        st.warning("Placeholder: plot_temporal_evolution_frequency not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_temporal_evolution_frequency not available", showarrow=False)
    def plot_class_diversity_focus(_filtered_df): # Added placeholder
        st.warning("Placeholder: plot_class_diversity_focus not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_class_diversity_focus not available", showarrow=False)
    def plot_classification_methodology(filtered_df, chart_type='pie'): # Corrected placeholder
        st.warning("Placeholder: plot_classification_methodology not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_classification_methodology not available", showarrow=False)
    # Placeholders for new resolution charts if main import fails
    def plot_resolution_vs_launch_year(filtered_df):
        st.warning("Placeholder: plot_resolution_vs_launch_year not loaded.")
        return go.Figure().add_annotation(text="plot_resolution_vs_launch_year not available", showarrow=False)
    def plot_initiatives_by_resolution_category(filtered_df):
        st.warning("Placeholder: plot_initiatives_by_resolution_category not loaded.")
        return go.Figure().add_annotation(text="plot_initiatives_by_resolution_category not available", showarrow=False)
    def plot_resolution_coverage_heatmap(filtered_df):
        st.warning("Placeholder: plot_resolution_coverage_heatmap not loaded.")
        return go.Figure().add_annotation(text="plot_resolution_coverage_heatmap not available", showarrow=False)
    def plot_resolution_by_sensor_family(filtered_df, sensors_meta):
        st.warning("Placeholder: plot_resolution_by_sensor_family not loaded.")
        return go.Figure().add_annotation(text="plot_resolution_by_sensor_family not available", showarrow=False)
    def plot_resolution_slopegraph(filtered_df, sensors_meta):
        st.warning("Placeholder: plot_resolution_slopegraph not loaded.")
        return go.Figure().add_annotation(text="plot_resolution_slopegraph not available", showarrow=False)
    # Placeholders for distribution charts for new tabs
    def plot_distribuicao_classes(filtered_df):
        st.warning("Placeholder: plot_distribuicao_classes not loaded.")
        return go.Figure().add_annotation(text="plot_distribuicao_classes not available", showarrow=False)
    def plot_distribuicao_metodologias(method_counts):
        st.warning("Placeholder: plot_distribuicao_metodologias not loaded.")
        return go.Figure().add_annotation(text="plot_distribuicao_metodologias not available", showarrow=False)
    def plot_acuracia_por_metodologia(filtered_df):
        st.warning("Placeholder: plot_acuracia_por_metodologia not loaded.")
        return go.Figure().add_annotation(text="plot_acuracia_por_metodologia not available", showarrow=False)

# --- End of plotting function import attempt ---


# Import table functions
try:
    from scripts.utilities.tables import gap_analysis
except ImportError:
    def gap_analysis(metadata, filtered_df):
        """Placeholder for gap_analysis"""
        return pd.DataFrame()

# Helper function to safely get min/max for sliders
def get_slider_range(series_min: pd.Series, series_max: pd.Series, 
                     default_min: Union[int, float], default_max: Union[int, float], 
                     data_type: Union[Type[int], Type[float]] = int):
    
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
    except Exception: # Broad exception for any calculation error
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    if pd.isna(overall_min_val) or pd.isna(overall_max_val):
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    overall_min = data_type(overall_min_val)
    overall_max = data_type(overall_max_val)
    
    if overall_min > overall_max: # Fallback if data is inconsistent
        overall_min, overall_max = data_type(default_min), data_type(default_max)

    return overall_min, overall_max, (overall_min, overall_max)


def run():
    st.header("📊 Comparative Analysis Dashboard")
    st.markdown("Use the filters below to select and compare LULC initiatives based on various criteria.")

    # Load data using the new JSON interpreter
    if 'df_interpreted' not in st.session_state:
        try:
            # Path to the metadata file
            metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
            df_interpreted = interpret_initiatives_metadata(metadata_file_path)
            if df_interpreted.empty:
                st.error("❌ Data interpretation resulted in an empty DataFrame. Please check the interpreter and data file.")
                return
            st.session_state.df_interpreted = df_interpreted
        except Exception as e:
            st.error(f"❌ Error loading or interpreting data: {e}")
            # Fallback to an empty DataFrame in session state to prevent further errors
            st.session_state.df_interpreted = pd.DataFrame()
            return

    df = st.session_state.get('df_interpreted', pd.DataFrame())

    if df.empty:
        st.error("❌ Interpreted data is not loaded or is empty. Cannot proceed.")
        # Optionally, display a message about how to fix or where to check logs
        st.info("Ensure `initiatives_metadata.jsonc` exists at the correct path and the `json_interpreter.py` is functioning correctly.")
        return

    # Ensure Display_Name exists, if not, it should have been created by the interpreter
    if 'Display_Name' not in df.columns:
        st.warning("⚠️ 'Display_Name' column is missing from the interpreted data. Charts might not display names correctly.")
        # As a fallback, create a simple display name if absolutely necessary, though interpreter should handle this
        if 'Name' in df.columns:
            df['Display_Name'] = df['Name'].apply(lambda x: str(x)[:20]) # Simple fallback
        else:
            df['Display_Name'] = "Unknown"


    st.markdown("### 🔎 Initiative Filters")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        tipos = sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else []
        selected_types = st.multiselect("Type", options=tipos, default=tipos, key="type_filter")
    
    with filter_col2:
        metodologias = sorted(df["Methodology"].dropna().unique().tolist()) if "Methodology" in df.columns else []
        selected_methods = st.multiselect("Methodology", options=metodologias, default=metodologias, key="methodology_filter")

    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        # Use the new min/max columns from the interpreter
        res_min_series = df.get('Resolution_min_val', pd.Series(dtype=float))
        res_max_series = df.get('Resolution_max_val', pd.Series(dtype=float))
        min_r, max_r, default_r_val = get_slider_range(res_min_series, res_max_series, 0, 1000, data_type=int)
        selected_res_range = st.slider("Resolution (m)", 
                                       min_value=min_r, 
                                       max_value=max_r, 
                                       value=default_r_val,
                                       help="Filters initiatives whose resolution range overlaps with the selected range.",
                                       key="resolution_filter")
    
    with filter_col4:
        # Use the new min/max columns from the interpreter
        acc_min_series = df.get('Accuracy_min_val', pd.Series(dtype=float))
        acc_max_series = df.get('Accuracy_max_val', pd.Series(dtype=float))
        min_a, max_a, default_a_val = get_slider_range(acc_min_series, acc_max_series, 0.0, 100.0, data_type=float)
        selected_acc_range = st.slider("Accuracy (%)", 
                                       min_value=min_a, 
                                       max_value=max_a, 
                                       value=default_a_val,
                                       format="%.1f",
                                       help="Filters initiatives whose accuracy range overlaps with the selected range.",
                                       key="accuracy_filter")

    # Row 3 for new filters - Reference System and Detailed Products
    filter_col5, filter_col6 = st.columns(2)
    with filter_col5:
        # Assuming Reference_System is a string or list of strings from the interpreter
        all_ref_systems = set()
        if 'Reference_System' in df.columns:
            for item in df['Reference_System'].dropna():
                if isinstance(item, list): # If interpreter returns a list
                    all_ref_systems.update(item)
                elif isinstance(item, str): # If interpreter returns a string
                    all_ref_systems.update(item.split(', ')) # Simple split if it's a comma-sep string
        selected_ref_systems = st.multiselect("Reference System", 
                                              options=sorted(list(all_ref_systems)), 
                                              default=sorted(list(all_ref_systems)), 
                                              key="ref_system_filter")

    # Filter data based on selections
    filtered_df = df.copy()
    if selected_types:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    if selected_methods:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]
    
    # Resolution filtering: an initiative is included if its range [res_min, res_max] overlaps with selected_res_range [sel_min, sel_max]
    # Overlap condition: sel_min <= res_max AND sel_max >= res_min
    if 'Resolution_min_val' in filtered_df.columns and 'Resolution_max_val' in filtered_df.columns:
        sel_res_min, sel_res_max = selected_res_range
        filtered_df = filtered_df[
            (filtered_df['Resolution_max_val'] >= sel_res_min) & 
            (filtered_df['Resolution_min_val'] <= sel_res_max)
        ]

    # Accuracy filtering (similar logic)
    if 'Accuracy_min_val' in filtered_df.columns and 'Accuracy_max_val' in filtered_df.columns:
        sel_acc_min, sel_acc_max = selected_acc_range
        filtered_df = filtered_df[
            (filtered_df['Accuracy_max_val'] >= sel_acc_min) & 
            (filtered_df['Accuracy_min_val'] <= sel_acc_max)
        ]
        
    if selected_ref_systems and 'Reference_System' in filtered_df.columns:
        # This filter needs to be robust if Reference_System can be a list or a string
        def check_ref_system(row_val):
            if isinstance(row_val, list):
                return any(rs in selected_ref_systems for rs in row_val)
            elif isinstance(row_val, str):
                return any(rs in selected_ref_systems for rs in row_val.split(', ')) # Simple split
            return False
        filtered_df = filtered_df[filtered_df['Reference_System'].apply(check_ref_system)]

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the current filter criteria.")
        # Display tabs even if filtered_df is empty, charts will show their own "no data" messages
    
    st.markdown("---")
    st.markdown("### 📊 Comparison Charts")

    tab_spatial, tab_accuracy, tab_temporal, tab_diversity, tab_methodology_dist, tab_resolution_analysis, tab_class_details, tab_methodology_details = st.tabs([
        "Spatial Resolution", 
        "Global Accuracy", 
        "Temporal Evolution", 
        "Class Diversity", 
        "Overall Methodology Dist.", # Renamed for clarity from just "Methodology Distribution"
        "Resolution Analysis",
        "Class Details",
        "Methodology Deep Dive"  # New Tab for Methodology charts
    ])

    # Renaming the original methodology tab variable for clarity
    # The original tab_methodology is now tab_methodology_dist
    with tab_methodology_dist:
        st.markdown("#### Overall Classification Methodology Distribution")
        st.write("This chart shows the distribution of different classification methodologies used across ALL selected initiatives.")
        
        methodology_chart_type = st.radio(
            "Select Methodology Chart Type:", 
            ('Pie Chart', 'Bar Chart'), 
            key='methodology_chart_type_comparison_tab' # Unique key for radio in tab
        )
        chart_type_param = 'pie' if methodology_chart_type == 'Pie Chart' else 'bar'
        
        if not filtered_df.empty:
            try:
                # This was plot_classification_methodology, which is a general distribution chart
                # For this tab, we use the specific plot_distribuicao_metodologias if it's meant for overall distribution
                # or ensure plot_classification_methodology is correctly handling the filtered_df for an overall view.
                # Assuming plot_classification_methodology is the correct one for this pre-existing tab.
                methodology_fig = plot_classification_methodology(filtered_df, chart_type=chart_type_param)
                st.plotly_chart(methodology_fig, use_container_width=True, key="overall_methodology_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating overall classification methodology chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Overall classification methodology chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display for overall methodology distribution based on current filters.")

    with tab_spatial:
        st.markdown("#### Spatial Resolution Overview")
        st.write("This chart compares the spatial resolution (in meters) of the selected LULC initiatives. Lower values indicate finer (better) resolution.")
        if not filtered_df.empty:
            try:
                spatial_res_fig = plot_spatial_resolution_comparison(filtered_df)
                st.plotly_chart(spatial_res_fig, use_container_width=True, key="spatial_res_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating spatial resolution chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Spatial resolution chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display based on current filters.")

    with tab_accuracy:
        st.markdown("#### Global Accuracy Overview")
        st.write("This chart compares the global accuracy (in %) of the selected LULC initiatives. Higher values indicate better accuracy.")
        if not filtered_df.empty:
            try:
                global_acc_fig = plot_global_accuracy_comparison(filtered_df)
                st.plotly_chart(global_acc_fig, use_container_width=True, key="global_acc_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating global accuracy chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Global accuracy chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display based on current filters.")

    with tab_temporal:
        st.markdown("#### Temporal Evolution & Update Frequency")
        st.write("This timeline chart shows the operational period (start to end year) of selected LULC initiatives, colored by their update frequency.")
        if not filtered_df.empty:
            try:
                temporal_evo_fig = plot_temporal_evolution_frequency(filtered_df)
                st.plotly_chart(temporal_evo_fig, use_container_width=True, key="temporal_evo_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating temporal evolution chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Temporal evolution chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display based on current filters.")

    with tab_diversity:
        st.markdown("#### Class Diversity and Agricultural Focus")
        st.write("This chart compares the total number of classes versus the number of agricultural-specific classes for each initiative.")
        if not filtered_df.empty:
            try:
                class_diversity_fig = plot_class_diversity_focus(filtered_df)
                st.plotly_chart(class_diversity_fig, use_container_width=True, key="class_div_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating class diversity chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Class diversity chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display based on current filters.")

    with tab_resolution_analysis: # Content for the new tab
        st.markdown("#### In-depth Resolution Analysis")
        st.write("This section provides a deeper dive into spatial resolution characteristics, including its evolution, distribution by sensor, and relationship with other factors.")

        if not plotting_functions_loaded:
            st.warning("Resolution analysis charts cannot be loaded because essential plotting functions failed to import.")
        elif filtered_df.empty:
            st.info("No data to display for resolution analysis based on current filters.")
        else:
            # Load sensor metadata (once per session or if not already loaded)
            sensors_data_path = current_dir / "data" / "sensors_metadata.jsonc"
            if 'sensors_meta' not in st.session_state:
                try:
                    with open(sensors_data_path, 'r', encoding='utf-8') as f:
                        # Attempt to parse JSONC by removing comments first
                        content = f.read()
                        # Basic comment removal: lines starting with // and block comments /* ... */
                        import re
                        content_no_comments = re.sub(r"//.*", "", content) # Remove single line comments
                        content_no_comments = re.sub(r"/\*.*?\*/", "", content_no_comments, flags=re.DOTALL) # Remove block comments
                        st.session_state.sensors_meta = json.loads(content_no_comments)
                    st.success("Sensor metadata loaded successfully.")
                except Exception as e_sensor_load:
                    st.error(f"❌ Error loading or parsing sensor metadata from {sensors_data_path}: {e_sensor_load}")
                    st.session_state.sensors_meta = {} # Fallback to empty dict
            
            sensors_meta_data = st.session_state.get('sensors_meta', {})

            # Chart 1: Resolution vs. Launch Year
            st.markdown("##### Resolution vs. Launch Year")
            st.write("Shows the relationship between spatial resolution and the year each initiative began. Lower resolution values (Y-axis) are generally better. Points are labeled by initiative.")
            try:
                fig_res_launch = plot_resolution_vs_launch_year(filtered_df)
                st.plotly_chart(fig_res_launch, use_container_width=True, key="res_vs_launch_comp")
            except Exception as e:
                st.error(f"❌ Error generating 'Resolution vs. Launch Year' chart: {e}")

            # Chart 2: Initiatives by Resolution Category
            st.markdown("##### Initiatives by Resolution Category")
            st.write("Summarizes how many initiatives fall into predefined spatial resolution categories, stacked by initiative type.")
            try:
                fig_res_cat = plot_initiatives_by_resolution_category(filtered_df)
                st.plotly_chart(fig_res_cat, use_container_width=True, key="res_by_cat_comp")
            except Exception as e:
                st.error(f"❌ Error generating 'Initiatives by Resolution Category' chart: {e}")

            # Chart 3: Resolution vs. Coverage Type Heatmap
            st.markdown("##### Resolution vs. Coverage Type Heatmap")
            st.write("Visualizes the number of initiatives at the intersection of spatial resolution categories and geographic coverage types.")
            try:
                fig_res_heatmap = plot_resolution_coverage_heatmap(filtered_df)
                st.plotly_chart(fig_res_heatmap, use_container_width=True, key="res_cov_heatmap_comp")
            except Exception as e:
                st.error(f"❌ Error generating 'Resolution vs.Coverage Heatmap' chart: {e}")

            # Charts requiring sensor metadata
            if not sensors_meta_data:
                st.warning("Sensor metadata (`sensors_metadata.jsonc`) could not be loaded or is empty. Skipping charts that depend on it (Resolution by Sensor Family, Resolution Slopegraph).")
            else:
                # Chart 4: Resolution by Sensor Family
                st.markdown("##### Resolution Distribution by Sensor Family")
                st.write("Compares the spread (median, quartiles, outliers) of spatial resolutions for initiatives, grouped by the primary sensor families they utilize.")
                try:
                    fig_res_sensor = plot_resolution_by_sensor_family(filtered_df, sensors_meta_data)
                    st.plotly_chart(fig_res_sensor, use_container_width=True, key="res_by_sensor_comp")
                except Exception as e:
                    st.error(f"❌ Error generating 'Resolution by Sensor Family' chart: {e}")

                # Chart 5: Resolution Improvement Slopegraph
                st.markdown("##### Resolution Improvement Over Time (Slopegraph)")
                st.write("Shows how individual initiatives have changed their spatial resolution over time, based on changes in their referenced sensors and associated operational years.")
                try:
                    fig_res_slope = plot_resolution_slopegraph(filtered_df, sensors_meta_data)
                    st.plotly_chart(fig_res_slope, use_container_width=True, key="res_slope_comp")
                except Exception as e:
                    st.error(f"❌ Error generating 'Resolution Slopegraph' chart: {e}")
    
    with tab_class_details: # Content for the new Class Details tab
        st.markdown("#### Distribution of Number of Classes")
        st.write("This chart shows the distribution of the total number of classes identified by the selected LULC initiatives, colored by initiative type.")
        if not plotting_functions_loaded:
            st.warning("Class details chart cannot be loaded because essential plotting functions failed to import.")
        elif filtered_df.empty:
            st.info("No data to display for class details based on current filters.")
        else:
            if 'Classes' in filtered_df.columns and 'Type' in filtered_df.columns:
                try:
                    # Ensure the 'Classes' column is numeric for the histogram
                    df_for_chart = filtered_df.copy()
                    df_for_chart['Classes'] = pd.to_numeric(df_for_chart['Classes'], errors='coerce')
                    df_for_chart.dropna(subset=['Classes'], inplace=True) # Remove rows where 'Classes' could not be converted
                    
                    if not df_for_chart.empty:
                        fig_dist_classes = plot_distribuicao_classes(df_for_chart)
                        st.plotly_chart(fig_dist_classes, use_container_width=True, key="dist_classes_comp")
                    else:
                        st.info("No valid data for 'Classes' to display the chart after attempting conversion.")
                except Exception as e:
                    st.error(f"❌ Error generating 'Distribution of Classes' chart: {e}")
            else:
                missing_cols = []
                if 'Classes' not in filtered_df.columns: missing_cols.append('Classes')
                if 'Type' not in filtered_df.columns: missing_cols.append('Type') # plot_distribuicao_classes uses 'Type' for color
                st.warning(f"The column(s) {', '.join(missing_cols)} are not available in the filtered data, so the 'Distribution of Classes' chart cannot be generated.")

    with tab_methodology_details: # Content for the new Methodology Details tab
        st.markdown("#### Methodology Deep Dive")
        st.write("Explore the distribution of methodologies and their associated accuracies.")

        if not plotting_functions_loaded:
            st.warning("Methodology details charts cannot be loaded because essential plotting functions failed to import.")
        elif filtered_df.empty:
            st.info("No data to display for methodology details based on current filters.")
        else:
            # Chart 1: Distribution of Methodologies (Pie Chart)
            st.markdown("##### Distribution of Methodologies Used")
            if 'Methodology' in filtered_df.columns:
                try:
                    method_counts = filtered_df['Methodology'].value_counts()
                    if not method_counts.empty:
                        fig_dist_meth = plot_distribuicao_metodologias(method_counts)
                        st.plotly_chart(fig_dist_meth, use_container_width=True, key="dist_meth_comp")
                    else:
                        st.info("No methodology data to display the distribution chart.")
                except Exception as e:
                    st.error(f"❌ Error generating 'Distribution of Methodologies' chart: {e}")
            else:
                st.warning("The 'Methodology' column is not available, so 'Distribution of Methodologies' chart cannot be generated.")

            st.markdown("---") # Separator

            # Chart 2: Accuracy by Methodology (Box Plot)
            st.markdown("##### Accuracy by Methodology")
            if 'Methodology' in filtered_df.columns and 'Accuracy (%)' in filtered_df.columns and 'Type' in filtered_df.columns:
                try:
                    # Ensure 'Accuracy (%)' is numeric
                    df_for_acc_chart = filtered_df.copy()
                    df_for_acc_chart['Accuracy (%)'] = pd.to_numeric(df_for_acc_chart['Accuracy (%)'], errors='coerce')
                    df_for_acc_chart.dropna(subset=['Accuracy (%)', 'Methodology', 'Type'], inplace=True)

                    if not df_for_acc_chart.empty:
                        fig_acc_meth = plot_acuracia_por_metodologia(df_for_acc_chart)
                        st.plotly_chart(fig_acc_meth, use_container_width=True, key="acc_meth_comp")
                    else:
                        st.info("No valid data for 'Accuracy (%)' or 'Methodology' to display the accuracy chart after attempting conversion.")
                except Exception as e:
                    st.error(f"❌ Error generating 'Accuracy by Methodology' chart: {e}")
            else:
                missing_cols_acc = []
                if 'Methodology' not in filtered_df.columns: missing_cols_acc.append('Methodology')
                if 'Accuracy (%)' not in filtered_df.columns: missing_cols_acc.append('Accuracy (%)')
                if 'Type' not in filtered_df.columns: missing_cols_acc.append('Type') # plot_acuracia_por_metodologia uses 'Type' for color
                st.warning(f"The column(s) {', '.join(missing_cols_acc)} are not available, so 'Accuracy by Methodology' chart cannot be generated.")

    st.markdown("---")
    st.markdown("### 📋 Detailed Data Table")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Correct way to download DataFrame as CSV
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_initiatives_comparison.csv",
            mime="text/csv",
            key="download-comparison-csv"
        )
    else:
        st.info("No data to download based on current filters.")

if __name__ == '__main__':
    run()


