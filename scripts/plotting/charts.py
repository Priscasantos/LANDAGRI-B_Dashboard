import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_comparison_matrix(produtos):
    df = pd.DataFrame([
        {
            'produto': v['nome'],
            'acuracia': v['acuracia_numerica'],
            'resolucao_espacial': v['resolucao_espacial_metros'],
            'classes': v['classes_numero']
        }
        for v in produtos.values()
        if 'acuracia_numerica' in v and 'resolucao_espacial_metros' in v and 'classes_numero' in v
    ])
    matrix_data = df.pivot_table(
        values=['acuracia', 'resolucao_espacial', 'classes'],
        index='produto',
        aggfunc='mean'
    )
    fig = px.imshow(
        matrix_data.T,
        labels=dict(x="Produto", y="Métrica", color="Valor"),
        x=matrix_data.index,
        y=['Acurácia (%)', 'Resolução (m)', 'Nº Classes'],
        color_continuous_scale='RdYlBu_r',
        title='Matriz de Comparação: Múltiplas Métricas'
    )
    return fig

def create_improved_bubble_chart(produtos):
    df = pd.DataFrame([
        {
            'produto': v['nome'],
            'acuracia': v['acuracia_numerica'],
            'resolucao_espacial': v['resolucao_espacial_metros'],
            'classes': v['classes_numero'],
            'metodologia': v.get('metodologia_principal', ''),
            'frequencia_temporal': v.get('frequencia_temporal', ''),
            'cobertura_anos': v.get('anos_cobertura', None)
        }
        for v in produtos.values()
        if 'acuracia_numerica' in v and 'resolucao_espacial_metros' in v and 'classes_numero' in v
    ])
    fig = px.scatter(
        df,
        x='resolucao_espacial',
        y='acuracia',
        size='classes',
        color='metodologia',
        hover_name='produto',
        hover_data=['frequencia_temporal', 'cobertura_anos'],
        title='Resolução vs Acurácia (Tamanho = Nº Classes)',
        labels={
            'resolucao_espacial': 'Resolução Espacial (metros)',
            'acuracia': 'Acurácia (%)'
        }
    )
    fig.update_xaxes(type='linear')
    fig.update_layout(height=600)
    return fig

def create_ranking_chart(produtos):
    df = pd.DataFrame([
        {
            'produto': v['nome'],
            'acuracia': v['acuracia_numerica'],
            'resolucao_espacial': v['resolucao_espacial_metros'],
            'classes': v['classes_numero']
        }
        for v in produtos.values()
        if 'acuracia_numerica' in v and 'resolucao_espacial_metros' in v and 'classes_numero' in v
    ])
    df['score_total'] = (df['acuracia'] * 0.4 + (100 - df['resolucao_espacial'] / 10) * 0.3 + df['classes'] * 0.3)
    df_sorted = df.sort_values('score_total', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Score Acurácia',
        x=df_sorted['acuracia'] * 0.4,
        y=df_sorted['produto'],
        orientation='h',
        marker_color='lightgreen'
    ))
    fig.add_trace(go.Bar(
        name='Score Resolução',
        x=(100 - df_sorted['resolucao_espacial'] / 10) * 0.3,
        y=df_sorted['produto'],
        orientation='h',
        marker_color='lightblue'
    ))
    fig.update_layout(
        barmode='stack',
        title='Ranking de Produtos (Score Composto)',
        xaxis_title='Score Total',
        height=600
    )
    return fig
