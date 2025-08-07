"""
CONAB Charts Module
==================

Módulo de gráficos específicos para dados CONAB.
Implementa visualizações especializadas para análise de qualidade e metodologia.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional, Any
import numpy as np


def plot_conab_spatial_coverage(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de cobertura espacial dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Mapeia estados para regiões
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

        # Conta cobertura por região
        region_coverage = {}
        for initiative in conab_data.values():
            state = initiative.get('state', '')
            region = state_to_region.get(state, 'Indefinido')
            region_coverage[region] = region_coverage.get(region, 0) + 1

        if not region_coverage:
            return None

        # Cria gráfico de pizza
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


def plot_conab_temporal_coverage(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de cobertura temporal dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Extrai anos dos dados
        years = []
        for initiative in conab_data.values():
            start_year = initiative.get('start_year')
            end_year = initiative.get('end_year')
            
            if start_year:
                years.append(start_year)
            if end_year and end_year != start_year:
                years.append(end_year)

        if not years:
            return None

        # Conta frequência por ano
        year_counts = pd.Series(years).value_counts().sort_index()

        # Cria gráfico de linha
        fig = px.line(
            x=year_counts.index,
            y=year_counts.values,
            title="📊 Cobertura Temporal CONAB",
            labels={'x': 'Ano', 'y': 'Número de Iniciativas'}
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de cobertura temporal: {e}")
        return None


def plot_conab_crop_diversity(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de diversidade de culturas nos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Extrai tipos de cultura
        crop_types = []
        for initiative in conab_data.values():
            crop_type = initiative.get('crop_type', 'Indefinido')
            crop_types.append(crop_type)

        if not crop_types:
            return None

        # Conta frequência por tipo de cultura
        crop_counts = pd.Series(crop_types).value_counts()

        # Cria gráfico de barras horizontais
        fig = px.bar(
            x=crop_counts.values,
            y=crop_counts.index,
            orientation='h',
            title="🌾 Diversidade de Culturas CONAB",
            labels={'x': 'Número de Iniciativas', 'y': 'Tipo de Cultura'}
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de diversidade de culturas: {e}")
        return None


def plot_conab_spatial_temporal_distribution(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de distribuição espaço-temporal dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Mapeia estados para regiões
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

        # Prepara dados para distribuição
        distribution_data = []
        for initiative in conab_data.values():
            state = initiative.get('state', '')
            region = state_to_region.get(state, 'Indefinido')
            start_year = initiative.get('start_year')
            
            if start_year:
                distribution_data.append({
                    'Região': region,
                    'Ano': start_year,
                    'Estado': state
                })

        if not distribution_data:
            return None

        df = pd.DataFrame(distribution_data)
        
        # Agrupa por região e ano
        df_grouped = df.groupby(['Região', 'Ano']).size().reset_index(name='Contagem')

        # Cria heatmap
        fig = px.density_heatmap(
            df_grouped,
            x='Ano',
            y='Região',
            z='Contagem',
            title="🗺️ Distribuição Espaço-Temporal CONAB",
            color_continuous_scale='Viridis'
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de distribuição espaço-temporal: {e}")
        return None


def plot_conab_quality_metrics(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de métricas de qualidade dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Calcula métricas de qualidade
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
            # Completude
            fields_present = sum([
                bool(initiative.get('state')),
                bool(initiative.get('crop_type')),
                bool(initiative.get('start_year')),
                bool(initiative.get('methodology'))
            ])
            quality_metrics['Completude de Dados'] += fields_present / 4

            # Cobertura geográfica
            if initiative.get('state'):
                states_covered.add(initiative['state'])

            # Diversidade de culturas
            if initiative.get('crop_type'):
                crops_covered.add(initiative['crop_type'])

            # Consistência temporal
            start_year = initiative.get('start_year')
            end_year = initiative.get('end_year')
            if start_year and (not end_year or end_year >= start_year):
                temporal_consistent += 1

        # Normaliza métricas
        quality_metrics['Completude de Dados'] = (quality_metrics['Completude de Dados'] / total_initiatives) * 100
        quality_metrics['Consistência Temporal'] = (temporal_consistent / total_initiatives) * 100
        quality_metrics['Cobertura Geográfica'] = (len(states_covered) / 27) * 100  # 27 estados brasileiros
        quality_metrics['Diversidade de Culturas'] = min((len(crops_covered) / 10) * 100, 100)  # Max 10 culturas esperadas

        # Cria gráfico de barras radial
        categories = list(quality_metrics.keys())
        values = list(quality_metrics.values())

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Métricas de Qualidade',
            line=dict(color='rgb(90, 171, 71)', width=2),
            fillcolor='rgba(90, 171, 71, 0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title="📊 Métricas de Qualidade CONAB (%)",
            height=500
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de métricas de qualidade CONAB: {e}")
        return None


def plot_conab_seasonal_analysis(conab_data: dict, calendar_data: Optional[dict] = None) -> Optional[go.Figure]:
    """
    Cria análise sazonal dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        calendar_data: Dados do calendário agrícola (opcional)
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Análise simples baseada apenas nos dados CONAB
        # Conta iniciativas por tipo de cultura e ano
        seasonal_data = []
        
        for initiative in conab_data.values():
            crop_type = initiative.get('crop_type', 'Indefinido')
            start_year = initiative.get('start_year')
            end_year = initiative.get('end_year')
            
            if start_year:
                for year in range(start_year, (end_year or start_year) + 1):
                    seasonal_data.append({
                        'Ano': year,
                        'Tipo_Cultura': crop_type,
                        'Duração': (end_year or start_year) - start_year + 1
                    })

        if not seasonal_data:
            return None

        df = pd.DataFrame(seasonal_data)
        
        # Agrupa por ano e tipo de cultura
        df_grouped = df.groupby(['Ano', 'Tipo_Cultura']).size().reset_index(name='Contagem')

        # Cria gráfico de área empilhada
        fig = px.area(
            df_grouped,
            x='Ano',
            y='Contagem',
            color='Tipo_Cultura',
            title="📅 Análise Sazonal CONAB - Iniciativas por Ano e Cultura"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Ano",
            yaxis_title="Número de Iniciativas"
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar análise sazonal CONAB: {e}")
        return None


def plot_conab_methodology_overview(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria overview das metodologias utilizadas nos dados CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Extrai dados de metodologia
        methodology_data = []
        for initiative in conab_data.values():
            methodology = initiative.get('methodology', 'Indefinido')
            crop_type = initiative.get('crop_type', 'Indefinido')
            state = initiative.get('state', 'Indefinido')
            
            methodology_data.append({
                'Metodologia': methodology,
                'Tipo_Cultura': crop_type,
                'Estado': state
            })

        if not methodology_data:
            return None

        df = pd.DataFrame(methodology_data)
        
        # Conta metodologias
        method_counts = df['Metodologia'].value_counts()
        
        # Cria gráfico de barras
        fig = px.bar(
            x=method_counts.index,
            y=method_counts.values,
            title="🔬 Overview de Metodologias CONAB",
            labels={'x': 'Metodologia', 'y': 'Frequência'}
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar overview de metodologias CONAB: {e}")
        return None


def plot_conab_crop_production_trends(conab_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de tendências de produção de culturas CONAB.
    
    Args:
        conab_data: Dados detalhados da CONAB
        
    Returns:
        go.Figure: Figura do Plotly ou None se não há dados
    """
    try:
        if not conab_data:
            return None

        # Simula tendências baseado nos dados disponíveis
        production_data = []
        
        for initiative in conab_data.values():
            crop_type = initiative.get('crop_type', 'Indefinido')
            start_year = initiative.get('start_year')
            end_year = initiative.get('end_year')
            state = initiative.get('state', 'Indefinido')
            
            if start_year:
                for year in range(start_year, (end_year or start_year) + 1):
                    # Simula dados de produção baseado na atividade
                    production_data.append({
                        'Ano': year,
                        'Tipo_Cultura': crop_type,
                        'Estado': state,
                        'Atividade': 1  # Indica presença de monitoramento
                    })

        if not production_data:
            return None

        df = pd.DataFrame(production_data)
        
        # Agrupa por ano e cultura
        df_trends = df.groupby(['Ano', 'Tipo_Cultura'])['Atividade'].sum().reset_index()

        # Filtra top 5 culturas
        top_crops = df.groupby('Tipo_Cultura')['Atividade'].sum().nlargest(5).index

        df_filtered = df_trends[df_trends['Tipo_Cultura'].isin(top_crops)]

        # Cria gráfico de linha
        fig = px.line(
            df_filtered,
            x='Ano',
            y='Atividade',
            color='Tipo_Cultura',
            title="📈 Tendências de Monitoramento CONAB por Cultura",
            labels={'Atividade': 'Intensidade de Monitoramento'}
        )

        fig.update_layout(height=400)
        return fig

    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de tendências de produção: {e}")
        return None