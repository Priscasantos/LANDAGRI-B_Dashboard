"""
CONAB Specific Charts Component
==============================

Componente responsável por gerar gráficos específicos para dados CONAB,
incluindo análises de safras, distribuições regionais e métricas de qualidade.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional, Any
import numpy as np


def plot_conab_quality_metrics(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar dashboard de métricas de qualidade dos dados CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        if not initiative:
            return None
        
        # Métricas de qualidade
        accuracy = initiative.get('overall_accuracy', 0)
        resolution = initiative.get('spatial_resolution', 0)
        years = initiative.get('available_years', [])
        crops = initiative.get('detailed_crop_coverage', {})
        
        # Criar subplot com múltiplas métricas
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Precisão Geral', 'Resolução Espacial', 'Cobertura Temporal', 'Diversidade de Culturas'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Precisão geral (gauge)
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=accuracy,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Precisão (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ), row=1, col=1)
        
        # Resolução espacial (gauge)
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=resolution,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Resolução (m)"},
            gauge={
                'axis': {'range': [0, 1000]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 100], 'color': "yellow"},
                    {'range': [100, 1000], 'color': "lightgray"}
                ]
            }
        ), row=1, col=2)
        
        # Cobertura temporal (barras)
        if years:
            year_counts = pd.Series(years).value_counts().sort_index()
            fig.add_trace(go.Bar(
                x=year_counts.index[-10:],  # Últimos 10 anos
                y=year_counts.values[-10:],
                name="Anos com Dados",
                marker_color='steelblue'
            ), row=2, col=1)
        
        # Diversidade de culturas (pizza)
        if crops:
            crop_regions = {crop: len(data.get('regions', [])) 
                          for crop, data in crops.items()}
            
            crops_df = pd.DataFrame(list(crop_regions.items()), 
                                  columns=['crop', 'regions'])
            crops_df = crops_df.sort_values('regions', ascending=False).head(8)
            
            fig.add_trace(go.Pie(
                labels=crops_df['crop'],
                values=crops_df['regions'],
                name="Culturas por Região"
            ), row=2, col=2)
        
        fig.update_layout(
            height=600,
            title_text="Métricas de Qualidade - Iniciativa CONAB",
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar métricas de qualidade: {e}")
        return None


def plot_conab_crop_production_trends(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar gráfico de tendências de produção das culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        available_years = initiative.get('available_years', [])
        
        if not detailed_coverage or not available_years:
            return None
        
        # Simular dados de produção baseados na cobertura real
        production_data = []
        
        # Culturas principais com maior cobertura
        main_crops = ['Soybean', 'Corn', 'Cotton', 'Sugar cane']
        
        for crop in main_crops:
            if crop in detailed_coverage:
                crop_info = detailed_coverage[crop]
                regions = crop_info.get('regions', [])
                
                # Simular tendência baseada no número de regiões
                base_production = len(regions) * 10  # Base arbitrária
                
                for i, year in enumerate(available_years[-10:]):  # Últimos 10 anos
                    # Simular variação anual
                    variation = np.random.normal(1.0, 0.1)  # Variação de ±10%
                    trend_factor = 1 + (i * 0.02)  # Crescimento de 2% ao ano
                    
                    production = base_production * trend_factor * variation
                    
                    production_data.append({
                        'year': year,
                        'crop': crop,
                        'production_index': round(production, 1)
                    })
        
        if not production_data:
            return None
        
        df = pd.DataFrame(production_data)
        
        # Criar gráfico de linhas
        fig = px.line(
            df,
            x='year',
            y='production_index',
            color='crop',
            title="Tendências de Produção por Cultura (Índice Simulado)",
            labels={
                'year': 'Ano',
                'production_index': 'Índice de Produção',
                'crop': 'Cultura'
            },
            markers=True
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar tendências de produção: {e}")
        return None


def plot_conab_regional_comparison(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar comparação regional das culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Mapear estados para regiões brasileiras
        state_to_region = {
            'RO': 'Norte', 'TO': 'Norte', 'PA': 'Norte',
            'MA': 'Nordeste', 'PI': 'Nordeste', 'BA': 'Nordeste',
            'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'DF': 'Centro-Oeste',
            'MG': 'Sudeste', 'SP': 'Sudeste', 'RJ': 'Sudeste',
            'PR': 'Sul', 'SC': 'Sul', 'RS': 'Sul'
        }
        
        # Contar culturas por região
        regional_crops = {}
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            
            for state_code in regions:
                region = state_to_region.get(state_code, 'Outros')
                
                if region not in regional_crops:
                    regional_crops[region] = set()
                regional_crops[region].add(crop)
        
        # Preparar dados para visualização
        comparison_data = []
        for region, crops_set in regional_crops.items():
            comparison_data.append({
                'region': region,
                'crop_diversity': len(crops_set),
                'crops_list': list(crops_set)
            })
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('crop_diversity', ascending=False)
        
        # Criar gráfico de barras com detalhamento
        fig = px.bar(
            df,
            x='region',
            y='crop_diversity',
            color='crop_diversity',
            color_continuous_scale='RdYlGn',
            title="Diversidade de Culturas por Região Brasileira",
            labels={
                'region': 'Região',
                'crop_diversity': 'Número de Culturas Diferentes'
            }
        )
        
        # Adicionar anotações com as culturas
        for i, row in df.iterrows():
            crops_text = ', '.join(row['crops_list'][:3])
            if len(row['crops_list']) > 3:
                crops_text += f" (+{len(row['crops_list'])-3})"
            
            fig.add_annotation(
                x=row['region'],
                y=row['crop_diversity'] + 0.1,
                text=crops_text,
                showarrow=False,
                font=dict(size=10),
                textangle=-15
            )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar comparação regional: {e}")
        return None


def plot_conab_data_availability_matrix(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar matriz de disponibilidade de dados CONAB por cultura e região.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Criar matriz de disponibilidade
        all_regions = set()
        for crop_data in detailed_coverage.values():
            all_regions.update(crop_data.get('regions', []))
        
        all_regions = sorted(list(all_regions))
        all_crops = list(detailed_coverage.keys())
        
        # Matriz de disponibilidade (1 = tem dados, 0 = não tem)
        matrix_data = []
        for crop in all_crops:
            crop_regions = detailed_coverage[crop].get('regions', [])
            row = [1 if region in crop_regions else 0 for region in all_regions]
            matrix_data.append(row)
        
        # Criar heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=all_regions,
            y=all_crops,
            colorscale=[[0, '#f8f9fa'], [1, '#28a745']],
            hovertemplate="<b>%{y}</b><br>%{x}: %{customdata}<extra></extra>",
            customdata=[['Disponível' if val else 'Não disponível' for val in row] for row in matrix_data]
        ))
        
        fig.update_layout(
            title="Matriz de Disponibilidade de Dados CONAB",
            xaxis_title="Estados/Regiões",
            yaxis_title="Culturas",
            height=max(400, len(all_crops) * 25),
            xaxis={'tickangle': -45}
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar matriz de disponibilidade: {e}")
        return None


def plot_conab_seasonal_analysis(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar análise sazonal das culturas CONAB (primeira vs segunda safra).
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Analisar padrões sazonais
        seasonal_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Contar regiões com cada tipo de safra
            first_regions = len([r for r, years in first_crop_years.items() if years])
            second_regions = len([r for r, years in second_crop_years.items() if years])
            
            total_regions = len(set(list(first_crop_years.keys()) + list(second_crop_years.keys())))
            
            seasonal_data.append({
                'crop': crop,
                'primeira_safra': first_regions,
                'segunda_safra': second_regions,
                'total_regioes': total_regions,
                'dupla_safra_ratio': second_regions / total_regions if total_regions > 0 else 0
            })
        
        df = pd.DataFrame(seasonal_data)
        df = df.sort_values('dupla_safra_ratio', ascending=False)
        
        # Criar gráfico de barras duplas
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Primeira Safra',
            x=df['crop'],
            y=df['primeira_safra'],
            marker_color='#28a745',
            yaxis='y'
        ))
        
        fig.add_trace(go.Bar(
            name='Segunda Safra',
            x=df['crop'],
            y=df['segunda_safra'],
            marker_color='#ffc107',
            yaxis='y'
        ))
        
        # Adicionar linha com ratio de dupla safra
        fig.add_trace(go.Scatter(
            name='% Dupla Safra',
            x=df['crop'],
            y=df['dupla_safra_ratio'] * 100,
            mode='lines+markers',
            line=dict(color='#dc3545', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Análise Sazonal das Culturas CONAB",
            xaxis_title="Cultura",
            yaxis=dict(title="Número de Regiões", side="left"),
            yaxis2=dict(title="% Regiões com Dupla Safra", side="right", overlaying="y"),
            barmode='group',
            height=500,
            xaxis={'tickangle': -45}
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar análise sazonal: {e}")
        return None


def plot_conab_methodology_overview(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar overview da metodologia e sensores utilizados pelo CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        if not initiative:
            return None
        
        # Extrair informações metodológicas
        sensors_referenced = initiative.get('sensors_referenced', [])
        data_products = initiative.get('data_products', [])
        methodology = initiative.get('methodology', '')
        algorithm = initiative.get('algorithm', '')
        
        # Criar visualização de metodologia
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sensores Utilizados', 'Produtos de Dados', 'Metodologia', 'Informações Técnicas'),
            specs=[[{"type": "pie"}, {"type": "pie"}],
                   [{"type": "table", "colspan": 2}, None]]
        )
        
        # Sensores (se disponível)
        if sensors_referenced:
            sensor_names = [sensor.get('sensor_key', 'Unknown') for sensor in sensors_referenced]
            sensor_counts = pd.Series(sensor_names).value_counts()
            
            fig.add_trace(go.Pie(
                labels=sensor_counts.index,
                values=sensor_counts.values,
                name="Sensores"
            ), row=1, col=1)
        
        # Produtos de dados
        if data_products:
            product_types = [product.get('temporal_resolution', 'Unknown') for product in data_products]
            product_counts = pd.Series(product_types).value_counts()
            
            fig.add_trace(go.Pie(
                labels=product_counts.index,
                values=product_counts.values,
                name="Produtos"
            ), row=1, col=2)
        
        # Tabela com informações técnicas
        tech_info = [
            ['Metodologia', methodology[:100] + '...' if len(methodology) > 100 else methodology],
            ['Algoritmo', algorithm[:100] + '...' if len(algorithm) > 100 else algorithm],
            ['Precisão Geral', f"{initiative.get('overall_accuracy', 'N/A')}%"],
            ['Resolução Espacial', f"{initiative.get('spatial_resolution', 'N/A')}m"],
            ['Frequência Temporal', initiative.get('temporal_frequency', 'N/A')],
            ['Sistema de Referência', initiative.get('reference_system', 'N/A')]
        ]
        
        fig.add_trace(go.Table(
            header=dict(values=['Aspecto', 'Descrição'],
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[[row[0] for row in tech_info],
                              [row[1] for row in tech_info]],
                      fill_color='lavender',
                      align='left')
        ), row=2, col=1)
        
        fig.update_layout(
            height=600,
            title_text="Metodologia e Características Técnicas - CONAB",
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar overview metodológico: {e}")
        return None


def plot_conab_spatial_coverage(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar gráfico de cobertura espacial das culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Preparar dados de cobertura espacial
        spatial_data = []
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            
            spatial_data.append({
                'crop': crop,
                'regions_count': len(regions),
                'regions_list': ', '.join(regions[:5]) + ('...' if len(regions) > 5 else '')
            })
        
        df = pd.DataFrame(spatial_data)
        df = df.sort_values('regions_count', ascending=True)
        
        # Criar gráfico de barras horizontal
        fig = px.bar(
            df,
            x='regions_count',
            y='crop',
            orientation='h',
            color='regions_count',
            color_continuous_scale='Viridis',
            title="Cobertura Espacial por Cultura (CONAB)",
            labels={
                'regions_count': 'Número de Estados/Regiões',
                'crop': 'Cultura'
            },
            hover_data=['regions_list']
        )
        
        fig.update_layout(
            height=max(400, len(df) * 30),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de cobertura espacial: {e}")
        return None


def plot_conab_temporal_coverage(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar gráfico de cobertura temporal das culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        available_years = initiative.get('available_years', [])
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not available_years or not detailed_coverage:
            return None
        
        # Criar timeline de cobertura
        timeline_data = []
        
        for year in available_years:
            crops_with_data = 0
            
            for crop, crop_data in detailed_coverage.items():
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                # Verificar se há dados para este ano
                has_data = False
                for region_years in first_crop_years.values():
                    if any(str(year) in year_str for year_str in region_years):
                        has_data = True
                        break
                
                if not has_data:
                    for region_years in second_crop_years.values():
                        if any(str(year) in year_str for year_str in region_years):
                            has_data = True
                            break
                
                if has_data:
                    crops_with_data += 1
            
            timeline_data.append({
                'year': year,
                'crops_covered': crops_with_data,
                'total_crops': len(detailed_coverage)
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Criar gráfico de linha
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['crops_covered'],
            mode='lines+markers',
            name='Culturas com Dados',
            line=dict(color='#28a745', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['total_crops'],
            mode='lines',
            name='Total de Culturas',
            line=dict(color='#6c757d', width=2, dash='dash'),
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Evolução da Cobertura Temporal (CONAB)",
            xaxis_title="Ano",
            yaxis_title="Número de Culturas",
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de cobertura temporal: {e}")
        return None


def plot_conab_crop_diversity(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar gráfico de diversidade de culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Analisar diversidade por região
        region_crop_count = {}
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            for region in regions:
                if region not in region_crop_count:
                    region_crop_count[region] = []
                region_crop_count[region].append(crop)
        
        # Preparar dados para visualização
        diversity_data = []
        for region, crops in region_crop_count.items():
            diversity_data.append({
                'region': region,
                'crop_diversity': len(crops),
                'crops_list': ', '.join(crops[:3]) + ('...' if len(crops) > 3 else '')
            })
        
        df = pd.DataFrame(diversity_data)
        df = df.sort_values('crop_diversity', ascending=False)
        
        # Criar gráfico de barras
        fig = px.bar(
            df.head(15),  # Top 15 regiões
            x='region',
            y='crop_diversity',
            color='crop_diversity',
            color_continuous_scale='YlOrRd',
            title="Diversidade de Culturas por Região (CONAB)",
            labels={
                'region': 'Estado/Região',
                'crop_diversity': 'Número de Culturas'
            },
            hover_data=['crops_list']
        )
        
        fig.update_layout(
            height=400,
            xaxis={'tickangle': -45},
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de diversidade: {e}")
        return None


def plot_conab_spatial_temporal_distribution(conab_data: dict) -> Optional[go.Figure]:
    """
    Criar visualização integrada espaço-temporal das culturas CONAB.
    
    Args:
        conab_data: Dados detalhados do CONAB
        
    Returns:
        Figura Plotly ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Preparar dados espaço-temporais
        spatiotemporal_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Processar primeira safra
            for region, years_list in first_crop_years.items():
                for year_range in years_list:
                    # Extrair anos do range (ex: "2020-2021")
                    if '-' in year_range:
                        start_year = int(year_range.split('-')[0])
                        spatiotemporal_data.append({
                            'crop': crop,
                            'region': region,
                            'year': start_year,
                            'season': 'Primeira Safra',
                            'has_data': 1
                        })
            
            # Processar segunda safra
            for region, years_list in second_crop_years.items():
                for year_range in years_list:
                    if '-' in year_range:
                        start_year = int(year_range.split('-')[0])
                        spatiotemporal_data.append({
                            'crop': crop,
                            'region': region,
                            'year': start_year,
                            'season': 'Segunda Safra',
                            'has_data': 1
                        })
        
        if not spatiotemporal_data:
            return None
        
        df = pd.DataFrame(spatiotemporal_data)
        
        # Filtrar dados mais recentes
        recent_years = df['year'].max() - 5
        df_recent = df[df['year'] >= recent_years]
        
        # Criar sunburst chart
        fig = px.sunburst(
            df_recent,
            path=['season', 'crop', 'region'],
            values='has_data',
            title="Distribuição Espaço-Temporal das Culturas (Últimos 5 Anos)",
            color='has_data',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=600)
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar visualização espaço-temporal: {e}")
        return None
