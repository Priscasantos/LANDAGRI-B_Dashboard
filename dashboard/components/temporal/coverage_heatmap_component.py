"""
Coverage Heatmap Component
-------------------------
Exibe o heatmap de cobertura das iniciativas LULC.
"""
import streamlit as st
import pandas as pd
from plotly import graph_objects as go

try:
    from scripts.plotting.charts.temporal_charts import plot_coverage_heatmap_chart
except ImportError:
    plot_coverage_heatmap_chart = None

def render_coverage_heatmap(temporal_data):
    """Renderiza o heatmap de cobertura e métricas relacionadas."""
    fig_heatmap = None
    if plot_coverage_heatmap_chart:
        fig_heatmap = plot_coverage_heatmap_chart(temporal_data)
    if fig_heatmap is None:
        fig_heatmap = create_comprehensive_coverage_heatmap(temporal_data)
    if fig_heatmap:
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No data to display for the coverage heatmap.")
    if not temporal_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            total_types = temporal_data["Tipo"].nunique() if "Tipo" in temporal_data.columns else 0
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
                sum(len(anos) for anos in temporal_data["Anos_Lista"] if isinstance(anos, list))
                if "Anos_Lista" in temporal_data.columns else 0
            )
            st.metric("Total Data Points", total_data_points)

def create_comprehensive_coverage_heatmap(temporal_data):
    try:
        if (
            temporal_data.empty
            or "Anos_Lista" not in temporal_data.columns
            or "Tipo" not in temporal_data.columns
        ):
            return None
        heatmap_data = []
        for _, row in temporal_data.iterrows():
            if isinstance(row["Anos_Lista"], list):
                initiative_type = row["Tipo"] if pd.notna(row["Tipo"]) else "Uncategorized"
                for year in row["Anos_Lista"]:
                    if isinstance(year, int | float):
                        heatmap_data.append({"Type": initiative_type, "Year": int(year), "Available": 1})
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
        current_year = 2024
        start_year = (
            max(pivot_df.columns.min(), current_year - 20)
            if len(pivot_df.columns) > 0 else current_year - 10
        )
        year_range = range(int(start_year), current_year + 1)
        pivot_df = pivot_df.reindex(columns=year_range, fill_value=0)
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale="Viridis",
                hoverongaps=False,
                hovertemplate="<b>Type: %{y}</b><br>Year: %{x}<br>Active Initiatives: %{z}<extra></extra>",
                colorbar={"title": "Active<br>Initiatives"},
            )
        )
        fig.update_layout(
            title="Initiative Availability by Type and Year",
            xaxis_title="Year",
            yaxis_title="Initiative Type",
            height=600,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "tickmode": "linear",
                "tick0": start_year,
                "dtick": 2,
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
        st.error(f"Error creating comprehensive coverage heatmap: {e}")
        return None
