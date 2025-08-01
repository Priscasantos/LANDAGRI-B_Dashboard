"""
Dual Bars Component - Detailed Analysis
=======================================

Componente para renderizar a aba de barras duplas na análise detalhada.
Contém o gráfico create_dual_bars_chart migrado do detailed_charts.py.

Author: Dashboard Iniciativas LULC
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


def render_dual_bars_tab(filtered_df: pd.DataFrame) -> None:
    """
    Renderizar aba de gráfico de barras para comparação detalhada.
    
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas selecionadas
    """
    st.markdown("#### 📊 Bar Chart Comparison")
    
    if filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa selecionada para comparação.")
        return
    
    if len(filtered_df) < 2:
        st.warning("⚠️ Selecione pelo menos 2 iniciativas para comparação.")
        return

    # Controls for 3 metrics
    st.markdown("**Select up to 3 metrics for comparison:**")
    col1, col2, col3 = st.columns(3)
    
    available_metrics = get_numeric_columns(filtered_df)
    
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
    Obter colunas numéricas do DataFrame para comparação com nomes melhorados.
    
    Args:
        df: DataFrame com dados das iniciativas
        
    Returns:
        Lista de nomes de colunas numéricas com labels melhorados
    """
    numeric_cols = []
    # Mapeamento de nomes reais para nomes mais legíveis
    column_mapping = {
        "Accuracy (%)": "Accuracy (%)",
        "Accuracy_max_val": "Accuracy Max Value", 
        "Accuracy_min_val": "Accuracy Min Value",
        "Resolution": "Resolution",
        "Resolution_max_val": "Resolution Max Value",
        "Resolution_min_val": "Resolution Min Value", 
        "Num_Agri_Classes": "N° Agricultural Classes",
        "Classes": "Total Classes",
        "Temporal_Coverage": "Temporal Coverage",
        "Spatial_Coverage": "Spatial Coverage", 
        "Update_Frequency": "Update Frequency",
        "Data_Volume": "Data Volume"
    }
    
    for real_col, display_name in column_mapping.items():
        if real_col in df.columns:
            # Verificar se a coluna tem valores numéricos válidos
            values = pd.to_numeric(df[real_col], errors="coerce")
            if not values.isna().all():  # Se não for tudo NaN
                numeric_cols.append(display_name)
    
    return numeric_cols if numeric_cols else ["Accuracy (%)"]  # Fallback


def get_real_column_name(display_name: str) -> str:
    """Converter nome de exibição de volta para nome real da coluna."""
    reverse_mapping = {
        "Accuracy (%)": "Accuracy (%)",
        "Accuracy Max Value": "Accuracy_max_val",
        "Accuracy Min Value": "Accuracy_min_val", 
        "Resolution": "Resolution",
        "Resolution Max Value": "Resolution_max_val",
        "Resolution Min Value": "Resolution_min_val",
        "N° Agricultural Classes": "Num_Agri_Classes",
        "Total Classes": "Classes",
        "Temporal Coverage": "Temporal_Coverage",
        "Spatial Coverage": "Spatial_Coverage",
        "Update Frequency": "Update_Frequency", 
        "Data Volume": "Data_Volume"
    }
    return reverse_mapping.get(display_name, display_name)
