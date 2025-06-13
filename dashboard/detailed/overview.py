import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys
import os
from pathlib import Path

def run():
    # Adicionar scripts ao path se necessário
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
      # Importar módulos localmente
    try:
        from scripts.data_generation.data_processing import load_data, prepare_plot_data
        from scripts.utilities.utils import safe_download_image
    except ImportError as e:
        st.error(f"Erro ao importar módulos: {e}")
        st.stop()
    
    # Carregar dados originais e preparar para filtros
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state:
        df_loaded, metadata_loaded = load_data(
            "data/processed/initiatives_processed.csv",
            "data/processed/metadata_processed.json"
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
    
    # Adicionar link para comparações detalhadas
    st.markdown("---")
    st.info("💡 **Para comparações detalhadas entre múltiplas iniciativas**, acesse a página **'🔍 Análises Detalhadas'** no menu lateral.")
    st.markdown("---")

    # Adicionar gráfico de densidade temporal
    st.subheader("🌊 Densidade Temporal de Iniciativas LULC")
    
    if meta:
        # Criar dados de densidade usando metadados
        density_data = []
        all_years = set()
        
        for nome, meta_item in meta.items():
            if 'anos_disponiveis' in meta_item and meta_item['anos_disponiveis']:
                for ano in meta_item['anos_disponiveis']:
                    density_data.append({'nome': nome, 'ano': ano})
                    all_years.add(ano)
        
        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df['ano'].value_counts().sort_index()
            
            # Gráfico de densidade por ano (linha + área)
            fig_density_line = go.Figure()
            fig_density_line.add_trace(go.Scatter(
                x=year_counts.index,
                y=year_counts.values,
                mode='lines+markers',
                fill='tonexty',
                name='Iniciativas Ativas',
                line=dict(color='rgba(0,150,136,0.8)', width=3),
                marker=dict(size=8, color='rgba(0,150,136,1)')
            ))
            
            fig_density_line.update_layout(
                title='📊 Densidade Temporal: Número de Iniciativas por Ano (1985-2024)',
                xaxis_title='Ano',
                yaxis_title='Número de Iniciativas Ativas',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_density_line, use_container_width=True)
            # Tentativa de download da imagem
            try:
                safe_download_image(fig_density_line, "densidade_temporal_overview.png", "⬇️ Baixar Densidade Temporal (PNG)")
            except NameError:
                # Fallback se safe_download_image não estiver disponível
                st.info("Função de download não disponível")
            
            # Métricas de densidade temporal
            col1_temp, col2_temp, col3_temp, col4_temp = st.columns(4)
            with col1_temp:
                st.metric("🗓️ Primeiro Ano", min(all_years))
            with col2_temp:
                st.metric("📅 Último Ano", max(all_years))
            with col3_temp:
                st.metric("🎯 Pico de Atividade", f"{max(year_counts.values)} iniciativas")
            with col4_temp:
                st.metric("📈 Média por Ano", f"{np.mean(np.array(year_counts.values)):.1f}")
        else:
            st.info("Dados temporais não disponíveis nos metadados.")
    else:
        st.error("Metadados não disponíveis para análise temporal.")

    st.markdown("---")
