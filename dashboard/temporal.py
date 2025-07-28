import plotly.express as px
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Add scripts to path - This should be at the very top
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Importar componentes de gráficos
from dashboard.components.temporal.timeline_chart_component import render_timeline_chart
from dashboard.components.temporal.gaps_analysis_component import render_gaps_analysis
from dashboard.components.temporal.evolution_analysis_component import render_evolution_analysis
from dashboard.components.temporal.coverage_heatmap_component import render_coverage_heatmap


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
    # This logic mirrors the legacy show_timeline_chart for compatibility
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
    temporal_df["Anos_Faltando"] = temporal_df["Anos_Lista"].apply(calculate_largest_consecutive_gap)

    # --- Render all modular temporal charts in tabs ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Timeline", "⚠️ Gaps Analysis", "📈 Evolution", "🔥 Coverage Heatmap"
    ])

    with tab1:
        render_timeline_chart(df_for_analysis, meta_geral)

    with tab2:
        render_gaps_analysis(temporal_df)

    with tab3:
        render_evolution_analysis(temporal_df)

    with tab4:
        render_coverage_heatmap(temporal_df)


from dashboard.components.temporal.evolution_chart_utils import create_combined_evolution_chart

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


def show_timeline_chart(df_for_analysis, raw_initiatives_metadata):
    """Timeline chart showing discrete years for each initiative with proper gaps."""

    # Generate and display the main timeline chart
    fig_timeline = None

    if fig_timeline is None:
        # Fallback: create basic timeline chart
        fig_timeline = create_basic_timeline_chart(
            raw_initiatives_metadata, df_for_analysis
        )

    if fig_timeline is None:
        st.info("No data to display for the timeline chart.")
        return

    st.plotly_chart(fig_timeline, use_container_width=True)

    # Add download functionality
    if fig_timeline:
        # Download functionality removed for cleaner interface
        pass

    # Create name to acronym mapping
    nome_to_sigla = {}
    if (
        df_for_analysis is not None
        and "Acronym" in df_for_analysis.columns
        and "Name" in df_for_analysis.columns
    ):
        for _, row in df_for_analysis.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    # Prepare temporal data for metrics
    temporal_data = []
    for nome, details in raw_initiatives_metadata.items():
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
                    }
                )

    temporal_df = pd.DataFrame(temporal_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Initiatives", len(temporal_df))
    with col2:
        if (
            not temporal_df.empty
            and "Primeiro_Ano" in temporal_df.columns
            and "Ultimo_Ano" in temporal_df.columns
        ):
            primeiro_ano_geral = temporal_df["Primeiro_Ano"].min()
            ultimo_ano_geral = temporal_df["Ultimo_Ano"].max()
            periodo_total = f"{primeiro_ano_geral}-{ultimo_ano_geral}"
        else:
            periodo_total = "N/A"
        st.metric("Total Period Covered", periodo_total)
    with col3:
        if not temporal_df.empty:
            total_anos_disponiveis = sum(
                len(anos) for anos in temporal_df["Anos_Lista"]
            )
            st.metric("Total Years Available", total_anos_disponiveis)
        else:
            st.metric("Total Years Available", "N/A")


def create_basic_timeline_chart(metadata, df_for_analysis):
    """Create a basic timeline chart as fallback"""
    try:
        # Create name to acronym mapping
        nome_to_sigla = {}
        if (
            df_for_analysis is not None
            and "Acronym" in df_for_analysis.columns
            and "Name" in df_for_analysis.columns
        ):
            for _, row in df_for_analysis.iterrows():
                if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                    nome_to_sigla[row["Name"]] = row["Acronym"]

        fig = go.Figure()
        y_pos = 0
        colors = px.colors.qualitative.Plotly

        for i, (nome, details) in enumerate(metadata.items()):
            if isinstance(details, dict) and "available_years" in details:
                years = (
                    details["available_years"]
                    if isinstance(details["available_years"], list)
                    else []
                )
                if years:
                    display_name = nome_to_sigla.get(nome, nome[:15])

                    # Add scatter plot for each year
                    fig.add_trace(
                        go.Scatter(
                            x=years,
                            y=[y_pos] * len(years),
                            mode="markers",
                            name=display_name,
                            marker={
                                "size": 10,
                                "color": colors[i % len(colors)],
                                "symbol": "square",
                            },
                            hovertemplate=f"<b>{display_name}</b><br>Year: %{{x}}<extra></extra>",
                        )
                    )
                    y_pos += 1

        fig.update_layout(
            title="LULC Initiatives Timeline",
            xaxis_title="Year",
            yaxis_title="Initiative",
            height=600,  # Standardized height like CONAB
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "title_font": {"family": "Arial Black"},
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
            },
            yaxis={
                "title_font": {"family": "Arial Black"},
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
            },
        )

        return fig
    except Exception as e:
        st.error(f"Error creating basic timeline chart: {e}")
        return None


