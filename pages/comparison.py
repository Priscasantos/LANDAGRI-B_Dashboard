import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import ast
from utils import safe_download_image
from plots import (
    plot_resolucao_acuracia,
    plot_timeline,
    plot_annual_coverage_multiselect,
    plot_classes_por_iniciativa,
    plot_distribuicao_classes,
    plot_distribuicao_metodologias,
    plot_acuracia_por_metodologia
)
from tools.charts import (
    create_comparison_matrix,
    create_improved_bubble_chart,
    create_ranking_chart
)
from tools.tables import gap_analysis, safe_dataframe_display

def run():
    # Carregar dados originais e preparar para filtros
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state:
        from data import load_data, prepare_plot_data
        df_loaded, metadata_loaded = load_data(
            "initiative_data/initiatives_processed.csv",
            "initiative_data/metadata_processed.json"
        )
        st.session_state.df_original = df_loaded
        st.session_state.metadata = metadata_loaded
        st.session_state.df_prepared_initial = prepare_plot_data(df_loaded.copy())

    df = st.session_state.df_prepared_initial
    meta_geral = st.session_state.metadata
    df_geral_original = st.session_state.df_original

    # Filtros modernos no topo da página
    st.markdown("### 🔎 Filtros de Iniciativas")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tipos = df["Tipo"].unique().tolist()
        selected_types = st.multiselect("Tipo", options=tipos, default=tipos)
    with col2:
        min_res, max_res = int(df["Resolução (m)"].min()), int(df["Resolução (m)"].max())
        selected_res = st.slider("Resolução (m)", min_value=min_res, max_value=max_res, value=(min_res, max_res))
    with col3:
        min_acc, max_acc = int(df["Acurácia (%)"].min()), int(df["Acurácia (%)"].max())
        selected_acc = st.slider("Acurácia (%)", min_value=min_acc, max_value=max_acc, value=(min_acc, max_acc))
    with col4:
        metodologias = df["Metodologia"].unique().tolist()
        selected_methods = st.multiselect("Metodologia", options=metodologias, default=metodologias)

    # Aplicar filtros
    filtered_df = df[
        (df["Tipo"].isin(selected_types)) &
        (df["Resolução (m)"].between(selected_res[0], selected_res[1])) &
        (df["Acurácia (%)"].between(selected_acc[0], selected_acc[1])) &
        (df["Metodologia"].isin(selected_methods))
    ]
    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa corresponde aos filtros selecionados. Ajuste os filtros para visualizar os dados.")
        st.stop()

    df_filt = filtered_df    # Otimizações de performance
    st.markdown("### ⚡ Configurações de Performance")
    col_perf1, col_perf2, col_perf3 = st.columns(3)
    
    with col_perf1:
        max_records = st.selectbox(
            "Máximo de registros:", 
            [10, 25, 50, 100, 200], 
            index=2,  # Default: 50
            help="Limitar registros melhora a performance"
        )
    
    with col_perf2:
        use_cache = st.checkbox("Cache habilitado", value=True, help="Cache acelera carregamento")
    
    with col_perf3:
        show_loading = st.checkbox("Indicadores de carregamento", value=True)    # Aplicar limitação de dados para performance
    if len(df_filt) > max_records:
        df_filt_limited = df_filt.nlargest(max_records, 'Acurácia (%)')
        st.warning(f"⚠️ Mostrando top {max_records} iniciativas (de {len(df_filt)} total) para melhor performance")
    else:
        df_filt_limited = df_filt.copy()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Barras Duplas",
        "🎯 Resolução vs Acurácia",
        "📅 Cobertura Temporal",
        "🏷️ Número de Classes",
        "⚙️ Metodologias"
    ])

    with tab1:
        st.subheader("Barras Duplas: Acurácia x Resolução")
        df_filt_limited['resolucao_norm'] = (1 / df_filt_limited['Resolução (m)']) / (1 / df_filt_limited['Resolução (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filt_limited['Nome'],
            x=df_filt_limited['Acurácia (%)'],
            name='Acurácia (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filt_limited['Nome'],
            x=df_filt_limited['resolucao_norm'] * 100,  # Converter para porcentagem
            name='Resolução (normalizada)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group',
            xaxis_title='Valor (%)',
            yaxis_title='Produto',
            title='Comparação: Acurácia vs Resolução',
            height=max(400, len(df_filt_limited) * 25)
        )
        st.plotly_chart(fig, use_container_width=True)
        safe_download_image(fig, "barras_duplas_comparativo.png", "⬇️ Baixar Gráfico")

    with tab2:
        st.subheader("Resolução Espacial vs Acurácia (Scatter)")
        # Scatterplot moderno
        fig_scatter = px.scatter(
            df_filt_limited,
            x='Resolução (m)',
            y='Acurácia (%)',
            color='Metodologia' if 'Metodologia' in df_filt_limited.columns else None,
            hover_name='Nome',
            size='Classes' if 'Classes' in df_filt_limited.columns else None,
            title="Acurácia vs Resolução Espacial",
            labels={
                'Resolução (m)': 'Resolução Espacial (m)',
                'Acurácia (%)': 'Acurácia (%)',
                'Metodologia': 'Metodologia',
                'Classes': 'Nº de Classes'
            },
            height=500
        )
        fig_scatter.update_traces(marker=dict(size=14, opacity=0.8, line=dict(width=2, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True)
        safe_download_image(fig_scatter, "scatter_resolucao_acuracia.png", "⬇️ Baixar Scatter (PNG)")

        st.subheader("Disponibilidade Temporal das Iniciativas")
        from plots import plot_ano_overlap
        fig_disp = plot_ano_overlap(meta_geral, df_filt_limited)
        st.plotly_chart(fig_disp, use_container_width=True)
        safe_download_image(fig_disp, "disponibilidade_temporal.png", "⬇️ Baixar Disponibilidade (PNG)")

    with tab3:
        st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 Linha do Tempo Geral das Iniciativas</h2></div>', unsafe_allow_html=True)
        fig_timeline = plot_timeline(meta_geral, df_geral_original) 
        st.plotly_chart(fig_timeline, use_container_width=True)
        safe_download_image(fig_timeline, "timeline_geral.png", "⬇️ Baixar Timeline (PNG)")
        
        gap_df = gap_analysis(meta_geral, df_geral_original)
        if not gap_df.empty:
            st.markdown('#### Lacunas Temporais nas Séries (Todas Iniciativas)')
            # Tabela interativa com ordenação e sem índice
            st.dataframe(
                gap_df.sort_values('Maior lacuna temporal', ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Nome", width="large"),
                    "Primeiro Ano": st.column_config.NumberColumn("Primeiro ano de cobertura", format="%d"),
                    "Último Ano": st.column_config.NumberColumn("Último ano de cobertura", format="%d"),
                    "Número de anos com lacuna temporal": st.column_config.NumberColumn("Número de anos com lacuna temporal", format="%d"),
                    "Maior lacuna temporal": st.column_config.NumberColumn("Maior lacuna temporal", format="%d"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="medium")
                }
            )
            # Botão para download da tabela de lacunas temporais
            st.download_button(
                "⬇️ Baixar Tabela de Lacunas Temporais (CSV)",
                data=gap_df.sort_values('Maior lacuna temporal', ascending=False).to_csv(index=False).encode('utf-8'),
                file_name="lacunas_temporais_iniciativas.csv",
                mime="text/csv",
                help="Baixa a tabela completa de lacunas temporais das iniciativas"
            )
        else:
            st.info('Todas as iniciativas possuem séries temporais contínuas ou apenas um ano disponível.')

    with tab4:
        st.subheader("Distribuição do Número de Classes")
        col1_tab3, col2_tab3 = st.columns(2)
        with col1_tab3:
            fig_bar_classes = plot_classes_por_iniciativa(df_filt)
            st.plotly_chart(fig_bar_classes, use_container_width=True)
            safe_download_image(fig_bar_classes, "classes_por_iniciativa.png", "⬇️ Baixar Gráfico Barras (PNG)")
        with col2_tab3:
            fig_hist_classes = plot_distribuicao_classes(df_filt)
            st.plotly_chart(fig_hist_classes, use_container_width=True)
            safe_download_image(fig_hist_classes, "distribuicao_classes.png", "⬇️ Baixar Histograma (PNG)")

    with tab5:
        st.subheader("Distribuição por Metodologias")
        col1_tab4, col2_tab4 = st.columns(2)
        with col1_tab4:
            method_counts = df_filt['Metodologia'].value_counts()
            fig_metodologias = plot_distribuicao_metodologias(method_counts)
            st.plotly_chart(fig_metodologias, use_container_width=True)
            safe_download_image(fig_metodologias, "distribuicao_metodologias.png", "⬇️ Baixar Gráfico Metodologias (PNG)")
        
        with col2_tab4:
            st.markdown("#### Acurácia por Metodologia")
            fig_acuracia_metodologia = plot_acuracia_por_metodologia(df_filt)
            st.plotly_chart(fig_acuracia_metodologia, use_container_width=True)
            safe_download_image(fig_acuracia_metodologia, "acuracia_por_metodologia.png", "⬇️ Baixar Acurácia Metodologia (PNG)")

    # Seção de Performance e Estatísticas
    st.markdown("---")
    st.markdown("### 📊 Estatísticas de Performance")
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        total_records = len(df_geral_original)
        filtered_records = len(df_filt)
        st.metric("Total de Iniciativas", total_records, delta=None)
    
    with col_stats2:
        displayed_records = len(df_filt_limited)
        st.metric("Registros Exibidos", displayed_records, delta=f"-{filtered_records - displayed_records}" if filtered_records > displayed_records else None)
    
    with col_stats3:
        cache_info = "✅ Ativo" if use_cache else "❌ Desabilitado"
        st.metric("Cache", cache_info, delta=None)
    
    with col_stats4:
        perf_mode = f"Máx {max_records}"
        st.metric("Limite Performance", perf_mode, delta=None)

    st.info(f"""
        **📈 Análise atual:**
        - **Produtos analisados:** {len(df_filt_limited)} iniciativas (filtradas)
        - **Métricas avaliadas:** Acurácia, Resolução, Classes, Metodologia, Escopo
        - **Performance:** Dados limitados a {max_records} registros para otimização
        
        **💡 Funcionalidades:**
        - Filtros interativos por tipo, resolução, acurácia e metodologia
        - Normalização automática de dados para comparação
        - Tratamento robusto de dados ausentes
        - Downloads disponíveis para todos os gráficos principais
        - Cache inteligente para melhor performance
        
        **🧪 Testes de visualizações:** Movidos para sistema separado em `/tests/teste_graficos.py`
        """)
    
    # Dicas de performance
    with st.expander("💡 Dicas para Melhor Performance"):
        st.markdown("""
        **Para melhorar a velocidade do dashboard:**
        
        1. **Reduzir dados:** Use filtros para reduzir o número de iniciativas analisadas
        2. **Limite de registros:** Configure um limite menor (10-25) para visualizações complexas
        3. **Cache:** Mantenha o cache habilitado para evitar recálculos
        4. **Visualização simples:** Use "Coordenadas Paralelas" para análises rápidas
        5. **Fechar abas:** Feche abas não utilizadas para liberar memória
        
        **Visualizações por complexidade:**
        - 📊 **Coordenadas Paralelas**: Mais rápido (até 100+ registros)
        - 🎯 **Radar**: Médio (máximo 15 registros)
        - 📋 **Matriz**: Complexo (até 10 registros)
        """)
        
    # Botão para limpar cache
    if st.button("🧹 Limpar Cache", help="Limpa o cache para forçar atualização dos dados"):
        st.cache_data.clear()
        st.success("Cache limpo com sucesso! A próxima visualização será regenerada.")
