"""
Temporal Comparison Component
============================

Componente para comparação temporal entre iniciativas.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

import pandas as pd
import plotly.express as px
import streamlit as st


"""
Temporal Comparison Component
============================

Componente para comparação temporal entre iniciativas.

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
    from scripts.plotting.generate_graphics import plot_temporal_evolution_frequency
    plotting_functions_loaded = True
except ImportError as e:
    st.warning(f"⚠️ Some plotting functions could not be imported: {e}")
    plotting_functions_loaded = False
    
    def plot_temporal_evolution_frequency(df):
        fig = go.Figure()
        fig.add_annotation(text="Temporal evolution chart not available", showarrow=False)
        return fig


def render(df: pd.DataFrame, filters: dict) -> None:
    """
    Renderiza análise comparativa temporal.
    
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
    
    # Create tabs for different temporal analyses
    tab1, tab2 = st.tabs(["📈 Evolução Temporal", "📊 Análise de Períodos"])
    
    with tab1:
        st.markdown("#### Evolução Temporal e Frequência de Atualização")
        st.markdown("Este gráfico de linha do tempo mostra o período operacional (ano de início ao fim) das iniciativas LULC selecionadas, colorido pela frequência de atualização.")
        
        if not plotting_functions_loaded:
            st.warning("Gráfico de evolução temporal não pode ser carregado devido a erro de importação.")
        else:
            try:
                temporal_evo_fig = plot_temporal_evolution_frequency(filtered_df)
                st.plotly_chart(temporal_evo_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar gráfico de evolução temporal: {e}")
    
    with tab2:
        st.markdown("#### Análise Básica de Períodos")
        
        # Find year columns
        year_columns = [col for col in filtered_df.columns if col.isdigit() and len(col) == 4]
        
        if not year_columns:
            st.info("Dados temporais não encontrados.")
            return
        
        # Apply year range filter if available
        if filters and filters.get("year_range"):
            start_year, end_year = filters["year_range"]
            year_columns = [col for col in year_columns if start_year <= int(col) <= end_year]
        
        # Count initiatives per year
        yearly_data = {}
        for year in sorted(year_columns):
            count = filtered_df[year].notna().sum()
            yearly_data[int(year)] = count
        
        if not yearly_data:
            st.info("Nenhum dado temporal disponível no período selecionado.")
            return
        
        # Line chart
        fig = px.line(
            x=list(yearly_data.keys()),
            y=list(yearly_data.values()),
            title="Evolução das Iniciativas ao Longo do Tempo",
            labels={"x": "Ano", "y": "Número de Iniciativas Ativas"},
            markers=True
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Temporal statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Período Total",
                f"{min(yearly_data.keys())} - {max(yearly_data.keys())}"
            )
        
        with col2:
            st.metric(
                "Pico de Atividade",
                max(yearly_data, key=yearly_data.get)
            )
        
        with col3:
            st.metric(
                "Máximo de Iniciativas",
                max(yearly_data.values())
            )
        
        # Additional temporal analysis
        st.markdown("##### 📈 Tendências Temporais")
        
        # Calculate year-over-year growth
        years = sorted(yearly_data.keys())
        if len(years) > 1:
            growth_data = []
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                prev_count = yearly_data[prev_year]
                curr_count = yearly_data[curr_year]
                
                if prev_count > 0:
                    growth_rate = ((curr_count - prev_count) / prev_count) * 100
                    growth_data.append({
                        'Ano': curr_year,
                        'Crescimento (%)': growth_rate
                    })
            
            if growth_data:
                growth_df = pd.DataFrame(growth_data)
                
                fig_growth = px.bar(
                    growth_df,
                    x='Ano',
                    y='Crescimento (%)',
                    title="Taxa de Crescimento Anual (%)",
                    color='Crescimento (%)',
                    color_continuous_scale="RdYlBu_r"
                )
                
                fig_growth.update_layout(height=300)
                st.plotly_chart(fig_growth, use_container_width=True)
        
        # Period analysis by initiative type
        if "Type" in filtered_df.columns:
            st.markdown("##### 🗂️ Análise por Tipo de Iniciativa")
            
            type_period_data = []
            for init_type in filtered_df["Type"].unique():
                type_df = filtered_df[filtered_df["Type"] == init_type]
                
                # Find active years for this type
                active_years = []
                for year in year_columns:
                    if type_df[year].notna().sum() > 0:
                        active_years.append(int(year))
                
                if active_years:
                    type_period_data.append({
                        'Tipo': init_type,
                        'Primeiro Ano': min(active_years),
                        'Último Ano': max(active_years),
                        'Duração (anos)': max(active_years) - min(active_years) + 1,
                        'Total de Iniciativas': len(type_df)
                    })
            
            # Temporal period details table removed to reduce redundancy