def show_coverage_heatmap(temporal_data):
    """Heatmap of initiative availability by type and year using display names"""

    # Create heatmap with consistent dimensions
    fig_heatmap = None

    if fig_heatmap is None:
        # Enhanced fallback: create comprehensive coverage heatmap
        fig_heatmap = create_comprehensive_coverage_heatmap(temporal_data)

    if fig_heatmap:
        st.plotly_chart(fig_heatmap, use_container_width=True)
        # Download functionality removed for cleaner interface
        pass
    else:
        st.info("No data to display for the coverage heatmap.")

    # Add summary statistics
    if not temporal_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            total_types = (
                temporal_data["Tipo"].nunique()
                if "Tipo" in temporal_data.columns
                else 0
            )
            st.metric("Initiative Types", total_types)
        with col2:
            if "Anos_Lista" in temporal_data.columns:
                all_years = []
                for _, row in temporal_data.iterrows():
                    if isinstance(row["Anos_Lista"], list):
                        all_years.extend(row["Anos_Lista"])
                year_span = f"{min(all_years)}-{max(all_years)}" if all_years else "N/A"
                st.metric("Year Range", year_span)
            else:
                st.metric("Year Range", "N/A")
        with col3:
            total_data_points = (
                sum(
                    len(anos)
                    for anos in temporal_data["Anos_Lista"]
                    if isinstance(anos, list)
                )
                if "Anos_Lista" in temporal_data.columns
                else 0
            )
            st.metric("Total Data Points", total_data_points)


def create_basic_coverage_heatmap(temporal_data):
    """Create basic coverage heatmap as fallback"""
    try:
        if (
            temporal_data.empty
            or "Anos_Lista" not in temporal_data.columns
            or "Tipo" not in temporal_data.columns
        ):
            return None

        # Create heatmap data
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            if isinstance(row["Anos_Lista"], list):
                for year in row["Anos_Lista"]:
                    heatmap_data.append(
                        {"Year": year, "Type": row["Tipo"], "Available": 1}
                    )

        if not heatmap_data:
            return None

        heatmap_df = pd.DataFrame(heatmap_data)
        pivot_df = heatmap_df.pivot_table(
            values="Available",
            index="Type",
            columns="Year",
            aggfunc="sum",
            fill_value=0,
        )

        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale="Viridis",
                hoverongaps=False,
                hovertemplate="<b>Type: %{y}</b><br>Year: %{x}<br>Active Initiatives: %{z}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Initiative Availability by Type and Year",
            xaxis_title="Year",
            yaxis_title="Initiative Type",
            height=400,
            xaxis={"title_font": {"family": "Arial Black"}},  # Bold x-axis title
            yaxis={"title_font": {"family": "Arial Black"}},  # Bold y-axis title
        )

        return fig
    except Exception as e:
        st.error(f"Error creating coverage heatmap: {e}")
        return None


