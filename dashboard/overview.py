"""
Overview Dashboard - Modern Implementation
=========================================

Clean, component-based overview dashboard using only modular components.
This replaces all legacy overview implementations.

Author: LANDAGRI-B Project Team 
Date: 2025-07-30
"""

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.components.overview import lulc_classes, summary_cards
from dashboard.components import agricultural_data

# Add scripts to path if necessary
current_dir = Path(__file__).parent.parent  # dashboard-iniciativas/
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


def render_overview_metrics(df: pd.DataFrame, meta: dict) -> None:
    """
    Render key metrics using modern components.

    Args:
        df: DataFrame with initiatives data
        meta: Metadata dictionary
    """
    # st.subheader("📊 LULC Initiative Overview")

    # Use modern summary cards component (includes Coverage Distribution and Performance Metrics)
    summary_cards.render(df)


def render_initiative_details(df: pd.DataFrame, meta: dict, sensors_meta: dict) -> None:
    """
    Render detailed exploration using components.

    Args:
        df: DataFrame with initiatives data
        meta: Metadata dictionary
        sensors_meta: Sensor metadata dictionary
    """
    st.markdown("---")
    st.subheader("🔍 Initiative Details")

    if df.empty:
        st.warning("No initiative data available.")
        return

    # Create selectbox for initiative selection
    initiative_names = df["Name"].tolist() if "Name" in df.columns else []
    if not initiative_names:
        st.warning("No initiative names found in data.")
        return

    # Add acronyms if available
    options = []
    name_mapping = {}

    for name in initiative_names:
        acronym = (
            df[df["Name"] == name]["Acronym"].iloc[0]
            if "Acronym" in df.columns
            else "N/A"
        )
        display_name = f"{name} ({acronym})" if acronym != "N/A" else name
        options.append(display_name)
        name_mapping[display_name] = name

    selected_display = st.selectbox(
        "Select an initiative for detailed analysis:",
        options=options,
        key="modern_overview_select",
    )

    if selected_display:
        selected_name = name_mapping[selected_display]
        selected_data = df[df["Name"] == selected_name].iloc[0]
        selected_metadata = meta.get(selected_name, {})

        # Display initiative details using components
        _render_selected_initiative(selected_data, selected_metadata, sensors_meta)


