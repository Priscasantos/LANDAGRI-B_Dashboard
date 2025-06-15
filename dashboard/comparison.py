import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# import plotly.express as px # This line can be removed if px is not directly used in this file
import sys
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
        plot_classification_methodology
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
    def plot_classification_methodology(_filtered_df, chart_type='pie'): # Added placeholder
        st.warning("Placeholder: plot_classification_methodology not loaded due to import error.")
        return go.Figure().add_annotation(text="plot_classification_methodology not available", showarrow=False)

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

    tab_spatial, tab_accuracy, tab_temporal, tab_diversity, tab_methodology = st.tabs([
        "Spatial Resolution", 
        "Global Accuracy", 
        "Temporal Evolution", 
        "Class Diversity", 
        "Methodology Distribution"
    ])

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

    with tab_methodology:
        st.markdown("#### Classification Methodology Distribution")
        st.write("This chart shows the distribution of different classification methodologies used across the selected initiatives.")
        
        methodology_chart_type = st.radio(
            "Select Methodology Chart Type:", 
            ('Pie Chart', 'Bar Chart'), 
            key='methodology_chart_type_comparison_tab' # Unique key for radio in tab
        )
        chart_type_param = 'pie' if methodology_chart_type == 'Pie Chart' else 'bar'
        
        if not filtered_df.empty:
            try:
                methodology_fig = plot_classification_methodology(filtered_df, chart_type=chart_type_param)
                st.plotly_chart(methodology_fig, use_container_width=True, key="methodology_chart_comp")
            except Exception as e:
                st.error(f"❌ Error generating classification methodology chart: {e}")
        elif not plotting_functions_loaded:
            st.warning("Classification methodology chart cannot be loaded because plotting functions failed to import.")
        else:
            st.info("No data to display based on current filters.")

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