def create_comprehensive_coverage_heatmap(temporal_data):
    """Create modernized temporal coverage chart with continuity indicators and standardized styling"""
    try:
        if (
            temporal_data.empty
            or "Anos_Lista" not in temporal_data.columns
            or "Tipo" not in temporal_data.columns
        ):
            return None

        # Create timeline data with continuity tracking
        timeline_data = []
        for _, row in temporal_data.iterrows():
            if isinstance(row["Anos_Lista"], list) and row["Anos_Lista"]:
                initiative_name = row.get("Display_Name", row.get("Nome", "Unknown"))
                initiative_type = row["Tipo"] if pd.notna(row["Tipo"]) else "Uncategorized"
                years = sorted([int(y) for y in row["Anos_Lista"] if isinstance(y, (int, float))])
                
                if years:
                    start_year = min(years)
                    end_year = max(years)
                    total_possible_years = end_year - start_year + 1
                    available_years = len(years)
                    continuity = available_years / total_possible_years
                    
                    # Determine status
                    current_year = 2024
                    is_active = end_year >= current_year - 1
                    is_discontinued = end_year < current_year - 2
                    
                    timeline_data.append({
                        "Initiative": initiative_name,
                        "Type": initiative_type,
                        "Start_Year": start_year,
                        "End_Year": end_year,
                        "Duration": end_year - start_year + 1,
                        "Continuity": continuity,
                        "Status": "Active" if is_active else ("Discontinued" if is_discontinued else "Completed"),
                        "Available_Years": available_years
                    })

        if not timeline_data:
            return None

        timeline_df = pd.DataFrame(timeline_data)
        
        # Sort by start year and then by type
        timeline_df = timeline_df.sort_values(["Start_Year", "Type"])
        
        # Create modern scatter plot with timeline bars
        fig = go.Figure()
        
        # Define modern standardized colors
        status_colors = {
            "Active": "#2E8B57",      # Sea green
            "Completed": "#4682B4",   # Steel blue  
            "Discontinued": "#CD5C5C" # Indian red
        }
        
        # Add timeline bars for each initiative
        for i, row in timeline_df.iterrows():
            y_pos = i
            
            # Main timeline bar
            fig.add_trace(go.Scatter(
                x=[row["Start_Year"], row["End_Year"]],
                y=[y_pos, y_pos],
                mode="lines",
                line=dict(
                    color=status_colors[row["Status"]],
                    width=8,
                    # Dash pattern based on continuity
                    dash="solid" if row["Continuity"] > 0.8 else ("dash" if row["Continuity"] > 0.5 else "dot")
                ),
                name=row["Status"],
                legendgroup=row["Status"],
                showlegend=row["Status"] not in [trace.legendgroup for trace in fig.data if hasattr(trace, 'legendgroup')],
                hovertemplate=f"<b>{row['Initiative']}</b><br>" +
                             f"Type: {row['Type']}<br>" +
                             f"Duration: {row['Start_Year']}-{row['End_Year']} ({row['Duration']} years)<br>" +
                             f"Continuity: {row['Continuity']:.1%}<br>" +
                             f"Status: {row['Status']}<extra></extra>"
            ))
            
            # Start point marker
            fig.add_trace(go.Scatter(
                x=[row["Start_Year"]],
                y=[y_pos],
                mode="markers",
                marker=dict(
                    color=status_colors[row["Status"]],
                    size=10,
                    symbol="circle",
                    line=dict(color="white", width=2)
                ),
                name="Start/End Points",
                legendgroup="points",
                showlegend=i == 0,
                hoverinfo="skip"
            ))
            
            # End point marker
            fig.add_trace(go.Scatter(
                x=[row["End_Year"]],
                y=[y_pos],
                mode="markers",
                marker=dict(
                    color=status_colors[row["Status"]],
                    size=10,
                    symbol="square",
                    line=dict(color="white", width=2)
                ),
                legendgroup="points",
                showlegend=False,
                hoverinfo="skip"
            ))

        # Update layout with modern styling
        fig.update_layout(
            title={
                'text': "Comprehensive Temporal Analysis of LULC Initiatives",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif', 'color': '#2E3440'}
            },
            xaxis={
                'title': 'Year',
                'showgrid': True,
                'gridcolor': 'rgba(128,128,128,0.1)',
                'zeroline': False,
                'tickmode': 'linear',
                'dtick': 2,
                'title_font': {'family': 'Arial, sans-serif', 'size': 14},
                'tickfont': {'family': 'Arial, sans-serif', 'size': 12}
            },
            yaxis={
                'title': 'Initiatives',
                'tickmode': 'array',
                'tickvals': list(range(len(timeline_df))),
                'ticktext': [f"{row['Initiative']} ({row['Type']})" for _, row in timeline_df.iterrows()],
                'showgrid': True,
                'gridcolor': 'rgba(128,128,128,0.1)',
                'zeroline': False,
                'title_font': {'family': 'Arial, sans-serif', 'size': 14},
                'tickfont': {'family': 'Arial, sans-serif', 'size': 10}
            },
            height=max(600, len(timeline_df) * 40),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'left',
                'x': 0,
                'font': {'family': 'Arial, sans-serif', 'size': 12}
            },
            margin=dict(l=200, r=50, t=100, b=50)
        )

        # Add annotations for continuity legend
        fig.add_annotation(
            text="Line Patterns: Solid (>80% continuity) • Dashed (50-80%) • Dotted (<50%)",
            xref="paper", yref="paper",
            x=0, y=-0.05,
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor="left"
        )

        return fig
    except Exception as e:
        st.error(f"Error creating comprehensive coverage heatmap: {e}")
        return None


