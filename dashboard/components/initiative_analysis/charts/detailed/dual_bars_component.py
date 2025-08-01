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
    Renderizar aba de barras duplas para comparação detalhada.
    
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas selecionadas
    """
    st.markdown("#### 📊 Comparação em Barras Duplas")
    
    if filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa selecionada para comparação.")
        return
    
    if len(filtered_df) < 2:
        st.warning("⚠️ Selecione pelo menos 2 iniciativas para comparação.")
        return
    
    # Controles de configuração
    col1, col2 = st.columns(2)
    
    with col1:
        metric1 = st.selectbox(
            "Primeira métrica:",
            options=get_numeric_columns(filtered_df),
            index=0,
            help="Selecione a primeira métrica para comparação"
        )
    
    with col2:
        available_metrics = [col for col in get_numeric_columns(filtered_df) if col != metric1]
        if available_metrics:
            metric2 = st.selectbox(
                "Segunda métrica:",
                options=available_metrics,
                index=0,
                help="Selecione a segunda métrica para comparação"
            )
        else:
            st.error("❌ Não há métricas suficientes para comparação dupla.")
            return
    
    # Configurações de visualização
    show_values = st.checkbox(
        "Mostrar valores nas barras",
        value=True,
        help="Exibir valores numéricos nas barras"
    )
    
    # Informações das métricas selecionadas
    st.markdown("**Métricas Selecionadas:**")
    metric_col1, metric_col2 = st.columns(2)
    
    with metric_col1:
        st.info(f"**{metric1}**")
        values1 = pd.to_numeric(filtered_df[metric1], errors="coerce")
        st.write(f"Média: {values1.mean():.2f}")
        st.write(f"Min-Max: {values1.min():.1f} - {values1.max():.1f}")
    
    with metric_col2:
        st.info(f"**{metric2}**")
        values2 = pd.to_numeric(filtered_df[metric2], errors="coerce")
        st.write(f"Média: {values2.mean():.2f}")
        st.write(f"Min-Max: {values2.min():.1f} - {values2.max():.1f}")
    
    # Gerar gráfico
    fig_dual_bars = create_dual_bars_chart(
        filtered_df, 
        metric1, 
        metric2, 
        show_values=show_values
    )
    
    if fig_dual_bars:
        st.plotly_chart(fig_dual_bars, use_container_width=True)
        
        # Download option
        st.download_button(
            label="📥 Download Dual Bars Chart",
            data=fig_dual_bars.to_html(),
            file_name="dual_bars_chart.html",
            mime="text/html"
        )
    else:
        st.error("❌ Erro ao gerar gráfico de barras duplas.")


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """
    Obter colunas numéricas do DataFrame para comparação.
    
    Args:
        df: DataFrame com dados das iniciativas
        
    Returns:
        Lista de nomes de colunas numéricas
    """
    numeric_cols = []
    potential_cols = [
        "Accuracy (%)", "Resolution", "Temporal_Coverage", 
        "Spatial_Coverage", "Update_Frequency", "Data_Volume"
    ]
    
    for col in potential_cols:
        if col in df.columns:
            # Verificar se a coluna tem valores numéricos válidos
            values = pd.to_numeric(df[col], errors="coerce")
            if not values.isna().all():
                numeric_cols.append(col)
    
    return numeric_cols if numeric_cols else ["Value"]


@smart_cache_data(ttl=300)
def create_dual_bars_chart(
    filtered_df: pd.DataFrame, 
    metric1: str, 
    metric2: str,
    show_values: bool = True
) -> go.Figure | None:
    """
    Criar gráfico de barras duplas para comparação de duas métricas.
    
    Args:
        filtered_df: DataFrame com dados filtrados
        metric1: Nome da primeira métrica
        metric2: Nome da segunda métrica
        show_values: Se deve mostrar valores nas barras
        
    Returns:
        Figura Plotly com gráfico de barras duplas ou None se erro
    """
    if filtered_df.empty or len(filtered_df) < 2:
        return None
    
    try:
        # Preparar dados
        initiatives = filtered_df.get("Display_Name", filtered_df.get("Name", range(len(filtered_df)))).tolist()
        values1 = pd.to_numeric(filtered_df[metric1], errors="coerce")
        values2 = pd.to_numeric(filtered_df[metric2], errors="coerce")
        
        # Verificar se há dados válidos
        if values1.isna().all() or values2.isna().all():
            return None
        
        # Criar figura
        fig = go.Figure()
        
        colors = get_chart_colors()
        
        # Adicionar primeira métrica
        fig.add_trace(go.Bar(
            name=metric1,
            x=initiatives,
            y=values1,
            marker_color=colors[0],
            text=values1.round(2) if show_values else None,
            textposition="auto",
            hovertemplate=f"<b>%{{x}}</b><br>" +
                         f"{metric1}: %{{y}}<br>" +
                         "<extra></extra>"
        ))
        
        # Adicionar segunda métrica  
        fig.add_trace(go.Bar(
            name=metric2,
            x=initiatives,
            y=values2,
            marker_color=colors[1],
            text=values2.round(2) if show_values else None,
            textposition="auto",
            hovertemplate=f"<b>%{{x}}</b><br>" +
                         f"{metric2}: %{{y}}<br>" +
                         "<extra></extra>"
        ))
        
        # Layout
        apply_standard_layout(
            fig,
            title=f"Comparação: {metric1} vs {metric2}",
            xaxis_title="Iniciativas",
            yaxis_title="Valores"
        )
        
        fig.update_layout(
            barmode="group",
            showlegend=True,
            height=500
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de barras duplas: {e}")
        return None
