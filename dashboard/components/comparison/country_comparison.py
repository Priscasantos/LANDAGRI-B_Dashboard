"""
Country Comparison Component
===========================

Componente para comparação entre países.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

import pandas as pd
import plotly.express as px
import streamlit as st


"""
Country Comparison Component
===========================

Componente para comparação entre países e análise de precisão global.

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
    from scripts.plotting.generate_graphics import plot_global_accuracy_comparison
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    def plot_global_accuracy_comparison(df):
        fig = go.Figure()
        fig.add_annotation(text="Global accuracy chart not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise comparativa por país e precisão global.
    
    Args:
        df: DataFrame com dados das iniciativas
        filters: Filtros aplicados
    """    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply country filter only if specific countries are selected
    if filters and filters.get("countries"):
        filtered_df = filtered_df[filtered_df["Country"].isin(filters["countries"])]
        
    # Apply type filter if specified
    if filters and filters.get("types"):
        filtered_df = filtered_df[filtered_df["Type"].isin(filters["types"])]

    if filtered_df.empty:
        st.warning("❌ Nenhum dado disponível com os filtros selecionados.")
        st.info("💡 Tente ajustar os filtros na barra lateral ou verificar se os dados contêm informações de país.")
        return
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["🌍 Análise por País", "🎯 Precisão Global"])
    
    with tab1:
        st.markdown("#### Distribuição de Iniciativas por País")
        
        # Verify Country column exists
        if "Country" not in filtered_df.columns:
            st.error("❌ Coluna 'Country' não encontrada nos dados.")
            st.info("Colunas disponíveis: " + ", ".join(filtered_df.columns))
            return

        # Country statistics
        country_stats = filtered_df["Country"].value_counts()
        
        if country_stats.empty:
            st.warning("❌ Nenhum país encontrado nos dados filtrados.")
            return
        
        # Bar chart
        fig = px.bar(
            x=country_stats.index,
            y=country_stats.values,
            title="Número de Iniciativas por País",
            labels={"x": "País", "y": "Número de Iniciativas"},
            color=country_stats.values,
            color_continuous_scale="viridis"
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.markdown("##### 📊 Resumo por País")
        
        summary_df = pd.DataFrame({
            "País": country_stats.index,
            "Iniciativas": country_stats.values,
            "Percentual": (country_stats.values / country_stats.sum() * 100).round(1)
        })
        
        # Add percentage format
        summary_df["Percentual"] = summary_df["Percentual"].apply(lambda x: f"{x}%")
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Additional statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Países", len(country_stats))
        
        with col2:
            st.metric("País com Mais Iniciativas", country_stats.index[0])
        
        with col3:
            st.metric("Máximo de Iniciativas", country_stats.values[0])
    
    with tab2:
        st.markdown("#### Comparação de Precisão Global")
        st.markdown("Compara a precisão global (em %) das iniciativas LULC selecionadas. Valores maiores indicam melhor precisão.")
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de precisão global não pode ser carregado devido a erro de importação.")
        else:
            try:
                global_acc_fig = plot_global_accuracy_comparison(filtered_df)
                st.plotly_chart(global_acc_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de precisão global: {e}")
        
        # Additional accuracy analysis
        if "Accuracy (%)" in filtered_df.columns:
            st.markdown("##### 📈 Estatísticas de Precisão")
            
            # Convert to numeric for analysis
            accuracy_data = pd.to_numeric(filtered_df["Accuracy (%)"], errors='coerce').dropna()
            
            if not accuracy_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Precisão Média", f"{accuracy_data.mean():.1f}%")
                
                with col2:
                    st.metric("Precisão Mediana", f"{accuracy_data.median():.1f}%")
                
                with col3:
                    st.metric("Precisão Máxima", f"{accuracy_data.max():.1f}%")
                
                with col4:
                    st.metric("Precisão Mínima", f"{accuracy_data.min():.1f}%")
                
                # Distribution histogram
                st.markdown("##### 📊 Distribuição de Precisão")
                fig_hist = px.histogram(
                    x=accuracy_data,
                    nbins=20,
                    title="Distribuição de Precisão Global (%)",
                    labels={"x": "Precisão (%)", "y": "Número de Iniciativas"}
                )
                fig_hist.update_layout(height=300)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Dados de precisão não disponíveis para análise estatística.")
        else:
            st.info("Coluna 'Accuracy (%)' não encontrada para análise adicional.")
