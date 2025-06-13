#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Generate Graphics Module with Acronyms from DataFrame
===========================================================

Updated graphics functions that use acronyms directly from the DataFrame's 'Sigla' column
instead of external acronym mapping files.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from scripts.utilities.config import get_initiative_color_map
import streamlit as st

@st.cache_data(ttl=300)  # Cache por 5 minutos para melhor performance
def plot_timeline(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """Plot an improved timeline using anos_disponiveis from metadata, with siglas from DataFrame."""
    if not metadata:
        return go.Figure()
    
    # Criar mapeamento de nome para sigla a partir do DataFrame
    nome_to_sigla = {}
    if filtered_df is not None and not filtered_df.empty and 'Sigla' in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']
    
    # Criar dados de disponibilidade ano a ano
    timeline_data = []
    all_years = set()
    
    # Mapear produtos para obter características técnicas
    produto_info = {}
    if filtered_df is not None and not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            produto_info[row['Nome']] = {
                'metodologia': row.get('Metodologia', 'N/A'),
                'escopo': row.get('Escopo', 'N/A'),
                'sigla': row.get('Sigla', row['Nome'][:10])  # Usar sigla ou truncar nome
            }
    
    # Coletar todos os anos de todas as iniciativas
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
            info = produto_info.get(nome, {})
            sigla = nome_to_sigla.get(nome, nome[:10])  # Usar sigla do JSON ou truncar
            for ano in meta['anos_disponiveis']:
                timeline_data.append({
                    'produto': nome,
                    'produto_sigla': sigla,
                    'ano': ano,
                    'disponivel': 1,
                    'metodologia': info.get('metodologia', 'N/A'),
                    'escopo': info.get('escopo', 'N/A')
                })
                all_years.add(ano)
    
    if not timeline_data or not all_years:
        fig = go.Figure()
        fig.update_layout(
            title="Timeline das Iniciativas (Dados insuficientes)",
            xaxis_title="Ano",
            yaxis_title="Iniciativas",
            height=400
        )
        return fig
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Criar range completo de anos
    min_year, max_year = 1985, 2024
    all_years_range = list(range(min_year, max_year + 1))
    produtos_unicos = sorted(timeline_df['produto'].unique())
    siglas_unicas = [nome_to_sigla.get(produto, produto[:10]) for produto in produtos_unicos]
    
    # Criar matriz completa (produto x ano)
    matrix_data = []
    for produto in produtos_unicos:
        produto_anos = timeline_df[timeline_df['produto'] == produto]['ano'].tolist()
        produto_metodologia = timeline_df[timeline_df['produto'] == produto]['metodologia'].iloc[0]
        produto_sigla = nome_to_sigla.get(produto, produto[:10])
        for ano in all_years_range:
            matrix_data.append({
                'produto': produto,
                'produto_sigla': produto_sigla,
                'ano': ano,
                'disponivel': 1 if ano in produto_anos else 0,
                'metodologia': produto_metodologia
            })
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # Criar o gráfico de timeline
    fig_timeline = go.Figure()
    
    # Usar cores Set1
    colors = px.colors.qualitative.Set1
    color_map = {produto: colors[i % len(colors)] for i, produto in enumerate(produtos_unicos)}
    
    legend_added = set()
    
    for i, produto in enumerate(produtos_unicos):
        produto_data = matrix_df[matrix_df['produto'] == produto]
        anos_disponiveis = produto_data[produto_data['disponivel'] == 1]['ano'].tolist()
        metodologia = produto_data['metodologia'].iloc[0]
        cor = color_map.get(produto, colors[0])
        sigla = nome_to_sigla.get(produto, produto[:10])
        
        if anos_disponiveis:
            # Criar segmentos contínuos
            segments = []
            start = anos_disponiveis[0]
            end = anos_disponiveis[0]
            
            for j in range(1, len(anos_disponiveis)):
                if anos_disponiveis[j] == end + 1:
                    end = anos_disponiveis[j]
                else:
                    segments.append((start, end))
                    start = anos_disponiveis[j]
                    end = anos_disponiveis[j]
            
            segments.append((start, end))
            
            # Plotar cada segmento
            for seg_start, seg_end in segments:
                show_legend = produto not in legend_added
                if show_legend:
                    legend_added.add(produto)
                    
                fig_timeline.add_trace(go.Scatter(
                    x=[seg_start, seg_end + 1],
                    y=[i, i],
                    mode='lines',
                    line=dict(color=cor, width=15),
                    name=sigla if show_legend else None,  # Usar sigla na legenda
                    showlegend=show_legend,
                    legendgroup=produto,
                    hovertemplate=f"<b>{sigla}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>"
                ))
    
    # Configurar layout
    fig_timeline.update_layout(
        title=dict(
            text='📅 Timeline de Disponibilidade das Iniciativas LULC (1985-2024)',
            font=dict(size=22, color="#2D3748", family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif")
        ),
        xaxis_title=dict(
            text='Ano',
            font=dict(size=16, color="#2D3748")
        ),
        yaxis_title=dict(
            text='Produtos LULC',
            font=dict(size=16, color="#2D3748")
        ),
        height=max(600, len(produtos_unicos) * 35),
        font=dict(size=16, color="#2D3748", family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=200, r=30, t=100, b=80),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(produtos_unicos))),
            ticktext=siglas_unicas,  # Usar siglas em vez de nomes completos
            showgrid=True,
            gridcolor='#E2E8F0',
            color="#2D3748",
            tickfont=dict(size=14)
        ),
        xaxis=dict(
            range=[1985, 2024],
            dtick=1,
            gridcolor='#E2E8F0',
            gridwidth=1,
            showgrid=True,
            color="#2D3748",
            tickformat='d',
            tickangle=-45,
            tickfont=dict(size=16),
            categoryorder='category ascending'
        ),
        hovermode='closest',
        showlegend=False  # Remover legenda para não poluir
    )
    
    return fig_timeline

