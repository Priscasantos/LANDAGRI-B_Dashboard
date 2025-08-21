"""
Modular component for temporal evolution analysis of LULC initiatives.
Contains line charts and heatmaps to show data availability evolution.
"""

import re
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_evolution_analysis(temporal_df: pd.DataFrame) -> None:
    """
    Renders temporal evolution analysis with tab-based navigation.
    
    Args:
        temporal_df: DataFrame with temporal data of initiatives
    """
    st.markdown("### 📈 Evolution Analysis")
    st.markdown("*Analyzing how LULC initiatives have evolved over time.*")
    
    if temporal_df.empty:
        st.warning("❌ No temporal data available for evolution analysis.")
        return
        
    # Ensure correct column names for compatibility
    if 'Anos_Lista' in temporal_df.columns and 'Years_List' not in temporal_df.columns:
        temporal_df = temporal_df.rename(columns={'Anos_Lista': 'Years_List'})
    
    # Tab-based navigation instead of dropdown
    tab1, tab2 = st.tabs(["📊 Initiative Timeline", "🔥 Resolution Evolution"])
    
    with tab1:
        st.markdown("#### 📊 Initiative Count Over Time")
        fig = plot_evolution_line_chart(temporal_df)
        st.plotly_chart(fig, use_container_width=True, key="evolution_line_chart")
        
        with st.expander("📊 Evolution Statistics"):
            all_years = []
            for _, row in temporal_df.iterrows():
                if isinstance(row.get('Years_List'), list):
                    all_years.extend(row['Years_List'])
            if all_years:
                year_counts = pd.Series(all_years).value_counts().sort_index()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Peak Year", year_counts.idxmax(), f"{year_counts.max()} initiatives")
                with col2:
                    st.metric("Average per Year", f"{year_counts.mean():.1f}", "initiatives")
                with col3:
                    st.metric("Total Years Covered", len(year_counts), "years")
    
    with tab2:
        st.markdown("#### 🔥 Spatial Resolution Evolution")
        if 'metadata' not in st.session_state:
            st.warning("❌ Metadata not available for resolution evolution analysis.")
            return
        fig = plot_evolution_heatmap_chart(st.session_state.metadata, temporal_df)
        st.plotly_chart(fig, use_container_width=True, key="evolution_heatmap_chart")


def plot_evolution_line_chart(temporal_data: pd.DataFrame) -> go.Figure:
    """
    Generate line chart showing how data availability evolves over time.
    
    Args:
        temporal_data: DataFrame with temporal data containing 'Years_List' column
        
    Returns:
        go.Figure: Plotly figure showing evolution of data availability
    """
    if temporal_data.empty or 'Years_List' not in temporal_data.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No temporal data available for evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 14, "color": "gray"}
        )
        fig.update_layout(
            title="Evolution Analysis - No Data",
            xaxis={"title": "Year"},
            yaxis={"title": "Number of Active Initiatives"}
        )
        return fig
    # Processar dados para contar iniciativas por ano
    all_years = []
    for _, row in temporal_data.iterrows():
        if isinstance(row.get('Years_List'), list):
            all_years.extend(row['Years_List'])
    if not all_years:
        fig = go.Figure()
        fig.add_annotation(
            text="No year data available for evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Evolution Analysis - No Year Data",
            xaxis=dict(title="Year"),
            yaxis=dict(title="Number of Active Initiatives")
        )
        return fig
    # Contar iniciativas por ano
    year_counts = pd.Series(all_years).value_counts().sort_index()
    years_df = pd.DataFrame({
        'Year': year_counts.index,
        'Number_Initiatives': year_counts.values
    })
    
    # Criar a figura
    fig = go.Figure()
    
    # Adicionar linha principal de evolução com preenchimento de área
    fig.add_trace(go.Scatter(
        x=years_df['Year'],
        y=years_df['Number_Initiatives'],
        mode='lines+markers',
        name='Active Initiatives',
        line={"color": 'rgba(0, 150, 136, 1)', "width": 3},
        marker={
            "size": 8,
            "color": 'rgba(0, 150, 136, 0.8)',
            "line": {"width": 2, "color": 'rgba(0, 150, 136, 1)'}
        },
        fill='tozeroy',
        fillcolor='rgba(0, 150, 136, 0.2)',
        hovertemplate='<b>Year: %{x}</b><br>Active Initiatives: %{y}<extra></extra>'
    ))
    
    # Adicionar marcadores de tendência para pontos-chave
    max_initiatives_year = years_df.loc[years_df['Number_Initiatives'].idxmax()]
    
    # Marcar ano de pico
    fig.add_trace(go.Scatter(
        x=[max_initiatives_year['Year']],
        y=[max_initiatives_year['Number_Initiatives']],
        mode='markers',
        name='Peak Year',
        marker=dict(
            size=12,
            color='rgba(255, 193, 7, 1)',
            symbol='star',
            line=dict(width=2, color='rgba(255, 152, 0, 1)')
        ),
        hovertemplate=f'<b>Peak Year: {max_initiatives_year["Year"]}</b><br>Initiatives: {max_initiatives_year["Number_Initiatives"]}<extra></extra>',
        showlegend=True
    ))
    
    # Layout aprimorado específico para gráfico de evolução
    fig.update_layout(
        title="Evolution of LULC Initiative Availability Over Time",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="Year",
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            dtick=2,  # Mostrar a cada 2 anos para melhor legibilidade
            tickangle=-45 if len(years_df) > 15 else 0  # Rotacionar labels se muitos anos
        ),
        yaxis=dict(
            title="Number of Active Initiatives",
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            zeroline=True,
            zerolinecolor='rgba(128,128,128,0.4)',
            zerolinewidth=1
        ),
        hovermode='x unified'
    )
    
    # Adicionar anotações para contexto
    avg_initiatives = years_df['Number_Initiatives'].mean()
    fig.add_hline(
        y=avg_initiatives,
        line_dash="dash",
        line_color="rgba(128,128,128,0.6)",
        annotation_text=f"Average: {avg_initiatives:.1f}",
        annotation_position="bottom right"
    )
    
    return fig


