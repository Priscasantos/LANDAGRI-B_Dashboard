"""
Utility functions for combined evolution chart (LULC Initiative Growth & Resolution)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_combined_evolution_chart(metadata, filtered_df, years_df):
    """Create combined evolution chart showing initiatives count, min/avg resolution over time"""
    try:
        if not metadata or filtered_df is None or filtered_df.empty or years_df.empty:
            return None

        # Process metadata to extract resolution and years data
        resolution_data = []

        for initiative_name, meta_info in metadata.items():
            if not isinstance(meta_info, dict):
                continue

            # Get available years
            years_key = (
                "available_years"
                if "available_years" in meta_info
                else "anos_disponiveis"
            )
            if years_key not in meta_info or not meta_info[years_key]:
                continue

            years = meta_info[years_key]
            if not isinstance(years, list):
                continue

            # Get spatial resolution
            spatial_res = meta_info.get("spatial_resolution")
            if spatial_res is None:
                continue

            # Parse resolution to get a single representative value
            resolution_value = _parse_resolution_for_combined_chart(spatial_res)
            if resolution_value is None:
                continue

            # Add data for each year
            for year in years:
                if isinstance(year, (int, float)) and 1985 <= year <= 2024:
                    resolution_data.append(
                        {
                            "initiative": initiative_name,
                            "year": int(year),
                            "resolution_value": resolution_value,
                        }
                    )

        if not resolution_data:
            return None

        # Create DataFrame and aggregate
        df_resolution = pd.DataFrame(resolution_data)

        # Calculate yearly statistics
        yearly_stats = (
            df_resolution.groupby("year")
            .agg({"resolution_value": ["min", "mean"], "initiative": "count"})
            .reset_index()
        )

        # Flatten column names
        yearly_stats.columns = ["year", "min_res", "avg_res", "count"]

        # Ensure we have all years from 1985 to 2024
        all_years = list(range(1985, 2025))
        full_df = pd.DataFrame({"year": all_years})
        full_df = full_df.merge(yearly_stats, on="year", how="left")
        full_df = full_df.merge(
            years_df.rename(
                columns={"Year": "year", "Number_Initiatives": "total_initiatives"}
            ),
            on="year",
            how="left",
        )

        # Fill missing values
        full_df["count"] = full_df["count"].fillna(0)
        full_df["total_initiatives"] = full_df["total_initiatives"].fillna(0)

        # Create subplots with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add initiatives count (line)
        fig.add_trace(
            go.Scatter(
                x=full_df["year"],
                y=full_df["total_initiatives"],
                mode="lines+markers",
                name="Initiatives",
                line={"color": "#26828e", "width": 3},
                marker={"size": 6, "color": "#26828e"},
                hovertemplate="<b>Year: %{x}</b><br>Initiatives: %{y}<extra></extra>",
            ),
            secondary_y=False,
        )

        # Add min resolution (line)
        fig.add_trace(
            go.Scatter(
                x=full_df["year"],
                y=full_df["min_res"],
                mode="lines",
                name="Min Res (m)",
                line={"color": "#c62d42", "width": 2},
                connectgaps=False,
                hovertemplate="<b>Year: %{x}</b><br>Min Resolution: %{y}m<extra></extra>",
            ),
            secondary_y=True,
        )

        # Add avg resolution (line with dots)
        fig.add_trace(
            go.Scatter(
                x=full_df["year"],
                y=full_df["avg_res"],
                mode="lines+markers",
                name="Avg Res (m)",
                line={"color": "#f39800", "width": 2, "dash": "dot"},
                marker={"size": 4, "color": "#f39800"},
                connectgaps=False,
                hovertemplate="<b>Year: %{x}</b><br>Avg Resolution: %{y:.1f}m<extra></extra>",
            ),
            secondary_y=True,
        )

        # Add milestone annotations
        milestones = {
            2000: "Milestone 2000",
            2010: "Milestone 2010",
            2020: "Milestone 2020",
        }

        for year, label in milestones.items():
            fig.add_vline(
                x=year,
                line_dash="dash",
                line_color="rgba(128,128,128,0.4)",
                line_width=1,
                annotation_text=label,
                annotation_position="top",
                annotation_font_size=10,
                annotation_font_color="rgba(139,69,19,0.6)",
            )

        # Set x-axis title
        fig.update_xaxes(title_text="Year", range=[1985, 2024])

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Initiatives</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Res (m)</b>", secondary_y=True)

        # Update layout
        fig.update_layout(
            title="LULC Initiative Growth & Resolution (1985-2024)",
            height=500,
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
                "tickformat": "d",
                "dtick": 5,
            },
        )

        return fig

    except Exception as e:
        st.error(f"Error creating combined evolution chart: {e}")
        return None

def _parse_resolution_for_combined_chart(spatial_res):
    """Parse spatial resolution for the combined chart"""
    if spatial_res is None:
        return None
    try:
        if isinstance(spatial_res, (int, float)):
            return float(spatial_res)
        elif isinstance(spatial_res, str):
            import re
            numbers = re.findall(r"\d+(?:\.\d+)?", spatial_res)
            if numbers:
                return float(numbers[0])
    except (ValueError, TypeError, AttributeError):
        return None
    return None
