import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from config import get_initiative_color_map
import streamlit as st

@st.cache_data(ttl=300)  # Cache por 5 minutos para melhor performance
def plot_timeline(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> go.Figure:
    """Plot an improved timeline using anos_disponiveis from metadata, with enhanced visualization."""
    if not metadata:
        return go.Figure()
    
    # Criar dados de disponibilidade ano a ano com informações adicionais
    timeline_data = []
    all_years = set()
    
    # Mapear produtos para obter características técnicas
    produto_info = {}
    if filtered_df is not None and not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            produto_info[row['Nome']] = {
                'metodologia': row.get('Metodologia', 'N/A'),
                'escopo': row.get('Escopo', 'N/A'),
                'acuracia': row.get('Acurácia (%)', 0),
                'resolucao': row.get('Resolução (m)', 0)
            }
    
    # Coletar todos os anos de todas as iniciativas
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
            info = produto_info.get(nome, {})
            for ano in meta['anos_disponiveis']:
                timeline_data.append({
                    'produto': nome,
                    'ano': ano,
                    'disponivel': 1,
                    'metodologia': info.get('metodologia', 'N/A'),
                    'escopo': info.get('escopo', 'N/A')
                })
                all_years.add(ano)
    
    if not timeline_data or not all_years:
        return go.Figure()
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Criar range completo de anos (1985-2024 para manter escala consistente)
    min_year, max_year = 1985, 2024
    all_years_range = list(range(min_year, max_year + 1))
    produtos_unicos = sorted(timeline_df['produto'].unique())
    
    # Criar matriz completa (produto x ano)
    matrix_data = []
    for produto in produtos_unicos:
        produto_anos = timeline_df[timeline_df['produto'] == produto]['ano'].tolist()
        produto_metodologia = timeline_df[timeline_df['produto'] == produto]['metodologia'].iloc[0]
        for ano in all_years_range:
            matrix_data.append({
                'produto': produto,
                'ano': ano,
                'disponivel': 1 if ano in produto_anos else 0,
                'metodologia': produto_metodologia
            })
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # Criar o gráfico de timeline como barras horizontais
    fig_timeline = go.Figure()
    
    # Usar cores Set1 (padrão do sistema) e mapear por produto/iniciativa
    colors = px.colors.qualitative.Set1
    color_map = {produto: colors[i % len(colors)] for i, produto in enumerate(produtos_unicos)}
    
    # Adicionar uma legenda personalizada para cada iniciativa
    legend_added = set()
    
    for i, produto in enumerate(produtos_unicos):
        produto_data = matrix_df[matrix_df['produto'] == produto]
        anos_disponiveis = produto_data[produto_data['disponivel'] == 1]['ano'].tolist()
        metodologia = produto_data['metodologia'].iloc[0]
        cor = color_map.get(produto, colors[0])
        
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
                # Adicionar legenda apenas uma vez por produto/iniciativa
                show_legend = produto not in legend_added
                if show_legend:
                    legend_added.add(produto)
                    
                fig_timeline.add_trace(go.Scatter(
                    x=[seg_start, seg_end + 1],
                    y=[i, i],
                    mode='lines',
                    line=dict(
                        color=cor,
                        width=15
                    ),
                    name=produto if show_legend else None,
                    showlegend=show_legend,
                    legendgroup=produto,
                    hovertemplate=f"<b>{produto}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>"
                ))    # Configurar layout com fundo escuro e sem legenda - mais compacto
    fig_timeline.update_layout(
        title=dict(
            text='📅 Timeline de Disponibilidade das Iniciativas LULC (1985-2024)',
            font=dict(size=22, color="#F3F4F6", family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif")
        ),
        xaxis_title=dict(
            text='Ano',
            font=dict(size=20, color="#F3F4F6")
        ),
        yaxis_title=dict(
            text='Produtos LULC',
            font=dict(size=20, color="#F3F4F6")
        ),
        height=max(600, len(produtos_unicos) * 35),  # Aumentar altura dos eixos
        font=dict(size=20, color="#F3F4F6", family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        margin=dict(l=200, r=30, t=100, b=80),  # Reduzir margens laterais
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(produtos_unicos))),
            ticktext=produtos_unicos,
            showgrid=True,
            gridcolor='#444',
            color="#F3F4F6",
            tickfont=dict(size=20)
        ),        xaxis=dict(
            range=[1985, 2024],  # Manter escala fixa
            dtick=1,  # Mostrar todos os anos (de ano em ano)
            gridcolor='#444',
            gridwidth=1,
            showgrid=True,
            color="#F3F4F6",
            tickformat='d',
            tickangle=-45,  # Anos "tombados" para caber todos
            tickfont=dict(size=20),
            categoryorder='category ascending'
        ),
        hovermode='closest',
        showlegend=False  # Remover legenda
    )
    
    return fig_timeline

