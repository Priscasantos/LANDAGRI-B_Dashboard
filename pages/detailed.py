import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import safe_download_image
import os
import sys

def run():
    st.header("🔍 Análises Detalhadas - Comparações Personalizadas")
    st.markdown("Selecione duas ou mais iniciativas para análises comparativas detalhadas.")
    
    if 'df_geral' not in st.session_state or st.session_state.df_geral.empty:
        # Tentar carregar dados processados diretamente
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from data import load_data
        df_loaded, metadata_loaded = load_data(
            os.path.join("initiative_data", "initiatives_processed.csv"),
            os.path.join("initiative_data", "metadata_processed.json")
        )
        if df_loaded is not None and not df_loaded.empty:
            st.session_state.df_geral = df_loaded
            st.session_state.metadata = metadata_loaded
        else:
            st.warning("⚠️ Dados não encontrados. Execute a página principal (app.py) primeiro.")
            st.stop()
    df_geral = st.session_state.df_geral
    
    # Seleção de iniciativas para comparação
    selected_initiatives = st.multiselect(
        "🎯 Selecione as iniciativas para comparar:",
        options=df_geral["Nome"].tolist(),
        default=df_geral["Nome"].tolist()[:min(3, len(df_geral))],
        help="Escolha 2 ou mais iniciativas para análise comparativa detalhada"
    )
    
    if len(selected_initiatives) < 2:
        st.info("👈 Selecione pelo menos duas iniciativas no menu acima para começar a análise.")
        return
    
    # Filtrar dados para as iniciativas selecionadas
    df_filtered = df_geral[df_geral["Nome"].isin(selected_initiatives)].copy()

    # Abas padronizadas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Barras Duplas",
        "🎯 Radar",
        "🔥 Heatmap",
        "📈 Tabela",
        "📅 Cobertura Anual"
    ])

    with tab1:
        # Barras Duplas
        df_filtered['resolucao_norm'] = (1 / df_filtered['Resolução (m)']) / (1 / df_filtered['Resolução (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered['Nome'],
            x=df_filtered['Acurácia (%)'],
            name='Acurácia (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered['Nome'],
            x=df_filtered['resolucao_norm'] * 100,
            name='Resolução (normalizada)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group', 
            xaxis_title='Valor (%)', 
            yaxis_title='Produto',
            title='Comparação: Acurácia vs Resolução',
            height=max(400, len(df_filtered) * 25)
        )
        st.plotly_chart(fig, use_container_width=True)
        safe_download_image(fig, "barras_duplas_detalhado.png", "⬇️ Baixar Gráfico")

    with tab2:
        # Radar
        radar_columns = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        if len(available_radar_cols) >= 2:
            radar_df = df_filtered[['Nome'] + available_radar_cols].copy()
            for col in available_radar_cols:
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolução (m)':
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Set1
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[available_radar_cols].tolist()
                values_closed = values + [values[0]]
                theta_closed = available_radar_cols + [available_radar_cols[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Nome'],
                    line_color=colors[i % len(colors)]
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Comparação Multi-dimensional (Radar)',
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            safe_download_image(fig_radar, "radar_chart_detalhado.png", "⬇️ Baixar Gráfico")
        else:
            st.warning("Dados insuficientes para o gráfico de radar.")

    with tab3:
        # Heatmap
        if len(available_radar_cols) >= 2:
            heatmap_df = radar_df.set_index('Nome')[available_radar_cols]
            fig_heatmap = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns,
                y=heatmap_df.index,
                color_continuous_scale='viridis',
                aspect='auto',
                title='Heatmap de Performance (valores normalizados)',
                labels=dict(x='Métrica', y='Produto', color='Valor Normalizado')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            safe_download_image(fig_heatmap, "heatmap_detalhado.png", "⬇️ Baixar Gráfico")
        else:
            st.warning("Dados insuficientes para o heatmap.")

    with tab4:
        # Tabela
        st.dataframe(df_filtered, use_container_width=True)

    with tab5:
        st.subheader("Cobertura Anual por Iniciativa (Seleção Múltipla)")
        meta = st.session_state.get('metadata', {})
        if not selected_initiatives:
            st.info("Selecione ao menos uma iniciativa para visualizar a cobertura anual.")
        else:
            from plots import plot_annual_coverage_multiselect
            fig_annual = plot_annual_coverage_multiselect(meta, df_filtered, selected_initiatives)
            st.plotly_chart(fig_annual, use_container_width=True)
            safe_download_image(fig_annual, "cobertura_anual_detalhada.png", "⬇️ Baixar Cobertura (PNG)")
