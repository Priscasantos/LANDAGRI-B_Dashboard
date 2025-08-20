"""
Dual Bars Component - Detailed Analysis
=======================================

Component for rendering dual bars tab in detailed analysis.
Contains the create_dual_bars_chart migrated from detailed_charts.py.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import (
    apply_standard_layout,
    get_chart_colors,
)
from dashboard.components.shared.nomenclature import clean_column_names


def render_bars_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render dual bars chart tab for detailed comparison.
    
    Args:
        filtered_df: Filtered DataFrame with selected initiative data
    """
    if filtered_df.empty:
        st.warning("⚠️ No initiatives selected for comparison.")
        return
    
    if len(filtered_df) < 2:
        st.warning("⚠️ Select at least 2 initiatives for comparison.")
        return

    # Controls for 3 metrics
    st.markdown("**Select up to 3 metrics for comparison:**")
    col1, col2, col3 = st.columns(3)



    available_metrics = [col for col in filtered_df.columns if pd.api.types.is_numeric_dtype(filtered_df[col])]
    print(f"Available metrics: {available_metrics}")

    with col1:
        metric1 = st.selectbox(
            "First metric:",
            options=available_metrics,
            index=0,
            help="Select the first metric for comparison"
        )
    
    with col2:
        remaining_metrics = [col for col in available_metrics if col != metric1]
        if remaining_metrics:
            metric2 = st.selectbox(
                "Second metric:",
                options=["None"] + remaining_metrics,
                index=1 if len(remaining_metrics) > 0 else 0,
                help="Select the second metric for comparison"
            )
        else:
            metric2 = "None"
    
    with col3:
        if metric2 != "None":
            remaining_metrics2 = [col for col in available_metrics if col not in [metric1, metric2]]
            if remaining_metrics2:
                metric3 = st.selectbox(
                    "Third metric:",
                    options=["None"] + remaining_metrics2,
                    index=0,
                    help="Select the third metric for comparison"
                )
            else:
                metric3 = "None"
        else:
            metric3 = "None"
        
    # Prepare data for bar chart
    initiatives = filtered_df["Display_Name"].tolist()
    
    # Convert display names back to real column names
    real_metric1 = get_real_column_name(metric1)
    values1 = filtered_df[real_metric1].tolist()
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=initiatives,
        y=values1,
        name=metric1,
        marker_color="#3b82f6"
    ))
    
    if metric2 != "None":
        real_metric2 = get_real_column_name(metric2)
        values2 = filtered_df[real_metric2].tolist()
        fig.add_trace(go.Bar(
            x=initiatives,
            y=values2,
            name=metric2,
            marker_color="#10b981"
        ))
    
    if metric3 != "None":
        real_metric3 = get_real_column_name(metric3)
        values3 = filtered_df[real_metric3].tolist()
        fig.add_trace(go.Bar(
            x=initiatives,
            y=values3,
            name=metric3,
            marker_color="#f59e0b"
        ))
    
    fig.update_layout(
        barmode="group",
        title="<b>Bar Chart Comparison</b>",
        xaxis_title="Initiative",
        yaxis_title="Value",
        font=dict(family="Inter", size=12),
        title_font=dict(size=14, family="Inter", color="#1f2937"),
        xaxis_tickangle=-45,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, key="bar_chart_comparison")


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """
    Get numeric columns from DataFrame for comparison with improved names.
    
    Args:
        df: DataFrame with initiatives data
        
    Returns:
        List of numeric column names with improved labels
    """
    numeric_cols = []
    
    # Use our standardized nomenclature system
    for col in df.columns:
        if col in ["Display_Name", "Name", "Initiative", "ID"]:
            continue
            
        # Check if column has valid numeric values
        try:
            values = pd.to_numeric(df[col], errors="coerce")
            if not values.isna().all():  # If not all NaN
                # Get friendly name using nomenclature system
                friendly_name = clean_column_names([col])[0]
                numeric_cols.append(friendly_name)
        except Exception:
            continue
    
    return numeric_cols if numeric_cols else ["Accuracy (%)"]  # Fallback


def get_real_column_name(display_name: str) -> str:
    """Convert display name back to real column name."""
    from dashboard.components.shared.nomenclature import get_friendly_name
    
    # Try to find the original column name by reverse lookup
    # Since we don't have a direct reverse mapping in nomenclature,
    # we'll use a simplified approach for common columns
    common_mappings = {
        "Accuracy (%)": "Accuracy (%)",
        "Accuracy Max Value": "Accuracy_max_val",
        "Accuracy Min Value": "Accuracy_min_val", 
        "Spatial Resolution (m)": "Resolution",
        "Resolution Max Value": "Resolution_max_val",
        "Resolution Min Value": "Resolution_min_val",
        "Agricultural Classes": "Num_Agri_Classes",
        "Total Classes": "Classes",
        "Temporal Coverage": "Temporal_Coverage",
        "Spatial Coverage": "Spatial_Coverage",
        "Update Frequency": "Update_Frequency", 
        "Data Volume": "Data_Volume"
    }
    return common_mappings.get(display_name, display_name)
