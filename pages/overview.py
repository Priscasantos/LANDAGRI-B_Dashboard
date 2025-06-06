import streamlit as st
import pandas as pd
from utils import safe_download_image
from tools.radar import plot_radar_comparacao
from tools.tables import safe_dataframe_display

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
    meta = st.session_state.metadata

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

    # Conteúdo principal da página Overview
    # (deixe apenas o conteúdo específico desta página, sem dashboard ou instruções globais)
    st.subheader("📈 Métricas Principais Agregadas")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_accuracy = filtered_df["Acurácia (%)"].mean()
        st.metric("🎯 Acurácia Média", f"{avg_accuracy:.1f}%" if pd.notna(avg_accuracy) else "N/A")
    with col2:
        avg_resolution = filtered_df["Resolução (m)"].mean()
        st.metric("🔬 Resolução Média", f"{avg_resolution:.0f}m" if pd.notna(avg_resolution) else "N/A")
    with col3:
        total_classes = filtered_df["Classes"].sum()
        st.metric("🏷️ Total de Classes", f"{total_classes}" if pd.notna(total_classes) else "N/A")
    with col4:
        global_initiatives = len(filtered_df[filtered_df["Tipo"] == "Global"])
        st.metric("🌍 Iniciativas Globais", f"{global_initiatives}")
    st.markdown("---")

    st.subheader("🔍 Exploração Detalhada por Iniciativa")
    selected_initiative_detailed = st.selectbox(
        "Selecione uma iniciativa para ver detalhes:",
        options=filtered_df["Nome"].tolist(),
        help="Escolha uma iniciativa para ver informações detalhadas",
        key="visao_geral_detailed_select" 
    )
    if selected_initiative_detailed:
        init_data = filtered_df[filtered_df["Nome"] == selected_initiative_detailed].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {}) 

        col1_detail, col2_detail = st.columns([2, 3])
        with col1_detail:
            st.markdown(f"### {selected_initiative_detailed}")
            st.markdown("#### 📊 Métricas Principais")
            metrics_col1, metrics_col2 = st.columns(2)
            with metrics_col1:
                st.metric("🎯 Acurácia", f"{init_data.get('Acurácia (%)', 'N/A')}%")
                st.metric("🏷️ Classes", init_data.get("Classes", "N/A"))
            with metrics_col2:
                st.metric("🔬 Resolução", f"{init_data.get('Resolução (m)', 'N/A')}m")
                st.metric("📅 Frequência", init_data.get("Frequência Temporal", "N/A"))
            st.markdown("#### ⚙️ Informações Técnicas")
            st.info(f"**Tipo:** {init_data.get('Tipo', 'N/A')}")
            st.info(f"**Metodologia:** {init_data.get('Metodologia', 'N/A')}")
            st.info(f"**Escopo:** {init_data.get('Escopo', 'N/A')}")
            st.info(f"**Período:** {init_data.get('Anos Disponíveis', 'N/A')}")
        with col2_detail:
            st.markdown("#### 📋 Detalhes Metodológicos")
            st.markdown("**🔬 Metodologia:**")
            st.write(init_metadata.get("metodologia", "Não disponível"))
            st.markdown("**✅ Validação:**")
            st.success(init_metadata.get("validacao", "Não disponível"))
            st.markdown("**🌍 Cobertura:**")
            st.warning(init_metadata.get("cobertura", "Não disponível"))
            st.markdown("**📡 Fontes de Dados:**")
            st.info(init_metadata.get("fonte_dados", "Não disponível"))
    st.markdown("---")

    # Comparação Direta Entre Duas Iniciativas
    if len(filtered_df) > 1:
        st.markdown("---")
        st.subheader("⚡ Comparação Direta entre Iniciativas")
        col1_comp, col2_comp = st.columns(2)
        initiative_names = filtered_df["Nome"].tolist()
        with col1_comp:
            init1 = st.selectbox(
                "Primeira iniciativa:",
                options=initiative_names,
                key="visao_geral_direct_comparison1",
            )
        with col2_comp:
            init2 = st.selectbox(
                "Segunda iniciativa:",
                options=initiative_names,
                key="visao_geral_direct_comparison2",
            )
        if init1 and init2 and init1 != init2:
            data_comp = filtered_df[filtered_df["Nome"].isin([init1, init2])]
            if not data_comp.empty:
                data1 = data_comp[data_comp["Nome"] == init1].iloc[0]
                data2 = data_comp[data_comp["Nome"] == init2].iloc[0]
                st.markdown("#### 📊 Comparação de Métricas")
                fig = plot_radar_comparacao(data1, data2, filtered_df, init1, init2)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("#### 📋 Tabela Comparativa")
                comparison_df = data_comp[["Nome", "Acurácia (%)", "Resolução (m)", "Classes", "Frequência Temporal"]]
                safe_dataframe_display(comparison_df)

                # Download links for images
                st.markdown("#### ⬇️ Download das Imagens do Gráfico")
                safe_download_image(fig, f"comparacao_{init1}_vs_{init2}.png", "⬇️ Baixar Comparação (PNG)")
            else:
                st.warning("⚠️ Dados para comparação não encontrados.")
        else:
            st.info("🔄 Selecione duas iniciativas diferentes para comparar.")
    else:
        st.info("⚠️ Pelo menos duas iniciativas são necessárias para comparação direta.")
