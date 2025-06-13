import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import ast
import sys
from pathlib import Path

# Adicionar scripts ao path
current_dir = Path(__file__).parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Importar funções de forma segura
try:
    from scripts.utilities.utils import safe_download_image
except ImportError:
    def safe_download_image(fig, filename, button_text):
        st.info(f"Download available: {filename}")

try:
    from scripts.utilities.english_translations import (
        translate_text, 
        INTERFACE_TRANSLATIONS,
        translate_chart_elements
    )
except ImportError:
    def translate_text(text): return text
    INTERFACE_TRANSLATIONS = {}
    def translate_chart_elements(fig): return fig

try:
    from english_translations import (
        translate_text, 
        INTERFACE_TRANSLATIONS,
        translate_chart_elements
    )
except ImportError:
    def translate_text(text): return text
    INTERFACE_TRANSLATIONS = {}
    def translate_chart_elements(fig): return fig

try:
    from generate_graphics import (
        plot_resolucao_acuracia,
        plot_timeline,
        plot_annual_coverage_multiselect,
        plot_classes_por_iniciativa,
        plot_distribuicao_classes,
        plot_distribuicao_metodologias,
        plot_acuracia_por_metodologia
    )
except ImportError:
    # Placeholders
    def plot_resolucao_acuracia(*args): return go.Figure()
    def plot_timeline(*args): return go.Figure()
    def plot_annual_coverage_multiselect(*args): return go.Figure()
    def plot_classes_por_iniciativa(*args): return go.Figure()
    def plot_distribuicao_classes(*args): return go.Figure()
    def plot_distribuicao_metodologias(*args): return go.Figure()
    def plot_acuracia_por_metodologia(*args): return go.Figure()

try:
    from charts import (
        create_comparison_matrix,
        create_improved_bubble_chart,
        create_ranking_chart
    )
except ImportError:
    # Placeholders
    def create_comparison_matrix(*args): return go.Figure()
    def create_improved_bubble_chart(*args): return go.Figure()
    def create_ranking_chart(*args): return go.Figure()

try:
    from tables import gap_analysis, safe_dataframe_display
except ImportError:
    def gap_analysis(*args): return pd.DataFrame()
    def safe_dataframe_display(*args): pass