def plot_evolution_heatmap_chart(metadata: dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """
    Gera gráfico de área mostrando a evolução da resolução espacial em iniciativas LULC no tempo.
    Usa três categorias de resolução: Coarse (≥100m), Medium (30-99m), e High (<30m).
    
    Args:
        metadata: Metadados das iniciativas contendo resolução espacial e anos disponíveis
        filtered_df: DataFrame filtrado com dados das iniciativas
        
    Returns:
        go.Figure: Figura Plotly mostrando gráfico de área empilhada da evolução de resolução
    """
    if not metadata or filtered_df is None or filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for resolution evolution analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Resolution Evolution Analysis - No Data",
            xaxis=dict(title="Year"),
            yaxis=dict(title="Initiatives")
        )
        return fig
    
    # Processar metadados para extrair dados de resolução e anos
    resolution_data = []
    
    for initiative_name, meta_info in metadata.items():
        if not isinstance(meta_info, dict):
            continue
            
        # Obter anos disponíveis
        years_key = 'available_years' if 'available_years' in meta_info else 'anos_disponiveis'
        if years_key not in meta_info or not meta_info[years_key]:
            continue
            
        years = meta_info[years_key]
        if not isinstance(years, list):
            continue
            
        # Obter resolução espacial
        spatial_res = meta_info.get('spatial_resolution')
        if spatial_res is None:
            continue
            
        # Parsear resolução para obter um valor representativo único
        resolution_value = _parse_resolution_for_categorization(spatial_res)
        if resolution_value is None:
            continue
            
        # Categorizar resolução
        if resolution_value >= 100:
            category = "Coarse (≥100m)"
        elif resolution_value >= 30:
            category = "Medium (30-99m)"
        else:
            category = "High (<30m)"
            
        # Adicionar dados para cada ano
        for year in years:
            if isinstance(year, (int, float)) and 1985 <= year <= 2024:
                resolution_data.append({
                    'initiative': initiative_name,
                    'year': int(year),
                    'resolution_value': resolution_value,
                    'category': category
                })
    
    if not resolution_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No resolution data available for the selected initiatives",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Resolution Evolution Analysis - No Resolution Data",
            xaxis=dict(title="Year"),
            yaxis=dict(title="Initiatives")
        )
        return fig
    
    # Criar DataFrame e agregar por ano e categoria
    df_resolution = pd.DataFrame(resolution_data)
    
    # Contar iniciativas por ano e categoria
    yearly_counts = df_resolution.groupby(['year', 'category']).size().reset_index(name='count')
    
    # Pivotar para obter categorias como colunas
    pivot_df = yearly_counts.pivot(index='year', columns='category', values='count').fillna(0)
    
    # Garantir que temos todos os anos de 1985 a 2024
    all_years = list(range(1985, 2025))
    pivot_df = pivot_df.reindex(all_years, fill_value=0)
    
    # Definir ordem das categorias e cores
    category_order = ["High (<30m)", "Medium (30-99m)", "Coarse (≥100m)"]
    colors = {
        "High (<30m)": 'rgba(76, 175, 80, 0.7)',
        "Medium (30-99m)": 'rgba(255, 193, 7, 0.7)',
        "Coarse (≥100m)": 'rgba(244, 67, 54, 0.7)'
    }
    
    # Garantir que todas as categorias existem no DataFrame
    for category in category_order:
        if category not in pivot_df.columns:
            pivot_df[category] = 0
    
    # Criar a figura
    fig = go.Figure()
    
    # Adicionar traces de área empilhada
    for i, category in enumerate(category_order):
        if category in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[category],
                mode='lines',
                name=category,
                fill='tonexty' if i > 0 else 'tozeroy',
                fillcolor=colors[category],
                line=dict(color=colors[category], width=2),
                hovertemplate=f'<b>{category}</b><br>Year: %{{x}}<br>Initiatives: %{{y}}<extra></extra>',
                stackgroup='one'  # Isso cria o efeito de área empilhada
            ))
    
    # Adicionar anotações de marcos para anos-chave
    milestones = {
        2000: "Lower Number of Initiatives",
        2020: "Higher Number of Initiatives"
    }
    
    for year, label in milestones.items():
        if year in pivot_df.index:
            fig.add_vline(
                x=year,
                line_dash="dash",
                line_color="rgba(128,128,128,0.6)",
                line_width=1,
                annotation_text=label,
                annotation_position="top",
                annotation_font_size=10,
                annotation_font_color="rgba(139,69,19,0.8)"
            )
    
    # Personalizar layout para gráfico de área
    fig.update_layout(
        title="Evolution of Spatial Resolution in LULC Initiatives",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="Year",
            range=[1985, 2024],
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            dtick=5,  # Mostrar a cada 5 anos
            tickangle=0
        ),
        yaxis=dict(
            title="Number of Initiatives",
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            tickformat='d',
            zeroline=True,
            zerolinecolor='rgba(128,128,128,0.4)',
            zerolinewidth=1
        ),
        hovermode='x unified'
    )
    
    # Adicionar legenda com explicação das categorias de resolução
    fig.add_annotation(
        text="High: <30m | Medium: 30-99m | Coarse: ≥100m",
        xref="paper", yref="paper",
        x=0.5, y=-0.20,
        showarrow=False,
        font=dict(size=12, color="gray"),
        align="center"
    )
    
    return fig


