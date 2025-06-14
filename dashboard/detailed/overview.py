import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

def run():
    # Adicionar scripts ao path se necessário
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    # Importar módulos localmente
    try:
        from scripts.data_generation.data_wrapper import DataWrapper # Import DataWrapper class
        from scripts.utilities.utils import safe_download_image
    except ImportError as e:
        st.error(f"Erro ao importar módulos: {e}")
        st.stop()
    
    # Initialize DataWrapper
    data_wrapper = DataWrapper()

      # Carregar dados originais e preparar para filtros
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state or 'auxiliary_data' not in st.session_state:
        df_loaded, metadata_loaded, auxiliary_data_loaded = data_wrapper.load_data() # Corrected assignment for three values
        st.session_state.df_original = df_loaded
        st.session_state.metadata = metadata_loaded
        st.session_state.auxiliary_data = auxiliary_data_loaded # Store auxiliary_data
        
        # Corrected call to prepare_plot_data, using the instance method
        prepared_data_dict = data_wrapper.prepare_plot_data(df_loaded.copy(), plot_type="overview")
        st.session_state.df_prepared_initial = prepared_data_dict.get('data', pd.DataFrame()) # Get DataFrame from dict

    df = st.session_state.df_prepared_initial
    meta = st.session_state.metadata

    # Create nome_to_sigla mapping from the main DataFrame
    nome_to_sigla = {}
    if 'df_original' in st.session_state and not st.session_state.df_original.empty and 'Acronym' in st.session_state.df_original.columns and 'Name' in st.session_state.df_original.columns:
        for _, row in st.session_state.df_original.iterrows():
            nome_to_sigla[row['Name']] = row['Acronym']




    # Filtros modernos no topo da página
    st.markdown("### 🔎 Filtros de Iniciativas")
    col1, col2, col3, col4 = st.columns(4)    
    with col1:
        # Ensure df is not empty and 'Type' column exists before accessing unique values
        tipos = df["Type"].unique().tolist() if not df.empty and "Type" in df.columns else []
        selected_types = st.multiselect("Type", options=tipos, default=tipos)
    with col2:
        # Ensure df is not empty and 'Resolution (m)' column exists
        if not df.empty and "Resolution (m)" in df.columns and df["Resolution (m)"].notna().any():
            min_res, max_res = int(df["Resolution (m)"].min()), int(df["Resolution (m)"].max())
            selected_res = st.slider("Resolution (m)", min_value=min_res, max_value=max_res, value=(min_res, max_res))
        else:
            selected_res = st.slider("Resolution (m)", min_value=0, max_value=1000, value=(0, 1000), disabled=True)
            st.caption("Resolution data not available for current selection.")
    with col3:
        # Ensure df is not empty and 'Accuracy (%)' column exists
        if not df.empty and "Accuracy (%)" in df.columns and df["Accuracy (%)"].notna().any():
            min_acc, max_acc = int(df["Accuracy (%)"].min()), int(df["Accuracy (%)"].max())
            selected_acc = st.slider("Accuracy (%)", min_value=min_acc, max_value=max_acc, value=(min_acc, max_acc))
        else:
            selected_acc = st.slider("Accuracy (%)", min_value=0, max_value=100, value=(0,100), disabled=True)
            st.caption("Accuracy data not available for current selection.")
    with col4:
        # Ensure df is not empty and 'Methodology' column exists
        metodologias = df["Methodology"].unique().tolist() if not df.empty and "Methodology" in df.columns else []
        selected_methods = st.multiselect("Methodology", options=metodologias, default=metodologias)    # Aplicar filtros
    filtered_df = df[
        (df["Type"].isin(selected_types)) &
        (df["Resolution (m)"].between(selected_res[0], selected_res[1])) &
        (df["Accuracy (%)"].between(selected_acc[0], selected_acc[1])) &
        (df["Methodology"].isin(selected_methods))
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
        avg_accuracy = filtered_df["Accuracy (%)"].mean()
        st.metric("🎯 Acurácia Média", f"{avg_accuracy:.1f}%" if pd.notna(avg_accuracy) else "N/A")
    with col2:
        avg_resolution = filtered_df["Resolution (m)"].mean()
        st.metric("🔬 Resolução Média", f"{avg_resolution:.0f}m" if pd.notna(avg_resolution) else "N/A")
    with col3:
        total_classes = filtered_df["Classes"].sum()
        st.metric("🏷️ Total de Classes", f"{total_classes}" if pd.notna(total_classes) else "N/A")
    with col4:
        global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"])
        st.metric("🌍 Iniciativas Globais", f"{global_initiatives}")
    st.markdown("---")

    st.subheader("🔍 Exploração Detalhada por Iniciativa")
    selected_initiative_detailed = st.selectbox(
        "Selecione uma iniciativa para ver detalhes:",
        options=filtered_df["Name"].tolist(),
        help="Escolha uma iniciativa para ver informações detalhadas",
        key="visao_geral_detailed_select" 
    )
    if selected_initiative_detailed:
        init_data = filtered_df[filtered_df["Name"] == selected_initiative_detailed].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {})
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(selected_initiative_detailed, selected_initiative_detailed[:10])


        col1_detail, col2_detail = st.columns([2, 3])
        with col1_detail:
            st.markdown(f"### {initiative_acronym}") # Use acronym
            st.markdown("#### 📊 Métricas Principais")
            metrics_col1, metrics_col2 = st.columns(2)
            with metrics_col1:
                st.metric("🎯 Acurácia", f"{init_data.get('Accuracy (%)', 'N/A')}%")
                st.metric("🏷️ Classes", init_data.get("Classes", "N/A"))
            with metrics_col2:
                st.metric("🔬 Resolução", f"{init_data.get('Resolution (m)', 'N/A')}m")
                st.metric("📅 Frequência", init_data.get("Temporal Frequency", "N/A"))
            st.markdown("#### ⚙️ Informações Técnicas")
            st.info(f"**Tipo:** {init_data.get('Type', 'N/A')}")
            st.info(f"**Metodologia:** {init_data.get('Methodology', 'N/A')}")
            st.info(f"**Escopo:** {init_data.get('Scope', 'N/A')}")
            st.info(f"**Período:** {init_data.get('Available Years', 'N/A')}")
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
    
    if meta:        # Criar dados de densidade usando metadados
        density_data = []
        all_years = set()
        
        for nome, meta_item in meta.items():
            if 'available_years' in meta_item and meta_item['available_years']:
                for ano in meta_item['available_years']:
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
                marker=dict(size=8, color='rgba(0,150,136,1)')            ))
            
            fig_density_line.update_layout(
                title='📊 Densidade Temporal: Número de Iniciativas por Ano (1985-2024)',
                xaxis_title='Ano',
                yaxis_title='Número de Iniciativas Ativas',
                height=450,
                hovermode='x unified',
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                )
            )
            st.plotly_chart(fig_density_line, use_container_width=True)
            
            # Add download button
            try:
                safe_download_image(fig_density_line, "densidade_temporal_overview.png", "⬇️ Baixar Densidade Temporal (PNG)")
            except NameError:
                st.info("📥 Função de download não disponível")
            
            # Enhanced temporal metrics
            col1_temp, col2_temp, col3_temp, col4_temp = st.columns(4)
            with col1_temp:
                st.metric("🗓️ Primeiro Ano", f"{min(all_years)}")
            with col2_temp:
                st.metric("📅 Último Ano", f"{max(all_years)}")
            with col3_temp:
                peak_year = year_counts.idxmax()
                st.metric("🎯 Pico de Atividade", f"{max(year_counts.values)} iniciativas", f"Em {peak_year}")
            with col4_temp:
                st.metric("📈 Média por Ano", f"{np.mean(np.array(year_counts.values)):.1f}")
            
            # Add timeline details
            st.markdown("#### 📅 Detalhes da Linha Temporal")
            col_timeline1, col_timeline2 = st.columns(2)
            
            with col_timeline1:
                st.markdown("**🚀 Iniciativas Mais Recentes:**")
                recent_initiatives = []
                for nome, meta_item in meta.items():
                    if 'available_years' in meta_item and meta_item['available_years']:
                        latest_year = max(meta_item['available_years'])
                        acronym = nome_to_sigla.get(nome, nome[:10]) # Get acronym
                        recent_initiatives.append((acronym, latest_year, nome)) # Store acronym and original name
                
                # Show top 5 most recent
                recent_initiatives.sort(key=lambda x: x[1], reverse=True)
                for acronym, year, original_name in recent_initiatives[:5]:
                    st.write(f"• **{acronym}** ({year})") # Display acronym
            
            with col_timeline2:
                st.markdown("**📊 Período de Cobertura por Iniciativa:**")
                coverage_info = []
                for nome, meta_item in meta.items():
                    if 'available_years' in meta_item and meta_item['available_years']:
                        years = meta_item['available_years']
                        span = max(years) - min(years) + 1
                        acronym = nome_to_sigla.get(nome, nome[:10]) # Get acronym
                        coverage_info.append((acronym, span, len(years), nome)) # Store acronym and original name
                
                # Show initiatives with longest coverage
                coverage_info.sort(key=lambda x: x[1], reverse=True)
                for acronym, span, count, original_name in coverage_info[:5]:
                    st.write(f"• **{acronym}**: {span} anos ({count} datasets)") # Display acronym
                    
        else:
            st.warning("📅 Dados temporais não foram encontrados nos metadados processados.")
            st.info("💡 **Dica:** Verifique se os metadados contêm informações sobre anos disponíveis para cada iniciativa.")
    else:
        st.error("Metadados não disponíveis para análise temporal.")

    st.markdown("---")
