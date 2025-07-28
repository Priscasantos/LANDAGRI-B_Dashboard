"""
Evolution Analysis Component
---------------------------
Exibe os gráficos de evolução da disponibilidade e resolução das iniciativas LULC.
"""
import streamlit as st
import pandas as pd
from plotly import graph_objects as go

try:
    from scripts.plotting.charts.temporal_charts import plot_evolution_line_chart, plot_evolution_heatmap_chart
except ImportError:
    plot_evolution_line_chart = None
    plot_evolution_heatmap_chart = None

def render_evolution_analysis(temporal_data):
    """Renderiza os gráficos de evolução e métricas relacionadas."""
    if temporal_data.empty or "Anos_Lista" not in temporal_data.columns:
        st.warning("No temporal data available for evolution analysis.")
        return
    temporal_data_for_evolution = temporal_data.copy()
    if "Tipo" not in temporal_data_for_evolution.columns:
        temporal_data_for_evolution["Tipo"] = "Uncategorized"
    else:
        temporal_data_for_evolution["Tipo"] = temporal_data_for_evolution["Tipo"].fillna("Uncategorized")
    all_years = []
    for _, row in temporal_data_for_evolution.iterrows():
        if isinstance(row["Anos_Lista"], list):
            all_years.extend(row["Anos_Lista"])
    if not all_years:
        st.warning("No year data available for evolution analysis.")
        return
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({"Year": year_counts.index, "Number_Initiatives": year_counts.values})
    st.markdown("#### Evolution of Data Availability Over Time")
    fig_evolution = None
    if plot_evolution_line_chart:
        fig_evolution = plot_evolution_line_chart(temporal_data_for_evolution)
    if fig_evolution is None:
        fig_evolution = create_basic_evolution_chart(years_df)
    if fig_evolution:
        st.plotly_chart(fig_evolution, use_container_width=True)
    else:
        st.info("Could not generate evolution chart.")
    st.markdown("#### Evolution of Spatial Resolution in LULC (1985-2024)")
    metadata = st.session_state.get("metadata", {})
    filtered_df = st.session_state.get("df_interpreted", pd.DataFrame())
    if metadata and not filtered_df.empty:
        if plot_evolution_heatmap_chart:
            fig_evolution_heatmap = plot_evolution_heatmap_chart(metadata, filtered_df)
            if fig_evolution_heatmap:
                st.plotly_chart(fig_evolution_heatmap, use_container_width=True, key="evolution_heatmap_chart")
            else:
                show_evolution_stats(years_df)
        else:
            st.info("Spatial resolution evolution chart not available.")
    else:
        show_evolution_stats(years_df)
    st.markdown("#### LULC Initiative Growth & Resolution (1985-2024)")
    fig_combined = create_combined_evolution_chart(metadata, filtered_df, years_df)
    if fig_combined:
        st.plotly_chart(fig_combined, use_container_width=True, key="combined_evolution_chart")
    else:
        st.info("Could not generate combined evolution chart.")

def show_evolution_stats(years_df):
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

def create_basic_evolution_chart(years_df):
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
            height=600,
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
from .evolution_chart_utils import create_combined_evolution_chart
