import json  # Ensure json is imported
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.overview import filters, lulc_classes
# Download form import removed

# Add scripts to path if necessary
# Correct current_dir to point to the project root (dashboard-iniciativas)
current_dir = Path(__file__).parent.parent  # This should be dashboard-iniciativas/
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


def _format_year_ranges(years_list: list) -> str:
    """Formats a list of years into a string with consecutive years as ranges."""
    if not years_list:
        return ""

    # Ensure years are integers and sorted uniquely
    try:
        years = sorted(list(set(int(y) for y in years_list if str(y).isdigit())))
    except ValueError:  # Handle cases where conversion might fail for unexpected data
        # Fallback to simple comma-separated list if conversion to int fails for any element
        return ", ".join(sorted(list(set(str(y) for y in years_list))))

    if not years:
        return ""

    ranges = []
    start_range = years[0]

    for i in range(1, len(years)):
        if years[i] != years[i - 1] + 1:
            # End of a range
            if start_range == years[i - 1]:
                ranges.append(str(start_range))
            else:
                ranges.append(f"{start_range}-{years[i - 1]}")
            start_range = years[i]

    # Add the last range
    if start_range == years[-1]:
        ranges.append(str(start_range))
    else:
        ranges.append(f"{start_range}-{years[-1]}")

    return ", ".join(ranges)


