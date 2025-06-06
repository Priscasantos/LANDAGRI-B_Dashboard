import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import ast
from utils import safe_download_image
from tests.teste_graficos import run_test_acuracia_aprimorada

def run():
    st.title('📊 Comparativo Visual de Produtos LULC')

    # Carregar dados processados se não estiverem no session_state
    if 'df_geral' not in st.session_state or st.session_state.df_geral.empty:
        from data import load_data
        df_loaded, metadata_loaded = load_data(
            os.path.join("initiative_data", "initiatives_processed.csv"),
            os.path.join("initiative_data", "metadata_processed.json")
        )
        if df_loaded is not None and not df_loaded.empty:
            st.session_state.df_geral = df_loaded
            st.session_state.metadata = metadata_loaded
        else:
            st.warning("⚠️ Dados não encontrados. Verifique os arquivos de dados processados.")
            st.stop()
    df = st.session_state.df_geral.copy()

    required_columns = ['Nome', 'Acurácia (%)', 'Resolução (m)', 'Classes']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Colunas faltando no dataset: {missing_columns}")
        st.info("Colunas disponíveis: " + ", ".join(df.columns.tolist()))
        return

    tab1, tab2, tab3 = st.tabs([
        "📊 Barras Duplas",
        "📈 Análise de Acurácia Aprimorada",
        "📋 Tabela"
    ])

    with tab1:
        # Barras Duplas: Acurácia x Resolução
        df['resolucao_norm'] = (1 / df['Resolução (m)']) / (1 / df['Resolução (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df['Nome'],
            x=df['Acurácia (%)'],
            name='Acurácia (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df['Nome'],
            x=df['resolucao_norm'] * 100,  # Converter para porcentagem
            name='Resolução (normalizada)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group', 
            xaxis_title='Valor (%)', 
            yaxis_title='Produto',
            title='Comparação: Acurácia vs Resolução',
            height=max(400, len(df) * 25)
        )
        st.plotly_chart(fig, use_container_width=True)
        safe_download_image(fig, "barras_duplas.png", "⬇️ Baixar Gráfico")

    with tab2:
        # Análise de Acurácia Aprimorada (Ranking, Scatter, Heatmap, etc)
        st.subheader('📊 Análise de Acurácia - Visualizações Aprimoradas')
        # Aproveita a função do teste para mostrar as opções de análise aprimorada
        # Adapta para o DataFrame do dashboard
        from tests.teste_graficos import run_test_acuracia_aprimorada as run_acuracia
        # Renomeia colunas para compatibilidade
        df_teste = df.rename(columns={
            'Nome': 'produto',
            'Acurácia (%)': 'acuracia',
            'Resolução (m)': 'resolucao',
            'Classes': 'num_classes',
            'Metodologia': 'metodologia',
            'Escopo': 'escopo',
            'Anos Disponíveis': 'disponibilidade',
            'Categoria Resolução': 'categoria_resolucao',
            'Score Geral': 'score_geral'
        })
        run_acuracia(df_teste, show_loading=False)

    with tab3:
        st.dataframe(df, use_container_width=True)
        st.header('📈 Resumo Estatístico')
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            st.dataframe(df[numeric_columns].describe(), use_container_width=True)
        else:
            st.warning("Nenhuma coluna numérica encontrada para estatísticas.")

if __name__ == "__main__":
    run()