def show_gaps_analysis(temporal_data):
    """Temporal gaps analysis using display names"""

    if temporal_data.empty or "Anos_Faltando" not in temporal_data.columns:
        st.warning("No temporal data available for gaps analysis.")
        return

    # Ensure Anos_Faltando is numeric and handle string/int comparison issue
    try:
        temporal_data["Anos_Faltando"] = pd.to_numeric(temporal_data["Anos_Faltando"], errors='coerce')
        temporal_data["Anos_Faltando"] = temporal_data["Anos_Faltando"].fillna(0)
        
        gaps_data = temporal_data[temporal_data["Anos_Faltando"] > 0].copy()
    except Exception as e:
        st.error(f"Error processing Anos_Faltando data: {e}")
        return
    
    if "Tipo" not in gaps_data.columns:
        gaps_data["Tipo"] = "Uncategorized"
    else:
        gaps_data["Tipo"] = gaps_data["Tipo"].fillna("Uncategorized")

    if gaps_data.empty:
        st.success("✅ No temporal gaps found in the initiatives!")
        return


    # Use only the fallback chart, as modular components are now used
    fig_gaps = create_comprehensive_gaps_chart(gaps_data)
    if fig_gaps:
        st.plotly_chart(fig_gaps, use_container_width=True)
    else:
        st.info("Could not generate gaps analysis chart.")

    # Gap Statistics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        initiatives_with_gaps = len(gaps_data)
        st.metric("Initiatives with Gaps", initiatives_with_gaps)
    with col2:
        avg_gap = gaps_data["Anos_Faltando"].mean()
        st.metric("Average Missing Years", f"{avg_gap:.1f}")
    with col3:
        max_gap = gaps_data["Anos_Faltando"].max()
        st.metric("Maximum Missing Years", f"{max_gap}")


def create_basic_gaps_chart(gaps_data):
    """Create basic gaps chart as fallback"""
    try:
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=gaps_data["Display_Name"],
                y=gaps_data["Anos_Faltando"],
                name="Missing Years",
                marker_color="rgba(255, 99, 71, 0.8)",
                hovertemplate="<b>%{x}</b><br>Missing Years: %{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title="Missing Years in Time Series by Initiative",
            xaxis_title="Initiative",
            yaxis_title="Number of Missing Years",
            height=400,
            showlegend=False,
            xaxis={"title_font": {"family": "Arial Black"}},  # Bold x-axis title
            yaxis={"title_font": {"family": "Arial Black"}},  # Bold y-axis title
        )

        return fig
    except Exception as e:
        st.error(f"Error creating gaps chart: {e}")
        return None


def create_comprehensive_gaps_chart(gaps_data):
    """Create comprehensive gaps chart with standardized dimensions"""
    try:
        if gaps_data.empty or "Display_Name" not in gaps_data.columns:
            return None

        # Ensure Anos_Faltando is numeric
        gaps_data["Anos_Faltando"] = pd.to_numeric(gaps_data["Anos_Faltando"], errors='coerce')
        gaps_data = gaps_data.dropna(subset=["Anos_Faltando"])
        
        if gaps_data.empty:
            return None

        # Sort by missing years for better visualization
        gaps_data_sorted = gaps_data.sort_values("Anos_Faltando", ascending=True)

        # Create figure with standardized height
        fig = go.Figure()

        # Color scale based on severity
        colors = []
        for missing in gaps_data_sorted["Anos_Faltando"]:
            if missing <= 2:
                colors.append("#4CAF50")  # Green for low gaps
            elif missing <= 5:
                colors.append("#FF9800")  # Orange for medium gaps
            else:
                colors.append("#F44336")  # Red for high gaps

        fig.add_trace(
            go.Bar(
                x=gaps_data_sorted["Display_Name"],
                y=gaps_data_sorted["Anos_Faltando"],
                name="Missing Years",
                marker_color=colors,
                hovertemplate="<b>%{x}</b><br>Missing Years: %{y}<br>Severity: %{marker.color}<extra></extra>",
                text=gaps_data_sorted["Anos_Faltando"],
                textposition="auto",
            )
        )

        # Add severity threshold lines
        fig.add_hline(
            y=2,
            line_dash="dash",
            line_color="orange",
            annotation_text="Medium Severity",
            annotation_position="top right",
        )
        fig.add_hline(
            y=5,
            line_dash="dash",
            line_color="red",
            annotation_text="High Severity",
            annotation_position="top right",
        )

        fig.update_layout(
            title="Temporal Gaps Analysis - Missing Years by Initiative",
            xaxis_title="Initiative",
            yaxis_title="Number of Missing Years",
            height=500,  # Standardized height
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "tickangle": 45,
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
            },
            yaxis={"showgrid": True, "gridcolor": "rgba(128,128,128,0.2)"},
        )

        return fig
    except Exception as e:
        st.error(f"Error creating comprehensive gaps chart: {e}")
        return None