@st.cache_data(ttl=300)
def plot_distribuicao_classes(filtered_df):
    """Plot histogram distribution of number of classes with improved error handling."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribuição do Número de Classes (Dados insuficientes)")
        return fig
    
    # Verificar se a coluna 'Classes' existe e tem dados válidos
    if 'Classes' not in filtered_df.columns:
        fig = go.Figure()
        fig.update_layout(title="Distribuição do Número de Classes (Coluna 'Classes' não encontrada)")
        return fig
    
    # Filtrar dados válidos (não nulos e numéricos)
    valid_data = filtered_df.dropna(subset=['Classes'])
    if valid_data.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribuição do Número de Classes (Nenhum dado válido)")
        return fig
    
    # Determinar cor baseada na coluna Tipo se existir
    color_column = 'Tipo' if 'Tipo' in valid_data.columns else None
    color_map = {'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'} if color_column else None
    
    fig = px.histogram(
        valid_data,
        x='Classes',
        color=color_column,
        title="Distribuição do Número de Classes",
        nbins=10,
        height=500,
        color_discrete_map=color_map
    )
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

@st.cache_data(ttl=300)
def plot_classes_por_iniciativa(filtered_df):
    """Plot number of classes per initiative using siglas for y-axis labels."""
    if filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Número de Classes por Iniciativa (Dados insuficientes)")
        return fig
    
    # Use siglas if available, otherwise truncate names
    display_names = []
    if 'Sigla' in filtered_df.columns:
        display_names = filtered_df['Sigla'].tolist()
    else:
        display_names = [nome[:15] + '...' if len(nome) > 15 else nome for nome in filtered_df['Nome'].tolist()]
    
    # Create a copy of the dataframe with display names
    plot_df = filtered_df.copy()
    plot_df['Display_Name'] = display_names
    
    fig = px.bar(
        plot_df.sort_values('Classes', ascending=True),
        x='Classes',
        y='Display_Name',
        color='Tipo',
        orientation='h',
        title="Número de Classes por Iniciativa",
        height=500,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Iniciativa"
    )
    return fig

@st.cache_data(ttl=300)
def plot_annual_coverage_multiselect(metadata: Dict[str, Any], filtered_df: pd.DataFrame, selected_initiatives: List[str]) -> go.Figure:
    """Plot annual coverage for selected initiatives using siglas."""
    if not selected_initiatives:
        fig = go.Figure()
        fig.update_layout(title="Cobertura Anual (Nenhuma iniciativa selecionada)")
        return fig
    
    # Create name to sigla mapping
    nome_to_sigla = {}
    if filtered_df is not None and not filtered_df.empty and 'Sigla' in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']
    
    # Prepare data for selected initiatives only
    data = []
    for nome in selected_initiatives:
        meta = metadata.get(nome, {})
        if 'anos_disponiveis' in meta:
            anos = sorted(meta['anos_disponiveis'])
            sigla = nome_to_sigla.get(nome, nome[:10])
            for ano in anos:
                data.append({'Nome': nome, 'Sigla': sigla, 'Ano': ano})
    
    if not data:
        fig = go.Figure()
        fig.update_layout(title="Cobertura Anual (Nenhum dado temporal disponível)")
        return fig
        
    df_anos = pd.DataFrame(data)
    color_map = get_initiative_color_map(selected_initiatives)
    
    fig = go.Figure()
    
    for nome in selected_initiatives:
        initiative_data = df_anos[df_anos['Nome'] == nome]
        if not initiative_data.empty:
            anos = initiative_data['Ano'].tolist()
            sigla = initiative_data['Sigla'].iloc[0]
            
            fig.add_trace(go.Scatter(
                x=anos,
                y=[sigla]*len(anos),
                mode='markers+lines',
                name=sigla,
                marker=dict(
                    color=color_map.get(nome, '#1f77b4'), 
                    size=12, 
                    line=dict(width=2, color=color_map.get(nome, '#1f77b4'))
                ),
                line=dict(color=color_map.get(nome, '#1f77b4'), width=3),
                showlegend=True
            ))
    
    # Fix x-axis to show all years in range
    if not df_anos.empty:
        min_year = int(df_anos['Ano'].min())
        max_year = int(df_anos['Ano'].max())
        fig.update_xaxes(
            tickmode='linear',
            tick0=min_year,
            dtick=1,
            range=[min_year-0.5, max_year+0.5],
            title='Ano',
            showgrid=True,
            gridcolor="#E2E8F0",
            tickformat='d',
        )
    
    fig.update_layout(
        title="Cobertura Anual das Iniciativas Selecionadas",
        xaxis_title="Ano",
        yaxis_title="Iniciativa",
        yaxis=dict(type='category'),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#2D3748", size=13, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(color="#2D3748"),
            title="Iniciativa"
        ),
        margin=dict(l=120, r=50, t=60, b=50)
    )
    return fig

# Manter outras funções existentes que não precisam de modificação
@st.cache_data(ttl=300)
def plot_ano_overlap(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    all_anos = []
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta:
            tipo = filtered_df[filtered_df['Nome'] == nome]['Tipo'].iloc[0] if nome in filtered_df['Nome'].values else None
            if not tipo:
                continue
            for ano in meta['anos_disponiveis']:
                all_anos.append({'Ano': ano, 'Nome': nome, 'Tipo': tipo})
    all_anos_df = pd.DataFrame(all_anos)
    if all_anos_df.empty:
        return go.Figure()
    count_ano = all_anos_df.groupby('Ano').size().reset_index(name='N iniciativas')
    fig = px.bar(
        count_ano,
        x='Ano',
        y='N iniciativas',
        title='Número de Iniciativas Disponíveis por Ano',
        color='N iniciativas',
        color_continuous_scale='Blues',
        height=350
    )
    
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#2D3748"),
        xaxis=dict(color="#2D3748"),
        yaxis=dict(color="#2D3748")
    )
    return fig

def plot_heatmap(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    all_anos = []
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta:
            tipo = filtered_df[filtered_df['Nome'] == nome]['Tipo'].iloc[0] if nome in filtered_df['Nome'].values else None
            if not tipo:
                continue
            for ano in meta['anos_disponiveis']:
                all_anos.append({'Ano': ano, 'Nome': nome, 'Tipo': tipo})
    all_anos_df = pd.DataFrame(all_anos)
    if all_anos_df.empty:
        return go.Figure()
    pivot = all_anos_df.pivot_table(index='Nome', columns='Ano', values='Tipo', aggfunc='count', fill_value=0)
    fig = px.imshow(
        pivot,
        aspect='auto',
        color_continuous_scale='Blues',
        labels=dict(color='Cobertura'),
        title='Cobertura Anual por Iniciativa',
        height=max(400, 20 * len(pivot))
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#2D3748"),
        xaxis=dict(color="#2D3748"),
        yaxis=dict(color="#2D3748")
    )
    return fig

@st.cache_data(ttl=300)
def plot_distribuicao_metodologias(method_counts):
    import plotly.express as px
    if method_counts is None or method_counts.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribuição das Metodologias Utilizadas (Dados insuficientes)")
        return fig
    
    fig = px.pie(
        values=method_counts.values,
        names=method_counts.index,
        title="Distribuição das Metodologias Utilizadas",
        height=400
    )
    
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# Adicionar outras funções necessárias (placeholder para as funções que não foram modificadas)
def plot_acuracia_por_metodologia(filtered_df):
    fig = px.box(
        filtered_df,
        x='Metodologia',
        y='Acurácia (%)',
        color='Tipo',
        title="Acurácia por Metodologia",
        height=400,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig
