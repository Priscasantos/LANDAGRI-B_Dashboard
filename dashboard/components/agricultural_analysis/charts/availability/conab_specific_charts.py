"""
CONAB Charts for Availability Module
===================================

CONAB-specific charts integrated into the availability analysis module.
Specialized visualizations for CONAB data quality and coverage analysis.

Author: Dashboard Iniciativas LULC
Date: 2025-08-07
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Optional
from ...agricultural_loader import safe_get_data, validate_data_structure


def create_conab_spatial_coverage_chart(conab_data: dict) -> Optional[go.Figure]:
    """
    Creates spatial coverage chart for CONAB data.
    
    Args:
        conab_data: Detailed CONAB data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        if not validate_data_structure(conab_data):
            return None

        # Map states to regions
        state_to_region = {
            'Acre': 'Norte', 'Amapá': 'Norte', 'Amazonas': 'Norte', 'Pará': 'Norte',
            'Rondônia': 'Norte', 'Roraima': 'Norte', 'Tocantins': 'Norte',
            'Alagoas': 'Nordeste', 'Bahia': 'Nordeste', 'Ceará': 'Nordeste', 
            'Maranhão': 'Nordeste', 'Paraíba': 'Nordeste', 'Pernambuco': 'Nordeste',
            'Piauí': 'Nordeste', 'Rio Grande do Norte': 'Nordeste', 'Sergipe': 'Nordeste',
            'Distrito Federal': 'Centro-Oeste', 'Goiás': 'Centro-Oeste', 
            'Mato Grosso': 'Centro-Oeste', 'Mato Grosso do Sul': 'Centro-Oeste',
            'Espírito Santo': 'Sudeste', 'Minas Gerais': 'Sudeste', 
            'Rio de Janeiro': 'Sudeste', 'São Paulo': 'Sudeste',
            'Paraná': 'Sul', 'Rio Grande do Sul': 'Sul', 'Santa Catarina': 'Sul'
        }

        # Count coverage by region
        region_coverage = {}
        for initiative in conab_data.values():
            state = safe_get_data(initiative, 'state', '')
            region = state_to_region.get(state, 'Indefinido')
            region_coverage[region] = region_coverage.get(region, 0) + 1

        if not region_coverage:
            return None

        # Create pie chart
        fig = px.pie(
            values=list(region_coverage.values()),
            names=list(region_coverage.keys()),
            title="🌍 Cobertura Espacial CONAB por Região"
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de cobertura espacial: {e}")
        return None


def create_conab_quality_metrics_chart(conab_data: dict) -> Optional[go.Figure]:
    """
    Creates quality metrics chart for CONAB data.
    
    Args:
        conab_data: Detailed CONAB data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        if not validate_data_structure(conab_data):
            return None

        # Calculate quality metrics
        quality_metrics = {
            'Completude de Dados': 0.0,
            'Consistência Temporal': 0.0,
            'Cobertura Geográfica': 0.0,
            'Diversidade de Culturas': 0.0
        }

        total_initiatives = len(conab_data)
        states_covered = set()
        crops_covered = set()
        temporal_consistent = 0

        for initiative in conab_data.values():
            # Completeness
            fields_present = sum([
                bool(safe_get_data(initiative, 'state')),
                bool(safe_get_data(initiative, 'crop_type')),
                bool(safe_get_data(initiative, 'start_year')),
                bool(safe_get_data(initiative, 'methodology'))
            ])
            quality_metrics['Completude de Dados'] += fields_present / 4

            # Geographic coverage
            state = safe_get_data(initiative, 'state')
            if state:
                states_covered.add(state)

            # Crop diversity
            crop_type = safe_get_data(initiative, 'crop_type')
            if crop_type:
                crops_covered.add(crop_type)

            # Temporal consistency
            start_year = safe_get_data(initiative, 'start_year')
            end_year = safe_get_data(initiative, 'end_year')
            if start_year and (not end_year or end_year >= start_year):
                temporal_consistent += 1

        # Normalize metrics
        quality_metrics['Completude de Dados'] = (quality_metrics['Completude de Dados'] / total_initiatives) * 100
        quality_metrics['Consistência Temporal'] = (temporal_consistent / total_initiatives) * 100
        quality_metrics['Cobertura Geográfica'] = (len(states_covered) / 27) * 100  # 27 Brazilian states
        quality_metrics['Diversidade de Culturas'] = min((len(crops_covered) / 10) * 100, 100)  # Max 10 expected crops

        # Create polar chart
        categories = list(quality_metrics.keys())
        values = list(quality_metrics.values())

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Métricas de Qualidade',
            line={'color': 'rgb(90, 171, 71)', 'width': 2},
            fillcolor='rgba(90, 171, 71, 0.3)'
        ))

        fig.update_layout(
            polar={
                'radialaxis': {
                    'visible': True,
                    'range': [0, 100]
                }
            },
            title="📊 Métricas de Qualidade CONAB (%)",
            height=500
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar métricas de qualidade CONAB: {e}")
        return None


def create_conab_crop_distribution_chart(conab_data: dict) -> Optional[go.Figure]:
    """
    Creates crop distribution chart for CONAB data.
    
    Args:
        conab_data: Detailed CONAB data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        if not validate_data_structure(conab_data):
            return None

        # Extract crop types
        crop_types = []
        for initiative in conab_data.values():
            crop_type = safe_get_data(initiative, 'crop_type', 'Indefinido')
            crop_types.append(crop_type)

        if not crop_types:
            return None

        # Count frequency by crop type
        crop_counts = pd.Series(crop_types).value_counts()

        # Create horizontal bar chart
        fig = px.bar(
            x=crop_counts.values,
            y=crop_counts.index,
            orientation='h',
            title="🌾 Distribuição de Culturas CONAB",
            labels={'x': 'Número de Iniciativas', 'y': 'Tipo de Cultura'}
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de distribuição de culturas: {e}")
        return None


def render_conab_charts_tab(conab_data: dict) -> None:
    """
    Render CONAB charts in organized tabs.
    
    Parameters:
    -----------
    conab_data : dict
        CONAB data dictionary
        
    Returns:
    --------
    None
        Renders directly in Streamlit
    """
    if not conab_data:
        st.info("📊 Dados CONAB não disponíveis para análise")
        return
    
    st.markdown("### 📊 Análises Específicas CONAB")
    
    # Create tabs for different CONAB analyses
    tab1, tab2, tab3 = st.tabs(["🌍 Cobertura", "📊 Qualidade", "🌾 Culturas"])
    
    with tab1:
        st.markdown("#### 🌍 Cobertura Espacial CONAB")
        spatial_fig = create_conab_spatial_coverage_chart(conab_data)
        if spatial_fig:
            st.plotly_chart(spatial_fig, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para análise de cobertura espacial")
    
    with tab2:
        st.markdown("#### 📊 Métricas de Qualidade")
        quality_fig = create_conab_quality_metrics_chart(conab_data)
        if quality_fig:
            st.plotly_chart(quality_fig, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para análise de qualidade")
    
    with tab3:
        st.markdown("#### 🌾 Distribuição de Culturas")
        crop_fig = create_conab_crop_distribution_chart(conab_data)
        if crop_fig:
            st.plotly_chart(crop_fig, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para análise de culturas")
