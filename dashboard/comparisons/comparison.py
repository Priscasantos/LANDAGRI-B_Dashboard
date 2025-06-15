import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
from typing import Type, Union
from scripts.utilities.ui_elements import setup_download_form # Import the new function

# Add scripts to path
current_dir = Path(__file__).parent.parent.parent
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

# Import graphics functions
try:
    from scripts.plotting.generate_graphics import plot_resolution_accuracy
except ImportError:
    def plot_resolution_accuracy(_filtered_df, _x_col='Resolution', _y_col='Accuracy', _text_col='Display_Name'):
        st.warning("Debug: plot_resolution_accuracy (placeholder from generate_graphics import error) called.")
        return go.Figure().add_annotation(text="Function plot_resolution_accuracy not available", xref="paper", yref="paper", x=0.5, y=0.5)

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
            # Path to the metadata file - adjust if necessary
            metadata_file_path = current_dir / "data" / "raw" / "initiatives_metadata.jsonc"
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
                # Check if any of the selected systems are in the (potentially comma-separated) string
                return any(sel_rs in row_val for sel_rs in selected_ref_systems)
            return False
        filtered_df = filtered_df[filtered_df['Reference_System'].apply(check_ref_system)]


    st.markdown("---")
    st.markdown("### 📊 Comparative Visualizations")

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the current filter criteria.")
    else:
        st.markdown(f"**Displaying {len(filtered_df)} of {len(df)} initiatives.**")

        tab1, tab2, tab3 = st.tabs([
            "Resolution vs. Accuracy", 
            "Classes vs. Frequency", 
            "Methodology by Type"
        ])

        with tab1:
            st.markdown("#### Resolution vs. Accuracy")
            plot_df_res_acc = filtered_df.copy()
            rename_map = {}
            if 'Resolution' in plot_df_res_acc.columns and 'Resolution (m)' not in plot_df_res_acc.columns:
                rename_map['Resolution'] = 'Resolution (m)'
            if 'Accuracy' in plot_df_res_acc.columns and 'Accuracy (%)' not in plot_df_res_acc.columns:
                rename_map['Accuracy'] = 'Accuracy (%)'
            if 'Number_of_Classes' in plot_df_res_acc.columns and 'Classes' not in plot_df_res_acc.columns:
                rename_map['Number_of_Classes'] = 'Classes'
            
            if rename_map:
                plot_df_res_acc.rename(columns=rename_map, inplace=True)

            if all(col in plot_df_res_acc.columns for col in ['Resolution (m)', 'Accuracy (%)', 'Display_Name', 'Classes']):
                fig_res_acc = plot_resolution_accuracy(plot_df_res_acc)
                st.plotly_chart(fig_res_acc, use_container_width=True)
                # Use the new download form setup
                setup_download_form(fig_res_acc, default_filename="resolution_accuracy_comparison", key_prefix="res_acc")
            else:
                st.warning("Required columns (Display_Name, Resolution, Accuracy, Classes) not available for Resolution vs. Accuracy chart.")

        with tab2:
            st.markdown("#### Number of Classes by Temporal Frequency")
            if 'Number_of_Classes' in filtered_df.columns and 'Temporal_Frequency' in filtered_df.columns:
                plot_df_classes_freq = filtered_df.dropna(subset=['Number_of_Classes', 'Temporal_Frequency']).copy()
                plot_df_classes_freq['Temporal_Frequency'] = plot_df_classes_freq['Temporal_Frequency'].astype(str)
                
                if not plot_df_classes_freq.empty:
                    fig_classes_freq = px.box(
                        plot_df_classes_freq,
                        x='Temporal_Frequency',
                        y='Number_of_Classes',
                        color='Type' if 'Type' in plot_df_classes_freq.columns else None,
                        labels={'Number_of_Classes': 'Number of Classes', 'Temporal_Frequency': 'Temporal Frequency'},
                        title='Distribution of Number of Classes by Temporal Frequency',
                        points="all"
                    )
                    fig_classes_freq.update_layout(xaxis={'categoryorder':'total descending'})
                    st.plotly_chart(fig_classes_freq, use_container_width=True)
                    
                    # Use the new download form setup
                    setup_download_form(fig_classes_freq, default_filename="classes_vs_frequency", key_prefix="classes_freq")
                else:
                    st.info("Not enough data to display Number of Classes vs. Temporal Frequency chart after filtering.")
            else:
                st.warning("Required columns ('Number_of_Classes', 'Temporal_Frequency') not available for this chart.")

        with tab3:
            st.markdown("#### Methodology Breakdown by Type")
            if 'Methodology' in filtered_df.columns and 'Type' in filtered_df.columns:
                plot_df_method_type = filtered_df.groupby(['Type', 'Methodology']).size().reset_index(name='Count')
                if not plot_df_method_type.empty:
                    fig_method_type = px.bar(
                        plot_df_method_type,
                        x='Type',
                        y='Count',
                        color='Methodology',
                        barmode='group',
                        labels={'Count': 'Number of Initiatives', 'Type': 'Initiative Type', 'Methodology': 'Methodology'},
                        title='Methodology Breakdown by Initiative Type'
                    )
                    st.plotly_chart(fig_method_type, use_container_width=True)

                    # Use the new download form setup
                    setup_download_form(fig_method_type, default_filename="methodology_by_type", key_prefix="method_type")
                else:
                    st.info("Not enough data to display Methodology Breakdown by Type chart after filtering.")
            else:
                st.warning("Required columns ('Methodology', 'Type') not available for this chart.")

        st.markdown("---") # Separator after tabs
        st.markdown("#### Selected Initiatives Data")
        display_cols = ['Display_Name', 'Type', 'Methodology', 'Resolution', 'Accuracy', 'Number_of_Classes', 'Temporal_Frequency']
        # Filter display_cols to only those present in filtered_df
        existing_display_cols = [col for col in display_cols if col in filtered_df.columns]
        if existing_display_cols:
            st.dataframe(filtered_df[existing_display_cols])
        else:
            st.warning("No data to display in table based on available columns.")

if __name__ == "__main__":
    run()