@st.cache_data(ttl=300)  # Cache por 5 minutos
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
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        font=dict(color="#F3F4F6"),
        xaxis=dict(color="#F3F4F6"),
        yaxis=dict(color="#F3F4F6")
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
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        font=dict(color="#F3F4F6"),
        xaxis=dict(color="#F3F4F6"),
        yaxis=dict(color="#F3F4F6")
    )
    return fig

@st.cache_data(ttl=300)  # Cache por 5 minutos
def plot_resolucao_acuracia(filtered_df, viz_mode="parallel"):
    """
    Cria visualizações alternativas para análise de acurácia e resolução.
    OTIMIZADO PARA PERFORMANCE
    
    Parâmetros:
    - filtered_df: DataFrame filtrado
    - viz_mode: tipo de visualização ("parallel", "radar", "matrix")
    """
    
    # Otimização: Limitar dados automaticamente se muito grande
    MAX_ITEMS = 100
    if len(filtered_df) > MAX_ITEMS:
        filtered_df = filtered_df.nlargest(MAX_ITEMS, 'Acurácia (%)')
    
    if viz_mode == "parallel":
        # Coordenadas Paralelas - OTIMIZADA
        numeric_cols = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_cols = [col for col in numeric_cols if col in filtered_df.columns]
        
        if len(available_cols) >= 2:
            # OTIMIZAÇÃO: Limitar ainda mais para coordenadas paralelas (max 30)
            parallel_df = filtered_df[available_cols + ['Nome', 'Metodologia']].dropna()
            if len(parallel_df) > 30:
                parallel_df = parallel_df.nlargest(30, 'Acurácia (%)')
                st.info("ℹ️ Mostrando top 30 iniciativas para melhor performance na visualização paralela")
            
            if not parallel_df.empty:
                # Normalizar dados para melhor visualização
                parallel_norm = parallel_df.copy()
                for col in available_cols:
                    if col == 'Resolução (m)':
                        # Para resolução, inverter (menor é melhor)
                        if parallel_df[col].max() != parallel_df[col].min():
                            parallel_norm[col] = (parallel_df[col].max() - parallel_df[col]) / (parallel_df[col].max() - parallel_df[col].min())
                        else:
                            parallel_norm[col] = 0.5
                    else:
                        if parallel_df[col].max() != parallel_df[col].min():
                            parallel_norm[col] = (parallel_df[col] - parallel_df[col].min()) / (parallel_df[col].max() - parallel_df[col].min())
                        else:
                            parallel_norm[col] = 0.5
                
                # Mapear metodologias para cores numéricas
                if 'Metodologia' in parallel_norm.columns:
                    metodologias = parallel_norm['Metodologia'].astype('category')
                    parallel_norm['Color'] = metodologias.cat.codes
                else:
                    parallel_norm['Color'] = 0
                
                fig = px.parallel_coordinates(
                    parallel_norm, 
                    dimensions=available_cols,
                    color='Color',
                    color_continuous_scale='viridis',
                    title="📊 Coordenadas Paralelas - Comparação Multidimensional",
                    labels={col: col for col in available_cols}
                )
                # Otimizações de rendering
                fig.update_layout(
                    template='plotly_white',
                    height=600
                )
            else:
                # Fallback para radar se parallel não funcionar
                return plot_resolucao_acuracia(filtered_df, "radar")
        else:
            return plot_resolucao_acuracia(filtered_df, "radar")
    elif viz_mode == "radar":
        # Gráfico Radar Comparativo - OTIMIZADO (máximo 5 para performance)
        radar_cols = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_radar = [col for col in radar_cols if col in filtered_df.columns]
        
        if len(available_radar) >= 2:
            # OTIMIZAÇÃO: Sempre máximo 5 iniciativas para não sobrecarregar
            top_initiatives = filtered_df.nlargest(5, 'Acurácia (%)')
            
            fig = go.Figure()
            
            # Cores predefinidas para melhor performance
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            
            for idx, (_, row) in enumerate(top_initiatives.iterrows()):
                if idx >= 5:  # Garantir limite máximo
                    break
                    
                values = []
                for col in available_radar:
                    if col == 'Resolução (m)':
                        # Normalizar resolução (inverter - menor é melhor)
                        if filtered_df[col].max() != filtered_df[col].min():
                            norm_val = (filtered_df[col].max() - row[col]) / (filtered_df[col].max() - filtered_df[col].min()) * 100
                        else:
                            norm_val = 50
                    else:
                        # Normalizar outras métricas
                        if filtered_df[col].max() != filtered_df[col].min():
                            norm_val = (row[col] - filtered_df[col].min()) / (filtered_df[col].max() - filtered_df[col].min()) * 100
                        else:
                            norm_val = 50
                    values.append(norm_val)
                
                # Fechar o polígono
                values.append(values[0])
                theta_labels = available_radar + [available_radar[0]]
                
                # OTIMIZAÇÃO: Truncar nomes muito longos
                display_name = row['Nome'][:25] + ('...' if len(row['Nome']) > 25 else '')
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=theta_labels,
                    fill='toself',
                    name=display_name,
                    line_color=colors[idx % len(colors)]
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,                title="🎯 Gráfico Radar - Top 5 Iniciativas por Acurácia",
                height=600,
                template='plotly_white'
            )
        else:
            # Fallback para matrix se radar não tiver dados suficientes
            return plot_resolucao_acuracia(filtered_df, "matrix")
    elif viz_mode == "matrix":
        # Matriz de Comparação - OTIMIZADA (top 15 máximo)
        comparison_cols = ['Acurácia (%)', 'Resolução (m)', 'Classes', 'Metodologia', 'Tipo']
        available_matrix = [col for col in comparison_cols if col in filtered_df.columns]
        
        if len(available_matrix) >= 3:
            matrix_df = filtered_df[['Nome'] + available_matrix].copy()
            
            # OTIMIZAÇÃO: Processar apenas top 15 para evitar sobrecarga
            if len(matrix_df) > 15:
                matrix_df = matrix_df.nlargest(15, 'Acurácia (%)')
                st.info("ℹ️ Mostrando top 15 iniciativas para melhor performance na matriz")
            
            # Criar score composto
            score_components = []
            if 'Acurácia (%)' in matrix_df.columns:
                score_components.append(matrix_df['Acurácia (%)'] * 0.5)  # 50% peso
            if 'Resolução (m)' in matrix_df.columns:
                # Inverter resolução (menor é melhor)
                max_res = matrix_df['Resolução (m)'].max()
                if max_res > 0:
                    score_components.append((max_res - matrix_df['Resolução (m)']) / max_res * 100 * 0.3)  # 30% peso
            if 'Classes' in matrix_df.columns:
                if matrix_df['Classes'].max() != matrix_df['Classes'].min():
                    norm_classes = (matrix_df['Classes'] - matrix_df['Classes'].min()) / (matrix_df['Classes'].max() - matrix_df['Classes'].min()) * 100
                    score_components.append(norm_classes * 0.2)  # 20% peso
            
            if score_components:
                matrix_df['Score_Composto'] = sum(score_components)
                matrix_sorted = matrix_df.sort_values('Score_Composto', ascending=False)
                
                fig = px.bar(
                    matrix_sorted.head(10),  # Top 10 sempre
                    x='Score_Composto',
                    y='Nome',
                    orientation='h',
                    color='Score_Composto',
                    color_continuous_scale='Viridis',
                    title="📋 Matriz de Comparação - Score Composto (Top 10)",
                    labels={'Score_Composto': 'Score Composto', 'Nome': 'Iniciativas'},
                    text='Score_Composto',
                    height=600
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_layout(
                    showlegend=False,
                    font=dict(size=12),
                    margin=dict(l=200),
                    template='plotly_white'                )
            else:
                # Fallback para parallel se matrix não conseguir criar score
                return plot_resolucao_acuracia(filtered_df, "parallel")
        else:
            # Fallback para parallel se matrix não tiver colunas suficientes
            return plot_resolucao_acuracia(filtered_df, "parallel")            
    else:  # Default: parallel
        return plot_resolucao_acuracia(filtered_df, "parallel")
    
    # Configurações comuns de layout OTIMIZADAS
    fig.update_layout(
        font=dict(size=12),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        # OTIMIZAÇÕES DE RENDERING
        dragmode=False,  # Desabilitar drag para melhor performance
        hovermode='closest',  # Hover mais eficiente
        modebar_remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale2d']  # Remover controles desnecessários
    )
    
    return fig

@st.cache_data(ttl=300)  # Cache por 5 minutos
def plot_classes_por_iniciativa(filtered_df):
    fig = px.bar(
        filtered_df.sort_values('Classes', ascending=True),
        x='Classes',
        y='Nome',
        color='Tipo',
        orientation='h',
        title="Número de Classes por Iniciativa",
        height=500,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

@st.cache_data(ttl=300)  # Cache por 5 minutos
def plot_distribuicao_classes(filtered_df):
    fig = px.histogram(
        filtered_df,
        x='Classes',
        color='Tipo',
        title="Distribuição do Número de Classes",
        nbins=10,
        height=500,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

@st.cache_data(ttl=300)  # Cache por 5 minutos
def plot_distribuicao_metodologias(method_counts):
    import plotly.express as px
    # Verificar se method_counts tem dados
    if method_counts is None or method_counts.empty:
        # Retorna uma figura vazia ou uma mensagem, se preferir
        fig = go.Figure()
        fig.update_layout(title="Distribuição das Metodologias Utilizadas (Dados insuficientes)")
        return fig

    fig = px.pie(
        values=method_counts.values,  # Passar os valores explicitamente
        names=method_counts.index,    # Passar os índices (nomes das metodologias) explicitamente
        title="Distribuição das Metodologias Utilizadas",
        height=400
    )
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

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

def plot_radar_comparacao(data1, data2, filtered_df, init1, init2):
    categories = ['Acurácia (%)', 'Resolução (m)', 'Classes']
    def normalize_for_radar(value, column, df):
        if column == 'Resolução (m)':
            return (df[column].max() - value) / (df[column].max() - df[column].min()) * 100
        else:
            return (value - df[column].min()) / (df[column].max() - df[column].min()) * 100
    values1 = [normalize_for_radar(data1[cat], cat, filtered_df) for cat in categories]
    values2 = [normalize_for_radar(data2[cat], cat, filtered_df) for cat in categories]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values1 + [values1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init1,
        line_color='#ff6b6b'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=values2 + [values2[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init2,
        line_color='#4dabf7'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Comparação em Gráfico Radar (Valores Normalizados)",
        height=500,
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig_radar

def plot_heatmap_tecnico(filtered_df):
    from sklearn.preprocessing import MinMaxScaler
    features = ['Resolução (m)', 'Acurácia (%)', 'Classes']
    heatmap_data = filtered_df[features + ['Nome']].set_index('Nome')
    scaler = MinMaxScaler()
    heatmap_normalized = pd.DataFrame(
        scaler.fit_transform(heatmap_data),
        columns=heatmap_data.columns,
        index=heatmap_data.index
    )
    fig = px.imshow(
        heatmap_normalized.T,
        labels=dict(x="Iniciativa", y="Característica", color="Valor Normalizado"),
        x=heatmap_normalized.index,
        y=heatmap_normalized.columns,
        aspect="auto",
        color_continuous_scale='Viridis',
        title="Heatmap de Características Técnicas (Valores Normalizados)",
        height=400
    )
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_annual_coverage_multiselect(metadata: Dict[str, Any], filtered_df: pd.DataFrame, selected_initiatives: List[str]) -> go.Figure:
    """Plot annual coverage for selected initiatives, each with a unique color."""
    # Prepare data for selected initiatives only
    data = []
    for nome in selected_initiatives:
        meta = metadata.get(nome, {})
        if 'anos_disponiveis' in meta:
            anos = sorted(meta['anos_disponiveis'])
            for ano in anos:
                data.append({'Nome': nome, 'Ano': ano})
    if not data:
        return go.Figure()
    df_anos = pd.DataFrame(data)
    color_map = get_initiative_color_map(selected_initiatives)
    fig = go.Figure()
    for nome in selected_initiatives:
        anos = df_anos[df_anos['Nome'] == nome]['Ano'].tolist()
        fig.add_trace(go.Scatter(
            x=anos,
            y=[nome]*len(anos),
            mode='markers+lines',
            name=nome,
            marker=dict(color=color_map[nome], size=12, line=dict(width=2, color=color_map[nome])),
            line=dict(color=color_map[nome], width=3),
            showlegend=True
        ))
    # Fix x-axis to show all years in range, with correct labels
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
            gridcolor="#444",
            tickformat='d',
        )
    fig.update_layout(
        title="Cobertura Anual das Iniciativas Selecionadas",
        xaxis_title="Ano",
        yaxis_title="Iniciativa",
        yaxis=dict(type='category', categoryorder='array', categoryarray=selected_initiatives),
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        font=dict(color="#F3F4F6", size=13, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(color="#F3F4F6"),
            title="Iniciativa"
        ),
        margin=dict(l=120, r=50, t=60, b=50)
    )
    return fig
