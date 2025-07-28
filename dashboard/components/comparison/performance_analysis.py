"""
Performance Analysis Component
=============================

Componente para análise de performance normalizada.

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
    from scripts.plotting.generate_graphics import plot_normalized_performance_heatmap
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    def plot_normalized_performance_heatmap(df):
        fig = go.Figure()
        fig.add_annotation(text="Normalized performance heatmap not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise de performance normalizada.
    
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
    
    st.markdown("#### Heatmap de Performance Normalizada")
    st.markdown("Este heatmap exibe uma visão normalizada de várias métricas de performance em todas as iniciativas selecionadas. Os valores são escalonados para destacar a performance relativa dentro de cada métrica.")
    
    if not plotting_functions_loaded:
        st.warning("Heatmap de Performance Normalizada não pode ser carregado devido a erro de importação.")
        return
    
    try:
        fig_normalized_heatmap = plot_normalized_performance_heatmap(filtered_df)
        st.plotly_chart(fig_normalized_heatmap, use_container_width=True)
        
        # Additional performance analysis
        st.markdown("##### 📊 Análise de Performance Detalhada")
        
        # Identify numeric columns for performance analysis
        numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
        performance_cols = [col for col in numeric_cols if col in [
            'Accuracy (%)', 'Resolution', 'Classes', 'Num_Agri_Classes'
        ]]
        
        if performance_cols:
            # Calculate performance scores
            performance_data = []
            
            for _, row in filtered_df.iterrows():
                initiative_name = row.get('Display_Name', row.get('Name', 'Unknown'))
                performance_score = 0
                valid_metrics = 0
                
                for col in performance_cols:
                    value = pd.to_numeric(row[col], errors='coerce')
                    if not pd.isna(value):
                        # Normalize based on column type
                        if col == 'Resolution':
                            # Lower is better for resolution
                            max_res = filtered_df[col].max()
                            normalized = (max_res - value) / max_res if max_res > 0 else 0
                        else:
                            # Higher is better for other metrics
                            max_val = filtered_df[col].max()
                            normalized = value / max_val if max_val > 0 else 0
                        
                        performance_score += normalized
                        valid_metrics += 1
                
                if valid_metrics > 0:
                    avg_performance = (performance_score / valid_metrics) * 100
                    performance_data.append({
                        'Iniciativa': initiative_name,
                        'Score de Performance (%)': round(avg_performance, 1),
                        'Métricas Válidas': valid_metrics
                    })
            
            if performance_data:
                performance_df = pd.DataFrame(performance_data)
                performance_df = performance_df.sort_values('Score de Performance (%)', ascending=False)
                
                # Performance distribution
                st.markdown("##### 📊 Distribuição de Performance")
                
                fig_dist = px.histogram(
                    performance_df,
                    x='Score de Performance (%)',
                    nbins=20,
                    title="Distribuição dos Scores de Performance",
                    labels={'x': 'Score de Performance (%)', 'y': 'Número de Iniciativas'}
                )
                fig_dist.update_layout(height=300)
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Performance statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Performance Média", f"{performance_df['Score de Performance (%)'].mean():.1f}%")
                
                with col2:
                    st.metric("Performance Mediana", f"{performance_df['Score de Performance (%)'].median():.1f}%")
                
                with col3:
                    st.metric("Melhor Performance", f"{performance_df['Score de Performance (%)'].max():.1f}%")
                
                with col4:
                    st.metric("Pior Performance", f"{performance_df['Score de Performance (%)'].min():.1f}%")
            else:
                st.info("Não foi possível calcular scores de performance com os dados disponíveis.")
        else:
            st.info("Colunas de performance numérica não encontradas para análise detalhada.")
            
    except Exception as e:
        st.error(f"❌ Erro ao gerar análise de performance: {e}")