def _render_selected_initiative(
    data: pd.Series, metadata: dict, sensors_meta: dict
) -> None:
    """Render selected initiative details using modern components."""

    # Initiative header com caixa azul escuro e fonte branca
    st.markdown(
        f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(30, 41, 59, 0.18);
        color: #fff;
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        {data.get("Name", "Unknown Initiative")} ({data.get("Acronym", "N/A")})
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Centralized KEY METRICS section
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 1.5rem;">
        <h2 style="font-size: 2rem; font-weight: 700; color: #1e293b; margin: 0;">📊 KEY METRICS</h2>
    </div>
    """, unsafe_allow_html=True)
    _render_key_metrics_cards(data)

    # Lower section: two columns
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 🏷️ Classification")
        class_legend = data.get("Class_Legend", "[]")
        lulc_classes.render_lulc_classes_section(class_legend)

    with col_right:
        st.markdown("### 🔧 Technical Details")
        _render_technical_details(data, metadata)

        st.markdown("### 🛰️ Sensor Information")
        _render_sensor_details(data, sensors_meta)


def _render_key_metrics_cards(data: pd.Series) -> None:
    """Render key metrics as modern cards."""

    # Extract metrics
    accuracy = pd.to_numeric(data.get("Accuracy (%)", ""), errors="coerce")
    resolution = pd.to_numeric(data.get("Resolution", ""), errors="coerce")
    classes = pd.to_numeric(
        data.get("Classes", data.get("Number_of_Classes", "")), errors="coerce"
    )
    # Calculate temporal coverage (years)
    available_years_str = data.get("Available_Years_List", "[]")
    try:
        available_years = (
            json.loads(available_years_str) if available_years_str else []
        )
    except Exception:
        available_years = []
    years_coverage = len(available_years)
    frequency = str(data.get("Temporal_Frequency", "")).strip()

    # Custom CSS for colored cards
    st.markdown(
        """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%);
        border-radius: 14px;
        padding: 1.2rem 0.8rem 1rem 0.8rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 12px rgba(59, 130, 246, 0.08);
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 120px;
    }
    .metric-card.accuracy { background: linear-gradient(135deg, #fef9c3 0%, #fde68a 100%); }
    .metric-card.resolution { background: linear-gradient(135deg, #d1fae5 0%, #6ee7b7 100%); }
    .metric-card.classes { background: linear-gradient(135deg, #fbcfe8 0%, #f472b6 100%); }
    .metric-card.frequency { background: linear-gradient(135deg, #bae6fd 0%, #38bdf8 100%); }
    .metric-icon {
        font-size: 2.1rem;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-help {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.2rem;
        text-align: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.markdown(
            """
        <div class='metric-card accuracy'>
            <div class='metric-icon'>🎯</div>
            <div class='metric-label'>Accuracy</div>
            <div class='metric-value'>{}</div>
            <div class='metric-help'>Overall accuracy</div>
        </div>
        """.format(
                f"{accuracy:.1f}%" if pd.notna(accuracy) else "-"
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
        <div class='metric-card resolution'>
            <div class='metric-icon'>🔬</div>
            <div class='metric-label'>Resolution</div>
            <div class='metric-value'>{}</div>
            <div class='metric-help'>Raster Spatial Resolution</div>
        </div>
        """.format(
                f"{resolution:.0f}m" if pd.notna(resolution) else "-"
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
        <div class='metric-card classes'>
            <div class='metric-icon'>🏷️</div>
            <div class='metric-label'>Classes</div>
            <div class='metric-value'>{}</div>
            <div class='metric-help'>Land cover classes</div>
        </div>
        """.format(
                f"{classes:.0f}" if pd.notna(classes) else "-"
            ),
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
        <div class='metric-card frequency'>
            <div class='metric-icon'>📅</div>
            <div class='metric-label'>Temporal Coverage</div>
            <div class='metric-value'>{}</div>
            <div class='metric-help'>Years of data</div>
        </div>
        """.format(
                years_coverage if years_coverage > 0 else "-"
            ),
            unsafe_allow_html=True,
        )


def _render_sensor_details(data: pd.Series, sensors_meta: dict) -> None:
    """Render sensor details using metadata."""

    # Look for sensor information in the initiative data
    sensor_fields = ["Sensor", "Primary_Sensor", "Sensors_Used", "Data_Source"]
    sensor_info = None

    for field in sensor_fields:
        if field in data and pd.notna(data[field]) and str(data[field]).strip():
            sensor_info = str(data[field]).strip()
            break

    if not sensor_info or sensor_info.lower() in ["n/a", "none", "-", ""]:
        st.info("💡 No specific sensor information available for this initiative.")

        # Try to show alternative sensor-related information
        alternative_fields = ["Data_Source", "Source", "Provider"]
        for field in alternative_fields:
            if field in data and pd.notna(data[field]) and str(data[field]).strip():
                alt_info = str(data[field]).strip()
                if alt_info.lower() not in ["n/a", "none", "-", ""]:
                    st.markdown(f"**📊 Data Source:** {alt_info}")
                    break
        return

    # Try to match with sensor metadata
    sensor_key = None
    sensor_data = None

    # Look for exact matches or partial matches in sensor metadata
    for key, meta in sensors_meta.items():
        if (
            key.lower() in sensor_info.lower()
            or sensor_info.lower() in key.lower()
            or meta.get("display_name", "").lower() in sensor_info.lower()
        ):
            sensor_key = key
            sensor_data = meta
            break

    if sensor_data:
        # Display rich sensor information
        st.markdown(f"**🛰️ {sensor_data.get('display_name', sensor_key)}**")

        # Sensor details in expandable sections
        with st.expander("🔍 Sensor Specifications", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Platform:** {sensor_data.get('platform_name', '-')}")
                st.write(f"**Sensor Family:** {sensor_data.get('sensor_family', '-')}")
                st.write(f"**Type:** {sensor_data.get('sensor_type_description', '-')}")

            with col2:
                resolutions = sensor_data.get("spatial_resolutions_m", [])
                if resolutions:
                    st.write(
                        f"**Spatial Res.:** {min(resolutions)}-{max(resolutions)}m"
                    )
                else:
                    st.write("**Spatial Res.:** -")

                revisit = sensor_data.get("revisit_time_days", "")
                if revisit:
                    st.write(f"**Revisit Time:** {revisit} days")
                else:
                    st.write("**Revisit Time:** -")

                status = sensor_data.get("status", "")
                if status:
                    st.write(f"**Status:** {status}")

        # Spectral bands information
        bands = sensor_data.get("spectral_bands", [])
        if bands:
            with st.expander("🌈 Spectral Bands"):
                bands_df = pd.DataFrame(bands)
                if not bands_df.empty:
                    st.dataframe(bands_df, use_container_width=True)
    else:
        # Display basic sensor information
        st.markdown(f"**🛰️ Sensor:** {sensor_info}")
        st.info("💡 Detailed sensor metadata not available in database.")


def _render_technical_details(data: pd.Series, metadata: dict) -> None:
    """Render technical details in a clean format."""

    # Basic information
    with st.expander("🏢 Basic Information", expanded=True):
        st.write(f"**Provider:** {data.get('Provider', '-')}")
        st.write(f"**Source:** {data.get('Source', '-')}")
        st.write(f"**Coverage:** {data.get('Coverage', '-')}")

    # Technical specifications
    with st.expander("🔬 Technical Specifications"):
        st.write(f"**Methodology:** {data.get('Methodology', '-')}")
        st.write(f"**Algorithm:** {data.get('Algorithm', '-')}")
        st.write(f"**Spatial Resolution:** {data.get('Spatial_Resolution', '-')}")
        st.write(f"**Reference System:** {data.get('Reference_System', '-')}")

    # Temporal information
    with st.expander("⏳ Temporal Information"):
        # Parse available years
        available_years_str = data.get("Available_Years_List", "[]")
        try:
            available_years = (
                json.loads(available_years_str) if available_years_str else []
            )
        except json.JSONDecodeError:
            available_years = []

        if available_years:
            st.write(f"**First Year:** {min(available_years)}")
            st.write(f"**Last Year:** {max(available_years)}")
            st.write(f"**Total Years:** {len(available_years)}")
        else:
            st.write("**Temporal Coverage:** Not available")


def load_sensor_metadata() -> dict:
    """Load sensor metadata with proper error handling."""
    sensors_meta = {}

    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file

        current_dir = Path(__file__).parent.parent
        sensors_metadata_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
        fallback_metadata_path = (
            current_dir / "data" / "json" / "sensors_metadata_original.jsonc"
        )

        if sensors_metadata_path.exists():
            sensors_meta = _load_jsonc_file(sensors_metadata_path)
        elif fallback_metadata_path.exists():
            sensors_meta = _load_jsonc_file(fallback_metadata_path)

        if isinstance(sensors_meta, dict):
            return sensors_meta

    except Exception as e:
        st.error(f"❌ Error loading sensor metadata: {e}")

    return {}


def run() -> None:
    """Main function to run the modern overview dashboard."""

    # Check session state for required data
    if "metadata" not in st.session_state or "df_interpreted" not in st.session_state:
        st.error(
            "❌ Data not found in session state. Please ensure the app loads data correctly."
        )
        return

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    meta = st.session_state.get("metadata", {})

    if df is None or df.empty:
        st.error("❌ No initiative data available for the overview dashboard.")
        return

    # Load sensor metadata
    sensors_meta = load_sensor_metadata()
    if sensors_meta:
        st.session_state.sensors_meta = sensors_meta

    # Apply any filters (using components)
    # filters.render(df)  # Uncomment if filter component is needed

    # Render visually styled header (like Initiative Analysis)
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
        <h1 style=\"color: white; margin: 0; font-size: 2.5rem; font-weight: 700;\">
            🌍 Overview
        </h1>
        <p style=\"color: #dbeafe; margin: 0.5rem 0 0 0; font-size: 1.2rem;\">
            General summary and key metrics of LULC initiatives
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Render main overview sections using components
    render_overview_metrics(df, meta)
    render_initiative_details(df, meta, sensors_meta)
    
    # Add Brazilian agricultural data section
    st.markdown("---")
    agricultural_data.render()


if __name__ == "__main__":
    run()