def run():
    # Load original data and prepare for filters
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state:
        try:
            from data_processing import load_data, prepare_plot_data
            df_loaded, metadata_loaded = load_data(
                "data/processed/initiatives_processed.csv",
                "data/processed/metadata_processed.json"
            )
        except ImportError:
            st.error("Error loading data. Check if modules are available.")
            return
        st.session_state.df_original = df_loaded
        st.session_state.metadata = metadata_loaded
        st.session_state.df_prepared_initial = prepare_plot_data(df_loaded.copy())

    df = st.session_state.df_prepared_initial
    meta_geral = st.session_state.metadata
    df_geral_original = st.session_state.df_original

    # Create nome to sigla mapping
    nome_to_sigla = {}
    if df_geral_original is not None and not df_geral_original.empty and 'Sigla' in df_geral_original.columns:
        for _, row in df_geral_original.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']

    # Add Display_Name column for consistent sigla usage
    if 'Display_Name' not in df.columns:
        df['Display_Name'] = df['Nome'].map(lambda x: nome_to_sigla.get(x, x[:10]))

    # Modern filters at the top of the page (translated to English)
    st.markdown("### 🔎 Initiative Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tipos = df["Tipo"].unique().tolist()
        selected_types = st.multiselect("Type", options=tipos, default=tipos)
    with col2:
        min_res, max_res = int(df["Resolução (m)"].min()), int(df["Resolução (m)"].max())
        selected_res = st.slider("Resolution (m)", min_value=min_res, max_value=max_res, value=(min_res, max_res))
    with col3:
        min_acc, max_acc = int(df["Acurácia (%)"].min()), int(df["Acurácia (%)"].max())
        selected_acc = st.slider("Accuracy (%)", min_value=min_acc, max_value=max_acc, value=(min_acc, max_acc))
    with col4:
        metodologias = df["Metodologia"].unique().tolist()
        selected_methods = st.multiselect("Methodology", options=metodologias, default=metodologias)    # Apply filters
    filtered_df = df[
        (df["Tipo"].isin(selected_types)) &
        (df["Resolução (m)"].between(selected_res[0], selected_res[1])) &
        (df["Acurácia (%)"].between(selected_acc[0], selected_acc[1])) &
        (df["Metodologia"].isin(selected_methods))
    ]
    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the selected filters. Adjust filters to view data.")
        st.stop()

    df_filt = filtered_df
    # Apply basic filters
    df_filt_limited = df_filt.copy()

    # Tabs with English translations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dual Bars",
        "🎯 Resolution vs Accuracy",
        "📅 Temporal Coverage",
        "🏷️ Number of Classes",
        "⚙️ Methodologies",
        "🕸️ Radar Analysis"
    ])

    with tab1:
        st.subheader("Dual Bars: Accuracy x Resolution")
        df_filt_limited['resolucao_norm'] = (1 / df_filt_limited['Resolução (m)']) / (1 / df_filt_limited['Resolução (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filt_limited['Display_Name'],  # Use siglas for y-axis
            x=df_filt_limited['Acurácia (%)'],
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'        ))
        fig.add_trace(go.Bar(
            y=df_filt_limited['Display_Name'],  # Use siglas for y-axis
            x=df_filt_limited['resolucao_norm'] * 100,  # Convert to percentage
            name='Resolution (normalized)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group',
            xaxis_title='Value (%)',
            yaxis_title='Initiative',
            title='Comparison: Accuracy vs Resolution',
            height=max(400, len(df_filt_limited) * 25)
        )
        st.plotly_chart(fig, use_container_width=True, key="dual_bars_chart")
        safe_download_image(fig, "dual_bars_comparison.png", "⬇️ Download Chart")

        # Enhanced Analysis Features (translated to English)
        st.markdown("---")
        st.markdown("### 📊 Advanced Analysis")
        
        # Methodology Comparative Analysis
        st.markdown("#### 📈 Comparative Analysis by Methodology")
        
        if meta_geral:
            # Create timeline data for methodology analysis
            timeline_data = []
            produto_info = {}
            
            # Map products to get technical characteristics
            if df_geral_original is not None and not df_geral_original.empty:
                for _, row in df_geral_original.iterrows():
                    produto_info[row['Nome']] = {
                        'metodologia': row.get('Metodologia', 'N/A'),
                        'escopo': row.get('Escopo', 'N/A'),
                        'acuracia': row.get('Acurácia (%)', 0),
                        'resolucao': row.get('Resolução (m)', 0)
                    }
            
            # Collect all years from all initiatives
            for nome, meta in meta_geral.items():
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    info = produto_info.get(nome, {})
                    for ano in meta['anos_disponiveis']:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A'),
                            'escopo': info.get('escopo', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                produtos_unicos = sorted(timeline_df['produto'].unique())
                metodologias_unicas = timeline_df['metodologia'].unique()
                
                # Statistics by methodology
                metod_stats = timeline_df.groupby('metodologia').agg({
                    'produto': 'nunique',
                    'ano': ['min', 'max', 'count']
                }).round(1)
                metod_stats.columns = ['Produtos', 'Primeiro Ano', 'Último Ano', 'Total Anos-Produto']
                
                # Calculate average coverage period
                periodo_medio = {}
                for metodologia in metodologias_unicas:
                    produtos_metod = timeline_df[timeline_df['metodologia'] == metodologia]['produto'].unique()
                    periodos = []
                    for produto in produtos_metod:
                        anos_produto = timeline_df[
                            (timeline_df['produto'] == produto) & 
                            (timeline_df['metodologia'] == metodologia)
                        ]['ano'].tolist()
                        if anos_produto:
                            periodos.append(max(anos_produto) - min(anos_produto) + 1)
                    periodo_medio[metodologia] = np.mean(periodos) if periodos else 0
                metod_stats['Período Médio'] = [periodo_medio.get(metod, 0) for metod in metod_stats.index]
                
                st.dataframe(metod_stats, use_container_width=True)
                
                # LULC Products Accuracy Ranking
                if df_geral_original is not None and not df_geral_original.empty and 'Acurácia (%)' in df_geral_original.columns:
                    st.markdown("#### 🏆 Ranking de Acurácia dos Produtos LULC")
                    
                    # Create ranking data
                    ranking_data = []
                    for produto in produtos_unicos:
                        produto_timeline = timeline_df[timeline_df['produto'] == produto].iloc[0]
                        metodologia = produto_timeline['metodologia']
                        
                        # Get accuracy data
                        produto_row = df_geral_original[df_geral_original['Nome'] == produto]
                        if not produto_row.empty:
                            acuracia = produto_row['Acurácia (%)'].iloc[0] if pd.notna(produto_row['Acurácia (%)'].iloc[0]) else 0
                            resolucao = produto_row['Resolução (m)'].iloc[0] if 'Resolução (m)' in produto_row.columns and pd.notna(produto_row['Resolução (m)'].iloc[0]) else 0
                        else:
                            acuracia = 0
                            resolucao = 0
                        
                        # Calculate temporal coverage
                        anos_produto = timeline_df[timeline_df['produto'] == produto]['ano'].unique()
                        cobertura_temporal = len(anos_produto)
                        periodo_inicio = min(anos_produto) if len(anos_produto) > 0 else 0
                        periodo_fim = max(anos_produto) if len(anos_produto) > 0 else 0
                        
                        ranking_data.append({
                            'produto': produto,
                            'metodologia': metodologia,
                            'acuracia': acuracia,
                            'resolucao': resolucao,
                            'cobertura_temporal': cobertura_temporal,
                            'periodo_inicio': periodo_inicio,
                            'periodo_fim': periodo_fim
                        })
                    
                    ranking_df = pd.DataFrame(ranking_data)
                    
                    # Horizontal ranking chart by accuracy
                    if ranking_df['acuracia'].sum() > 0:  # If there's accuracy data
                        ranking_sorted = ranking_df.sort_values('acuracia', ascending=True)
                        
                        fig_ranking = px.bar(
                            ranking_sorted,
                            x='acuracia',
                            y='produto',
                            color='metodologia',
                            orientation='h',
                            title='🏆 Ranking de Acurácia dos Produtos LULC',
                            labels={'acuracia': 'Acurácia (%)', 'produto': 'Produto'},
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            text='acuracia'
                        )
                        
                        fig_ranking.update_traces(
                            texttemplate='%{text:.1f}%', 
                            textposition='outside',                            marker_line=dict(width=2, color='white')
                        )
                        
                        fig_ranking.update_layout(
                            height=max(400, len(ranking_sorted) * 25),
                            xaxis_title='Acurácia (%)',
                            yaxis_title='Produtos LULC',
                            font=dict(size=12, color="#2D3748"),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                title="Metodologia",
                                font=dict(color="#2D3748")
                            )
                        )
                        
                        st.plotly_chart(fig_ranking, use_container_width=True, key="ranking_acuracia_tab1")
                        safe_download_image(fig_ranking, "ranking_acuracia_lulc.png", "⬇️ Baixar Ranking (PNG)")
                        
                        # Top 5 and Bottom 5
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 🥇 Top 5 - Maior Acurácia")
                            top_5 = ranking_sorted.tail(5)[['produto', 'acuracia', 'metodologia']]
                            top_5 = top_5.sort_values('acuracia', ascending=False)
                            
                            for idx, row in top_5.iterrows():
                                st.success(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        with col2:
                            st.markdown("##### 📉 Bottom 5 - Menor Acurácia")
                            bottom_5 = ranking_sorted.head(5)[['produto', 'acuracia', 'metodologia']]
                            
                            for idx, row in bottom_5.iterrows():
                                st.warning(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        # Ranking statistics
                        st.markdown("##### 📊 Estatísticas do Ranking")
                        ranking_col1, ranking_col2, ranking_col3, ranking_col4 = st.columns(4)
                        
                        with ranking_col1:
                            st.metric("🏆 Melhor Acurácia", f"{ranking_df['acuracia'].max():.1f}%")
                        with ranking_col2:
                            st.metric("📊 Acurácia Média", f"{ranking_df['acuracia'].mean():.1f}%")
                        with ranking_col3:
                            st.metric("📉 Menor Acurácia", f"{ranking_df['acuracia'].min():.1f}%")
                        with ranking_col4:
                            desvio = ranking_df['acuracia'].std()
                            st.metric("📈 Desvio Padrão", f"{desvio:.1f}%")
                    
                    else:
                        st.info("ℹ️ Dados de acurácia não disponíveis para criar ranking.")
                else:
                    st.warning("⚠️ Dados de acurácia não disponíveis nos dados originais.")
            else:
                st.info("ℹ️ Dados temporais insuficientes para análise de metodologia.")
        else:
            st.warning("⚠️ Metadados não disponíveis para análise de metodologia.")    with tab2:
        st.subheader("Spatial Resolution vs Accuracy (Scatter)")
        # Modern scatterplot with siglas
        fig_scatter = px.scatter(
            df_filt_limited,
            x='Resolução (m)',
            y='Acurácia (%)',
            color='Metodologia' if 'Metodologia' in df_filt_limited.columns else None,
            hover_name='Display_Name',  # Use siglas for hover
            size='Classes' if 'Classes' in df_filt_limited.columns else None,
            title="Accuracy vs Spatial Resolution",
            labels={
                'Resolução (m)': 'Spatial Resolution (m)',
                'Acurácia (%)': 'Accuracy (%)',
                'Metodologia': 'Methodology',
                'Classes': 'No. of Classes'
            },
            height=500
        )
        fig_scatter.update_traces(marker=dict(size=14, opacity=0.8, line=dict(width=2, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_resolution_accuracy")
        safe_download_image(fig_scatter, "scatter_resolution_accuracy.png", "⬇️ Download Scatter (PNG)")
        
        st.subheader("Temporal Availability of Initiatives")
        try:
            from generate_graphics import plot_ano_overlap
            fig_disp = plot_ano_overlap(meta_geral, df_filt_limited)
        except ImportError:
            fig_disp = go.Figure()
            fig_disp.add_annotation(text="Overlap function not available", 
                                  xref="paper", yref="paper", x=0.5, y=0.5)
        st.plotly_chart(fig_disp, use_container_width=True, key="temporal_availability")
        safe_download_image(fig_disp, "temporal_availability.png", "⬇️ Download Availability (PNG)")

    with tab3:
        st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 General Timeline of Initiatives</h2></div>', unsafe_allow_html=True)        fig_timeline = plot_timeline(meta_geral, df_geral_original)
        st.plotly_chart(fig_timeline, use_container_width=True, key="general_timeline")
        safe_download_image(fig_timeline, "general_timeline.png", "⬇️ Download Timeline (PNG)")
        
        # Methodology Evolution Over Time Chart (translated to English)
        if meta_geral and df_geral_original is not None and not df_geral_original.empty:
            st.markdown("#### ⏰ Evolution of Methodologies Over Time")
            
            # Create enhanced timeline data for methodology analysis
            timeline_data = []
            produto_info = {}
            
            # Map products to get methodology information
            for _, row in df_geral_original.iterrows():
                produto_info[row['Nome']] = {
                    'metodologia': row.get('Metodologia', 'N/A'),
                    'escopo': row.get('Escopo', 'N/A')
                }
            
            # Collect all years from all initiatives with methodology info
            for nome, meta in meta_geral.items():
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    info = produto_info.get(nome, {})
                    for ano in meta['anos_disponiveis']:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                anos_reais = sorted(list(set(timeline_df['ano'].tolist())))
                
                # Create data for stacked area chart by methodology
                timeline_pivot = timeline_df.groupby(['ano', 'metodologia']).size().reset_index(name='count')
                
                fig_metodologia_evolucao = px.area(
                    timeline_pivot,
                    x='ano',
                    y='count',
                    color='metodologia',
                    title='📈 Evolution of LULC Methodology Adoption',
                    labels={'ano': 'Year', 'count': 'Number of Products', 'metodologia': 'Methodology'},
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                
                fig_metodologia_evolucao.update_layout(
                    height=400,
                    font=dict(size=12, color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(range=[min(anos_reais), max(anos_reais)], color="#2D3748"),
                    yaxis=dict(color="#2D3748"),
                    legend=dict(font=dict(color="#2D3748")),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_metodologia_evolucao, use_container_width=True, key="metodologia_evolucao_tab3")
                safe_download_image(fig_metodologia_evolucao, "evolucao_metodologias_tab3.png", "⬇️ Baixar Evolução (PNG)")
            else:
                st.info("Dados insuficientes para análise de evolução de metodologias.")
        
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
            st.info('Todas as iniciativas possuem séries temporais contínuas ou apenas um ano disponível.')        # Análise de sobreposição de anos
        st.markdown("#### Análise de Sobreposição de Anos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Heatmap de Cobertura Anual")
            # Criar dados anuais a partir dos metadados
            if meta_geral:
                yearly_data = []
                for nome, meta in meta_geral.items():
                    if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                        # Get accuracy from df_geral_original
                        produto_row = df_geral_original[df_geral_original['Nome'] == nome]
                        acuracia = produto_row['Acurácia (%)'].iloc[0] if not produto_row.empty and pd.notna(produto_row['Acurácia (%)'].iloc[0]) else 0
                        resolucao = produto_row['Resolução (m)'].iloc[0] if not produto_row.empty and 'Resolução (m)' in produto_row.columns and pd.notna(produto_row['Resolução (m)'].iloc[0]) else 0
                        
                        for ano in meta['anos_disponiveis']:
                            yearly_data.append({
                                'Ano': ano,
                                'Nome': nome,
                                'Acurácia (%)': acuracia,
                                'Resolução (m)': resolucao
                            })
                
                if yearly_data:
                    yearly_df = pd.DataFrame(yearly_data)
                    cobertura_anual = yearly_df.groupby('Ano').agg(
                        iniciativas_totais=('Nome', 'count'),
                        acuracia_media=('Acurácia (%)', 'mean'),
                        resolucao_media=('Resolução (m)', 'mean')
                    ).reset_index()
                    
                    fig_heatmap = px.bar(
                        cobertura_anual,
                        x='Ano',
                        y='iniciativas_totais',
                        color='iniciativas_totais',
                        color_continuous_scale='Viridis',
                        title="📈 Cobertura Anual das Iniciativas",
                        labels={'Ano': 'Ano', 'iniciativas_totais': 'Número de Iniciativas'}
                    )   
                    fig_heatmap.update_layout(
                        font=dict(color="#2D3748"),
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="#FFFFFF",
                        xaxis=dict(color="#2D3748"),
                        yaxis=dict(color="#2D3748")
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_cobertura_anual")
                    safe_download_image(fig_heatmap, "heatmap_cobertura_anual.png", "⬇️ Baixar Heatmap (PNG)")
                else:
                    st.info("Dados insuficientes para criar heatmap de cobertura anual.")
            else:
                st.warning("Metadados não disponíveis para análise temporal.")
        
        with col2:
            st.markdown("##### Tendência da Acurácia ao Longo dos Anos")
            if meta_geral and 'yearly_df' in locals() and not yearly_df.empty:
                tendencia_acuracia = yearly_df.groupby('Ano').agg(
                    acuracia_media=('Acurácia (%)', 'mean')
                ).reset_index()
                
                fig_tendencia_acuracia = px.line(
                    tendencia_acuracia,
                    x='Ano',
                    y='acuracia_media',
                    title="📉 Tendência da Acurácia Média ao Longo dos Anos",                    labels={"Ano": "Ano", "acuracia_media": "Acurácia Média (%)"},
                    markers=True
                )
                fig_tendencia_acuracia.update_traces(line=dict(width=2))
                fig_tendencia_acuracia.update_layout(
                    font=dict(color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(color="#2D3748"),
                    yaxis=dict(color="#2D3748")
                )
                st.plotly_chart(fig_tendencia_acuracia, use_container_width=True, key="tendencia_acuracia")
                safe_download_image(fig_tendencia_acuracia, "tendencia_acuracia.png", "⬇️ Baixar Tendência (PNG)")
            else:
                st.info("Dados insuficientes para análise de tendência.")    with tab4:
        st.subheader("Distribution of Number of Classes")
        col1_tab3, col2_tab3 = st.columns(2)
        with col1_tab3:
            fig_bar_classes = plot_classes_por_iniciativa(df_filt)
            st.plotly_chart(fig_bar_classes, use_container_width=True, key="bar_classes")
            safe_download_image(fig_bar_classes, "classes_per_initiative.png", "⬇️ Download Bar Chart (PNG)")
        with col2_tab3:
            fig_hist_classes = plot_distribuicao_classes(df_filt)
            st.plotly_chart(fig_hist_classes, use_container_width=True, key="hist_classes")
            safe_download_image(fig_hist_classes, "classes_distribution.png", "⬇️ Download Histogram (PNG)")

    with tab5:
        st.subheader("Distribution by Methodologies")
        col1_tab4, col2_tab4 = st.columns(2)
        with col1_tab4:
            method_counts = df_filt['Metodologia'].value_counts()
            fig_metodologias = plot_distribuicao_metodologias(method_counts)
            st.plotly_chart(fig_metodologias, use_container_width=True, key="methodology_distribution")
            safe_download_image(fig_metodologias, "methodology_distribution.png", "⬇️ Download Methodology Chart (PNG)")
        
        with col2_tab4:
            st.markdown("#### Accuracy by Methodology")
            fig_acuracia_metodologia = plot_acuracia_por_metodologia(df_filt)
            st.plotly_chart(fig_acuracia_metodologia, use_container_width=True, key="accuracy_methodology")
            safe_download_image(fig_acuracia_metodologia, "accuracy_by_methodology.png", "⬇️ Download Accuracy Methodology (PNG)")

    with tab6:
        st.subheader("🕸️ Radar Analysis - Multi-dimensional Comparison")
        # Radar chart with top initiatives using siglas
        radar_columns = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filt.columns]
        
        if len(available_radar_cols) >= 2 and len(df_filt) >= 2:
            # Allow users to select number of initiatives to compare
            col1_radar, col2_radar = st.columns(2)
            with col1_radar:
                max_initiatives = min(8, len(df_filt))
                if max_initiatives > 2:
                    num_initiatives = st.slider(
                        "Number of initiatives in radar",
                        min_value=2,
                        max_value=max_initiatives,
                        value=min(5, max_initiatives),
                        help="Select how many initiatives to display in the radar chart"
                    )
                else:
                    # If only 2 initiatives available, don't show slider
                    num_initiatives = max_initiatives
                    st.info(f"Displaying all {max_initiatives} available initiatives")
              with col2_radar:
                sort_by = st.selectbox(
                    "Sort by",
                    options=['Acurácia (%)', 'Resolução (m)', 'Classes'],
                    help="Criteria to select top initiatives"
                )
            
            # Prepare radar data with siglas
            if sort_by == 'Resolução (m)':
                # For resolution, lower is better, so sort ascending
                top_initiatives = df_filt.nsmallest(num_initiatives, sort_by)
            else:
                # For others, higher is better
                top_initiatives = df_filt.nlargest(num_initiatives, sort_by)
            
            # Use Display_Name (siglas) for radar chart
            radar_df = top_initiatives[['Display_Name'] + available_radar_cols].copy()
            
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
            
            # Create radar chart with siglas
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
                    name=row['Display_Name'],  # Use siglas for legend
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
                        ticktext=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High']  # English labels
                    )
                ),
                showlegend=True,
                title=f'🎯 Radar Comparison - Top {num_initiatives} by {sort_by}',
                height=600,
                font=dict(size=12)
            )            st.plotly_chart(fig_radar, use_container_width=True, key="radar_comparison")
            safe_download_image(fig_radar, "radar_comparison.png", "⬇️ Download Radar Chart (PNG)")
            
            # Show normalized values table with siglas
            st.markdown("#### 📊 Normalized Values (0-1 Scale)")
            display_df = radar_df.copy()
            for col in available_radar_cols:
                display_df[col] = display_df[col].round(3)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Display_Name": st.column_config.TextColumn("Initiative", width="large"),
                    "Acurácia (%)": st.column_config.NumberColumn("Accuracy (norm.)", format="%.3f"),
                    "Resolução (m)": st.column_config.NumberColumn("Resolution (norm.)", format="%.3f", help="Inverted: 1 = better resolution"),
                    "Classes": st.column_config.NumberColumn("Classes (norm.)", format="%.3f")
                }
            )
            
            # Insights section (translated to English)
            st.markdown("#### 💡 Radar Analysis Insights")
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                # Find best overall performer using siglas
                radar_df['score_total'] = radar_df[available_radar_cols].mean(axis=1)
                best_overall = radar_df.loc[radar_df['score_total'].idxmax(), 'Display_Name']
                st.success(f"🏆 **Best Overall Performance:** {best_overall}")
                
                # Find specialist initiatives using siglas
                for col in available_radar_cols:
                    specialist = radar_df.loc[radar_df[col].idxmax(), 'Display_Name']
                    col_display = "Resolution" if col == "Resolução (m)" else col.replace(" (%)", "")
                    st.info(f"🎯 **Specialist in {col_display}:** {specialist}")
            
            with insights_col2:
                # Performance distribution (translated to English)
                st.markdown("**📈 Performance Distribution:**")
                for col in available_radar_cols:
                    avg_performance = radar_df[col].mean()
                    col_display = "Resolution" if col == "Resolução (m)" else col.replace(" (%)", "")
                    performance_level = "High" if avg_performance > 0.7 else "Medium" if avg_performance > 0.4 else "Low"
                    st.write(f"• **{col_display}:** {performance_level} ({avg_performance:.2f})")
                
                # Balance analysis using siglas
                balance_scores = radar_df[available_radar_cols].std(axis=1)
                most_balanced = radar_df.loc[balance_scores.idxmin(), 'Display_Name']
                st.info(f"⚖️ **Most Balanced:** {most_balanced}")
        
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
        
        # Enhanced Timeline Analysis - Additional Features
        st.markdown("---")
        st.markdown("### 📊 Análise Avançada do Timeline")
        
        # Create enhanced timeline data for analysis
        if meta_geral:
            timeline_data = []
            produto_info = {}
            
            # Map products to get technical characteristics
            if df_geral_original is not None and not df_geral_original.empty:
                for _, row in df_geral_original.iterrows():
                    produto_info[row['Nome']] = {
                        'metodologia': row.get('Metodologia', 'N/A'),
                        'escopo': row.get('Escopo', 'N/A'),
                        'acuracia': row.get('Acurácia (%)', 0),
                        'resolucao': row.get('Resolução (m)', 0)
                    }
              # Collect all years from all initiatives
            for nome, meta in meta_geral.items():
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    info = produto_info.get(nome, {})
                    for ano in meta['anos_disponiveis']:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A'),
                            'escopo': info.get('escopo', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                produtos_unicos = sorted(timeline_df['produto'].unique())
                metodologias_unicas = timeline_df['metodologia'].unique()
                
                # Methodology Comparative Analysis
                st.markdown("#### 📈 Análise Comparativa por Metodologia")
                
                # Statistics by methodology
                metod_stats = timeline_df.groupby('metodologia').agg({
                    'produto': 'nunique',
                    'ano': ['min', 'max', 'count']
                }).round(1)
                metod_stats.columns = ['Produtos', 'Primeiro Ano', 'Último Ano', 'Total Anos-Produto']
                
                # Calculate average coverage period
                periodo_medio = {}
                for metodologia in metodologias_unicas:
                    produtos_metod = timeline_df[timeline_df['metodologia'] == metodologia]['produto'].unique()
                    periodos = []
                    for produto in produtos_metod:
                        anos_produto = timeline_df[
                            (timeline_df['produto'] == produto) & 
                            (timeline_df['metodologia'] == metodologia)
                        ]['ano'].tolist()
                        if anos_produto:
                            periodos.append(max(anos_produto) - min(anos_produto) + 1)
                    periodo_medio[metodologia] = np.mean(periodos) if periodos else 0
                metod_stats['Período Médio'] = [periodo_medio.get(metod, 0) for metod in metod_stats.index]
                
                st.dataframe(metod_stats, use_container_width=True)
                
                # LULC Products Accuracy Ranking
                if df_geral_original is not None and not df_geral_original.empty and 'Acurácia (%)' in df_geral_original.columns:
                    st.markdown("#### 🏆 Ranking de Acurácia dos Produtos LULC")
                    
                    # Create ranking data
                    ranking_data = []
                    for produto in produtos_unicos:
                        produto_timeline = timeline_df[timeline_df['produto'] == produto].iloc[0]
                        metodologia = produto_timeline['metodologia']
                        
                        # Get accuracy data
                        produto_row = df_geral_original[df_geral_original['Nome'] == produto]
                        if not produto_row.empty:
                            acuracia = produto_row['Acurácia (%)'].iloc[0] if pd.notna(produto_row['Acurácia (%)'].iloc[0]) else 0
                            resolucao = produto_row['Resolução (m)'].iloc[0] if 'Resolução (m)' in produto_row.columns and pd.notna(produto_row['Resolução (m)'].iloc[0]) else 0
                        else:
                            acuracia = 0
                            resolucao = 0
                        
                        # Calculate temporal coverage
                        anos_produto = timeline_df[timeline_df['produto'] == produto]['ano'].unique()
                        cobertura_temporal = len(anos_produto)
                        periodo_inicio = min(anos_produto) if len(anos_produto) > 0 else 0
                        periodo_fim = max(anos_produto) if len(anos_produto) > 0 else 0
                        
                        ranking_data.append({
                            'produto': produto,
                            'metodologia': metodologia,
                            'acuracia': acuracia,
                            'resolucao': resolucao,
                            'cobertura_temporal': cobertura_temporal,
                            'periodo_inicio': periodo_inicio,
                            'periodo_fim': periodo_fim
                        })
                    
                    ranking_df = pd.DataFrame(ranking_data)
                    
                    # Horizontal ranking chart by accuracy
                    if ranking_df['acuracia'].sum() > 0:  # If there's accuracy data
                        ranking_sorted = ranking_df.sort_values('acuracia', ascending=True)
                        
                        fig_ranking = px.bar(
                            ranking_sorted,
                            x='acuracia',
                            y='produto',
                            color='metodologia',
                            orientation='h',
                            title='🏆 Ranking de Acurácia dos Produtos LULC',
                            labels={'acuracia': 'Acurácia (%)', 'produto': 'Produto'},
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            text='acuracia'
                        )
                        
                        fig_ranking.update_traces(
                            texttemplate='%{text:.1f}%', 
                            textposition='outside',
                            marker_line=dict(width=2, color='white')                        )
                        
                        fig_ranking.update_layout(
                            height=max(400, len(ranking_sorted) * 25),
                            xaxis_title='Acurácia (%)',
                            yaxis_title='Produtos LULC',
                            font=dict(size=12, color="#2D3748"),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                title="Metodologia",
                                font=dict(color="#2D3748")
                            )
                        )
                        
                        st.plotly_chart(fig_ranking, use_container_width=True, key="ranking_acuracia_tab6")
                        safe_download_image(fig_ranking, "ranking_acuracia_lulc.png", "⬇️ Baixar Ranking (PNG)")
                        
                        # Top 5 and Bottom 5
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 🥇 Top 5 - Maior Acurácia")
                            top_5 = ranking_sorted.tail(5)[['produto', 'acuracia', 'metodologia']]
                            top_5 = top_5.sort_values('acuracia', ascending=False)
                            
                            for idx, row in top_5.iterrows():
                                st.success(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        with col2:
                            st.markdown("##### 📉 Bottom 5 - Menor Acurácia")
                            bottom_5 = ranking_sorted.head(5)[['produto', 'acuracia', 'metodologia']]
                            
                            for idx, row in bottom_5.iterrows():
                                st.warning(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        # Ranking statistics
                        st.markdown("##### 📊 Estatísticas do Ranking")
                        ranking_col1, ranking_col2, ranking_col3, ranking_col4 = st.columns(4)
                        
                        with ranking_col1:
                            st.metric("🏆 Melhor Acurácia", f"{ranking_df['acuracia'].max():.1f}%")
                        with ranking_col2:
                            st.metric("📊 Acurácia Média", f"{ranking_df['acuracia'].mean():.1f}%")
                        with ranking_col3:
                            st.metric("📉 Menor Acurácia", f"{ranking_df['acuracia'].min():.1f}%")
                        with ranking_col4:
                            desvio = ranking_df['acuracia'].std()
                            st.metric("📈 Desvio Padrão", f"{desvio:.1f}%")
                
                # General timeline statistics
                st.markdown("#### 📈 Estatísticas Gerais do Timeline")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Produtos", len(produtos_unicos))
                with col2:
                    anos_reais = sorted(list(set(timeline_df['ano'].tolist())))
                    st.metric("📅 Período Real", f"{min(anos_reais)}-{max(anos_reais)}")
                with col3:
                    ano_mais_ativo = timeline_df['ano'].value_counts().idxmax()
                    produtos_ano_ativo = timeline_df['ano'].value_counts().max()
                    st.metric("🔥 Ano Mais Ativo", f"{ano_mais_ativo} ({produtos_ano_ativo} produtos)")
                with col4:
                    st.metric("🔬 Metodologias", len(metodologias_unicas))
                
                # Methodology evolution over time chart
                st.markdown("#### ⏰ Evolução das Metodologias ao Longo do Tempo")
                
                # Create data for stacked area chart by methodology
                timeline_pivot = timeline_df.groupby(['ano', 'metodologia']).size().reset_index(name='count')
                
                fig_metodologia_evolucao = px.area(
                    timeline_pivot,
                    x='ano',
                    y='count',
                    color='metodologia',
                    title='📈 Evolução da Adoção de Metodologias LULC',
                    labels={'ano': 'Ano', 'count': 'Número de Produtos', 'metodologia': 'Metodologia'},
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                fig_metodologia_evolucao.update_layout(
                    height=400,
                    font=dict(size=12, color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(range=[min(anos_reais), max(anos_reais)], color="#2D3748"),
                    yaxis=dict(color="#2D3748"),
                    legend=dict(font=dict(color="#2D3748")),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_metodologia_evolucao, use_container_width=True, key="metodologia_evolucao")
                safe_download_image(fig_metodologia_evolucao, "evolucao_metodologias.png", "⬇️ Baixar Evolução (PNG)")
