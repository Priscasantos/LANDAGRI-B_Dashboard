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
        selected_methods = st.multiselect("Metodologia", options=metodologias, default=metodologias)    # Aplicar filtros
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

    df_filt = filtered_df    # Aplicar filtros básicos
    df_filt_limited = df_filt.copy()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Barras Duplas",
        "🎯 Resolução vs Acurácia",
        "📅 Cobertura Temporal",
        "🏷️ Número de Classes",
        "⚙️ Metodologias",
        "🕸️ Análise Radar"
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

    with tab6:
        st.subheader("🕸️ Análise Radar - Comparação Multi-dimensional")
          # Radar chart with top initiatives
        radar_columns = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filt.columns]
        
        if len(available_radar_cols) >= 2 and len(df_filt) >= 2:
            # Allow users to select number of initiatives to compare
            col1_radar, col2_radar = st.columns(2)
            with col1_radar:
                max_initiatives = min(8, len(df_filt))
                if max_initiatives > 2:
                    num_initiatives = st.slider(
                        "Número de iniciativas no radar",
                        min_value=2,
                        max_value=max_initiatives,
                        value=min(5, max_initiatives),
                        help="Selecione quantas iniciativas exibir no gráfico radar"
                    )
                else:
                    # If only 2 initiatives available, don't show slider
                    num_initiatives = max_initiatives
                    st.info(f"Exibindo todas as {max_initiatives} iniciativas disponíveis")
            
            with col2_radar:
                sort_by = st.selectbox(
                    "Ordenar por",
                    options=['Acurácia (%)', 'Resolução (m)', 'Classes'],
                    help="Critério para selecionar as top iniciativas"
                )
            
            # Prepare radar data
            if sort_by == 'Resolução (m)':
                # For resolution, lower is better, so sort ascending
                top_initiatives = df_filt.nsmallest(num_initiatives, sort_by)
            else:
                # For others, higher is better
                top_initiatives = df_filt.nlargest(num_initiatives, sort_by)
            
            radar_df = top_initiatives[['Nome'] + available_radar_cols].copy()
            
            # Normalize data for radar chart (0-1 scale)
            for col in available_radar_cols:
                min_val, max_val = df_filt[col].min(), df_filt[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolução (m)':
                        # Invert resolution (lower is better)
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5
            
            # Create radar chart
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Set1
            
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[available_radar_cols].tolist()
                values_closed = values + [values[0]]  # Close the radar
                theta_closed = available_radar_cols + [available_radar_cols[0]]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Nome'],
                    line_color=colors[i % len(colors)],
                    opacity=0.7
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickmode='array',
                        tickvals=[0, 0.25, 0.5, 0.75, 1],
                        ticktext=['Baixo', 'Médio-Baixo', 'Médio', 'Médio-Alto', 'Alto']
                    )
                ),
                showlegend=True,
                title=f'🎯 Comparação Radar - Top {num_initiatives} por {sort_by}',
                height=600,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            safe_download_image(fig_radar, "radar_comparison.png", "⬇️ Baixar Gráfico Radar (PNG)")
            
            # Show normalized values table
            st.markdown("#### 📊 Valores Normalizados (Escala 0-1)")
            display_df = radar_df.copy()
            for col in available_radar_cols:
                display_df[col] = display_df[col].round(3)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Iniciativa", width="large"),
                    "Acurácia (%)": st.column_config.NumberColumn("Acurácia (norm.)", format="%.3f"),
                    "Resolução (m)": st.column_config.NumberColumn("Resolução (norm.)", format="%.3f", help="Invertido: 1 = melhor resolução"),
                    "Classes": st.column_config.NumberColumn("Classes (norm.)", format="%.3f")
                }
            )
            
            # Insights section
            st.markdown("#### 💡 Insights da Análise Radar")
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                # Find best overall performer
                radar_df['score_total'] = radar_df[available_radar_cols].mean(axis=1)
                best_overall = radar_df.loc[radar_df['score_total'].idxmax(), 'Nome']
                st.success(f"🏆 **Melhor Performance Geral:** {best_overall}")
                
                # Find specialist initiatives
                for col in available_radar_cols:
                    specialist = radar_df.loc[radar_df[col].idxmax(), 'Nome']
                    col_display = "Resolução" if col == "Resolução (m)" else col.replace(" (%)", "")
                    st.info(f"🎯 **Especialista em {col_display}:** {specialist}")
            
            with insights_col2:
                # Performance distribution
                st.markdown("**📈 Distribuição de Performance:**")
                for col in available_radar_cols:
                    avg_performance = radar_df[col].mean()
                    col_display = "Resolução" if col == "Resolução (m)" else col.replace(" (%)", "")
                    performance_level = "Alto" if avg_performance > 0.7 else "Médio" if avg_performance > 0.4 else "Baixo"
                    st.write(f"• **{col_display}:** {performance_level} ({avg_performance:.2f})")
                
                # Balance analysis
                balance_scores = radar_df[available_radar_cols].std(axis=1)
                most_balanced = radar_df.loc[balance_scores.idxmin(), 'Nome']
                st.info(f"⚖️ **Mais Equilibrada:** {most_balanced}")
        
        else:
            if len(df_filt) < 2:
                st.warning("⚠️ São necessárias pelo menos 2 iniciativas para comparação em radar.")
            else:
                st.warning("⚠️ Dados insuficientes para gráfico radar. Verifique se as colunas necessárias estão disponíveis.")
            
            # Show available data info
            st.info("📋 **Dados disponíveis:**")
            st.write(f"• Iniciativas filtradas: {len(df_filt)}")
            st.write(f"• Colunas para radar disponíveis: {available_radar_cols}")
            st.write(f"• Colunas necessárias: {radar_columns}")
