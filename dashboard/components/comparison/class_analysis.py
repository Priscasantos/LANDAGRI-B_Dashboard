"""
Class Analysis Component
=======================

Componente para análise de classes e diversidade.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add scripts to path for imports
current_dir = Path(__file__).parent.parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import plotting functions
try:
    from scripts.plotting.generate_graphics import (
        plot_class_diversity_focus,
        plot_distribuicao_classes
    )
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    def plot_class_diversity_focus(df):
        fig = go.Figure()
        fig.add_annotation(text="Class diversity chart not available", showarrow=False)
        return fig
    
    def plot_distribuicao_classes(df):
        fig = go.Figure()
        fig.add_annotation(text="Class distribution chart not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise de classes e diversidade.
    
    Args:
        df: DataFrame com dados das iniciativas
        filters: Filtros aplicados
    """
    # Apply filters
    filtered_df = df.copy()
    if filters:
        if filters.get("countries") and "Country" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Country"].isin(filters["countries"])]
        if filters.get("types") and "Type" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Type"].isin(filters["types"])]
    
    if filtered_df.empty:
        st.warning("❌ Nenhum dado disponível com os filtros selecionados.")
        return
    
    # Create tabs for different class analyses
    tab1, tab2 = st.tabs(["🎯 Diversidade de Classes", "📊 Distribuição de Classes"])
    
    with tab1:
        st.markdown("#### Diversidade de Classes e Foco Agrícola")
        st.markdown("Compara o número total de classes versus o número de classes agrícolas específicas para cada iniciativa.")
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de diversidade de classes não pode ser carregado devido a erro de importação.")
        else:
            try:
                class_diversity_fig = plot_class_diversity_focus(filtered_df)
                st.plotly_chart(class_diversity_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de diversidade de classes: {e}")
        
        # Additional class analysis
        if "Classes" in filtered_df.columns and "Num_Agri_Classes" in filtered_df.columns:
            st.markdown("##### 📈 Estatísticas de Classes")
            
            # Convert to numeric for analysis
            classes_data = pd.to_numeric(filtered_df["Classes"], errors='coerce').dropna()
            agri_classes_data = pd.to_numeric(filtered_df["Num_Agri_Classes"], errors='coerce').dropna()
            
            if not classes_data.empty and not agri_classes_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Média de Classes Total", f"{classes_data.mean():.1f}")
                
                with col2:
                    st.metric("Média de Classes Agrícolas", f"{agri_classes_data.mean():.1f}")
                
                with col3:
                    st.metric("Máximo de Classes", f"{classes_data.max():.0f}")
                
                with col4:
                    ratio = (agri_classes_data.sum() / classes_data.sum() * 100) if classes_data.sum() > 0 else 0
                    st.metric("% Foco Agrícola", f"{ratio:.1f}%")
            else:
                st.info("Dados de classes não disponíveis para análise estatística.")
        else:
            st.info("Colunas de classes não encontradas para análise adicional.")
    
    with tab2:
        st.markdown("#### Distribuição do Número de Classes")
        st.markdown("Mostra a distribuição do número total de classes identificadas pelas iniciativas LULC selecionadas, colorido por tipo de iniciativa.")
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de distribuição de classes não pode ser carregado devido a erro de importação.")
        elif "Classes" not in filtered_df.columns:
            st.warning("A coluna 'Classes' não está disponível nos dados filtrados.")
        elif "Type" not in filtered_df.columns:
            st.warning("A coluna 'Type' não está disponível nos dados filtrados.")
        else:
            try:
                # Ensure the 'Classes' column is numeric for the histogram
                df_for_chart = filtered_df.copy()
                df_for_chart['Classes'] = pd.to_numeric(df_for_chart['Classes'], errors='coerce')
                df_for_chart = df_for_chart.dropna(subset=['Classes'])
                
                if not df_for_chart.empty:
                    fig_dist_classes = plot_distribuicao_classes(df_for_chart)
                    st.plotly_chart(fig_dist_classes, use_container_width=True)
                    
                    # Class distribution statistics table removed to reduce redundancy
                else:
                    st.info("Nenhum dado válido para 'Classes' após conversão numérica.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de distribuição de classes: {e}")