def _parse_resolution_for_categorization(spatial_res: Any) -> float | None:
    """
    Função auxiliar para parsear resolução espacial para categorização.
    Retorna um valor de resolução representativo único em metros.
    """
    if spatial_res is None:
        return None
        
    # Tratar valores numéricos diretos
    if isinstance(spatial_res, (int, float)):
        return float(spatial_res)
    
    # Tratar valores string
    if isinstance(spatial_res, str):
        # Extrair valor numérico de strings como "30m", "100", etc.
        res_str = re.sub(r'[^\d.]', '', spatial_res)
        if res_str:
            return float(res_str)
        return None
    
    # Tratar lista de valores ou objetos
    if isinstance(spatial_res, list):
        values = []
        
        # Procurar por resolução 'current' primeiro
        for item in spatial_res:
            if isinstance(item, dict) and item.get('current', False):
                val = item.get('resolution')
                if val is not None:
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, str):
                        res_str = re.sub(r'[^\d.]', '', val)
                        if res_str:
                            return float(res_str)
        
        # Se não encontrou 'current', coletar todos os valores
        for item in spatial_res:
            if isinstance(item, dict):
                val = item.get('resolution')
            else:
                val = item
                
            if val is not None:
                if isinstance(val, (int, float)):
                    values.append(float(val))
                elif isinstance(val, str):
                    res_str = re.sub(r'[^\d.]', '', val)
                    if res_str:
                        values.append(float(res_str))
        
        # Retornar a resolução mínima (maior detalhe) se múltiplos valores
        if values:
            return min(values)
    
    return None
