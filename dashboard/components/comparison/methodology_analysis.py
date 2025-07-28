"""
Methodology Analysis Component
=============================

Componente para análise detalhada de metodologias.

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
        plot_distribuicao_metodologias,
        plot_acuracia_por_metodologia
    )
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    def plot_distribuicao_metodologias(method_counts):
        fig = go.Figure()
        fig.add_annotation(text="Methodology distribution chart not available", showarrow=False)
        return fig
    
    def plot_acuracia_por_metodologia(df):
        fig = go.Figure()
        fig.add_annotation(text="Accuracy by methodology chart not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise detalhada de metodologias.
    
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
    
    st.markdown("#### Análise Aprofundada de Metodologias")
    st.markdown("Explore a distribuição de metodologias e suas precisões associadas.")
    
    if not plotting_functions_loaded:
        st.warning("Gráficos de análise de metodologias não podem ser carregados devido a erro de importação.")
        return
    
    # Chart 1: Distribution of Methodologies
    st.markdown("##### Distribuição de Metodologias Utilizadas")
    
    if "Methodology" not in filtered_df.columns:
        st.warning("A coluna 'Methodology' não está disponível nos dados.")
        return
    
    try:
        method_counts = filtered_df['Methodology'].value_counts()
        if not method_counts.empty:
            fig_dist_meth = plot_distribuicao_metodologias(method_counts)
            st.plotly_chart(fig_dist_meth, use_container_width=True)
            
            # Show methodology statistics
            st.markdown("##### 📊 Estatísticas de Metodologias")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Metodologias", len(method_counts))
            
            with col2:
                st.metric("Metodologia Mais Comum", method_counts.index[0])
            
            with col3:
                st.metric("Uso da Metodologia Principal", f"{method_counts.iloc[0]} iniciativas")
            
            # Detailed methodology table
            methodology_df = pd.DataFrame({
                "Metodologia": method_counts.index,
                "Iniciativas": method_counts.values,
                "Percentual": (method_counts.values / method_counts.sum() * 100).round(1)
            })
            methodology_df["Percentual"] = methodology_df["Percentual"].apply(lambda x: f"{x}%")
        else:
            st.info("Nenhum dado de metodologia encontrado.")
    except Exception as e:
        st.error(f"❌ Erro ao gerar gráfico de distribuição de metodologias: {e}")
    
    st.markdown("---")
    
    # Chart 2: Accuracy by Methodology
    st.markdown("##### Precisão por Metodologia")
    
    required_cols = ["Methodology", "Accuracy (%)", "Type"]
    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
    
    if missing_cols:
        st.warning(f"As colunas {', '.join(missing_cols)} não estão disponíveis para análise de precisão por metodologia.")
        return
    
    try:
        # Ensure 'Accuracy (%)' is numeric
        df_for_acc_chart = filtered_df.copy()
        df_for_acc_chart['Accuracy (%)'] = pd.to_numeric(df_for_acc_chart['Accuracy (%)'], errors='coerce')
        df_for_acc_chart = df_for_acc_chart.dropna(subset=['Accuracy (%)', 'Methodology', 'Type'])

        if not df_for_acc_chart.empty:
            fig_acc_meth = plot_acuracia_por_metodologia(df_for_acc_chart)
            st.plotly_chart(fig_acc_meth, use_container_width=True)
            
            # Additional accuracy analysis
            st.markdown("##### 📈 Análise Detalhada de Precisão")
            
            # Group by methodology for statistics
            accuracy_by_method = df_for_acc_chart.groupby('Methodology')['Accuracy (%)'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(2)
            
            accuracy_by_method.columns = [
                'Qtd Iniciativas', 'Média (%)', 'Mediana (%)', 
                'Desvio Padrão', 'Mín (%)', 'Máx (%)'
            ]
            
            # Sort by mean accuracy descending
            accuracy_by_method = accuracy_by_method.sort_values('Média (%)', ascending=False)
            
            # Highlight best and worst performing methodologies
            if len(accuracy_by_method) > 1:
                best_method = accuracy_by_method.index[0]
                worst_method = accuracy_by_method.index[-1]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"🏆 **Melhor Metodologia**: {best_method}")
                    st.write(f"Precisão média: {accuracy_by_method.loc[best_method, 'Média (%)']}%")
                
                with col2:
                    st.info(f"📊 **Metodologia com Menor Precisão**: {worst_method}")
                    st.write(f"Precisão média: {accuracy_by_method.loc[worst_method, 'Média (%)']}%")
        else:
            st.info("Nenhum dado válido para análise de precisão por metodologia após limpeza dos dados.")
    except Exception as e:
        st.error(f"❌ Erro ao gerar análise de precisão por metodologia: {e}")
