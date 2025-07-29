import json  # Ensure json is imported
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.overview import filters, lulc_classes

# Add scripts to path if necessary
current_dir = Path(__file__).parent.parent  # dashboard-iniciativas/
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
    except ValueError:
        # Fallback to simple comma-separated list if conversion to int fails
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


def _render_initiative_metrics(init_data: pd.Series):
    """Render key metrics for a specific initiative."""
    st.markdown("#### 📊 Key Metrics")

    # CSS for mini-metrics
    st.markdown(
        """
    <style>
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .mini-metric {
        background: #f8f9fa;
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
    </style>
    """,
        unsafe_allow_html=True,
    )

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
    """Render comprehensive technical information for a specific initiative."""
    st.markdown("#### ⚙️ Comprehensive Initiative Details")
    
    # Enhanced CSS for info sections
    st.markdown(
        """
    <style>
    .info-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: transparent !important;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        box-shadow: none !important;
        color: #e0e6f0 !important;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    .info-title {
        font-weight: 600;
        color: #e0e6f0 !important;
        margin-bottom: 0.5rem;
        font-size: 1.1em;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
        background: transparent !important;
        color: #e0e6f0 !important;
    }
    .badge-sensor { 
        background: transparent !important; 
        color: #e0e6f0 !important; 
        border: 1px solid #b2dfdb; 
        margin-right: 0.5rem; 
        margin-bottom: 0.5rem; 
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.5rem;
        margin: 0.5rem 0;
        background: transparent !important;
    }
    .metric-item {
        background: transparent !important;
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #444a5a;
        color: #e0e6f0 !important;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    tech_info_html_parts = []

    # --- Basic Initiative Info ---
    provider = str(init_data.get("Provider", "-")).strip()
    source = str(init_data.get("Source", "-")).strip()
    acronym = str(init_data.get("Acronym", "-")).strip()
    coverage = str(init_data.get("Coverage", "-")).strip()
    
    basic_info_html = f"""
        <div class="info-section" style="border-left-color: #007bff;">
            <div class="info-title">🏢 Basic Information</div>
            <div class="metric-grid">
                <div class="metric-item"><b>Provider:</b> {provider}</div>
                <div class="metric-item"><b>Source:</b> {source}</div>
                <div class="metric-item"><b>Acronym:</b> {acronym}</div>
                <div class="metric-item"><b>Coverage:</b> {coverage}</div>
            </div>
        </div>
    """
    tech_info_html_parts.append(basic_info_html)

    # --- Technical Specifications ---
    spatial_res = str(init_data.get("Spatial_Resolution", "-")).strip()
    methodology = str(init_data.get("Methodology", "-")).strip()
    classification_method = str(init_data.get("Classification_Method", "-")).strip()
    algorithm = str(init_data.get("Algorithm", "-")).strip()
    reference_system = str(init_data.get("Reference_System", "-")).strip()
    
    tech_specs_html = f"""
        <div class="info-section" style="border-left-color: #6f42c1;">
            <div class="info-title">🔬 Technical Specifications</div>
            <div class="metric-grid">
                <div class="metric-item"><b>Spatial Resolution:</b> {spatial_res}m</div>
                <div class="metric-item"><b>Methodology:</b> {methodology}</div>
                <div class="metric-item"><b>Classification Method:</b> {classification_method}</div>
                <div class="metric-item"><b>Reference System:</b> {reference_system}</div>
            </div>
            {f'<p style="margin-top:0.5rem;"><b>Algorithm:</b> {algorithm}</p>' if algorithm != "-" else ""}
        </div>
    """
    tech_info_html_parts.append(tech_specs_html)

    # --- Classification & Accuracy ---
    num_classes = str(init_data.get("Number_Of_Classes", "-")).strip()
    overall_accuracy = str(init_data.get("Overall_Accuracy", "-")).strip()
    num_ag_classes = str(init_data.get("Number_Of_Agriculture_Classes", "-")).strip()
    ag_capabilities = str(init_data.get("Agricultural_Capabilities", "-")).strip()
    class_legend = str(init_data.get("Class_Legend", "-")).strip()
    
    classification_html = f"""
        <div class="info-section" style="border-left-color: #28a745;">
            <div class="info-title">🎯 Classification & Accuracy</div>
            <div class="metric-grid">
                <div class="metric-item"><b>Number of Classes:</b> {num_classes}</div>
                <div class="metric-item"><b>Overall Accuracy:</b> {overall_accuracy}{'%' if overall_accuracy != '-' and overall_accuracy.replace('.','').isdigit() else ''}</div>
                <div class="metric-item"><b>Agriculture Classes:</b> {num_ag_classes}</div>
            </div>
            {f'<p style="margin-top:0.5rem;"><b>Agricultural Capabilities:</b> {ag_capabilities}</p>' if ag_capabilities != "-" else ""}
            {f'<p style="margin-top:0.5rem;"><b>Class Legend:</b> {class_legend}</p>' if class_legend != "-" else ""}
        </div>
    """
    tech_info_html_parts.append(classification_html)

    # --- Temporal Info Section ---
    available_years_str_from_df = init_data.get("Available_Years_List", "[]")
    try:
        available_years_list = (
            json.loads(available_years_str_from_df)
            if available_years_str_from_df
            else []
        )
    except json.JSONDecodeError:
        available_years_list = []
    first_year = min(available_years_list) if available_years_list else "-"
    last_year = max(available_years_list) if available_years_list else "-"
    recurrence = str(init_data.get("Update_Frequency", init_data.get("Temporal_Frequency", "-")))
    if recurrence.lower() in ["n/a", "none", "", "-"]:
        recurrence = "-"
    formatted_years_str = _format_year_ranges(available_years_list) if available_years_list else "-"
    temporal_html = f"""
        <div class="info-section" style="border-left-color: #fd7e14;">
            <div class="info-title">⏳ Temporal Info</div>
            <ul style='margin:0; padding-left:1.2em;'>
                <li><b>Recurrence:</b> {recurrence}</li>
                <li><b>First Year:</b> {first_year}</li>
                <li><b>Last Year:</b> {last_year}</li>
                <li><b>Available Years:</b> {formatted_years_str}</li>
            </ul>
        </div>
    """
    tech_info_html_parts.append(temporal_html)

    # --- Sensor Details Section (Enhanced) ---
    # Always show comprehensive sensor details
    sensors_referenced_str_from_df = init_data.get("Sensors_Referenced", "[]")
    try:
        sensors_referenced_list_for_display = (
            json.loads(sensors_referenced_str_from_df)
            if sensors_referenced_str_from_df
            else []
        )
    except json.JSONDecodeError:
        sensors_referenced_list_for_display = []

    sensor_details_html = ""
    if sensors_referenced_list_for_display:
        # Aggregate sensor information
        all_platforms = []
        all_families = []
        all_instruments = []
        all_agencies = []
        combined_resolutions = []
        combined_bands = []
        
        # Start the sensor details section with proper opening div
        sensor_details_html += """
        <div class='info-section' style='border-left-color:#00bcd4; background: transparent !important; color: #e0e6f0;'>
          <div class='info-title'>🛰️ Sensor & Satellite Details</div>
        """

        for sensor_ref_obj in sensors_referenced_list_for_display:
            current_sensor_key_str = None
            if isinstance(sensor_ref_obj, dict):
                _key_from_dict = sensor_ref_obj.get("sensor_key")
                if _key_from_dict is not None:
                    current_sensor_key_str = str(_key_from_dict)
            elif isinstance(sensor_ref_obj, str):
                current_sensor_key_str = sensor_ref_obj

            if current_sensor_key_str:
                sensor_info = sensors_meta.get(str(current_sensor_key_str), {})
                display_name = sensor_info.get("display_name", str(current_sensor_key_str).replace("_", " ").title())
                platform = sensor_info.get("platform_name", "-")
                family = sensor_info.get("sensor_family", "-")
                instrument = sensor_info.get("instrument_names", [])
                sensor_type = sensor_info.get("sensor_type_description", "-")
                agency = sensor_info.get("agency", "-")
                swath = sensor_info.get("swath_width_km", "-")
                revisit = sensor_info.get("revisit_time_days", "-")
                status = sensor_info.get("status", "-")
                launch = sensor_info.get("launch_date", "-")
                resolutions = sensor_info.get("spatial_resolutions_m", [])
                spectral_bands = sensor_info.get("spectral_bands", [])

                # Aggregate for summary
                if platform != "-": all_platforms.append(platform)
                if family != "-": all_families.append(family)
                if instrument: all_instruments.extend(instrument)
                if agency != "-": all_agencies.append(agency)
                if resolutions: combined_resolutions.extend(resolutions)
                if spectral_bands: combined_bands.extend(spectral_bands)

                instrument_str = ", ".join(instrument) if instrument else "-"
                # Build HTML for each sensor, ensuring all tags are closed and not wrapped in code formatting
                sensor_html = f"""
                  <div style='background: transparent !important; margin:0.5rem 0; padding:0.8rem; border-radius:5px; border: 1px solid #444a5a; color: #e0e6f0;'>
                    <h5 style='margin:0 0 0.5rem 0; color:#56b6c2;'>🛰️ {display_name}</h5>
                    <div class="metric-grid">
                      <div class="metric-item"><b>Platform:</b> {platform}</div>
                      <div class="metric-item"><b>Family:</b> {family}</div>
                      <div class="metric-item"><b>Type:</b> {sensor_type}</div>
                      <div class="metric-item"><b>Agency:</b> {agency}</div>
                      <div class="metric-item"><b>Swath (km):</b> {swath}</div>
                      <div class="metric-item"><b>Revisit (days):</b> {revisit}</div>
                      <div class="metric-item"><b>Status:</b> {status}</div>
                      <div class="metric-item"><b>Launch:</b> {launch}</div>
                    </div>
                    <p style='margin:0.5rem 0 0 0; color: #e0e6f0;'><b>Instruments:</b> {instrument_str}</p>
                """
                if resolutions:
                    sensor_html += f"<p style='margin:0.5rem 0 0 0; color: #e0e6f0;'><b>Resolutions (m):</b> {', '.join(map(str, sorted(set(resolutions))))}</p>"
                if spectral_bands:
                    sensor_html += f"<p style='margin:0.5rem 0 0 0; color: #e0e6f0;'><b>Spectral Bands:</b> {len(spectral_bands)} bands</p>"
                sensor_html += "</div>"  # Close main sensor div
                sensor_details_html += sensor_html
        
        # Add aggregated summary if multiple sensors
        if len(sensors_referenced_list_for_display) > 1:
            unique_platforms = list(set(all_platforms))
            unique_families = list(set(all_families))
            unique_agencies = list(set(all_agencies))
            unique_resolutions = sorted(set(combined_resolutions))
            
            sensor_details_html += f"""
              <div style='background: transparent !important; margin:0.5rem 0; padding:0.8rem; border-radius:5px; border: 1px solid #444a5a; color: #e0e6f0;'>
                <h6 style='margin:0 0 0.5rem 0; color:#56b6c2;'>📊 Aggregated Sensor Summary</h6>
                <div class="metric-grid">
                  <div class="metric-item"><b>Total Sensors:</b> {len(sensors_referenced_list_for_display)}</div>
                  <div class="metric-item"><b>Platforms:</b> {len(unique_platforms)}</div>
                  <div class="metric-item"><b>Families:</b> {', '.join(unique_families) if unique_families else '-'}</div>
                  <div class="metric-item"><b>Agencies:</b> {', '.join(unique_agencies) if unique_agencies else '-'}</div>
                </div>
                <p style='margin:0.5rem 0 0 0; color: #e0e6f0;'><b>Combined Resolutions (m):</b> {', '.join(map(str, unique_resolutions)) if unique_resolutions else '-'}</p>
                <p style='margin:0.5rem 0 0 0; color: #e0e6f0;'><b>Total Spectral Bands:</b> {len(combined_bands) if combined_bands else 0}</p>
              </div>
            """
        
        sensor_details_html += "</div>"  # Close the sensor details section
    else:
        sensor_details_html += """
        <div class='info-section' style='border-left-color:#00bcd4; background: transparent !important; color: #e0e6f0;'>
          <div class='info-title'>🛰️ Sensor Details</div>
          <p>No sensor metadata available for this initiative.</p>
        </div>
        """
    # Ensure all tags are closed and no raw HTML is left open
    tech_info_html_parts.append(sensor_details_html)

    # --- Other Technical Info ---
    type_val = str(init_data.get("Type", "")).strip()
    if type_val and type_val.lower() not in ["n/a", "none"]:
        tech_info_html_parts.append(
            f"""<div class="info-section" style="border-left-color: #17a2b8;">
                <div class="info-title">🏷️ Type</div>
                <p>{type_val}</p></div>"""
        )

    # Add references if available
    references = str(init_data.get("References", "")).strip()
    if references and references.lower() not in ["n/a", "none", "[]"]:
        tech_info_html_parts.append(
            f"""<div class="info-section" style="border-left-color: #ffc107;">
                <div class="info-title">📚 References</div>
                <p>{references}</p></div>"""
        )

    st.markdown(
        f"""<div style="margin: 1rem 0;">{"".join(tech_info_html_parts)}</div>""",
        unsafe_allow_html=True,
    )


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


def _render_key_metrics(filtered_df: pd.DataFrame, meta: dict = None):
    """
    Render key aggregated metrics cards for the overview with LULC-specific focus.
    
    Args:
        filtered_df: DataFrame with filtered initiatives data
        meta: Initiative metadata dictionary
    """
    st.subheader("📊 LULC Initiative Metrics")

    # CSS for enhanced metrics cards
    st.markdown(
        """
    <style>
    .lulc-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .lulc-metric-card:hover {
        transform: translateY(-5px);
    }
    .lulc-metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .lulc-metric-label {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 500;
    }
    .lulc-metric-sublabel {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-top: 0.3rem;
    }
    .coverage-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Calculate coverage-based statistics
    coverage_stats = {"Global": 0, "Regional": 0, "National": 0, "Other": 0}
    
    if not filtered_df.empty and "Coverage" in filtered_df.columns:
        for coverage in filtered_df["Coverage"]:
            coverage_str = str(coverage).strip()
            if coverage_str.lower() in ["global", "worldwide"]:
                coverage_stats["Global"] += 1
            elif coverage_str.lower() in ["regional", "continental"]:
                coverage_stats["Regional"] += 1
            elif coverage_str.lower() in ["national", "country"]:
                coverage_stats["National"] += 1
            elif coverage_str.lower() not in ["n/a", "none", ""]:
                coverage_stats["Other"] += 1

    # Display coverage metrics
    st.markdown("#### 🌍 Initiative Coverage Distribution")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
        <div class="lulc-metric-card">
            <div class="lulc-metric-value">🌍 {coverage_stats['Global']}</div>
            <div class="lulc-metric-label">Global Initiatives</div>
            <div class="lulc-metric-sublabel">Worldwide coverage</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f"""
        <div class="lulc-metric-card">
            <div class="lulc-metric-value">🗺️ {coverage_stats['Regional']}</div>
            <div class="lulc-metric-label">Regional Initiatives</div>
            <div class="lulc-metric-sublabel">Continental/regional</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col3:
        st.markdown(
            f"""
        <div class="lulc-metric-card">
            <div class="lulc-metric-value">🏛️ {coverage_stats['National']}</div>
            <div class="lulc-metric-label">National Initiatives</div>
            <div class="lulc-metric-sublabel">Country-specific</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col4:
        st.markdown(
            f"""
        <div class="lulc-metric-card">
            <div class="lulc-metric-value">📍 {coverage_stats['Other']}</div>
            <div class="lulc-metric-label">Other Coverage</div>
            <div class="lulc-metric-sublabel">Specialized scope</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Performance metrics
    st.markdown("#### 🎯 Performance Metrics")
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        # Average accuracy
        avg_accuracy_series = pd.to_numeric(
            filtered_df.get("Accuracy (%)", []), errors="coerce"
        ).dropna()
        if not avg_accuracy_series.empty:
            avg_accuracy = avg_accuracy_series.mean()
            st.markdown(
                f"""
            <div class="lulc-metric-card">
                <div class="lulc-metric-value">🎯 {avg_accuracy:.1f}%</div>
                <div class="lulc-metric-label">Average Accuracy</div>
                <div class="lulc-metric-sublabel">Classification precision</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    
    with perf_col2:
        # Average resolution
        avg_resolution_series = pd.to_numeric(
            filtered_df.get("Resolution", []), errors="coerce"
        ).dropna()
        if not avg_resolution_series.empty:
            avg_resolution = avg_resolution_series.mean()
            st.markdown(
                f"""
            <div class="lulc-metric-card">
                <div class="lulc-metric-value">🔬 {avg_resolution:.0f}m</div>
                <div class="lulc-metric-label">Average Resolution</div>
                <div class="lulc-metric-sublabel">Spatial precision</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    
    with perf_col3:
        # Total classes
        total_classes = 0
        if "Classes" in filtered_df.columns:
            classes_series = pd.to_numeric(
                filtered_df["Classes"], errors="coerce"
            ).dropna()
            if not classes_series.empty:
                total_classes = classes_series.sum()
        
        if total_classes > 0:
            st.markdown(
                f"""
            <div class="lulc-metric-card">
                <div class="lulc-metric-value">🏷️ {total_classes}</div>
                <div class="lulc-metric-label">Total Classes</div>
                <div class="lulc-metric-sublabel">Classification categories</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    
    with perf_col4:
        # Temporal coverage
        if meta:
            total_years = set()
            for meta_item in meta.values():
                if "available_years" in meta_item and meta_item["available_years"]:
                    total_years.update(meta_item["available_years"])
            
            if total_years:
                year_span = max(total_years) - min(total_years) + 1
                st.markdown(
                    f"""
                <div class="lulc-metric-card">
                    <div class="lulc-metric-value">📅 {year_span}</div>
                    <div class="lulc-metric-label">Temporal Coverage</div>
                    <div class="lulc-metric-sublabel">Years of data</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def _render_detailed_exploration(filtered_df: pd.DataFrame, meta: dict, sensors_meta: dict, nome_to_sigla: dict):
    """
    Render the detailed exploration section for individual initiative analysis.
    
    Args:
        filtered_df: DataFrame with filtered initiatives data
        meta: Initiative metadata dictionary
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
        key="overview_detailed_select_clean",
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
        initiative_acronym = nome_to_sigla.get(
            selected_initiative_detailed, selected_initiative_detailed[:10]
        )

        st.markdown(f"## {selected_initiative_detailed}")
        st.markdown(f"### {initiative_acronym}")

        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown("#### 📊 Key Metrics")
            accuracy_val = pd.to_numeric(init_data.get("Accuracy (%)", ""), errors="coerce")
            resolution_val = pd.to_numeric(init_data.get("Resolution", ""), errors="coerce")
            classes_val = pd.to_numeric(init_data.get("Classes", init_data.get("Number_of_Classes", "")), errors="coerce")
            freq_val = str(init_data.get("Temporal_Frequency", "")).strip()
            st.markdown("""
                <div style='display: flex; gap: 1rem;'>
                    <div style='background: #181c2a; color: #e06c75; padding: 1rem; border-radius: 10px; min-width: 120px; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>🎯 {}</div>
                        <div style='font-size: 1rem;'>Accuracy</div>
                    </div>
                    <div style='background: #181c2a; color: #61afef; padding: 1rem; border-radius: 10px; min-width: 120px; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>🔬 {}</div>
                        <div style='font-size: 1rem;'>Resolution</div>
                    </div>
                    <div style='background: #181c2a; color: #e5c07b; padding: 1rem; border-radius: 10px; min-width: 120px; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>🏷️ {}</div>
                        <div style='font-size: 1rem;'>Classes</div>
                    </div>
                    <div style='background: #181c2a; color: #56b6c2; padding: 1rem; border-radius: 10px; min-width: 120px; text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>📅 {}</div>
                        <div style='font-size: 1rem;'>Frequency</div>
                    </div>
                </div>
            """.format(
                f"{accuracy_val:.1f}%" if pd.notna(accuracy_val) else "-",
                f"{resolution_val:.0f}m" if pd.notna(resolution_val) else "-",
                f"{classes_val:.0f}" if pd.notna(classes_val) else "-",
                freq_val if freq_val else "-"
            ), unsafe_allow_html=True)

            st.markdown("#### ⚙️ Technical Information")
            # Sensor Details, Type, Methodology, Scope, Available Years, Sensors Referenced
            _render_initiative_tech_info(init_data, sensors_meta)

        with right_col:
            st.markdown("#### 📋 Methodological Details")
            _render_initiative_methodology(init_data, init_metadata, sensors_meta)

    st.markdown("---")
    st.info(
        "💡 **For detailed comparisons between multiple initiatives**, go to the **'🔍 Detailed Analyses'** page in the sidebar."
    )


def run():
    # Removed test/debug message
    """Main function to run the LULC overview dashboard."""
    # Check session state for required data
    if "metadata" not in st.session_state or "df_interpreted" not in st.session_state:
        st.error(
            "❌ Interpreted data not found in session state. Ensure app.py loads data correctly."
        )
        return

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    meta = st.session_state.get("metadata", {})

    if df is None or df.empty:
        st.error("❌ No data available for overview dashboard.")
        return

    filtered_df = df.copy()
    nome_to_sigla = {}
    if "Acronym" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            nome_to_sigla[row["Name"]] = row["Acronym"]

    # Load sensor metadata with fallback and debug output
    sensors_meta = {}
    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file
        current_dir = Path(__file__).parent.parent  # dashboard-iniciativas/
        sensors_metadata_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
        fallback_metadata_path = current_dir / "data" / "json" / "sensors_metadata_original.jsonc"
        sensors_meta_loaded = None
        if sensors_metadata_path.exists():
            sensors_meta_loaded = _load_jsonc_file(sensors_metadata_path)
            st.info(f"Loaded sensors metadata from {sensors_metadata_path}")
        elif fallback_metadata_path.exists():
            sensors_meta_loaded = _load_jsonc_file(fallback_metadata_path)
            st.warning(f"Main sensors metadata not found, loaded fallback from {fallback_metadata_path}")
        else:
            st.warning(f"⚠️ Neither sensors_metadata.jsonc nor sensors_metadata_original.jsonc found.")
        if isinstance(sensors_meta_loaded, dict):
            sensors_meta = sensors_meta_loaded
            st.session_state.sensors_meta = sensors_meta
            st.info(f"Sensor metadata keys: {list(sensors_meta.keys())}")
        else:
            st.warning("⚠️ Sensor metadata file format is invalid")
    except ImportError:
        st.warning("⚠️ JSON interpreter not available for sensor metadata loading")
    except Exception as e:
        st.warning(f"⚠️ Error loading sensors metadata: {e}")

    # Render enhanced LULC-specific metrics
    _render_key_metrics(filtered_df, meta)

    # Render detailed exploration section
    _render_detailed_exploration(filtered_df, meta, sensors_meta, nome_to_sigla)

    # Temporal density chart
    st.markdown("---")
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

            # Enhanced temporal metrics
            st.markdown("#### 📈 Temporal Metrics")

            # Calculate and display temporal metrics
            if all_years:
                first_year = min(all_years)
                last_year = max(all_years)
                peak_activity_year = year_counts.idxmax() if not year_counts.empty else "N/A"
                avg_initiatives_per_year = year_counts.mean() if not year_counts.empty else 0

                tm_col1, tm_col2, tm_col3, tm_col4 = st.columns(4)
                with tm_col1:
                    st.metric("🗓️ First Year", str(first_year))
                with tm_col2:
                    st.metric("🗓️ Last Year", str(last_year))
                with tm_col3:
                    st.metric("🚀 Peak Activity Year", str(peak_activity_year))
                with tm_col4:
                    st.metric("📊 Avg. Initiatives/Year", f"{avg_initiatives_per_year:.1f}")
            else:
                st.info(
                    "ℹ️ Temporal metrics cannot be calculated as no year data is available from the filtered initiatives' metadata."
                )
        else:
            st.info(
                "ℹ️ No temporal density data to display based on current filters and available metadata."
            )


if __name__ == "__main__":
    run()
