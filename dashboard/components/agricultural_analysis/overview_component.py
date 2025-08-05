"""
Overview Component - Agriculture Analysis
=======================================

Componente para renderizar visão geral dos dados de agricultura.
Inclui métricas principais, estatísticas e visualizações gerais.
Integrado com gráficos aprimorados baseados em FAO GIEWS e AntV AVA.

Author: Dashboard Iniciativas LULC
Date: 2025-01-17
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.shared.cache import smart_cache_data
from dashboard.components.shared.chart_core import apply_standard_layout, get_chart_colors

# Import dos novos gráficos aprimorados
try:
    from dashboard.components.agricultural_analysis.enhanced_charts import render_enhanced_agriculture_charts
    ENHANCED_CHARTS_AVAILABLE = True
except ImportError:
    ENHANCED_CHARTS_AVAILABLE = False


def render_agriculture_overview(filtered_df: pd.DataFrame | None = None) -> None:
    """
    Renderizar página de overview de agricultura brasileira usando dados CONAB.
    
    Args:
        filtered_df: DataFrame filtrado com dados das iniciativas CONAB
    """
    st.title("🌾 Agriculture Analysis - Overview Brasil")
    
    if filtered_df is None or filtered_df.empty:
        st.warning("⚠️ Nenhum dado de agricultura CONAB disponível.")
        return
    
    # Informações sobre fonte dos dados
    if 'Provider' in filtered_df.columns:
        provider = filtered_df['Provider'].iloc[0]
        data_source = filtered_df.get('Data_Source', ['CONAB']).iloc[0] if 'Data_Source' in filtered_df.columns else "CONAB"
        
        st.info(f"""
        📊 **Fonte dos Dados:** {provider}  
        🔗 **Sistema:** {data_source}  
        🇧🇷 **Cobertura:** Brasil (Estados e Cultivos)  
        📅 **Última Atualização:** {filtered_df['Year'].max()} (dados disponíveis)
        """)
    
    # Métricas principais
    render_key_metrics(filtered_df)
    
    # Distribuição por tipo de cultivo
    render_crop_distribution(filtered_df)
    
    # Evolução temporal
    render_temporal_evolution(filtered_df)
    
    # Análise de cobertura geográfica brasileira
    render_geographic_coverage(filtered_df)
    
    # Nova análise: Cobertura de cultivos por estado
    render_crop_coverage_by_state(filtered_df)


def render_key_metrics(df: pd.DataFrame) -> None:
    """Renderizar métricas principais de agricultura."""
    st.markdown("## 📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_initiatives = len(df)
        st.metric(
            label="Total de Iniciativas",
            value=total_initiatives,
            delta=None
        )
    
    with col2:
        # Calcular total de classes agrícolas
        if 'Num_Agri_Classes' in df.columns:
            total_agri_classes = df['Num_Agri_Classes'].sum()
            avg_classes = df['Num_Agri_Classes'].mean()
        else:
            total_agri_classes = 0
            avg_classes = 0
        
        st.metric(
            label="Classes Agrícolas (Total)",
            value=int(total_agri_classes) if total_agri_classes else "N/A",
            delta=f"Média: {avg_classes:.1f}" if avg_classes else None
        )
    
    with col3:
        # Calcular cobertura temporal média
        if 'available_years' in df.columns or 'Available_Years_List' in df.columns:
            years_col = 'available_years' if 'available_years' in df.columns else 'Available_Years_List'
            years_data = df[years_col].dropna()
            if not years_data.empty:
                total_years = sum(len(years) if isinstance(years, list) else 0 for years in years_data)
                avg_coverage = total_years / len(years_data) if years_data.size > 0 else 0
            else:
                avg_coverage = 0
        else:
            avg_coverage = 0
        
        st.metric(
            label="Cobertura Temporal Média",
            value=f"{avg_coverage:.1f} anos" if avg_coverage else "N/A",
            delta=None
        )
    
    with col4:
        # Calcular acurácia média
        accuracy_cols = [col for col in df.columns if 'Accuracy' in col and '%' in col]
        if accuracy_cols:
            avg_accuracy = df[accuracy_cols[0]].mean()
            st.metric(
                label="Acurácia Média",
                value=f"{avg_accuracy:.1f}%" if pd.notna(avg_accuracy) else "N/A",
                delta=None
            )
        else:
            st.metric(label="Acurácia Média", value="N/A", delta=None)


def render_crop_distribution(df: pd.DataFrame) -> None:
    """Renderizar distribuição por tipos de cultivo."""
    st.markdown("## 🌱 Distribuição por Cultivos")
    
    # Verificar se existem dados de classes agrícolas
    if 'Agricultural_Class_Legend' in df.columns:
        crop_data = analyze_crop_classes(df)
        
        if not crop_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de pizza
                fig_pie = create_crop_pie_chart(crop_data)
                if fig_pie:
                    st.plotly_chart(fig_pie, use_container_width=True, key="crop_distribution_pie")
            
            with col2:
                # Gráfico de barras
                fig_bar = create_crop_bar_chart(crop_data)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True, key="crop_distribution_bar")
        else:
            st.info("ℹ️ Dados detalhados de classes agrícolas não disponíveis.")
    else:
        st.info("ℹ️ Dados de classificação agrícola não disponíveis.")


def render_temporal_evolution(df: pd.DataFrame) -> None:
    """Renderizar evolução temporal das iniciativas agrícolas."""
    st.markdown("## 📈 Evolução Temporal")
    
    temporal_data = prepare_temporal_data(df)
    
    if not temporal_data.empty:
        fig_temporal = create_temporal_chart(temporal_data)
        if fig_temporal:
            st.plotly_chart(fig_temporal, use_container_width=True, key="agriculture_temporal_evolution")
        
        # Estatísticas temporais
        with st.expander("📊 Estatísticas Temporais"):
            render_temporal_stats(temporal_data, df)
    else:
        st.info("ℹ️ Dados temporais não disponíveis para análise.")


def render_geographic_coverage(df: pd.DataFrame) -> None:
    """Renderizar análise de cobertura geográfica brasileira usando dados CONAB."""
    st.markdown("## 🗺️ Cobertura Geográfica - Brasil")
    
    # Analisar cobertura por estado brasileiro se disponível
    if 'State' in df.columns and 'Region' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise por estado
            st.markdown("### Distribuição por Estado")
            state_stats = df['State'].value_counts()
            
            fig_state = px.bar(
                x=state_stats.values,
                y=state_stats.index,
                orientation='h',
                title="Iniciativas por Estado Brasileiro",
                labels={'x': 'Número de Iniciativas', 'y': 'Estado'},
                color=state_stats.values,
                color_continuous_scale='viridis'
            )
            apply_standard_layout(fig_state)
            st.plotly_chart(fig_state, use_container_width=True, key="state_distribution")
        
        with col2:
            # Análise por região
            st.markdown("### Distribuição por Região")
            region_stats = df['Region'].value_counts()
            
            fig_region = px.pie(
                values=region_stats.values,
                names=region_stats.index,
                title="Distribuição por Região Brasileira",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            apply_standard_layout(fig_region)
            st.plotly_chart(fig_region, use_container_width=True, key="region_distribution")
        
        # Tabela detalhada de estatísticas geográficas
        st.markdown("### Estatísticas Detalhadas por Estado")
        
        # Criar tabela agregada por estado
        state_summary = df.groupby(['State', 'Region']).agg({
            'Crop': 'nunique',
            'Year': lambda x: f"{x.min()}-{x.max()}" if x.min() != x.max() else str(x.min()),
            'Overall_Accuracy': 'mean'
        }).reset_index()
        
        state_summary.columns = ['Estado', 'Região', 'Cultivos', 'Período', 'Acurácia Média (%)']
        state_summary['Acurácia Média (%)'] = state_summary['Acurácia Média (%)'].round(1)
        
        st.dataframe(
            state_summary.sort_values('Cultivos', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
    elif 'State_Code' in df.columns:
        # Fallback para código de estado se nome completo não estiver disponível
        st.markdown("### Distribuição por Código de Estado")
        state_code_stats = df['State_Code'].value_counts()
        
        fig_code = px.bar(
            x=state_code_stats.values,
            y=state_code_stats.index,
            orientation='h',
            title="Iniciativas por Código de Estado",
            labels={'x': 'Número de Iniciativas', 'y': 'Código do Estado'}
        )
        apply_standard_layout(fig_code)
        st.plotly_chart(fig_code, use_container_width=True, key="state_code_distribution")
        
        # Tabela de estatísticas por código
        total_sum = int(state_code_stats.sum())
        st.dataframe(
            pd.DataFrame({
                'Código do Estado': state_code_stats.index,
                'Iniciativas': state_code_stats.values,
                'Percentual': (state_code_stats.values / total_sum * 100).round(1)
            }),
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.info("ℹ️ Dados de localização geográfica brasileira não disponíveis.")
        
        # Mostrar informações sobre cobertura do CONAB se disponível
        if 'Coverage' in df.columns:
            coverage_info = df['Coverage'].iloc[0] if not df.empty else "N/A"
            provider_info = df['Provider'].iloc[0] if 'Provider' in df.columns and not df.empty else "N/A"
            
            st.info(f"""
            📍 **Informações de Cobertura Disponíveis:**
            - **Cobertura:** {coverage_info}
            - **Provedor:** {provider_info}
            - **Registros:** {len(df)} iniciativas agrícolas
            """)


# Adicionar nova função para análise de cobertura de cultivos por estado
def render_crop_coverage_by_state(df: pd.DataFrame) -> None:
    """Renderizar análise de cobertura de cultivos por estado brasileiro."""
    if 'State' in df.columns and 'Crop' in df.columns:
        st.markdown("### 🌾 Cobertura de Cultivos por Estado")
        
        # Criar matriz de cultivos por estado
        crop_state_matrix = df.groupby(['State', 'Crop']).size().unstack(fill_value=0)
        
        if not crop_state_matrix.empty:
            # Heatmap de cultivos por estado
            fig_heatmap = px.imshow(
                crop_state_matrix.values,
                x=crop_state_matrix.columns,
                y=crop_state_matrix.index,
                color_continuous_scale='viridis',
                title="Matriz de Cultivos por Estado",
                labels={'color': 'Número de Iniciativas'}
            )
            
            fig_heatmap.update_layout(
                xaxis_title="Tipos de Cultivo",
                yaxis_title="Estados",
                height=max(400, len(crop_state_matrix.index) * 25)
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True, key="crop_state_heatmap")


@smart_cache_data(ttl=300)
def analyze_crop_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Analisar e processar dados de classes de cultivo."""
    crop_data = []
    
    for _, row in df.iterrows():
        legend = row.get('Agricultural_Class_Legend', '')
        if pd.notna(legend) and legend:
            # Processar legenda (assumindo formato separado por vírgula)
            crops = [crop.strip() for crop in str(legend).split(',')]
            for crop in crops:
                if crop:
                    crop_data.append({
                        'Crop': crop,
                        'Initiative': row.get('Display_Name', row.get('Name', 'Unknown')),
                        'Count': 1
                    })
    
    if crop_data:
        crop_df = pd.DataFrame(crop_data)
        return crop_df.groupby('Crop').agg({
            'Count': 'sum',
            'Initiative': 'nunique'
        }).reset_index()
    
    return pd.DataFrame()