def _render_key_metrics(filtered_df: pd.DataFrame):
    """
    Render key aggregated metrics cards.

    Args:
        filtered_df: Filtered dataframe to calculate metrics from
    """
    st.subheader("📈 Key Aggregated Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_accuracy_series = pd.to_numeric(
            filtered_df["Accuracy (%)"], errors="coerce"
        ).dropna()
        if not avg_accuracy_series.empty:
            avg_accuracy = avg_accuracy_series.mean()
            st.markdown(
                f"""
            <div class="metric-card accuracy">
                <span class="metric-icon">🎯</span>
                <div class="metric-value">{avg_accuracy:.1f}%</div>
                <div class="metric-label">Average Accuracy</div>
                <div class="metric-sublabel">Across filtered initiatives</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        avg_resolution_series = pd.to_numeric(
            filtered_df["Resolution"], errors="coerce"
        ).dropna()
        if not avg_resolution_series.empty:
            avg_resolution = avg_resolution_series.mean()
            st.markdown(
                f"""
            <div class="metric-card resolution">
                <span class="metric-icon">🔬</span>
                <div class="metric-value">{avg_resolution:.0f}m</div>
                <div class="metric-label">Average Resolution</div>
                <div class="metric-sublabel">Spatial precision</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col3:
        total_classes = 0
        if "Classes" in filtered_df.columns:
            classes_series = pd.to_numeric(
                filtered_df["Classes"], errors="coerce"
            ).dropna()
            if not classes_series.empty:
                total_classes = classes_series.sum()
        elif "Number_of_Classes" in filtered_df.columns:
            num_classes_series = pd.to_numeric(
                filtered_df["Number_of_Classes"], errors="coerce"
            ).dropna()
            if not num_classes_series.empty:
                total_classes = num_classes_series.sum()

        if total_classes > 0:
            st.markdown(
                f"""
            <div class="metric-card classes">
                <span class="metric-icon">🏷️</span>
                <div class="metric-value">{total_classes}</div>
                <div class="metric-label">Total Classes</div>
                <div class="metric-sublabel">Classification categories</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col4:
        if "Type" in filtered_df.columns:
            global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"])
            if global_initiatives > 0:
                st.markdown(
                    f"""
                <div class="metric-card global">
                    <span class="metric-icon">🌍</span>
                    <div class="metric-value">{global_initiatives}</div>
                    <div class="metric-label">Global Initiatives</div>
                    <div class="metric-sublabel">Worldwide coverage</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def _render_detailed_exploration(
    filtered_df: pd.DataFrame, meta: dict, sensors_meta: dict, nome_to_sigla: dict
):
    """
    Render the detailed exploration section for individual initiatives.

    Args:
        filtered_df: Filtered dataframe with initiatives
        meta: Metadata dictionary
        sensors_meta: Sensor metadata dictionary
        nome_to_sigla: Name to acronym mapping
    """
    st.subheader("🔍 Detailed Exploration by Initiative")

    # Create formatted options for the selectbox
    formatted_options = []
    formatted_to_original_name = {}

    if not filtered_df.empty and "Name" in filtered_df.columns:
        for name in filtered_df["Name"].tolist():
            acronym = nome_to_sigla.get(name, "N/A")
            formatted_display = f"{name} ({acronym})"
            formatted_options.append(formatted_display)
            formatted_to_original_name[formatted_display] = name

    selected_initiative_formatted = st.selectbox(
        "Select an initiative to see details:",
        options=formatted_options,
        help="Choose an initiative for detailed information",
        key="overview_detailed_select",
    )

    # Get the original initiative name from the formatted selection
    selected_initiative_detailed = formatted_to_original_name.get(
        selected_initiative_formatted
    )

    if selected_initiative_detailed:
        init_data = filtered_df[
            filtered_df["Name"] == selected_initiative_detailed
        ].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {})
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(
            selected_initiative_detailed, selected_initiative_detailed[:10]
        )

        # Modern initiative header
        st.markdown(
            f"""
        <div class="initiative-header">
            <h2 class="initiative-title">🛰️ {initiative_acronym}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{selected_initiative_detailed}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("""<div class="detail-card">""", unsafe_allow_html=True)

        col1_detail, col2_detail = st.columns([2, 3])

        with col1_detail:
            _render_initiative_metrics(init_data)
            _render_initiative_tech_info(init_data, sensors_meta)

        with col2_detail:
            _render_initiative_methodology(init_data, init_metadata, sensors_meta)

        _render_initiative_classification_details(init_data)

        st.markdown("</div>", unsafe_allow_html=True)


def _render_initiative_metrics(init_data: pd.Series):
    """Render key metrics for a specific initiative."""
    st.markdown("#### 📊 Key Metrics")

    metrics_html_parts = []
    accuracy_val = pd.to_numeric(init_data.get("Accuracy (%)"), errors="coerce")
    if pd.notna(accuracy_val):
        metrics_html_parts.append(
            f"""<div class="mini-metric">
            <div class="mini-metric-value">🎯 {accuracy_val:.1f}%</div>
            <div class="mini-metric-label">Accuracy</div></div>"""
        )

    resolution_val = pd.to_numeric(init_data.get("Resolution"), errors="coerce")
    if pd.notna(resolution_val):
        metrics_html_parts.append(
            f"""<div class="mini-metric">
            <div class="mini-metric-value">🔬 {resolution_val:.0f}m</div>
            <div class="mini-metric-label">Resolution</div></div>"""
        )

    classes_val_str = str(
        init_data.get("Classes", init_data.get("Number_of_Classes", ""))
    ).strip()
    classes_val = pd.to_numeric(classes_val_str, errors="coerce")
    if pd.notna(classes_val) and classes_val_str:
        metrics_html_parts.append(
            f"""<div class="mini-metric">
            <div class="mini-metric-value">🏷️ {classes_val:.0f}</div>
            <div class="mini-metric-label">Classes</div></div>"""
        )

    frequency_val = str(init_data.get("Temporal_Frequency", "")).strip()
    if frequency_val and frequency_val.lower() not in ["n/a", "none"]:
        metrics_html_parts.append(
            f"""<div class="mini-metric">
            <div class="mini-metric-value">📅 {frequency_val}</div>
            <div class="mini-metric-label">Frequency</div></div>"""
        )

    if metrics_html_parts:
        st.markdown(
            f"""<div class="metric-grid">{"".join(metrics_html_parts)}</div>""",
            unsafe_allow_html=True,
        )


def _render_initiative_tech_info(init_data: pd.Series, sensors_meta: dict):
    """Render technical information for a specific initiative."""
    st.markdown("#### ⚙️ Technical Information")
    tech_info_html_parts = []

    type_val = str(init_data.get("Type", "")).strip()
    if type_val and type_val.lower() not in ["n/a", "none"]:
        tech_info_html_parts.append(
            f"""<div class="info-section" style="border-left-color: #17a2b8;">
                                            <div class="info-title">🏷️ Type</div>
                                            <p>{type_val}</p></div>"""
        )

    methodology_val = str(init_data.get("Methodology", "")).strip()
    if methodology_val and methodology_val.lower() not in ["n/a", "none"]:
        tech_info_html_parts.append(
            f"""<div class="info-section" style="border-left-color: #6f42c1;">
                                            <div class="info-title">🔬 Methodology</div>
                                            <p>{methodology_val}</p></div>"""
        )

    scope_val = str(init_data.get("Coverage", "")).strip()
    if scope_val and scope_val.lower() not in ["n/a", "none"]:
        tech_info_html_parts.append(
            f"""<div class="info-section" style="border-left-color: #28a745;">
                                            <div class="info-title">🌍 Scope</div>
                                            <p>{scope_val}</p></div>"""
        )

    # Get available_years from DataFrame
    available_years_str_from_df = init_data.get("Available_Years_List", "[]")
    try:
        available_years_list = (
            json.loads(available_years_str_from_df)
            if available_years_str_from_df
            else []
        )
    except json.JSONDecodeError:
        available_years_list = []

    if isinstance(available_years_list, list) and available_years_list:
        formatted_years_str = _format_year_ranges(available_years_list)
        if formatted_years_str:
            tech_info_html_parts.append(
                f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                <div class="info-title">📅 Available Years</div>
                                                <p>{formatted_years_str}</p></div>"""
            )

    # Display Sensors Referenced
    _render_sensors_referenced(init_data, sensors_meta, tech_info_html_parts)

    if tech_info_html_parts:
        st.markdown(
            f"""<div style="margin: 1rem 0;">{"".join(tech_info_html_parts)}</div>""",
            unsafe_allow_html=True,
        )


def _render_sensors_referenced(
    init_data: pd.Series, sensors_meta: dict, tech_info_html_parts: list
):
    """Render sensors referenced information."""
    sensors_referenced_str_from_df = init_data.get("Sensors_Referenced", "[]")
    try:
        sensors_referenced_list_for_display = (
            json.loads(sensors_referenced_str_from_df)
            if sensors_referenced_str_from_df
            else []
        )
    except json.JSONDecodeError:
        sensors_referenced_list_for_display = []

    if (
        isinstance(sensors_referenced_list_for_display, list)
        and sensors_referenced_list_for_display
    ):
        sensor_badges_html_parts = []
        sensor_details_expanders = []

        for sensor_ref_obj in sensors_referenced_list_for_display:
            current_sensor_key_str = None
            years_used_list = []

            if isinstance(sensor_ref_obj, dict):
                _key_from_dict = sensor_ref_obj.get("sensor_key")
                if _key_from_dict is not None:
                    current_sensor_key_str = str(_key_from_dict)
                years_used_list = sensor_ref_obj.get("years_used", [])
            elif isinstance(sensor_ref_obj, str):
                current_sensor_key_str = sensor_ref_obj

            if current_sensor_key_str:
                sensor_info_from_meta = sensors_meta.get(
                    str(current_sensor_key_str), {}
                )
                display_name = sensor_info_from_meta.get(
                    "display_name",
                    str(current_sensor_key_str).replace("_", " ").title(),
                )

                sensor_display_text_for_badge = display_name
                if years_used_list and isinstance(years_used_list, list):
                    years_used_str = _format_year_ranges(years_used_list)
                    sensor_display_text_for_badge += f" (Years: {years_used_str})"
                sensor_badges_html_parts.append(
                    f'<span class="badge badge-sensor">{sensor_display_text_for_badge}</span>'
                )

                # Prepare content for expander
                expander_title = f"🛰️ {display_name} Details"
                expander_content = _build_sensor_expander_content(sensor_info_from_meta)
                sensor_details_expanders.append((expander_title, expander_content))

        if sensor_badges_html_parts:
            tech_info_html_parts.append(
                f"""<div class="info-section" style="border-left-color: #00bcd4;">
                                                <div class="info-title">🛰️ Sensors Referenced</div>
                                                <p>{" ".join(sensor_badges_html_parts)}</p></div>"""
            )

        # Display expanders for sensor details
        if sensor_details_expanders:
            st.markdown("#### 🛰️ Detailed Sensor Specifications")
            for title, content in sensor_details_expanders:
                with st.expander(title):
                    st.markdown(content, unsafe_allow_html=True)


def _build_sensor_expander_content(sensor_info_from_meta: dict) -> str:
    """Build content for sensor details expander."""
    expander_content = ""

    if sensor_info_from_meta:
        expander_content += "**General Specifications:**\n"
        for spec_key, spec_value in sensor_info_from_meta.items():
            if spec_key not in ["display_name", "notes"]:
                formatted_spec_key = spec_key.replace("_", " ").title()
                if isinstance(spec_value, list):
                    # If list of dicts (like spectral_bands)
                    if all(isinstance(item, dict) for item in spec_value):
                        expander_content += f"  - **{formatted_spec_key}:**\n"
                        for item_dict in spec_value:
                            band_details = []
                            for k, v in item_dict.items():
                                band_details.append(
                                    f"{k.replace('_', ' ').title()}: {v}"
                                )
                            expander_content += f"    - {', '.join(band_details)}\n"
                    else:  # Simple list
                        expander_content += f"  - **{formatted_spec_key}:** {', '.join(map(str, spec_value))}\n"
                elif isinstance(spec_value, dict):
                    expander_content += f"  - **{formatted_spec_key}:**\n"
                    for sub_k, sub_v in spec_value.items():
                        expander_content += (
                            f"    - {sub_k.replace('_', ' ').title()}: {sub_v}\n"
                        )
                else:
                    expander_content += f"  - **{formatted_spec_key}:** {spec_value}\n"
        if "notes" in sensor_info_from_meta:
            expander_content += f"\n**Notes:** {sensor_info_from_meta['notes']}\n"
    else:
        expander_content += "_No detailed specifications found in sensor metadata._\n"

    return expander_content


def _render_initiative_methodology(
    init_data: pd.Series, init_metadata: dict, sensors_meta: dict
):
    """Render methodological details for a specific initiative."""
    st.markdown("#### 📋 Methodological Details")

    methodology_section_html = []

    # Approach and Algorithm
    methodology_approach = str(init_metadata.get("methodology", "")).strip()
    algorithm_info = str(
        init_metadata.get("algorithm", init_metadata.get("classification_method", ""))
    ).strip()
    approach_algo_html = []
    if methodology_approach and methodology_approach.lower() not in [
        "not available",
        "none",
        "n/a",
    ]:
        approach_algo_html.append(
            f"<p><strong>Approach:</strong> {methodology_approach}</p>"
        )
    if algorithm_info and algorithm_info.lower() not in [
        "not available",
        "none",
        "n/a",
    ]:
        approach_algo_html.append(
            f"<p><strong>Algorithm:</strong> {algorithm_info}</p>"
        )
    if approach_algo_html:
        methodology_section_html.append(
            f"""<div class="info-section">
                                            <div class="info-title">🔬 Methodology</div>
                                            {"".join(approach_algo_html)}</div>"""
        )

    # Provider & Sources
    provider_info = str(init_metadata.get("provider", "")).strip()
    source_info = str(init_metadata.get("source", "")).strip()
    provider_source_html = []
    if provider_info and provider_info.lower() not in ["not available", "none", "n/a"]:
        provider_source_html.append(
            f"<p><strong>Provider:</strong> {provider_info}</p>"
        )
    if source_info and source_info.lower() not in ["not available", "none", "n/a"]:
        provider_source_html.append(
            f"<p><strong>Data Source:</strong> {source_info}</p>"
        )
    if provider_source_html:
        methodology_section_html.append(
            f"""<div class="info-section" style="border-left-color: #28a745;">
                                            <div class="info-title">🏢 Provider & Sources</div>
                                            {"".join(provider_source_html)}</div>"""
        )

    # Update Information & Temporal Info
    update_freq_info = str(init_metadata.get("update_frequency", "")).strip()
    temporal_freq_init_data = str(init_data.get("Temporal_Frequency", "")).strip()
    update_info_html_parts = []

    if update_freq_info and update_freq_info.lower() not in [
        "not available",
        "none",
        "n/a",
    ]:
        update_info_html_parts.append(
            f"<p><strong>Update Frequency (Metadata):</strong> {update_freq_info}</p>"
        )
    if temporal_freq_init_data and temporal_freq_init_data.lower() not in [
        "not available",
        "none",
        "n/a",
    ]:
        update_info_html_parts.append(
            f"<p><strong>Temporal Frequency (Data):</strong> {temporal_freq_init_data}</p>"
        )

    if update_info_html_parts:
        methodology_section_html.append(
            f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                            <div class="info-title">🔄 Update & Temporal Info</div>
                                            {"".join(update_info_html_parts)}</div>"""
        )

    # Detailed Sensor Information in methodology section
    _render_detailed_sensor_info(init_data, sensors_meta, methodology_section_html)

    # Temporal Coverage Analysis
    _render_temporal_coverage(init_data, methodology_section_html)

    if methodology_section_html:
        st.markdown("".join(methodology_section_html), unsafe_allow_html=True)


def _render_detailed_sensor_info(
    init_data: pd.Series, sensors_meta: dict, methodology_section_html: list
):
    """Render detailed sensor information in methodology section."""
    sensors_referenced_str = init_data.get("Sensors_Referenced", "[]")
    try:
        sensors_referenced_metadata = (
            json.loads(sensors_referenced_str) if sensors_referenced_str else []
        )
    except json.JSONDecodeError:
        sensors_referenced_metadata = []

    if isinstance(sensors_referenced_metadata, list) and sensors_referenced_metadata:
        detailed_sensor_info_html = [
            '<div class="info-section" style="border-left-color: #6f42c1;"><div class="info-title">🛰️ Detailed Sensor Specifications</div>'
        ]
        for sensor_ref in sensors_referenced_metadata:
            if isinstance(sensor_ref, dict):
                sensor_key_from_ref = sensor_ref.get("sensor_key")

                key_to_use_for_get = None
                if isinstance(sensor_key_from_ref, str) and sensor_key_from_ref.strip():
                    key_to_use_for_get = sensor_key_from_ref.strip()

                sensor_details_from_meta = {}
                display_name_for_sensor_heading = "Unknown Sensor"

                if key_to_use_for_get:
                    sensor_details_from_meta = sensors_meta.get(key_to_use_for_get, {})
                    display_name_for_sensor_heading = sensor_details_from_meta.get(
                        "display_name", key_to_use_for_get
                    )
                elif sensor_key_from_ref is not None:
                    display_name_for_sensor_heading = (
                        f"Invalid Sensor Key ({str(sensor_key_from_ref)})"
                    )

                detailed_sensor_info_html.append(
                    f"<h5 style='margin-top: 1rem; color: #6f42c1;'>{display_name_for_sensor_heading}</h5><ul style='list-style-type: disc; margin-left: 20px;'>"
                )

                # Add sensor details
                sensor_specs = [
                    "sensor_family",
                    "platform_name",
                    "sensor_type_description",
                    "agency",
                    "status",
                    "revisit_time_days",
                ]
                for spec in sensor_specs:
                    spec_value = sensor_details_from_meta.get(spec)
                    if spec_value:
                        spec_label = spec.replace("_", " ").title()
                        if spec == "revisit_time_days":
                            detailed_sensor_info_html.append(
                                f"<li><strong>Revisit Time:</strong> {spec_value} days</li>"
                            )
                        else:
                            detailed_sensor_info_html.append(
                                f"<li><strong>{spec_label}:</strong> {spec_value}</li>"
                            )

                detailed_sensor_info_html.append("</ul>")
        detailed_sensor_info_html.append("</div>")
        methodology_section_html.append("".join(detailed_sensor_info_html))


def _render_temporal_coverage(init_data: pd.Series, methodology_section_html: list):
    """Render temporal coverage analysis."""
    available_years_str = init_data.get("Available_Years_List", "[]")
    try:
        available_years_metadata = (
            json.loads(available_years_str) if available_years_str else []
        )
    except json.JSONDecodeError:
        available_years_metadata = []

    processed_years_as_int = []
    if isinstance(available_years_metadata, list):
        for year in available_years_metadata:
            try:
                processed_years_as_int.append(int(year))
            except (ValueError, TypeError):
                continue

    if processed_years_as_int:
        min_year = min(processed_years_as_int)
        max_year = max(processed_years_as_int)
        year_range = f"{min_year} - {max_year}"
        temporal_coverage_html = f"<p><strong>🕒 Temporal Coverage:</strong> {year_range} (from metadata)</p>"
    else:
        temporal_coverage_html = (
            "<p><strong>🕒 Temporal Coverage:</strong> Not available</p>"
        )

    methodology_section_html.append(
        f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                        <div class="info-title">📅 Temporal Coverage</div>
                                        {temporal_coverage_html}
                                      </div>"""
    )


def _render_initiative_classification_details(init_data: pd.Series):
    """Render classification details for a specific initiative."""
    st.markdown("#### 🏷️ Classification Details")

    # Get class legend data
    class_legend_json_str = init_data.get("Class_Legend", "[]")

    # Use new modular component for LULC classes
    lulc_classes.render_lulc_classes_section(class_legend_json_str)


def run():
    """
    Main orchestrator function for the overview dashboard.

    This function coordinates all components of the overview page:
    1. Data loading and validation
    2. UI styling
    3. Filters rendering
    4. Key metrics display
    5. Detailed exploration interface
    """
    # Load data from session state
    if "metadata" not in st.session_state or "df_interpreted" not in st.session_state:
        st.error(
            "❌ Interpreted data not found in session state. Ensure app.py loads data correctly."
        )
        return  # Stop if data isn't loaded

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    meta = st.session_state.get("metadata", {})

    # --- Load Sensor Metadata ---
    sensors_meta = {}
    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file

        # Correct path to sensors_metadata.jsonc relative to app.py or a known base directory
        # Assuming current_dir is dashboard-iniciativas/
        current_dir = Path.cwd()
        sensors_metadata_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
        if sensors_metadata_path.exists():
            sensors_meta_loaded = _load_jsonc_file(sensors_metadata_path)
            if isinstance(
                sensors_meta_loaded, dict
            ):  # Ensure it loaded as a dictionary
                sensors_meta = sensors_meta_loaded
                st.session_state.sensors_meta = (
                    sensors_meta  # Store in session state if needed by other parts
                )
            else:
                sensors_meta = {}
        else:
            st.warning(f"⚠️ Sensors metadata file not found at {sensors_metadata_path}")
    except Exception as e:
        st.warning(f"⚠️ Error loading sensors metadata: {e}")
        sensors_meta = {}

    # Load name to acronym mapping
    nome_to_sigla = meta.get("Nome_to_Sigla", {})

    # Title and introduction
    st.title("🌍 Visão Geral das Iniciativas LULC")
    st.markdown(
        "Explore and analyze land use and land cover (LULC) classification initiatives with rich interactive features."
    )
    st.markdown("---")

    # Render initiative filters and apply them
    filter_values = filters.render_initiative_filters(df)
    filtered_df = filters.apply_filters(df, *filter_values)

    # Display filter results
    filters.display_filter_results(len(df), len(filtered_df))

    # Store filtered data in session state
    st.session_state.filtered_df = filtered_df

    # Check if no data after filtering
    if filtered_df.empty:
        st.warning(
            "⚠️ No initiatives match the selected filters. Adjust the filters to view data."
        )
        st.stop()
    st.subheader("📈 Key Aggregated Metrics")

    # Custom CSS for modern metric cards
    st.markdown(
        """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin: 0.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    .metric-card.accuracy { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .metric-card.resolution { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .metric-card.classes { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .metric-card.global { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .metric-card.agri-classes { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); } /* New style for agri classes */

    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-sublabel {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
    }
    .badge-type { background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
    .badge-methodology { background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8; }
    .badge-scope { background: #e8f5e8; color: #388e3c; border: 1px solid #a5d6a7; }
    .badge-years { background: #fff3e0; color: #f57c00; border: 1px solid #ffcc02; }
    .badge-sensor { background: #e0f7fa; color: #00796b; border: 1px solid #b2dfdb; margin-right: 0.5rem; margin-bottom: 0.5rem; } /* Added style for sensor badges */
    .info-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Calculate mean only on numeric 'Accuracy (%)' data, dropping NaNs
        avg_accuracy_series = pd.to_numeric(
            filtered_df["Accuracy (%)"], errors="coerce"
        ).dropna()  # Changed "Accuracy" to "Accuracy (%)"
        if not avg_accuracy_series.empty:
            avg_accuracy = avg_accuracy_series.mean()
            st.markdown(
                f"""
            <div class="metric-card accuracy">
                <span class="metric-icon">🎯</span>
                <div class="metric-value">{avg_accuracy:.1f}%</div>
                <div class="metric-label">Average Accuracy</div>
                <div class="metric-sublabel">Across filtered initiatives</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        # Calculate mean only on numeric 'Resolution' data, dropping NaNs
        avg_resolution_series = pd.to_numeric(
            filtered_df["Resolution"], errors="coerce"
        ).dropna()
        if not avg_resolution_series.empty:
            avg_resolution = avg_resolution_series.mean()
            st.markdown(
                f"""
            <div class="metric-card resolution">
                <span class="metric-icon">🔬</span>
                <div class="metric-value">{avg_resolution:.0f}m</div>
                <div class="metric-label">Average Resolution</div>
                <div class="metric-sublabel">Spatial precision</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col3:
        total_classes = 0
        if "Classes" in filtered_df.columns:
            classes_series = pd.to_numeric(
                filtered_df["Classes"], errors="coerce"
            ).dropna()
            if not classes_series.empty:
                total_classes = classes_series.sum()
        elif "Number_of_Classes" in filtered_df.columns:
            num_classes_series = pd.to_numeric(
                filtered_df["Number_of_Classes"], errors="coerce"
            ).dropna()
            if not num_classes_series.empty:
                total_classes = num_classes_series.sum()

        if total_classes > 0:  # Only show if there are classes to sum
            st.markdown(
                f"""
            <div class="metric-card classes">
                <span class="metric-icon">🏷️</span>
                <div class="metric-value">{total_classes}</div>
                <div class="metric-label">Total Classes</div>
                <div class="metric-sublabel">Classification categories</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col4:
        if "Type" in filtered_df.columns:
            global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"])
            if global_initiatives > 0:  # Only show if there are global initiatives
                st.markdown(
                    f"""
                <div class="metric-card global">
                    <span class="metric-icon">🌍</span>
                    <div class="metric-value">{global_initiatives}</div>
                    <div class="metric-label">Global Initiatives</div>
                    <div class="metric-sublabel">Worldwide coverage</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    st.subheader("🔍 Detailed Exploration by Initiative")

    # CSS for modern initiative details
    st.markdown(
        """
    <style>
    .initiative-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px 15px 0 0;
        margin: 1rem 0 0 0;
    }
    .initiative-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .detail-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 0 0 15px 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .mini-metric {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #007bff;
    }
    .mini-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #007bff;
        margin: 0.3rem 0;
    }
    .mini-metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
    }
    .badge-type { background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
    .badge-methodology { background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8; }
    .badge-scope { background: #e8f5e8; color: #388e3c; border: 1px solid #a5d6a7; }
    .badge-years { background: #fff3e0; color: #f57c00; border: 1px solid #ffcc02; }
    .badge-sensor { background: #e0f7fa; color: #00796b; border: 1px solid #b2dfdb; margin-right: 0.5rem; margin-bottom: 0.5rem; } /* Added style for sensor badges */
    .info-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    .info-title {
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create formatted options for the selectbox
    formatted_options = []
    # Create a reverse mapping from formatted string to original name for easy lookup
    formatted_to_original_name = {}

    if not filtered_df.empty and "Name" in filtered_df.columns:
        for name in filtered_df["Name"].tolist():
            acronym = nome_to_sigla.get(
                name, "N/A"
            )  # Get acronym, default to N/A if not found
            formatted_display = f"{name} ({acronym})"
            formatted_options.append(formatted_display)
            formatted_to_original_name[formatted_display] = name

    selected_initiative_formatted = st.selectbox(
        "Select an initiative to see details:",
        options=formatted_options,  # Use the new formatted options
        help="Choose an initiative for detailed information",
        key="overview_detailed_select",
    )

    # Get the original initiative name from the formatted selection
    selected_initiative_detailed = formatted_to_original_name.get(
        selected_initiative_formatted
    )

    if selected_initiative_detailed:
        init_data = filtered_df[
            filtered_df["Name"] == selected_initiative_detailed
        ].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {})
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(
            selected_initiative_detailed, selected_initiative_detailed[:10]
        )

        # Modern initiative header
        st.markdown(
            f"""
        <div class="initiative-header">
            <h2 class="initiative-title">🛰️ {initiative_acronym}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{selected_initiative_detailed}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("""<div class="detail-card">""", unsafe_allow_html=True)

        col1_detail, col2_detail = st.columns([2, 3])

        with col1_detail:
            st.markdown("#### 📊 Key Metrics")

            # Modern metric grid - Conditional rendering
            metrics_html_parts = []
            accuracy_val = pd.to_numeric(
                init_data.get("Accuracy (%)"), errors="coerce"
            )  # Corrected key to 'Accuracy (%)'
            if pd.notna(accuracy_val):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🎯 {accuracy_val:.1f}%</div>
                    <div class="mini-metric-label">Accuracy</div></div>"""
                )

            resolution_val = pd.to_numeric(init_data.get("Resolution"), errors="coerce")
            if pd.notna(resolution_val):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🔬 {resolution_val:.0f}m</div>
                    <div class="mini-metric-label">Resolution</div></div>"""
                )

            classes_val_str = str(
                init_data.get("Classes", init_data.get("Number_of_Classes", ""))
            ).strip()
            classes_val = pd.to_numeric(classes_val_str, errors="coerce")
            if (
                pd.notna(classes_val) and classes_val_str
            ):  # Ensure original was not empty
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🏷️ {classes_val:.0f}</div>
                    <div class="mini-metric-label">Classes</div></div>"""
                )

            frequency_val = str(init_data.get("Temporal_Frequency", "")).strip()
            if (
                frequency_val
                and frequency_val.lower() != "n/a"
                and frequency_val.lower() != "none"
            ):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">📅 {frequency_val}</div>
                    <div class="mini-metric-label">Frequency</div></div>"""
                )

            if metrics_html_parts:
                st.markdown(
                    f"""<div class="metric-grid">{"".join(metrics_html_parts)}</div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("#### ⚙️ Technical Information")
            tech_info_html_parts = []
            type_val = str(init_data.get("Type", "")).strip()
            if type_val and type_val.lower() != "n/a" and type_val.lower() != "none":
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #17a2b8;">
                                                    <div class="info-title">🏷️ Type</div>
                                                    <p>{type_val}</p></div>"""
                )

            methodology_val = str(init_data.get("Methodology", "")).strip()
            if (
                methodology_val
                and methodology_val.lower() != "n/a"
                and methodology_val.lower() != "none"
            ):
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #6f42c1;">
                                                    <div class="info-title">🔬 Methodology</div>
                                                    <p>{methodology_val}</p></div>"""
                )

            scope_val = str(
                init_data.get("Coverage", "")
            ).strip()  # Using Coverage for scope
            if scope_val and scope_val.lower() != "n/a" and scope_val.lower() != "none":
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #28a745;">
                                                    <div class="info-title">🌍 Scope</div>
                                                    <p>{scope_val}</p></div>"""
                )

            # Get available_years from DataFrame (already processed as JSON string then list)
            available_years_str_from_df = init_data.get("Available_Years_List", "[]")
            try:
                available_years_list = (
                    json.loads(available_years_str_from_df)
                    if available_years_str_from_df
                    else []
                )
            except json.JSONDecodeError:
                available_years_list = []

            if isinstance(available_years_list, list) and available_years_list:
                # sorted_years_str = ", ".join(sorted(map(str, set(available_years_list)))) # Old way
                formatted_years_str = _format_year_ranges(
                    available_years_list
                )  # New way
                if formatted_years_str:  # Check if the formatted string is not empty
                    tech_info_html_parts.append(
                        f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                        <div class="info-title">📅 Available Years</div>
                                                        <p>{formatted_years_str}</p></div>"""
                    )

            # Display Sensors Referenced using info-section and badges inside it
            sensors_referenced_str_from_df = init_data.get("Sensors_Referenced", "[]")
            try:
                sensors_referenced_list_for_display = (
                    json.loads(sensors_referenced_str_from_df)
                    if sensors_referenced_str_from_df
                    else []
                )
            except json.JSONDecodeError:
                sensors_referenced_list_for_display = []

            if (
                isinstance(sensors_referenced_list_for_display, list)
                and sensors_referenced_list_for_display
            ):
                sensor_badges_html_parts = (
                    []
                )  # Keep using badges for individual sensors within the section
                sensor_details_expanders = []  # For expanders

                for sensor_ref_obj in sensors_referenced_list_for_display:
                    current_sensor_key_str = None  # Initialize
                    years_used_list = []

                    if isinstance(sensor_ref_obj, dict):
                        _key_from_dict = sensor_ref_obj.get("sensor_key")
                        if _key_from_dict is not None:
                            current_sensor_key_str = str(
                                _key_from_dict
                            )  # Ensure string
                        years_used_list = sensor_ref_obj.get("years_used", [])
                    elif isinstance(sensor_ref_obj, str):
                        current_sensor_key_str = sensor_ref_obj  # Already a string

                    # Proceed only if current_sensor_key_str is a valid (non-empty) string
                    if (
                        current_sensor_key_str
                    ):  # Check if current_sensor_key_str is not None and not empty
                        sensor_info_from_meta = sensors_meta.get(
                            str(current_sensor_key_str), {}
                        )
                        display_name = sensor_info_from_meta.get(
                            "display_name",
                            str(current_sensor_key_str).replace("_", " ").title(),
                        )

                        sensor_display_text_for_badge = display_name
                        if years_used_list and isinstance(years_used_list, list):
                            years_used_str = _format_year_ranges(
                                years_used_list
                            )  # Use the formatter
                            sensor_display_text_for_badge += (
                                f" (Years: {years_used_str})"
                            )
                        sensor_badges_html_parts.append(
                            f'<span class="badge badge-sensor">{sensor_display_text_for_badge}</span>'
                        )  # Prepare content for expander
                        expander_title = f"🛰️ {display_name} Details"
                        expander_content = ""

                        # Add all details from sensors_meta for this sensor
                        if (
                            sensor_info_from_meta
                        ):  # Check if sensor_info_from_meta is not empty
                            expander_content += "**General Specifications:**\n"
                            for spec_key, spec_value in sensor_info_from_meta.items():
                                if spec_key not in ["display_name", "notes"]:
                                    formatted_spec_key = spec_key.replace(
                                        "_", " "
                                    ).title()
                                    if isinstance(spec_value, list):
                                        # If list of dicts (like spectral_bands)
                                        if all(
                                            isinstance(item, dict)
                                            for item in spec_value
                                        ):
                                            expander_content += (
                                                f"  - **{formatted_spec_key}:**\n"
                                            )
                                            for item_dict in spec_value:
                                                band_details = []
                                                for k, v in item_dict.items():
                                                    band_details.append(
                                                        f"{k.replace('_', ' ').title()}: {v}"
                                                    )
                                                expander_content += (
                                                    f"    - {', '.join(band_details)}\n"
                                                )
                                        else:  # Simple list
                                            expander_content += f"  - **{formatted_spec_key}:** {', '.join(map(str, spec_value))}\n"
                                    elif isinstance(spec_value, dict):
                                        expander_content += (
                                            f"  - **{formatted_spec_key}:**\n"
                                        )
                                        for sub_k, sub_v in spec_value.items():
                                            expander_content += f"    - {sub_k.replace('_', ' ').title()}: {sub_v}\n"
                                    else:
                                        expander_content += f"  - **{formatted_spec_key}:** {spec_value}\n"
                            if "notes" in sensor_info_from_meta:
                                expander_content += (
                                    f"\n**Notes:** {sensor_info_from_meta['notes']}\n"
                                )
                        else:
                            expander_content += "_No detailed specifications found in sensor metadata._\n"

                        sensor_details_expanders.append(
                            (expander_title, expander_content)
                        )
                    # else: current_sensor_key_str was None or empty, so this sensor_ref_obj is skipped

                if sensor_badges_html_parts:
                    tech_info_html_parts.append(
                        f"""<div class="info-section" style="border-left-color: #00bcd4;">
                                                        <div class="info-title">🛰️ Sensors Referenced</div>
                                                        <p>{" ".join(sensor_badges_html_parts)}</p></div>"""
                    )

                # Display expanders for sensor details
                if sensor_details_expanders:
                    st.markdown("#### 🛰️ Detailed Sensor Specifications")
                    for title, content in sensor_details_expanders:
                        with st.expander(title):
                            st.markdown(
                                content, unsafe_allow_html=True
                            )  # Allow markdown for formatting

            if tech_info_html_parts:
                st.markdown(
                    f"""<div style="margin: 1rem 0;">{"".join(tech_info_html_parts)}</div>""",
                    unsafe_allow_html=True,
                )

        with col2_detail:
            st.markdown("#### 📋 Methodological Details")

            methodology_section_html = []

            # Approach and Algorithm
            methodology_approach = str(init_metadata.get("methodology", "")).strip()
            algorithm_info = str(
                init_metadata.get(
                    "algorithm", init_metadata.get("classification_method", "")
                )
            ).strip()
            approach_algo_html = []
            if methodology_approach and methodology_approach.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                approach_algo_html.append(
                    f"<p><strong>Approach:</strong> {methodology_approach}</p>"
                )
            if algorithm_info and algorithm_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                approach_algo_html.append(
                    f"<p><strong>Algorithm:</strong> {algorithm_info}</p>"
                )
            if approach_algo_html:
                methodology_section_html.append(
                    f"""<div class="info-section">
                                                    <div class="info-title">🔬 Methodology</div>
                                                    {"".join(approach_algo_html)}</div>"""
                )

            # Provider & Sources
            provider_info = str(init_metadata.get("provider", "")).strip()
            source_info = str(init_metadata.get("source", "")).strip()
            provider_source_html = []
            if provider_info and provider_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                provider_source_html.append(
                    f"<p><strong>Provider:</strong> {provider_info}</p>"
                )
            if source_info and source_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                provider_source_html.append(
                    f"<p><strong>Data Source:</strong> {source_info}</p>"
                )
            if provider_source_html:
                methodology_section_html.append(
                    f"""<div class="info-section" style="border-left-color: #28a745;">
                                                    <div class="info-title">🏢 Provider & Sources</div>
                                                    {"".join(provider_source_html)}</div>"""
                )

            # Update Information & Sensors Referenced (Combined Section)
            update_freq_info = str(init_metadata.get("update_frequency", "")).strip()
            temporal_freq_init_data = str(
                init_data.get("Temporal_Frequency", "")
            ).strip()
            # Initialize sensors_referenced_metadata earlier to ensure it's available
            # sensors_referenced_metadata = init_metadata.get('sensors_referenced', [])
            # Now, get it from the DataFrame (it was stored as a JSON string)
            sensors_referenced_str = init_data.get("Sensors_Referenced", "[]")
            try:
                sensors_referenced_metadata = (
                    json.loads(sensors_referenced_str) if sensors_referenced_str else []
                )
            except json.JSONDecodeError:
                sensors_referenced_metadata = []  # Default to empty list on error

            update_info_html_parts = []

            if update_freq_info and update_freq_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                update_info_html_parts.append(
                    f"<p><strong>Update Frequency (Metadata):</strong> {update_freq_info}</p>"
                )
            if temporal_freq_init_data and temporal_freq_init_data.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                update_info_html_parts.append(
                    f"<p><strong>Temporal Frequency (Data):</strong> {temporal_freq_init_data}</p>"
                )

            # Display Sensors Referenced in this section as well, if not already covered or if more detail is needed here
            if (
                isinstance(sensors_referenced_metadata, list)
                and sensors_referenced_metadata
            ):
                sensors_display_parts = []
                for sensor_ref in sensors_referenced_metadata:
                    if isinstance(sensor_ref, dict):
                        sensor_key_from_dict = sensor_ref.get("sensor_key")
                        sensor_key = (
                            str(sensor_key_from_dict)
                            if sensor_key_from_dict is not None
                            else None
                        )  # Ensure string or None
                        years_used = sensor_ref.get("years_used")

                        # Get display_name from sensors_meta for this section as well
                        sensor_details_from_meta = {}
                        if sensor_key:  # Only proceed if sensor_key is a valid string
                            sensor_details_from_meta = sensors_meta.get(sensor_key, {})
                        display_name = sensor_details_from_meta.get(
                            "display_name",
                            sensor_key if sensor_key else "Unknown Sensor",
                        )

                        sensor_detail_display = display_name
                        if years_used and isinstance(years_used, list):
                            years_used_str = ", ".join(
                                map(str, sorted(list(set(years_used))))
                            )
                            sensor_detail_display += f" (Used in: {years_used_str})"
                        sensors_display_parts.append(
                            f"<li>{sensor_detail_display}</li>"
                        )

            # New section for detailed sensor information
            if (
                isinstance(sensors_referenced_metadata, list)
                and sensors_referenced_metadata
            ):
                detailed_sensor_info_html = [
                    '<div class="info-section" style="border-left-color: #6f42c1;"><div class="info-title">🛰️ Detailed Sensor Specifications</div>'
                ]
                for sensor_ref in sensors_referenced_metadata:
                    if isinstance(sensor_ref, dict):
                        sensor_key_from_ref = sensor_ref.get("sensor_key")

                        key_to_use_for_get = None
                        if (
                            isinstance(sensor_key_from_ref, str)
                            and sensor_key_from_ref.strip()
                        ):
                            key_to_use_for_get = sensor_key_from_ref.strip()

                        sensor_details_from_meta = {}
                        display_name_for_sensor_heading = "Unknown Sensor"

                        if (
                            key_to_use_for_get
                        ):  # This ensures key_to_use_for_get is a non-empty string
                            sensor_details_from_meta = sensors_meta.get(
                                key_to_use_for_get, {}
                            )
                            display_name_for_sensor_heading = (
                                sensor_details_from_meta.get(
                                    "display_name", key_to_use_for_get
                                )
                            )
                        elif (
                            sensor_key_from_ref is not None
                        ):  # Original key was present but not a valid string
                            display_name_for_sensor_heading = (
                                f"Invalid Sensor Key ({str(sensor_key_from_ref)})"
                            )
                        # else: sensor_key_from_ref was None, display_name_for_sensor_heading remains 'Unknown Sensor'

                        detailed_sensor_info_html.append(
                            f"<h5 style='margin-top: 1rem; color: #6f42c1;'>{display_name_for_sensor_heading}</h5><ul style='list-style-type: disc; margin-left: 20px;'>"
                        )

                        family = sensor_details_from_meta.get("sensor_family")
                        platform = sensor_details_from_meta.get("platform_name")
                        sensor_type = sensor_details_from_meta.get(
                            "sensor_type_description"
                        )
                        agency = sensor_details_from_meta.get("agency")
                        status = sensor_details_from_meta.get("status")
                        revisit = sensor_details_from_meta.get("revisit_time_days")

                        if family:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Family:</strong> {family}</li>"
                            )
                        if platform:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Platform:</strong> {platform}</li>"
                            )
                        if sensor_type:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Type:</strong> {sensor_type}</li>"
                            )
                        if agency:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Agency:</strong> {agency}</li>"
                            )
                        if status:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Status:</strong> {status}</li>"
                            )
                        if revisit:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Revisit Time:</strong> {revisit} days</li>"
                            )

                        detailed_sensor_info_html.append("</ul>")
                detailed_sensor_info_html.append("</div>")
                # Ensure this is appended to methodology_section_html, not update_info_html_parts, to place it correctly.
                methodology_section_html.append("".join(detailed_sensor_info_html))

            if update_info_html_parts:  # This section is for update frequency, etc.
                methodology_section_html.append(
                    f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                    <div class="info-title">🔄 Update & Temporal Info</div>
                                                    {"".join(update_info_html_parts)}</div>"""
                )

            # Detailed Temporal Coverage Analysis from init_metadata['available_years']
            # available_years_metadata = init_metadata.get('available_years', [])
            # Get available_years_list from the DataFrame instead
            # available_years_metadata = init_data.get('Available_Years_List', [])
            # Parse Available_Years_List from JSON string
            available_years_str = init_data.get("Available_Years_List", "[]")
            try:
                available_years_metadata = (
                    json.loads(available_years_str) if available_years_str else []
                )
            except json.JSONDecodeError:
                available_years_metadata = []
            # sensors_referenced_metadata is already defined above

            processed_years_as_int = []
            if isinstance(available_years_metadata, list):
                for year in available_years_metadata:
                    try:
                        processed_years_as_int.append(int(year))
                    except (ValueError, TypeError):
                        continue  # Skip invalid year values

            if processed_years_as_int:
                min_year = min(processed_years_as_int)
                max_year = max(processed_years_as_int)
                year_range = f"{min_year} - {max_year}"
                temporal_coverage_html = f"<p><strong>🕒 Temporal Coverage:</strong> {year_range} (from metadata)</p>"
            else:
                temporal_coverage_html = (
                    "<p><strong>🕒 Temporal Coverage:</strong> Not available</p>"
                )

            # Append temporal coverage info to the methodology section
            methodology_section_html.append(
                f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                <div class="info-title">📅 Temporal Coverage</div>
                                                {temporal_coverage_html}
                                              </div>"""
            )

            # Append all methodology sections to the main column
            if methodology_section_html:
                st.markdown("".join(methodology_section_html), unsafe_allow_html=True)

        # Additional section for class information
        # Always show classification details if we have class data
        st.markdown("#### 🏷️ Classification Details")

        # Get class legend data and use new modular component
        class_legend_json_str = init_data.get("Class_Legend", "[]")
        lulc_classes.render_lulc_classes_section(class_legend_json_str)

        # Ensure the detail-card div is closed after all content for the selected initiative
        st.markdown("</div>", unsafe_allow_html=True)  # Closes detail-card

    # Link to detailed comparisons
    st.markdown("---")
    st.info(
        "💡 **For detailed comparisons between multiple initiatives**, go to the **'🔍 Detailed Analyses'** page in the sidebar."
    )
    st.markdown("---")

    # --- START OF MOVED TEMPORAL DENSITY AND METRICS ---
    # Temporal density chart
    st.subheader("🌊 Temporal Density of LULC Initiatives")

    if meta:  # Create density data using metadata
        density_data = []
        all_years = set()

        for nome, meta_item in meta.items():
            # Ensure the initiative is in the filtered_df before processing
            if nome in filtered_df["Name"].values:
                if "available_years" in meta_item and meta_item["available_years"]:
                    for ano in meta_item["available_years"]:
                        density_data.append({"nome": nome, "ano": ano})
                        all_years.add(ano)

        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df["ano"].value_counts().sort_index()

            # Density chart by year (discrete bars)
            fig_density_line = go.Figure()
            fig_density_line.add_trace(
                go.Bar(
                    x=year_counts.index,
                    y=year_counts.values,
                    name="Active Initiatives",
                    marker=dict(
                        color="rgba(0,150,136,0.8)",
                        line=dict(color="rgba(0,150,136,1)", width=1),
                    ),
                    hovertemplate="<b>Year: %{x}</b><br>"
                    + "Active Initiatives: %{y}<extra></extra>",
                )
            )

            fig_density_line.update_layout(
                title="📊 Temporal Density: Number of Initiatives per Year",
                xaxis_title="Year",
                yaxis_title="Number of Active Initiatives",
                height=450,
                hovermode="x unified",
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="rgba(128,128,128,0.2)",
                    tickmode="linear",
                    dtick=2,
                ),
                yaxis=dict(
                    showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)"
                ),
            )
            st.plotly_chart(fig_density_line, use_container_width=True)

            # Download functionality removed for cleaner interface

            # Enhanced temporal metrics - Modern cards
            st.markdown("#### 📈 Temporal Metrics")

            # CSS for temporal metrics
            st.markdown(
                """
            <style>
            .temporal-metric {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.2rem;
                border-radius: 12px;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .temporal-metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0.3rem 0;
            }
            .temporal-metric-label {
                font-size: 0.9rem;
                opacity: 0.9;
            }
            .temporal-metric-delta {
                font-size: 0.8rem;
                opacity: 0.8;
                margin-top: 0.2rem;
            }
            .timeline-card { /* This style might be for the timeline details you mentioned */
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            # Calculate and display temporal metrics
            if all_years:  # Ensure all_years is not empty
                first_year = min(all_years) if all_years else "N/A"
                last_year = max(all_years) if all_years else "N/A"
                peak_activity_year = (
                    year_counts.idxmax() if not year_counts.empty else "N/A"
                )
                avg_initiatives_per_year = (
                    year_counts.mean() if not year_counts.empty else 0
                )

                tm_col1, tm_col2, tm_col3, tm_col4 = st.columns(4)
                with tm_col1:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🗓️ {first_year}</div>
                                        <div class="temporal-metric-label">First Year Covered</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col2:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🗓️ {last_year}</div>
                                        <div class="temporal-metric-label">Last Year Covered</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col3:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🚀 {peak_activity_year}</div>
                                        <div class="temporal-metric-label">Peak Activity Year</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col4:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">📊 {avg_initiatives_per_year:.1f}</div>
                                        <div class="temporal-metric-label">Avg. Initiatives/Year</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info(
                    "ℹ️ Temporal metrics cannot be calculated as no year data is available from the filtered initiatives' metadata."
                )
        else:
            st.info(
                "ℹ️ No temporal density data to display based on current filters and available metadata."
            )
    # --- END OF MOVED TEMPORAL DENSITY AND METRICS ---

    # Placeholder for any other final content or footers if needed.
    # For example, if there was a "Timeline Details" section showing most/oldest,
    # it would have been *before* the "Temporal Density" and "Temporal Metrics" above.


if __name__ == "__main__":
    run()


if __name__ == "__main__":
    run()
