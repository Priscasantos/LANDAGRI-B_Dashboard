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
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(
            selected_initiative_detailed, selected_initiative_detailed[:10]
        )

        # Modern initiative header
        st.markdown(f"### 🛰️ {initiative_acronym}")
        st.markdown(f"**{selected_initiative_detailed}**")
        
        col1_detail, col2_detail = st.columns([1, 1])

        with col1_detail:
            st.markdown("#### 📊 Key Metrics")
            
            # Display key metrics
            accuracy_val = pd.to_numeric(
                init_data.get("Accuracy (%)", ""), errors="coerce"
            )
            if pd.notna(accuracy_val):
                st.metric("🎯 Accuracy", f"{accuracy_val:.1f}%")

            resolution_val = pd.to_numeric(init_data.get("Resolution", ""), errors="coerce")
            if pd.notna(resolution_val):
                st.metric("🔬 Resolution", f"{resolution_val:.0f}m")

            classes_val = pd.to_numeric(
                init_data.get("Classes", init_data.get("Number_of_Classes", "")), 
                errors="coerce"
            )
            if pd.notna(classes_val):
                st.metric("🏷️ Classes", f"{classes_val:.0f}")

        with col2_detail:
            st.markdown("#### 🌍 Coverage Information")
            
            coverage_val = str(init_data.get("Coverage", "")).strip()
            if coverage_val and coverage_val.lower() not in ["n/a", "none", ""]:
                st.info(f"🌍 **Coverage:** {coverage_val}")

            scope_val = str(init_data.get("Scope", "")).strip()
            if scope_val and scope_val.lower() not in ["n/a", "none", ""]:
                st.info(f"🎯 **Scope:** {scope_val}")

        # Description section
        description_val = str(init_data.get("Description", "")).strip()
        if (
            description_val
            and description_val.lower() not in ["n/a", "none", ""]
            and len(description_val) > 10
        ):
            st.markdown("#### 📋 Description")
            st.markdown(description_val)

        # Classification details
        st.markdown("#### 🏷️ Classification Details")
        class_legend_json_str = init_data.get("Class_Legend", "[]")
        lulc_classes.render_lulc_classes_section(class_legend_json_str)

    # Link to detailed comparisons
    st.markdown("---")
    st.info(
        "💡 **For detailed comparisons between multiple initiatives**, go to the **'🔍 Detailed Analyses'** page in the sidebar."
    )


def run():
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

    # Load sensor metadata
    sensors_meta = {}
    try:
        sensors_metadata_path = Path(__file__).parent.parent / "data" / "json" / "sensors_metadata.jsonc"
        if sensors_metadata_path.exists():
            with open(sensors_metadata_path, "r", encoding="utf-8") as file:
                import commentjson
                sensors_meta = commentjson.load(file)
                st.session_state.sensors_meta = sensors_meta
        else:
            st.warning(f"⚠️ Sensors metadata file not found at {sensors_metadata_path}")
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