@smart_cache_data(ttl=300)
def create_crop_pie_chart(crop_data: pd.DataFrame) -> go.Figure:
    """Criar gráfico de pizza para distribuição de cultivos."""
    if crop_data.empty:
        return None
    
    colors = get_chart_colors()
    
    fig = go.Figure(data=[go.Pie(
        labels=crop_data['Crop'],
        values=crop_data['Count'],
        marker={"colors": colors[:len(crop_data)]},
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    apply_standard_layout(fig, title="Distribuição de Cultivos")
    return fig


@smart_cache_data(ttl=300)
def create_crop_bar_chart(crop_data: pd.DataFrame) -> go.Figure:
    """Criar gráfico de barras para cultivos."""
    if crop_data.empty:
        return None
    
    # Ordenar por contagem
    crop_data_sorted = crop_data.sort_values('Count', ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        x=crop_data_sorted['Count'],
        y=crop_data_sorted['Crop'],
        orientation='h',
        marker_color=get_chart_colors()[0],
        text=crop_data_sorted['Count'],
        textposition='outside'
    )])
    
    apply_standard_layout(fig,
                         title="Ranking de Cultivos",
                         xaxis_title="Número de Iniciativas",
                         yaxis_title="Tipo de Cultivo")
    return fig


@smart_cache_data(ttl=300)
def prepare_temporal_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preparar dados temporais para análise."""
    temporal_data = []
    
    years_col = None
    for col in ['available_years', 'Available_Years_List', 'Available_Years']:
        if col in df.columns:
            years_col = col
            break
    
    if years_col:
        for _, row in df.iterrows():
            years = row.get(years_col, [])
            if isinstance(years, list) and years:
                for year in years:
                    temporal_data.append({
                        'Year': year,
                        'Initiative': row.get('Display_Name', row.get('Name', 'Unknown')),
                        'Type': row.get('Type', 'Unknown')
                    })
    
    if temporal_data:
        return pd.DataFrame(temporal_data)
    
    return pd.DataFrame()


@smart_cache_data(ttl=300)
def create_temporal_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """Criar gráfico de evolução temporal."""
    if temporal_data.empty:
        return None
    
    # Agrupar por ano
    yearly_counts = temporal_data.groupby('Year').size().reset_index()
    yearly_counts.columns = ['Year', 'Count']
    yearly_counts = yearly_counts.sort_values('Year')
    
    fig = go.Figure()
    
    # Linha principal
    fig.add_trace(go.Scatter(
        x=yearly_counts['Year'],
        y=yearly_counts['Count'],
        mode='lines+markers',
        name='Iniciativas',
        line={"color": get_chart_colors()[0], "width": 3},
        marker={"size": 8}
    ))
    
    apply_standard_layout(fig,
                         title="Evolução Temporal das Iniciativas Agrícolas",
                         xaxis_title="Ano",
                         yaxis_title="Número de Iniciativas")
    return fig


def render_temporal_stats(temporal_data: pd.DataFrame, filtered_df: pd.DataFrame | None = None) -> None:
    """Renderizar estatísticas temporais e gráficos aprimorados."""
    if temporal_data.empty:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_year = temporal_data['Year'].min()
        max_year = temporal_data['Year'].max()
        st.metric("Período Coberto", f"{min_year} - {max_year}")
    
    with col2:
        total_years = len(temporal_data['Year'].unique())
        st.metric("Anos com Dados", total_years)
    
    with col3:
        avg_per_year = temporal_data.groupby('Year').size().mean()
        st.metric("Média de Iniciativas/Ano", f"{avg_per_year:.1f}")
    
    # Adicionar gráficos aprimorados se disponíveis
    if ENHANCED_CHARTS_AVAILABLE and filtered_df is not None and not filtered_df.empty:
        st.markdown("---")
        render_enhanced_agriculture_charts(filtered_df)
