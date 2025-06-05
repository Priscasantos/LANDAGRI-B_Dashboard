import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
import numpy as np
import ast

st.title('Comparativo Visual de Produtos')

# Carregar dados de exemplo (ajuste conforme seu dataset real)
df = pd.read_csv('initiative_data/initiatives_comparison.csv')

# 1. Gráfico de Barras Horizontais Duplas
st.header('1. Barras Horizontais Duplas: Acurácia x Resolução Espacial')

# Normalizar resolução para facilitar a leitura (quanto menor, melhor)
df['resolucao_norm'] = df['resolucao'] / df['resolucao'].max()

fig = go.Figure()
fig.add_trace(go.Bar(
    y=df['produto'],
    x=df['acuracia'],
    name='Acurácia (%)',
    orientation='h',
    marker_color='royalblue'
))
fig.add_trace(go.Bar(
    y=df['produto'],
    x=1 - df['resolucao_norm'],
    name='Resolução (normalizada, quanto maior melhor)',
    orientation='h',
    marker_color='orange'
))
fig.update_layout(barmode='group', xaxis_title='Valor', yaxis_title='Produto')
st.plotly_chart(fig, use_container_width=True)

# 2. Gráfico de Radar (Spider Chart)
st.header('2. Gráfico de Radar (Spider Chart)')

# Selecionar algumas métricas para o radar
eixos = ['acuracia', 'resolucao', 'num_classes', 'cobertura_temporal']
radar_df = df[['produto'] + eixos].copy()
# Normalizar todas as métricas para 0-1
for eixo in eixos:
    if eixo == 'resolucao':
        radar_df[eixo] = 1 - (radar_df[eixo] - radar_df[eixo].min()) / (radar_df[eixo].max() - radar_df[eixo].min())
    else:
        radar_df[eixo] = (radar_df[eixo] - radar_df[eixo].min()) / (radar_df[eixo].max() - radar_df[eixo].min())

fig_radar = go.Figure()
for i, row in radar_df.iterrows():
    fig_radar.add_trace(go.Scatterpolar(
        r=row[eixos].tolist() + [row[eixos[0]]],
        theta=eixos + [eixos[0]],
        fill='toself',
        name=row['produto']
    ))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0,1])),
    showlegend=True
)
st.plotly_chart(fig_radar, use_container_width=True)

# 3. Heatmap de Comparação
st.header('3. Heatmap de Comparação')

heatmap_df = radar_df.set_index('produto')
fig_heatmap = px.imshow(heatmap_df, color_continuous_scale='viridis', aspect='auto',
                       labels=dict(x='Métrica', y='Produto', color='Valor Normalizado'))
st.plotly_chart(fig_heatmap, use_container_width=True)

# 4. Gráfico de Ranking (Score Composto)
st.header('4. Gráfico de Ranking (Score Composto)')

# Exemplo de score composto: 50% acurácia, 30% resolução, 20% cobertura temporal
radar_df['score'] = 0.5*radar_df['acuracia'] + 0.3*radar_df['resolucao'] + 0.2*radar_df['cobertura_temporal']
ranked = radar_df.sort_values('score', ascending=False)
fig_score = px.bar(ranked, x='score', y='produto', orientation='h', color='score', color_continuous_scale='Blues')
st.plotly_chart(fig_score, use_container_width=True)

# 5. Pequenos Múltiplos (Small Multiples)
st.header('5. Pequenos Múltiplos')

small_multiples = pd.melt(df, id_vars=['produto'], value_vars=eixos, var_name='Métrica', value_name='Valor')
fig_sm = px.bar(small_multiples, x='produto', y='Valor', facet_col='Métrica', color='produto',
                category_orders={'Métrica': eixos})
st.plotly_chart(fig_sm, use_container_width=True)

# 6. Disponibilidade de dados ao longo do tempo (dinâmico)
st.header('6. Disponibilidade de Dados ao Longo do Tempo')

if 'disponibilidade' in df.columns:
    # Corrigir: garantir que a coluna 'disponibilidade' seja lista de anos (não string ou array 2D)
    anos = list(range(2010, 2025))
    disp_matrix = np.zeros((len(df), len(anos)))
    for i, disp in enumerate(df['disponibilidade']):
        # Se for string, converter para lista
        if isinstance(disp, str):
            try:
                disp = ast.literal_eval(disp)
            except Exception:
                disp = []
        # Se for float ou valor único, transformar em lista
        if isinstance(disp, (int, float)):
            disp = [int(disp)]
        for ano in disp:
            if isinstance(ano, (int, float)) and int(ano) in anos:
                disp_matrix[i, anos.index(int(ano))] = 1
    fig_disp = px.imshow(disp_matrix, aspect='auto',
                        labels=dict(x='Ano', y='Produto', color='Disponível'),
                        x=anos, y=df['produto'])
    st.plotly_chart(fig_disp, use_container_width=True)
else:
    st.info('Coluna "disponibilidade" não encontrada no dataset.')