def show_evolution_analysis(temporal_data):
    """Analysis of data availability evolution over time"""

    if temporal_data.empty or "Anos_Lista" not in temporal_data.columns:
        st.warning("No temporal data available for evolution analysis.")
        return

    temporal_data_for_evolution = temporal_data.copy()
    if "Tipo" not in temporal_data_for_evolution.columns:
        temporal_data_for_evolution["Tipo"] = "Uncategorized"
    else:
        temporal_data_for_evolution["Tipo"] = temporal_data_for_evolution[
            "Tipo"
        ].fillna("Uncategorized")

    all_years = []
    for _, row in temporal_data_for_evolution.iterrows():
        if isinstance(row["Anos_Lista"], list):
            all_years.extend(row["Anos_Lista"])

    if not all_years:
        st.warning("No year data available for evolution analysis.")
        return

    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame(
        {"Year": year_counts.index, "Number_Initiatives": year_counts.values}
    )
    # First chart: Evolution of Data Availability Over Time
    st.markdown("#### Evolution of Data Availability Over Time")

    # Use only the fallback chart, as modular components are now used
    fig_evolution = create_basic_evolution_chart(years_df)
    if fig_evolution:
        st.plotly_chart(fig_evolution, use_container_width=True)
    else:
        st.info("Could not generate evolution chart.")

    # Second chart: Spatial Resolution Evolution
    st.markdown("#### Evolution of Spatial Resolution in LULC (1985-2024)")
    metadata = st.session_state.get("metadata", {})
    filtered_df = st.session_state.get("df_interpreted", pd.DataFrame())


    if metadata and not filtered_df.empty:
        st.info("Spatial resolution evolution chart not available.")
    else:
        # Show summary statistics if no metadata available
        st.markdown("#### Evolution Statistics")
        if not years_df.empty:
            peak_year = years_df.loc[years_df["Number_Initiatives"].idxmax(), "Year"]
            peak_count = years_df["Number_Initiatives"].max()
            avg_initiatives = years_df["Number_Initiatives"].mean()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Peak Year", f"{peak_year}")
            with col2:
                st.metric("Peak Initiatives", f"{peak_count}")
            with col3:
                st.metric("Average per Year", f"{avg_initiatives:.1f}")
        else:
            st.info("No data available for statistics.")

    # Third chart: LULC Initiative Growth & Resolution Combined
    st.markdown("#### LULC Initiative Growth & Resolution (1985-2024)")
    fig_combined = create_combined_evolution_chart(metadata, filtered_df, years_df)
    if fig_combined:
        st.plotly_chart(
            fig_combined, use_container_width=True, key="combined_evolution_chart"
        )
        # Download functionality removed for cleaner interface
        pass
    else:
        st.info("Could not generate combined evolution chart.")


def create_basic_evolution_chart(years_df):
    """Create basic evolution chart as fallback"""
    try:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=years_df["Year"],
                y=years_df["Number_Initiatives"],
                mode="lines+markers",
                name="Active Initiatives",
                line={"color": "rgba(0, 150, 136, 1)", "width": 3},
                marker={"size": 8, "color": "rgba(0, 150, 136, 0.8)"},
                fill="tonexty",
                fillcolor="rgba(0, 150, 136, 0.2)",
                hovertemplate="<b>Year: %{x}</b><br>Active Initiatives: %{y}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Evolution of Data Availability Over Time",
            xaxis_title="Year",
            yaxis_title="Number of Active Initiatives",
            height=600,  # Standardized height like CONAB
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
                "title_font": {"family": "Arial Black"},
            },
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
                "title_font": {"family": "Arial Black"},
            },
        )

        return fig
    except Exception as e:
        st.error(f"Error creating evolution chart: {e}")
        return None


def _parse_resolution_for_combined_chart(spatial_res):
    """Parse spatial resolution for combined chart analysis."""
    # TODO: Implement resolution parsing logic if needed
    return None


# Non-streamlit version for script execution
def run_non_streamlit(metadata, df_data, output_dir="graphics/temporal"):
    """Run temporal analysis without Streamlit UI and save graphics to files."""
    pass

