"""
Gaps Analysis Component
----------------------
Exibe o gráfico de análise de lacunas temporais.
"""
import streamlit as st
import pandas as pd
from plotly import graph_objects as go

try:
    from scripts.plotting.charts.temporal_charts import plot_gaps_bar_chart
except ImportError:
    plot_gaps_bar_chart = None

def render_gaps_analysis(temporal_data):
    """Renderiza o gráfico de análise de lacunas e métricas relacionadas."""
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
    fig_gaps = None
    if plot_gaps_bar_chart:
        fig_gaps = plot_gaps_bar_chart(temporal_data)
    if fig_gaps is None:
        fig_gaps = create_comprehensive_gaps_chart(gaps_data)
    if fig_gaps:
        st.plotly_chart(fig_gaps, use_container_width=True)
    else:
        st.info("Could not generate gaps analysis chart.")
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

def create_comprehensive_gaps_chart(gaps_data):
    """Create comprehensive gaps chart with standardized dimensions (cópia da função original)."""
    try:
        if gaps_data.empty or "Display_Name" not in gaps_data.columns:
            return None
        
        # Ensure Anos_Faltando is numeric
        gaps_data["Anos_Faltando"] = pd.to_numeric(gaps_data["Anos_Faltando"], errors='coerce')
        gaps_data = gaps_data.dropna(subset=["Anos_Faltando"])
        
        if gaps_data.empty:
            return None
            
        gaps_data_sorted = gaps_data.sort_values("Anos_Faltando", ascending=True)
        fig = go.Figure()
        colors = []
        for missing in gaps_data_sorted["Anos_Faltando"]:
            if missing <= 2:
                colors.append("#4CAF50")
            elif missing <= 5:
                colors.append("#FF9800")
            else:
                colors.append("#F44336")
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
            height=500,
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
