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
            "initiative_data/initiatives_comparison.csv",
            "initiative_data/initiative_meta.json"
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

    df_filt = filtered_df

    tab1, tab2, tab3, tab4, tab_teste = st.tabs(
        ["🎯 Resolução vs Acurácia", "📅 Cobertura Temporal", "🏷️ Número de Classes", "⚙️ Metodologias", "🧪 Teste Gráficos"]
    )
    
    with tab1:
        st.subheader("Resolução Espacial vs Acurácia")
        fig_res_acc = plot_resolucao_acuracia(df_filt)
        st.plotly_chart(fig_res_acc, use_container_width=True)
        safe_download_image(fig_res_acc, "resolucao_acuracia.png", "⬇️ Baixar Gráfico (PNG)")
        st.download_button("⬇️ Baixar Tabela (CSV)", data=df_filt[['Nome', 'Resolução (m)', 'Acurácia (%)']].to_csv(index=False).encode('utf-8'), file_name="tabela_resolucao_acuracia.csv", mime="text/csv")
        if not df_filt.empty:
            best_accuracy = df_filt.loc[df_filt["Acurácia (%)"].idxmax()]
            best_resolution = df_filt.loc[df_filt["Resolução (m)"].idxmin()]
            col1_tab, col2_tab = st.columns(2)
            with col1_tab:
                st.info(f"🏆 **Maior Acurácia:** {best_accuracy['Nome']} ({best_accuracy['Acurácia (%)']}%)")
            with col2_tab:
                nome_val = best_resolution['Nome']
                res_val = best_resolution['Resolução (m)']
                st.info(f"🔍 **Melhor Resolução:** {nome_val} ({res_val}m)")

    with tab2:
        st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 Linha do Tempo Geral das Iniciativas</h2></div>', unsafe_allow_html=True)
        fig_timeline = plot_timeline(meta_geral, df_geral_original) 
        st.plotly_chart(fig_timeline, use_container_width=True)
        safe_download_image(fig_timeline, "timeline_geral.png", "⬇️ Baixar Timeline (PNG)")
        st.subheader('Cobertura Anual por Iniciativa (Seleção Múltipla)')
        default_annual_selection = df_filt['Nome'].tolist()[:min(3, len(df_filt['Nome'].tolist()))]
        multi_inits_annual = st.multiselect(
            'Selecione iniciativas para visualizar a cobertura anual:',
            options=df_filt['Nome'].tolist(),
            default=default_annual_selection,
            help='Selecione uma ou mais iniciativas para comparar a cobertura anual',
            key="analises_annual_coverage_select"
        )
        if multi_inits_annual:
            fig_annual = plot_annual_coverage_multiselect(meta_geral, df_filt, multi_inits_annual)
            st.plotly_chart(fig_annual, use_container_width=True)
            safe_download_image(fig_annual, "cobertura_anual_selecionada.png", "⬇️ Baixar Cobertura (PNG)")
        gap_df = gap_analysis(meta_geral, df_geral_original)
        if not gap_df.empty:
            st.markdown('#### Lacunas Temporais nas Séries (Todas Iniciativas)')
            st.markdown(gap_df.sort_values('Maior Lacuna (anos)', ascending=False).to_html(escape=False), unsafe_allow_html=True)
        else:
            st.info('Todas as iniciativas possuem séries temporais contínuas ou apenas um ano disponível.')

    with tab3:
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

    with tab4:
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

    with tab_teste:
        st.header("🧪 Teste - Novos Gráficos Comparativos")
        st.markdown("Esta aba contém os novos gráficos sugeridos para avaliação.")

        # Preparar dados para teste com mapeamento correto
        df_teste = df_filt.copy()
        
        # Mapear colunas para nomes mais simples
        column_mapping = {
            'Nome': 'produto',
            'Acurácia (%)': 'acuracia',
            'Resolução (m)': 'resolucao',
            'Classes': 'num_classes',
            'Metodologia': 'metodologia',
            'Escopo': 'escopo',
            'Anos Disponíveis': 'disponibilidade',
            'Categoria Resolução': 'categoria_resolucao',
            'Score Geral': 'score_geral'
        }
        
        df_teste = df_teste.rename(columns=column_mapping)

        if df_teste.empty:
            st.warning("Não há dados para exibir com os filtros atuais.")
            return

        # Função para processar disponibilidade de anos
        def processar_disponibilidade_para_range(disp_item):
            if pd.isna(disp_item):
                return []

            if isinstance(disp_item, str):
                try:
                    # Tentar processar como range (ex: "2015-2023")
                    if '-' in disp_item:
                        parts = disp_item.split('-')
                        if len(parts) == 2:
                            start, end = int(parts[0]), int(parts[1])
                            return list(range(start, end + 1))
                    
                    # Tentar avaliar como lista Python
                    evaluated = ast.literal_eval(disp_item)
                    if isinstance(evaluated, list):
                        return [int(y) for y in evaluated if isinstance(y, (int, float, np.number))]
                    elif isinstance(evaluated, (int, float, np.number)):
                        return [int(evaluated)]
                except (ValueError, SyntaxError, TypeError):
                    pass
                return []
            elif isinstance(disp_item, (int, float, np.number)):
                return [int(disp_item)]
            elif isinstance(disp_item, list):
                return [int(y) for y in disp_item if isinstance(y, (int, float, np.number))]
            return []

        # 1. Barras Horizontais Duplas
        st.subheader('1. Barras Horizontais Duplas: Acurácia x Resolução Espacial')
        if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
            df_teste_copy = df_teste.dropna(subset=['acuracia', 'resolucao'])
            if not df_teste_copy.empty:
                df_teste_copy['resolucao_norm'] = 100 * (1 / df_teste_copy['resolucao']) / (1 / df_teste_copy['resolucao']).max()
                fig_barras_duplas = go.Figure()
                fig_barras_duplas.add_trace(go.Bar(
                    y=df_teste_copy['produto'], 
                    x=df_teste_copy['acuracia'], 
                    name='Acurácia (%)', 
                    orientation='h', 
                    marker_color='royalblue'
                ))
                fig_barras_duplas.add_trace(go.Bar(
                    y=df_teste_copy['produto'], 
                    x=df_teste_copy['resolucao_norm'], 
                    name='Resolução (normalizada)', 
                    orientation='h', 
                    marker_color='orange'
                ))
                fig_barras_duplas.update_layout(
                    barmode='group', 
                    xaxis_title='Valor', 
                    yaxis_title='Produto',
                    title='Comparação: Acurácia vs Resolução (normalizada)'
                )
                st.plotly_chart(fig_barras_duplas, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico de barras duplas.")
        else:
            st.info("Colunas 'acuracia' ou 'resolucao' não encontradas.")

        # 2. Gráfico de Radar
        st.subheader('2. Gráfico de Radar (Spider Chart)')
        eixos_radar = ['acuracia', 'resolucao', 'num_classes']
        colunas_presentes_radar = [e for e in eixos_radar if e in df_teste.columns]
        
        if len(colunas_presentes_radar) >= 2:
            radar_df_teste_completo = df_teste[['produto'] + colunas_presentes_radar].dropna()
            
            if not radar_df_teste_completo.empty:
                radar_df_teste_norm = radar_df_teste_completo.copy()
                for eixo in colunas_presentes_radar:
                    min_val, max_val = radar_df_teste_norm[eixo].min(), radar_df_teste_norm[eixo].max()
                    if max_val - min_val == 0:
                        radar_df_teste_norm[eixo] = 0.5
                    elif eixo == 'resolucao':
                        # Para resolução, inverter: menor valor = melhor
                        radar_df_teste_norm[eixo] = 1 - (radar_df_teste_norm[eixo] - min_val) / (max_val - min_val)
                    else:
                        radar_df_teste_norm[eixo] = (radar_df_teste_norm[eixo] - min_val) / (max_val - min_val)
                
                fig_radar_teste = go.Figure()
                for i, row in radar_df_teste_norm.iterrows():
                    values = row[colunas_presentes_radar].tolist()
                    values.append(values[0])  # Fechar o polígono
                    fig_radar_teste.add_trace(go.Scatterpolar(
                        r=values,
                        theta=colunas_presentes_radar + [colunas_presentes_radar[0]],
                        fill='toself',
                        name=row['produto']
                    ))
                fig_radar_teste.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=True,
                    title='Comparação Multi-dimensional (Radar)'
                )
                st.plotly_chart(fig_radar_teste, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico de radar.")
        else:
            st.info("Métricas insuficientes para o gráfico de radar.")

        # 3. Heatmap de Comparação
        st.subheader('3. Heatmap de Comparação')
        if 'radar_df_teste_norm' in locals() and not radar_df_teste_norm.empty:
            heatmap_df_teste = radar_df_teste_norm.set_index('produto')[colunas_presentes_radar]
            fig_heatmap_teste = px.imshow(
                heatmap_df_teste, 
                color_continuous_scale='viridis', 
                aspect='auto',
                title='Heatmap de Comparação (valores normalizados)',
                labels=dict(x='Métrica', y='Produto', color='Valor Normalizado')
            )
            st.plotly_chart(fig_heatmap_teste, use_container_width=True)
        else:
            st.info("Heatmap depende dos dados normalizados do gráfico de radar.")

        # 4. Gráfico de Pizza - Distribuição por Metodologia
        st.subheader('4. Gráfico de Pizza - Distribuição por Metodologia')
        if 'metodologia' in df_teste.columns:
            metod_counts = df_teste['metodologia'].value_counts()
            if not metod_counts.empty:
                fig_pie_metod = px.pie(
                    values=metod_counts.values, 
                    names=metod_counts.index, 
                    title="Distribuição das Metodologias"
                )
                st.plotly_chart(fig_pie_metod, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o gráfico de pizza de metodologias.")
        else:
            st.info("Coluna 'metodologia' não encontrada.")

        # 5. Gráfico de Pizza - Distribuição por Escopo
        st.subheader('5. Gráfico de Pizza - Distribuição por Escopo')
        if 'escopo' in df_teste.columns:
            escopo_counts = df_teste['escopo'].value_counts()
            if not escopo_counts.empty:
                fig_pie_escopo = px.pie(
                    values=escopo_counts.values, 
                    names=escopo_counts.index,
                    title="Distribuição por Escopo Geográfico",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie_escopo, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o gráfico de pizza de escopo.")
        else:
            st.info("Coluna 'escopo' não encontrada.")

        # 6. Gráfico de Dispersão - Acurácia vs Resolução
        st.subheader('6. Gráfico de Dispersão - Acurácia vs Resolução')
        if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
            scatter_df = df_teste[['produto', 'acuracia', 'resolucao']].dropna()
            if not scatter_df.empty:
                fig_scatter = px.scatter(
                    scatter_df, 
                    x='resolucao', 
                    y='acuracia', 
                    text='produto', 
                    title="Acurácia vs Resolução Espacial",
                    labels={'resolucao': 'Resolução Espacial (m)', 'acuracia': 'Acurácia (%)'}
                )
                fig_scatter.update_traces(textposition="top center")
                fig_scatter.update_layout(height=500)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico de dispersão.")
        else:
            st.info("Colunas necessárias não encontradas para o gráfico de dispersão.")

        # 7. Gráfico de Bolhas - 3 Dimensões
        st.subheader('7. Gráfico de Bolhas - Acurácia vs Resolução vs Classes')
        if all(col in df_teste.columns for col in ['acuracia', 'resolucao', 'num_classes']):
            bubble_df = df_teste[['produto', 'acuracia', 'resolucao', 'num_classes']].dropna()
            if not bubble_df.empty:
                fig_bubble = px.scatter(
                    bubble_df, 
                    x='resolucao', 
                    y='acuracia', 
                    size='num_classes', 
                    hover_name='produto',
                    title="Acurácia vs Resolução (tamanho = nº de classes)",
                    labels={
                        'resolucao': 'Resolução Espacial (m)', 
                        'acuracia': 'Acurácia (%)',
                        'num_classes': 'Número de Classes'
                    }
                )
                fig_bubble.update_layout(height=500)
                st.plotly_chart(fig_bubble, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico de bolhas.")
        else:
            st.info("Colunas necessárias não encontradas para o gráfico de bolhas.")

        # 8. Disponibilidade de Dados ao Longo do Tempo
        st.subheader('8. Disponibilidade de Dados ao Longo do Tempo')
        if 'disponibilidade' in df_teste.columns:
            todos_anos_lista = []
            
            # Coletar todos os anos disponíveis
            for item_disp in df_teste['disponibilidade'].dropna():
                anos_processados = processar_disponibilidade_para_range(item_disp)
                todos_anos_lista.extend(anos_processados)
            
            if todos_anos_lista:
                min_ano_dados = min(todos_anos_lista)
                max_ano_dados = max(todos_anos_lista)
                anos_range = list(range(min_ano_dados, max_ano_dados + 1))
            else:
                anos_range = list(range(2000, 2026))  # Fallback

            # Criar matriz de disponibilidade
            disp_matrix_teste = np.zeros((len(df_teste), len(anos_range)))
            
            for i, disp_raw in enumerate(df_teste['disponibilidade']):
                disp_list = processar_disponibilidade_para_range(disp_raw)
                for ano in disp_list:
                    if ano in anos_range:
                        disp_matrix_teste[i, anos_range.index(ano)] = 1
            
            # Plotar apenas se há dados
            if not df_teste.empty and disp_matrix_teste.size > 0:
                fig_disp_teste = px.imshow(
                    disp_matrix_teste, 
                    aspect='auto',
                    labels=dict(x='Ano', y='Produto', color='Disponível'),
                    x=anos_range, 
                    y=df_teste['produto'],
                    title='Disponibilidade Temporal dos Dados'
                )
                fig_disp_teste.update_layout(height=max(400, len(df_teste) * 30))
                st.plotly_chart(fig_disp_teste, use_container_width=True)
            else:
                st.info("Não foi possível gerar a matriz de disponibilidade temporal.")
        else:
            st.info("Coluna 'disponibilidade' não encontrada.")

        # 9. Box Plot - Distribuição de Acurácia por Metodologia
        st.subheader('9. Box Plot - Distribuição de Acurácia por Metodologia')
        if 'acuracia' in df_teste.columns and 'metodologia' in df_teste.columns:
            box_df = df_teste[['acuracia', 'metodologia']].dropna()
            if not box_df.empty and len(box_df) > 1:
                fig_box = px.box(
                    box_df, 
                    x='metodologia', 
                    y='acuracia',
                    title="Distribuição da Acurácia por Metodologia"
                )
                fig_box.update_xaxes(tickangle=45)
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("Dados insuficientes para o box plot.")
        else:
            st.info("Colunas necessárias não encontradas para o box plot.")

        # 10. Sunburst Chart - Hierarquia de Categorias
        st.subheader('10. Gráfico Sunburst - Hierarquia Metodologia/Escopo')
        if 'metodologia' in df_teste.columns and 'escopo' in df_teste.columns:
            sunburst_df = df_teste.groupby(['metodologia', 'escopo']).size().reset_index(name='count')
            if not sunburst_df.empty:
                fig_sunburst = px.sunburst(
                    sunburst_df, 
                    path=['metodologia', 'escopo'], 
                    values='count',
                    title="Distribuição Hierárquica: Metodologia → Escopo"
                )
                st.plotly_chart(fig_sunburst, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico sunburst.")
        else:
            st.info("Colunas necessárias não encontradas para o gráfico sunburst.")

        # 11. Treemap - Área proporcional
        st.subheader('11. Treemap - Proporção por Categoria de Resolução')
        if 'categoria_resolucao' in df_teste.columns:
            treemap_df = df_teste['categoria_resolucao'].value_counts().reset_index()
            treemap_df.columns = ['Categoria', 'Contagem']
            if not treemap_df.empty:
                fig_treemap = px.treemap(
                    treemap_df, 
                    path=['Categoria'], 
                    values='Contagem',
                    title="Proporção de Produtos por Categoria de Resolução"
                )
                st.plotly_chart(fig_treemap, use_container_width=True)
            else:
                st.info("Dados insuficientes para o treemap.")
        else:
            st.info("Coluna 'categoria_resolucao' não encontrada.")

        # 12. Coordenadas Paralelas - Múltiplas dimensões
        st.subheader('12. Coordenadas Paralelas - Análise Multidimensional')
        numeric_cols = [col for col in ['acuracia', 'resolucao', 'num_classes', 'score_geral'] 
                       if col in df_teste.columns]
        if len(numeric_cols) >= 2 and 'metodologia' in df_teste.columns:
            parallel_df = df_teste[numeric_cols + ['metodologia', 'produto']].dropna()
            if not parallel_df.empty:
                fig_parallel = px.parallel_coordinates(
                    parallel_df, 
                    dimensions=numeric_cols,
                    color='metodologia',
                    title="Coordenadas Paralelas - Comparação Multidimensional"
                )
                st.plotly_chart(fig_parallel, use_container_width=True)
            else:
                st.info("Dados insuficientes para coordenadas paralelas.")
        else:
            st.info("Colunas numéricas insuficientes para coordenadas paralelas.")

        # 13. Violin Plot - Distribuição detalhada de métricas
        st.subheader('13. Violin Plot - Distribuição de Resolução por Metodologia')
        if 'resolucao' in df_teste.columns and 'metodologia' in df_teste.columns:
            violin_df = df_teste[['resolucao', 'metodologia']].dropna()
            if not violin_df.empty and len(violin_df) > 1:
                fig_violin = px.violin(
                    violin_df, 
                    x='metodologia', 
                    y='resolucao',
                    box=True,
                    title="Distribuição da Resolução por Metodologia (Violin Plot)"
                )
                fig_violin.update_xaxes(tickangle=45)
                st.plotly_chart(fig_violin, use_container_width=True)
            else:
                st.info("Dados insuficientes para o violin plot.")
        else:
            st.info("Colunas necessárias não encontradas para o violin plot.")

        # 14. Gráfico de Gantt - Timeline de projetos
        st.subheader('14. Gráfico de Gantt - Timeline dos Projetos')
        if 'disponibilidade' in df_teste.columns:
            gantt_data = []
            for idx, row in df_teste.iterrows():
                anos_list = processar_disponibilidade_para_range(row['disponibilidade'])
                if len(anos_list) > 0:
                    gantt_data.append({
                        'Task': row['produto'],
                        'Start': f"{min(anos_list)}-01-01",
                        'Finish': f"{max(anos_list)}-12-31",
                        'Resource': row.get('metodologia', 'Unknown')
                    })
            
            if gantt_data:
                gantt_df = pd.DataFrame(gantt_data)
                gantt_df['Start'] = pd.to_datetime(gantt_df['Start'])
                gantt_df['Finish'] = pd.to_datetime(gantt_df['Finish'])
                
                fig_gantt = px.timeline(
                    gantt_df,
                    x_start="Start", 
                    x_end="Finish", 
                    y="Task",
                    color="Resource",
                    title="Timeline de Disponibilidade dos Dados (Gantt)"
                )
                fig_gantt.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                st.info("Não foi possível criar o gráfico de Gantt com os dados disponíveis.")
        else:
            st.info("Coluna 'disponibilidade' não encontrada para o gráfico de Gantt.")

        # 15. Gráfico 3D - Scatter 3D
        st.subheader('15. Gráfico 3D - Acurácia vs Resolução vs Classes')
        if all(col in df_teste.columns for col in ['acuracia', 'resolucao', 'num_classes']):
            scatter3d_df = df_teste[['produto', 'acuracia', 'resolucao', 'num_classes', 'metodologia']].dropna()
            if not scatter3d_df.empty:
                fig_3d = px.scatter_3d(
                    scatter3d_df,
                    x='acuracia',
                    y='resolucao', 
                    z='num_classes',
                    color='metodologia',
                    hover_name='produto',
                    title="Visualização 3D: Acurácia × Resolução × Número de Classes",
                    labels={
                        'acuracia': 'Acurácia (%)',
                        'resolucao': 'Resolução (m)',
                        'num_classes': 'Número de Classes'
                    }
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico 3D.")
        else:
            st.info("Colunas necessárias não encontradas para o gráfico 3D.")

        # 16. Mapa de Densidade (Density Heatmap)
        st.subheader('16. Mapa de Densidade - Acurácia vs Resolução')
        if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
            density_df = df_teste[['acuracia', 'resolucao']].dropna()
            if not density_df.empty and len(density_df) > 2:
                fig_density = px.density_heatmap(
                    density_df,
                    x='resolucao',
                    y='acuracia',
                    title="Mapa de Densidade: Concentração de Iniciativas por Acurácia e Resolução"
                )
                st.plotly_chart(fig_density, use_container_width=True)
            else:
                st.info("Dados insuficientes para o mapa de densidade.")
        else:
            st.info("Colunas necessárias não encontradas para o mapa de densidade.")        # Informações de resumo
        st.markdown("---")
        st.subheader("📊 Resumo dos Gráficos Testados")
        
        # Contadores dinâmicos
        charts_implemented = [
            "Barras Horizontais Duplas", "Gráfico de Radar", "Heatmap de Comparação",
            "Pizza - Metodologia", "Pizza - Escopo", "Dispersão", "Bolhas 3D",
            "Timeline de Disponibilidade", "Box Plot", "Sunburst", "Treemap",
            "Coordenadas Paralelas", "Violin Plot", "Gantt Chart", "Scatter 3D", "Mapa de Densidade"
        ]
        
        chart_categories = {
            "Comparativos": ["Barras duplas", "Radar", "Heatmap", "Coordenadas Paralelas"],
            "Categóricos": ["Pizza (2 tipos)", "Sunburst", "Treemap"],
            "Relacionais": ["Dispersão", "Bolhas 3D", "Scatter 3D"],
            "Distribuição": ["Box Plot", "Violin Plot", "Mapa de Densidade"],
            "Temporais": ["Timeline", "Gantt Chart"],
            "Multidimensionais": ["Radar", "Coordenadas Paralelas", "Scatter 3D"]
        }
        
        st.success(f"""
        **✅ Total de gráficos implementados:** {len(charts_implemented)}
        
        **🎨 Tipos de visualização por categoria:**
        """)
        
        for category, charts in chart_categories.items():
            st.write(f"**{category}:** {', '.join(charts)}")
        
        st.info(f"""
        **📈 Análise atual:**
        - **Produtos analisados:** {len(df_teste)} iniciativas
        - **Métricas avaliadas:** Acurácia, Resolução, Classes, Metodologia, Escopo
        - **Período temporal:** Baseado em dados de disponibilidade
        
        **💡 Funcionalidades:**
        - Filtros interativos por tipo, resolução, acurácia e metodologia
        - Normalização automática de dados para comparação
        - Processamento de ranges temporais (ex: "2015-2023")
        - Tratamento robusto de dados ausentes
        - Downloads disponíveis para todos os gráficos principais
        """)
