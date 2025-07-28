"""
Sensor Comparison Component
==========================

Componente para comparação entre sensores e análise de resolução espacial.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

import sys
import json
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
        plot_spatial_resolution_comparison,
        plot_classification_methodology,
        plot_resolution_vs_launch_year,
        plot_initiatives_by_resolution_category,
        plot_resolution_coverage_heatmap,
        plot_resolution_by_sensor_family,
        plot_resolution_slopegraph,
    )
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    # Define placeholders
    def plot_spatial_resolution_comparison(df):
        fig = go.Figure()
        fig.add_annotation(text="Spatial resolution chart not available", showarrow=False)
        return fig
    
    def plot_classification_methodology(df, chart_type='pie'):
        fig = go.Figure()
        fig.add_annotation(text="Classification methodology chart not available", showarrow=False)
        return fig
    
    def plot_resolution_vs_launch_year(df):
        fig = go.Figure()
        fig.add_annotation(text="Resolution vs launch year chart not available", showarrow=False)
        return fig
    
    def plot_initiatives_by_resolution_category(df):
        fig = go.Figure()
        fig.add_annotation(text="Resolution category chart not available", showarrow=False)
        return fig
    
    def plot_resolution_coverage_heatmap(df):
        fig = go.Figure()
        fig.add_annotation(text="Resolution coverage heatmap not available", showarrow=False)
        return fig
    
    def plot_resolution_by_sensor_family(df, sensors_meta):
        fig = go.Figure()
        fig.add_annotation(text="Resolution by sensor family chart not available", showarrow=False)
        return fig
    
    def plot_resolution_slopegraph(df, sensors_meta):
        fig = go.Figure()
        fig.add_annotation(text="Resolution slopegraph not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise comparativa por sensor e resolução espacial.
    
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
    
    # Create tabs for different sensor analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📡 Resolução Espacial", 
        "🔬 Metodologias", 
        "📊 Análise Avançada", 
        "🛰️ Uso de Sensores"
    ])
    
    with tab1:
        st.markdown("#### Comparação de Resolução Espacial")
        st.markdown("Compara a resolução espacial (em metros) das iniciativas LULC selecionadas. Valores menores indicam resolução mais fina (melhor).")
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de resolução espacial não pode ser carregado devido a erro de importação.")
        else:
            try:
                spatial_res_fig = plot_spatial_resolution_comparison(filtered_df)
                st.plotly_chart(spatial_res_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de resolução espacial: {e}")
    
    with tab2:
        st.markdown("#### Distribuição de Metodologias de Classificação")
        st.markdown("Mostra a distribuição das diferentes metodologias de classificação utilizadas nas iniciativas selecionadas.")
        
        chart_type = st.radio(
            "Selecione o tipo de gráfico:",
            ('Gráfico de Pizza', 'Gráfico de Barras'),
            key='methodology_chart_type_sensor'
        )
        chart_type_param = 'pie' if chart_type == 'Gráfico de Pizza' else 'bar'
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de metodologias não pode ser carregado devido a erro de importação.")
        else:
            try:
                methodology_fig = plot_classification_methodology(filtered_df, chart_type=chart_type_param)
                st.plotly_chart(methodology_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de metodologias: {e}")
    
    with tab3:
        st.markdown("#### Análise Avançada de Resolução")
        st.markdown("Análise aprofundada das características de resolução espacial, incluindo evolução, distribuição por sensor e relação com outros fatores.")
        
        if not plotting_functions_loaded:
            st.warning("Gráficos de análise avançada não podem ser carregados devido a erro de importação.")
        else:
            # Load sensor metadata
            sensors_data_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
            if 'sensors_meta' not in st.session_state:
                try:
                    with open(sensors_data_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Basic comment removal for JSONC
                        import re
                        content_no_comments = re.sub(r"//.*", "", content)
                        content_no_comments = re.sub(r"/\*.*?\*/", "", content_no_comments, flags=re.DOTALL)
                        st.session_state.sensors_meta = json.loads(content_no_comments)
                except Exception as e_sensor_load:
                    st.warning(f"⚠️ Erro ao carregar metadados de sensores: {e_sensor_load}")
                    st.session_state.sensors_meta = {}
            
            sensors_meta_data = st.session_state.get('sensors_meta', {})
            
            # Resolution vs. Launch Year
            st.markdown("##### Resolução vs. Ano de Lançamento")
            try:
                fig_res_launch = plot_resolution_vs_launch_year(filtered_df)
                st.plotly_chart(fig_res_launch, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico 'Resolução vs. Ano de Lançamento': {e}")
            
            # Initiatives by Resolution Category
            st.markdown("##### Iniciativas por Categoria de Resolução")
            try:
                fig_res_cat = plot_initiatives_by_resolution_category(filtered_df)
                st.plotly_chart(fig_res_cat, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico 'Iniciativas por Categoria de Resolução': {e}")
            
            # Resolution vs. Coverage Type Heatmap
            st.markdown("##### Heatmap: Resolução vs. Tipo de Cobertura")
            try:
                fig_res_heatmap = plot_resolution_coverage_heatmap(filtered_df)
                st.plotly_chart(fig_res_heatmap, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar heatmap de resolução vs. cobertura: {e}")
            
            # Charts requiring sensor metadata
            if sensors_meta_data:
                st.markdown("##### Distribuição de Resolução por Família de Sensores")
                try:
                    fig_res_sensor = plot_resolution_by_sensor_family(filtered_df, sensors_meta_data)
                    st.plotly_chart(fig_res_sensor, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Erro ao gerar gráfico 'Resolução por Família de Sensores': {e}")
                
                st.markdown("##### Melhoria de Resolução ao Longo do Tempo (Slopegraph)")
                try:
                    fig_res_slope = plot_resolution_slopegraph(filtered_df, sensors_meta_data)
                    st.plotly_chart(fig_res_slope, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Erro ao gerar slopegraph de resolução: {e}")
            else:
                st.info("Metadados de sensores não disponíveis para gráficos avançados.")
    
    with tab4:
        st.markdown("#### Uso de Sensores")
        st.markdown("Análise tradicional do uso de sensores nas iniciativas selecionadas.")
        
        # Original sensor usage analysis
        sensor_columns = [col for col in filtered_df.columns if "sensor" in col.lower()]
        
        if not sensor_columns:
            st.info("Dados de sensores não encontrados.")
            return
        
        # Count sensor usage
        sensor_usage = {}
        for col in sensor_columns:
            if col in filtered_df.columns:
                count = filtered_df[col].notna().sum()
                if count > 0:
                    sensor_name = col.replace("_", " ").title().replace("Sensor", "").strip()
                    sensor_usage[sensor_name] = count
        
        if not sensor_usage:
            st.info("Nenhum sensor em uso nas iniciativas filtradas.")
            return
        
        # Pie chart
        fig = px.pie(
            values=list(sensor_usage.values()),
            names=list(sensor_usage.keys()),
            title="Distribuição de Uso de Sensores"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        # Sensor details removed to reduce redundancy
