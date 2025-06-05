import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import safe_download_image

def run():
    if 'filtered_df' not in st.session_state or st.session_state.filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa corresponde aos filtros selecionados na página principal. Ajuste os filtros para visualizar os dados.")
        st.stop()
    df_filt = st.session_state.filtered_df
    default_multi_selection = df_filt["Nome"].tolist()[:min(3, len(df_filt['Nome'].tolist()))]
    if len(default_multi_selection) < 2 and len(df_filt["Nome"].tolist()) >=2:
        default_multi_selection = df_filt["Nome"].tolist()[:2]
    elif len(df_filt["Nome"].tolist()) < 2:
        default_multi_selection = df_filt["Nome"].tolist()
    selected_inits_multi = st.multiselect(
        "Selecione 2 ou mais iniciativas para comparar:",
        options=df_filt["Nome"].tolist(),
        default=default_multi_selection,
        help="Selecione duas ou mais iniciativas para comparação detalhada",
        key="comparacao_multi_compare_select"
    )
    if len(selected_inits_multi) >= 2:
        categories_radar = ["Acurácia (%)", "Resolução (m)", "Classes"]
        fig_radar_multi = go.Figure()
        def normalize_for_radar_multi(value, column, df_source):
            if column not in df_source.columns or not pd.api.types.is_numeric_dtype(df_source[column]):
                return 50
            min_val = df_source[column].min()
            max_val = df_source[column].max()
            if max_val == min_val: return 50 
            if column == "Resolução (m)": 
                return (max_val - value) / (max_val - min_val) * 100
            else: 
                return (value - min_val) / (max_val - min_val) * 100
        for nome_init in selected_inits_multi:
            data_init = df_filt[df_filt["Nome"] == nome_init].iloc[0]
            values_radar = [normalize_for_radar_multi(data_init.get(cat_r), cat_r, df_filt) for cat_r in categories_radar]
            fig_radar_multi.add_trace(go.Scatterpolar(
                r=values_radar + [values_radar[0]], 
                theta=categories_radar + [categories_radar[0]],
                fill='toself',
                name=nome_init
            ))
        fig_radar_multi.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Comparação em Gráfico Radar (Valores Normalizados)",
            height=500,
            font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar_multi, use_container_width=True)
        safe_download_image(fig_radar_multi, "radar_multi_iniciativas.png", "⬇️ Baixar Radar (PNG)")
        comp_cols_multi = ['Acurácia (%)', 'Resolução (m)', 'Classes', 'Frequência Temporal', 'Metodologia', 'Escopo', 'Anos Disponíveis']
        valid_comp_cols_multi = [col for col in comp_cols_multi if col in df_filt.columns]
        comp_df_multi = df_filt[df_filt['Nome'].isin(selected_inits_multi)][['Nome'] + valid_comp_cols_multi].set_index('Nome').T
        st.markdown("### Tabela Comparativa (Multi-Iniciativas)")
        st.dataframe(comp_df_multi.astype(str))
        st.download_button("⬇️ Baixar Tabela (CSV)", data=comp_df_multi.to_csv().encode('utf-8'), file_name="tabela_comparativa_multi.csv", mime="text/csv")
    elif selected_inits_multi and len(selected_inits_multi) < 2:
        st.info("ℹ️ Selecione pelo menos duas iniciativas para a comparação.")
    elif not selected_inits_multi:
        st.info("ℹ️ Selecione iniciativas no menu acima para visualizar a comparação.")
