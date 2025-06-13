import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import ast
import time
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_generation.data_processing import load_data, prepare_plot_data
from scripts.utilities.utils import safe_download_image

def main():
    st.set_page_config(
        page_title="🧪 Testes Gráficos LULC COMPLETOS",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🧪 TODOS os Gráficos LULC - Testes Completos")
    st.markdown("### Sistema Completo de Visualizações para Iniciativas LULC")
    
    # Carregar dados
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state:
        df_loaded, metadata_loaded = load_data(
            "../initiative_data/initiatives_processed.csv",
            "../initiative_data/metadata_processed.json"
        )
        st.session_state.df_original = df_loaded
        st.session_state.metadata = metadata_loaded
        st.session_state.df_prepared_initial = prepare_plot_data(df_loaded.copy())

    df = st.session_state.df_prepared_initial
    meta_geral = st.session_state.metadata
    df_geral_original = st.session_state.df_original

    # Debug dos dados
    st.sidebar.markdown("### 🔍 Debug dos Dados")
    st.sidebar.write("**Colunas disponíveis:**", list(df.columns))
    st.sidebar.write("**Iniciativas no DataFrame:**", len(df))
    st.sidebar.write("**Iniciativas nos metadados:**", len(meta_geral) if meta_geral else 0)

    df_teste = df.copy()
    
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
        st.warning("Não há dados para exibir.")
        return

    # Função para processar disponibilidade de anos
    def processar_disponibilidade_para_range(disp_item):
        if pd.isna(disp_item):
            return []
        if isinstance(disp_item, str):
            try:
                if '-' in disp_item:
                    parts = disp_item.split('-')
                    if len(parts) == 2:
                        start, end = int(parts[0]), int(parts[1])
                        return list(range(start, end + 1))
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

    # MENU PRINCIPAL DE GRÁFICOS
    st.markdown("### 📊 TODOS os Gráficos Disponíveis")
      # Criar abas com TODOS os gráficos
    all_tabs = st.tabs([
        "📅 Timeline Correta",
        "🌊 Densidade Temporal", 
        "🔬 Performance Metodológica",
        "⚖️ Escopo vs Qualidade",
        "🧮 Análise Classes",
        "📈 Evolução Tecnológica",
        "🇧🇷 Brasil vs Global",
        "🔗 Ecossistema Provedores",
        "📊 Gráficos Clássicos",
        "🎯 Barras Duplas",
        "🕸️ Radar Charts",
        "🔥 Heatmaps",
        "🍰 Pizza Charts",
        "📦 Box Plots",
        "🎻 Violin Plots",
        "☀️ Sunburst",
        "🫧 Bolhas 3D",
        "📋 Disponibilidade Matrix",
        "📈 Área Empilhada",
        "🗺️ Mapa Hexagonal",
        "🌐 Rede de Sensores",
        "⏰ Timeline Melhorado",
        "🎯 Matriz Adequação",
        "🔍 Análise 3D Gaps"
    ])    # TAB 1: Timeline Correta
    with all_tabs[0]:
        run_timeline_correta(meta_geral, df_geral_original)
    
    # TAB 2: Densidade Temporal
    with all_tabs[1]:
        run_densidade_temporal_completa(df_teste, meta_geral, processar_disponibilidade_para_range)
    
    # TAB 3: Performance Metodológica
    with all_tabs[2]:
        run_lulc_performance_metodologica(df_teste, df_geral_original)
    
    # TAB 4: Escopo vs Qualidade
    with all_tabs[3]:
        run_lulc_escopo_qualidade(df_teste)
    
    # TAB 5: Análise Classes
    with all_tabs[4]:
        run_lulc_analise_classes(df_teste)
    
    # TAB 6: Evolução Tecnológica
    with all_tabs[5]:
        run_lulc_evolucao_tecnologica(df_teste, meta_geral)
    
    # TAB 7: Brasil vs Global
    with all_tabs[6]:
        run_lulc_brasil_vs_global(df_teste)
    
    # TAB 8: Ecossistema Provedores
    with all_tabs[7]:
        run_lulc_ecossistema_provedores(df_teste, df_geral_original)
    
    # TAB 9: Gráficos Clássicos
    with all_tabs[8]:
        run_graficos_classicos(df_teste, meta_geral, df_geral_original, processar_disponibilidade_para_range)
    
    # TAB 10: Barras Duplas
    with all_tabs[9]:
        run_barras_duplas_completo(df_teste)
    
    # TAB 11: Radar Charts
    with all_tabs[10]:
        run_radar_charts_completo(df_teste)
    
    # TAB 12: Heatmaps
    with all_tabs[11]:
        run_heatmaps_completo(df_teste)
    
    # TAB 13: Pizza Charts
    with all_tabs[12]:
        run_pizza_charts_completo(df_teste)
    
    # TAB 14: Box Plots
    with all_tabs[13]:
        run_box_plots_completo(df_teste)
    
    # TAB 15: Violin Plots
    with all_tabs[14]:
        run_violin_plots_completo(df_teste)
    
    # TAB 16: Sunburst
    with all_tabs[15]:
        run_sunburst_completo(df_teste)
    
    # TAB 17: Bolhas 3D
    with all_tabs[16]:
        run_bolhas_3d_completo(df_teste)
      # TAB 18: Disponibilidade Matrix
    with all_tabs[17]:
        run_disponibilidade_matrix_completo(df_teste, meta_geral, processar_disponibilidade_para_range)
    
    # TAB 19: Área Empilhada
    with all_tabs[18]:
        run_area_empilhada_evolucao(df_teste, meta_geral)
    
    # TAB 20: Mapa Hexagonal
    with all_tabs[19]:
        run_mapa_hexagonal_cobertura(df_teste)
    
    # TAB 21: Rede de Sensores
    with all_tabs[20]:
        run_rede_sensores_algoritmos(df_teste, df_geral_original)
    
    # TAB 22: Timeline Melhorado
    with all_tabs[21]:
        run_timeline_melhorado_barras(meta_geral, df_geral_original)
    
    # TAB 23: Matriz Adequação
    with all_tabs[22]:
        run_matriz_adequacao_uso(df_teste)
    
    # TAB 24: Análise 3D Gaps
    with all_tabs[23]:
        run_analise_3d_gaps(df_teste, meta_geral)

# ==========================================
# IMPLEMENTAÇÃO DE TODOS OS GRÁFICOS
# ==========================================

def run_timeline_correta(meta_geral, df_original):
    """Timeline usando dados corretos dos metadados JSON"""
    st.subheader('📅 Timeline Correta das Iniciativas LULC (1985-2024)')
    
    if meta_geral:
        from plots import plot_timeline
        fig_timeline = plot_timeline(meta_geral, df_original)
        st.plotly_chart(fig_timeline, use_container_width=True)
        safe_download_image(fig_timeline, "timeline_correta.png", "⬇️ Baixar Timeline (PNG)")
        
        # Estatísticas da timeline
        col1, col2, col3, col4 = st.columns(4)
        
        all_years = []
        for nome, meta in meta_geral.items():
            if 'anos_disponiveis' in meta:
                all_years.extend(meta['anos_disponiveis'])
        
        if all_years:
            with col1:
                st.metric("🗓️ Primeiro Ano", min(all_years))
            with col2:
                st.metric("📅 Último Ano", max(all_years))
            with col3:
                st.metric("🔢 Total de Anos", max(all_years) - min(all_years) + 1)
            with col4:
                st.metric("📊 Iniciativas", len(meta_geral))
    else:
        st.error("Metadados não disponíveis para timeline")

def run_densidade_temporal_completa(df_teste, meta_geral, processar_disponibilidade_para_range):
    """Análise completa de densidade temporal"""
    st.subheader('🌊 Densidade Temporal de Iniciativas LULC')
    
    if meta_geral:
        # Criar dados de densidade usando metadados
        density_data = []
        all_years = set()
        
        for nome, meta in meta_geral.items():
            if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                for ano in meta['anos_disponiveis']:
                    density_data.append({'nome': nome, 'ano': ano})
                    all_years.add(ano)
        
        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df['ano'].value_counts().sort_index()
            
            # Gráfico 1: Densidade por ano (linha + área)
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
                title='📊 Densidade Temporal: Número de Iniciativas por Ano',
                xaxis_title='Ano',
                yaxis_title='Número de Iniciativas Ativas',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_density_line, use_container_width=True)
            
            # Gráfico 2: Heatmap de densidade por década
            decade_data = []
            for year in sorted(all_years):
                decade = f"{(year//10)*10}s"
                count = year_counts.get(year, 0)
                decade_data.append({'ano': year, 'decada': decade, 'iniciativas': count})
            
            decade_df = pd.DataFrame(decade_data)
            
            fig_heatmap_decade = px.density_heatmap(
                decade_df,
                x='ano',
                y='decada',
                z='iniciativas',
                title='🔥 Heatmap de Densidade por Década',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_heatmap_decade, use_container_width=True)
            
            # Gráfico 3: Bar chart animado por períodos
            periods = {
                '1980-1989': len([y for y in all_years if 1980 <= y <= 1989]),
                '1990-1999': len([y for y in all_years if 1990 <= y <= 1999]),
                '2000-2009': len([y for y in all_years if 2000 <= y <= 2009]),
                '2010-2019': len([y for y in all_years if 2010 <= y <= 2019]),
                '2020-2024': len([y for y in all_years if 2020 <= y <= 2024])
            }
            
            fig_periods = px.bar(
                x=list(periods.keys()),
                y=list(periods.values()),
                title='📅 Concentração de Anos de Dados por Década',
                labels={'x': 'Período', 'y': 'Anos com Dados Disponíveis'},
                color=list(periods.values()),
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig_periods, use_container_width=True)
            
            # Métricas de densidade
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Pico de Atividade", f"{max(year_counts.values)} iniciativas")
            with col2:
                st.metric("📈 Média por Ano", f"{np.mean(year_counts.values):.1f}")
            with col3:
                st.metric("📊 Anos Cobertos", len(year_counts))
            with col4:
                st.metric("🔄 Período Total", f"{min(all_years)}-{max(all_years)}")
    
    else:
        st.error("Metadados não disponíveis para análise de densidade")

def run_lulc_performance_metodologica(df_teste, df_original):
    """Análise avançada de performance por metodologia LULC"""
    st.subheader('🔬 Performance Metodológica Avançada')
    
    if 'metodologia' in df_teste.columns and 'acuracia' in df_teste.columns:
        # Violin plot para distribuição de acurácia por metodologia
        fig_violin = px.violin(
            df_teste,
            x='metodologia',
            y='acuracia',
            color='metodologia',
            title='🎻 Distribuição de Acurácia por Metodologia (Violin Plot)',
            labels={'metodologia': 'Metodologia', 'acuracia': 'Acurácia (%)'}
        )
        fig_violin.update_layout(height=500, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)
        
        # Scatter com tendências por metodologia (com statsmodels)
        if 'resolucao' in df_teste.columns:
            fig_trend = px.scatter(
                df_teste,
                x='resolucao',
                y='acuracia',
                color='metodologia',
                trendline='ols',
                title='📈 Acurácia vs Resolução com Tendências por Metodologia',
                labels={'resolucao': 'Resolução Espacial (m)', 'acuracia': 'Acurácia (%)'}
            )
            fig_trend.update_layout(height=500)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Box plot comparativo
        fig_box_metod = px.box(
            df_teste,
            x='metodologia',
            y='acuracia',
            color='metodologia',
            title='📦 Box Plot: Acurácia por Metodologia'
        )
        fig_box_metod.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_box_metod, use_container_width=True)
        
        # Estatísticas por metodologia
        stats_metod = df_teste.groupby('metodologia').agg({
            'acuracia': ['mean', 'std', 'count', 'min', 'max'],
            'resolucao': ['mean', 'min', 'max'] if 'resolucao' in df_teste.columns else None
        }).round(2)
        
        st.markdown("### 📊 Estatísticas Detalhadas por Metodologia")
        st.dataframe(stats_metod, use_container_width=True)
    else:
        st.info("Dados insuficientes para análise de performance metodológica.")

def run_lulc_escopo_qualidade(df_teste):
    """Análise da relação entre escopo geográfico e qualidade técnica"""
    st.subheader('⚖️ Escopo Geográfico vs Qualidade Técnica')
    
    if all(col in df_teste.columns for col in ['escopo', 'acuracia', 'resolucao']):
        # Scatter plot com escopo como cor
        fig_scope = px.scatter(
            df_teste,
            x='resolucao',
            y='acuracia',
            color='escopo',
            size=[20] * len(df_teste),
            hover_name='produto',
            title='🌍 Trade-off: Qualidade Técnica vs Escopo Geográfico',
            labels={'resolucao': 'Resolução Espacial (m)', 'acuracia': 'Acurácia (%)', 'escopo': 'Escopo'}
        )
        fig_scope.update_traces(marker=dict(line=dict(width=2, color='white')))
        fig_scope.update_layout(height=500)
        st.plotly_chart(fig_scope, use_container_width=True)
        
        # Box plot por escopo
        fig_box_scope = px.box(
            df_teste,
            x='escopo',
            y='acuracia',
            color='escopo',
            title='📦 Distribuição de Acurácia por Escopo Geográfico'
        )
        fig_box_scope.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box_scope, use_container_width=True)
        
        # Análise estatística por escopo
        escopo_stats = df_teste.groupby('escopo').agg({
            'acuracia': ['mean', 'std', 'min', 'max'],
            'resolucao': ['mean', 'min', 'max'],
            'produto': 'count'
        }).round(2)
        
        st.markdown("### 📊 Estatísticas por Escopo Geográfico")
        st.dataframe(escopo_stats, use_container_width=True)
    else:
        st.info("Dados insuficientes para análise de escopo vs qualidade.")

def run_lulc_analise_classes(df_teste):
    """Análise da complexidade de classes LULC"""
    st.subheader('🧮 Análise de Complexidade de Classes')
    
    if 'num_classes' in df_teste.columns and 'acuracia' in df_teste.columns:
        # Scatter plot: número de classes vs acurácia
        fig_classes = px.scatter(
            df_teste,
            x='num_classes',
            y='acuracia',
            color='metodologia',
            size='resolucao' if 'resolucao' in df_teste.columns else None,
            hover_name='produto',
            title='🎯 Número de Classes vs Acurácia',
            labels={'num_classes': 'Número de Classes', 'acuracia': 'Acurácia (%)', 'resolucao': 'Resolução (m)'},
            trendline='ols'
        )
        fig_classes.update_layout(height=500)
        st.plotly_chart(fig_classes, use_container_width=True)
        
        # Histograma de distribuição de classes
        fig_hist_classes = px.histogram(
            df_teste,
            x='num_classes',
            nbins=10,
            title='📊 Distribuição do Número de Classes LULC',
            labels={'num_classes': 'Número de Classes', 'count': 'Frequência'}
        )
        fig_hist_classes.update_layout(height=400)
        st.plotly_chart(fig_hist_classes, use_container_width=True)
        
        # Categorização da complexidade
        df_classes = df_teste.copy()
        df_classes['complexidade'] = pd.cut(
            df_classes['num_classes'],
            bins=[0, 10, 20, 50],
            labels=['Baixa (≤10)', 'Média (11-20)', 'Alta (>20)']
        )
        
        if 'complexidade' in df_classes.columns:
            complexity_stats = df_classes.groupby('complexidade').agg({
                'acuracia': ['mean', 'std'],
                'produto': 'count'
            }).round(2)
            
            st.markdown("### 📈 Performance por Complexidade")
            st.dataframe(complexity_stats, use_container_width=True)
    else:
        st.info("Dados de classes não disponíveis.")

def run_lulc_evolucao_tecnologica(df_teste, meta_geral):
    """Análise da evolução tecnológica das iniciativas LULC ao longo do tempo"""
    st.subheader('📅 Evolução Tecnológica LULC')
    
    if meta_geral:
        # Extrair anos de início e características técnicas
        evolution_data = []
        for nome, meta in meta_geral.items():
            if nome in df_teste['produto'].values:
                row = df_teste[df_teste['produto'] == nome].iloc[0]
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    primeiro_ano = min(meta['anos_disponiveis'])
                    evolution_data.append({
                        'produto': nome,
                        'primeiro_ano': primeiro_ano,
                        'acuracia': row.get('acuracia', 0),
                        'resolucao': row.get('resolucao', 0),
                        'metodologia': row.get('metodologia', 'N/A'),
                        'num_classes': row.get('num_classes', 0)
                    })
        
        if evolution_data:
            evo_df = pd.DataFrame(evolution_data)
            
            # Evolução da acurácia ao longo do tempo
            fig_evo_acc = px.scatter(
                evo_df,
                x='primeiro_ano',
                y='acuracia',
                color='metodologia',
                size='num_classes',
                hover_name='produto',
                title='📈 Evolução da Acurácia ao Longo do Tempo',
                labels={'primeiro_ano': 'Ano de Início', 'acuracia': 'Acurácia (%)', 'num_classes': 'Nº Classes'},
                trendline='ols'
            )
            fig_evo_acc.update_layout(height=500)
            st.plotly_chart(fig_evo_acc, use_container_width=True)
            
            # Evolução da resolução espacial
            fig_evo_res = px.scatter(
                evo_df,
                x='primeiro_ano',
                y='resolucao',
                color='metodologia',
                hover_name='produto',
                title='🔍 Evolução da Resolução Espacial',
                labels={'primeiro_ano': 'Ano de Início', 'resolucao': 'Resolução Espacial (m)'},
                log_y=True
            )
            fig_evo_res.update_layout(height=500)
            st.plotly_chart(fig_evo_res, use_container_width=True)
            
            # Timeline de adoção de metodologias
            metodologia_timeline = evo_df.groupby(['primeiro_ano', 'metodologia']).size().reset_index(name='count')
            fig_metod_time = px.bar(
                metodologia_timeline,
                x='primeiro_ano',
                y='count',
                color='metodologia',
                title='⏰ Timeline de Adoção de Metodologias',
                labels={'primeiro_ano': 'Ano', 'count': 'Número de Iniciativas'}
            )
            fig_metod_time.update_layout(height=400)
            st.plotly_chart(fig_metod_time, use_container_width=True)
    else:
        st.info("Metadados temporais não disponíveis para análise evolutiva.")

def run_lulc_brasil_vs_global(df_teste):
    """Comparação entre iniciativas brasileiras e globais"""
    st.subheader('🇧🇷 Iniciativas Brasileiras vs Globais')
    
    if 'escopo' in df_teste.columns:
        # Classificar em categorias
        df_comp = df_teste.copy()
        df_comp['categoria'] = df_comp['escopo'].apply(
            lambda x: 'Brasil' if 'Brasil' in str(x) or 'Nacional' in str(x) or 'Regional' in str(x) else 'Global'
        )
        
        # Comparação lado a lado
        comparison_metrics = ['acuracia', 'resolucao', 'num_classes']
        available_metrics = [m for m in comparison_metrics if m in df_comp.columns]
        
        if available_metrics:
            fig_comparison = go.Figure()
            
            for categoria in ['Brasil', 'Global']:
                subset = df_comp[df_comp['categoria'] == categoria]
                if not subset.empty:
                    for metric in available_metrics:
                        values = subset[metric].dropna()
                        if not values.empty:
                            fig_comparison.add_trace(go.Box(
                                y=values,
                                name=f'{categoria} - {metric}',
                                boxpoints='all'
                            ))
            
            fig_comparison.update_layout(
                title='📊 Comparação: Iniciativas Brasileiras vs Globais',
                yaxis_title='Valores',
                height=500
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Radar chart comparativo
            brasil_data = df_comp[df_comp['categoria'] == 'Brasil'][available_metrics].mean()
            global_data = df_comp[df_comp['categoria'] == 'Global'][available_metrics].mean()
            
            if not brasil_data.empty and not global_data.empty:
                # Normalizar dados para radar
                combined = pd.concat([brasil_data, global_data], axis=1).fillna(0)
                combined.columns = ['Brasil', 'Global']
                
                # Normalizar (0-1) por métrica
                for metric in combined.index:
                    max_val = combined.loc[metric].max()
                    min_val = combined.loc[metric].min()
                    if max_val != min_val:
                        if metric == 'resolucao':  # Inverter resolução (menor é melhor)
                            combined.loc[metric] = 1 - (combined.loc[metric] - min_val) / (max_val - min_val)
                        else:
                            combined.loc[metric] = (combined.loc[metric] - min_val) / (max_val - min_val)
                
                fig_radar_comp = go.Figure()
                
                for col in combined.columns:
                    values = combined[col].tolist()
                    values.append(values[0])  # Fechar o polígono
                    
                    fig_radar_comp.add_trace(go.Scatterpolar(
                        r=values,
                        theta=list(combined.index) + [combined.index[0]],
                        fill='toself',
                        name=col
                    ))
                
                fig_radar_comp.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title='🎯 Radar: Brasil vs Global (normalizado)',
                    height=500
                )
                st.plotly_chart(fig_radar_comp, use_container_width=True)
            
            # Estatísticas comparativas
            stats_comp = df_comp.groupby('categoria')[available_metrics].agg(['mean', 'std', 'count']).round(2)
            st.markdown("### 📊 Estatísticas Comparativas")
            st.dataframe(stats_comp, use_container_width=True)
    else:
        st.info("Dados de escopo não disponíveis para comparação Brasil vs Global.")

def run_lulc_ecossistema_provedores(df_teste, df_original):
    """Análise do ecossistema de provedores LULC"""
    st.subheader('🔗 Ecossistema de Provedores LULC')
    
    if 'Provedor' in df_original.columns:
        # Adicionar provedor ao df_teste
        df_eco = df_teste.copy()
        provedor_map = dict(zip(df_original['Nome'], df_original['Provedor']))
        df_eco['provedor'] = df_eco['produto'].map(provedor_map)
        
        # Gráfico de barras por provedor
        if 'provedor' in df_eco.columns:
            provedor_counts = df_eco['provedor'].value_counts()
            
            fig_providers = px.bar(
                x=provedor_counts.values,
                y=provedor_counts.index,
                orientation='h',
                title='🏢 Número de Iniciativas por Provedor',
                labels={'x': 'Número de Iniciativas', 'y': 'Provedor'}
            )
            fig_providers.update_layout(height=500)
            st.plotly_chart(fig_providers, use_container_width=True)
            
            # Sunburst: Provedor -> Metodologia -> Escopo
            if all(col in df_eco.columns for col in ['provedor', 'metodologia', 'escopo']):
                sunburst_eco = df_eco.groupby(['provedor', 'metodologia', 'escopo']).size().reset_index(name='count')
                
                if not sunburst_eco.empty:
                    fig_sunburst_eco = px.sunburst(
                        sunburst_eco,
                        path=['provedor', 'metodologia', 'escopo'],
                        values='count',
                        title='☀️ Hierarquia: Provedor → Metodologia → Escopo'
                    )
                    fig_sunburst_eco.update_layout(height=600)
                    st.plotly_chart(fig_sunburst_eco, use_container_width=True)
            
            # Performance média por provedor
            if 'acuracia' in df_eco.columns:
                provider_performance = df_eco.groupby('provedor').agg({
                    'acuracia': ['mean', 'std', 'count'],
                    'resolucao': ['mean', 'min', 'max'] if 'resolucao' in df_eco.columns else None,
                    'num_classes': 'mean' if 'num_classes' in df_eco.columns else None
                }).round(2)
                
                st.markdown("### 🎯 Performance por Provedor")
                st.dataframe(provider_performance, use_container_width=True)
    else:
        st.info("Dados de provedor não disponíveis no dataset original.")

def run_graficos_classicos(df_teste, meta_geral, df_original, processar_disponibilidade_para_range):
    """Gráficos clássicos do dashboard"""
    st.subheader('📊 Gráficos Clássicos do Dashboard')
    
    # Sub-tabs para gráficos clássicos
    classic_tabs = st.tabs(["Scatter Plot", "Ranking Acurácia", "Box Plot", "Overlap Temporal"])
    
    with classic_tabs[0]:
        # Scatter plot básico
        if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
            fig_scatter = px.scatter(
                df_teste,
                x='resolucao',
                y='acuracia',
                color='metodologia',
                size=[20] * len(df_teste),
                hover_name='produto',
                title='🎯 Acurácia vs Resolução Espacial',
                labels={'resolucao': 'Resolução Espacial (m)', 'acuracia': 'Acurácia (%)'}
            )
            fig_scatter.update_traces(marker=dict(line=dict(width=2, color='white')))
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    with classic_tabs[1]:
        # Ranking de acurácia
        if 'acuracia' in df_teste.columns:
            accuracy_sorted = df_teste.sort_values('acuracia', ascending=True)
            fig_ranking = px.bar(
                accuracy_sorted,
                x='acuracia',
                y='produto',
                orientation='h',
                color='acuracia',
                color_continuous_scale='RdYlGn',
                title="🏆 Ranking de Acurácia por Produto LULC",
                labels={'acuracia': 'Acurácia (%)', 'produto': 'Produto'},
                text='acuracia'
            )
            fig_ranking.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_ranking, use_container_width=True)
    
    with classic_tabs[2]:
        # Box plot por metodologia
        if 'acuracia' in df_teste.columns and 'metodologia' in df_teste.columns:
            fig_box = px.box(
                df_teste,
                x='metodologia',
                y='acuracia',
                title='📦 Distribuição de Acurácia por Metodologia',
                labels={'metodologia': 'Metodologia', 'acuracia': 'Acurácia (%)'}
            )
            fig_box.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig_box, use_container_width=True)
    
    with classic_tabs[3]:
        # Overlap temporal usando plots.py
        if meta_geral:
            from plots import plot_ano_overlap
            fig_overlap = plot_ano_overlap(meta_geral, df_original)
            st.plotly_chart(fig_overlap, use_container_width=True)

def run_barras_duplas_completo(df_teste):
    """Gráficos de barras duplas"""
    st.subheader('🎯 Gráficos de Barras Duplas')
    
    if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
        df_copy = df_teste.dropna(subset=['acuracia', 'resolucao'])
        if not df_copy.empty:
            # Normalizar resolução (inverter para que maior seja melhor)
            df_copy['resolucao_norm'] = 100 * (1 / df_copy['resolucao']) / (1 / df_copy['resolucao']).max()
            
            fig_dual = go.Figure()
            fig_dual.add_trace(go.Bar(
                y=df_copy['produto'],
                x=df_copy['acuracia'],
                name='Acurácia (%)',
                orientation='h',
                marker_color='royalblue'
            ))
            fig_dual.add_trace(go.Bar(
                y=df_copy['produto'],
                x=df_copy['resolucao_norm'],
                name='Resolução (normalizada)',
                orientation='h',
                marker_color='orange'
            ))
            fig_dual.update_layout(
                barmode='group',
                title='📊 Comparação: Acurácia vs Resolução (normalizada)',
                height=600
            )
            st.plotly_chart(fig_dual, use_container_width=True)

def run_radar_charts_completo(df_teste):
    """Gráficos radar completos"""
    st.subheader('🕸️ Gráficos Radar Completos')
    
    metrics = ['acuracia', 'resolucao', 'num_classes']
    available_metrics = [m for m in metrics if m in df_teste.columns]
    
    if len(available_metrics) >= 2:
        df_radar = df_teste[['produto'] + available_metrics].dropna()
        
        if not df_radar.empty:
            # Normalizar dados
            df_normalized = df_radar.copy()
            for metric in available_metrics:
                min_val, max_val = df_radar[metric].min(), df_radar[metric].max()
                if max_val != min_val:
                    if metric == 'resolucao':  # Inverter resolução
                        df_normalized[metric] = 1 - (df_radar[metric] - min_val) / (max_val - min_val)
                    else:
                        df_normalized[metric] = (df_radar[metric] - min_val) / (max_val - min_val)
            
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Set1
            
            for i, (idx, row) in enumerate(df_normalized.iterrows()):
                values = row[available_metrics].tolist()
                values.append(values[0])  # Fechar o polígono
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=available_metrics + [available_metrics[0]],
                    fill='toself',
                    name=row['produto'],
                    line_color=colors[i % len(colors)]
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title='🕸️ Comparação Multi-dimensional (Radar)',
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)

def run_heatmaps_completo(df_teste):
    """Heatmaps completos"""
    st.subheader('🔥 Heatmaps Completos')
    
    metrics = ['acuracia', 'resolucao', 'num_classes']
    available_metrics = [m for m in metrics if m in df_teste.columns]
    
    if len(available_metrics) >= 2:
        df_heatmap = df_teste[['produto'] + available_metrics].dropna()
        
        if not df_heatmap.empty:
            # Normalizar dados
            df_normalized = df_heatmap.copy()
            for metric in available_metrics:
                min_val, max_val = df_heatmap[metric].min(), df_heatmap[metric].max()
                if max_val != min_val:
                    if metric == 'resolucao':
                        df_normalized[metric] = 1 - (df_heatmap[metric] - min_val) / (max_val - min_val)
                    else:
                        df_normalized[metric] = (df_heatmap[metric] - min_val) / (max_val - min_val)
            
            heatmap_data = df_normalized.set_index('produto')[available_metrics]
            
            fig_heatmap = px.imshow(
                heatmap_data,
                color_continuous_scale='viridis',
                aspect='auto',
                title='🔥 Heatmap de Comparação (valores normalizados)',
                labels=dict(x='Métrica', y='Produto', color='Valor Normalizado')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

def run_pizza_charts_completo(df_teste):
    """Gráficos de pizza completos"""
    st.subheader('🍰 Gráficos de Pizza Completos')
    
    pizza_tabs = st.tabs(["Por Metodologia", "Por Escopo", "Por Complexidade"])
    
    with pizza_tabs[0]:
        if 'metodologia' in df_teste.columns:
            metod_counts = df_teste['metodologia'].value_counts()
            fig_pie_metod = px.pie(
                values=metod_counts.values,
                names=metod_counts.index,
                title="🍰 Distribuição das Metodologias"
            )
            st.plotly_chart(fig_pie_metod, use_container_width=True)
    
    with pizza_tabs[1]:
        if 'escopo' in df_teste.columns:
            escopo_counts = df_teste['escopo'].value_counts()
            fig_pie_escopo = px.pie(
                values=escopo_counts.values,
                names=escopo_counts.index,
                title="🌍 Distribuição por Escopo Geográfico"
            )
            st.plotly_chart(fig_pie_escopo, use_container_width=True)
    
    with pizza_tabs[2]:
        if 'num_classes' in df_teste.columns:
            # Criar categorias de complexidade
            df_complexity = df_teste.copy()
            df_complexity['complexidade'] = pd.cut(
                df_complexity['num_classes'],
                bins=[0, 10, 20, 50],
                labels=['Baixa (≤10)', 'Média (11-20)', 'Alta (>20)']
            )
            complexity_counts = df_complexity['complexidade'].value_counts()
            fig_pie_complex = px.pie(
                values=complexity_counts.values,
                names=complexity_counts.index,
                title="🧮 Distribuição por Complexidade de Classes"
            )
            st.plotly_chart(fig_pie_complex, use_container_width=True)

def run_box_plots_completo(df_teste):
    """Box plots completos"""
    st.subheader('📦 Box Plots Completos')
    
    box_tabs = st.tabs(["Por Metodologia", "Por Escopo", "Múltiplas Métricas"])
    
    with box_tabs[0]:
        if 'acuracia' in df_teste.columns and 'metodologia' in df_teste.columns:
            fig_box_metod = px.box(
                df_teste,
                x='metodologia',
                y='acuracia',
                title='📦 Acurácia por Metodologia'
            )
            fig_box_metod.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_box_metod, use_container_width=True)
    
    with box_tabs[1]:
        if 'acuracia' in df_teste.columns and 'escopo' in df_teste.columns:
            fig_box_escopo = px.box(
                df_teste,
                x='escopo',
                y='acuracia',
                title='📦 Acurácia por Escopo'
            )
            fig_box_escopo.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_box_escopo, use_container_width=True)
    
    with box_tabs[2]:
        # Box plots para múltiplas métricas
        metrics = ['acuracia', 'resolucao', 'num_classes']
        available_metrics = [m for m in metrics if m in df_teste.columns]
        
        for metric in available_metrics:
            if 'metodologia' in df_teste.columns:
                fig_box = px.box(
                    df_teste,
                    x='metodologia',
                    y=metric,
                    title=f'📦 {metric.title()} por Metodologia'
                )
                fig_box.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_box, use_container_width=True)

def run_violin_plots_completo(df_teste):
    """Violin plots completos"""
    st.subheader('🎻 Violin Plots Completos')
    
    if 'acuracia' in df_teste.columns and 'metodologia' in df_teste.columns:
        fig_violin = px.violin(
            df_teste,
            x='metodologia',
            y='acuracia',
            color='metodologia',
            title='🎻 Distribuição de Acurácia por Metodologia'
        )
        fig_violin.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)
    
    if 'resolucao' in df_teste.columns and 'metodologia' in df_teste.columns:
        fig_violin_res = px.violin(
            df_teste,
            x='metodologia',
            y='resolucao',
            color='metodologia',
            title='🎻 Distribuição de Resolução por Metodologia',
            log_y=True
        )
        fig_violin_res.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_violin_res, use_container_width=True)

def run_sunburst_completo(df_teste):
    """Sunburst charts completos"""
    st.subheader('☀️ Sunburst Charts Completos')
    
    if all(col in df_teste.columns for col in ['metodologia', 'escopo']):
        # Sunburst: Metodologia -> Escopo
        sunburst_data = df_teste.groupby(['metodologia', 'escopo']).size().reset_index(name='count')
        
        if not sunburst_data.empty:
            fig_sunburst = px.sunburst(
                sunburst_data,
                path=['metodologia', 'escopo'],
                values='count',
                title='☀️ Hierarquia: Metodologia → Escopo'
            )
            fig_sunburst.update_layout(height=600)
            st.plotly_chart(fig_sunburst, use_container_width=True)

def run_bolhas_3d_completo(df_teste):
    """Gráficos de bolhas 3D completos"""
    st.subheader('🫧 Gráficos de Bolhas 3D Completos')
    
    if all(col in df_teste.columns for col in ['acuracia', 'resolucao', 'num_classes']):
        fig_bubble = px.scatter(
            df_teste,
            x='resolucao',
            y='acuracia',
            size='num_classes',
            color='metodologia',
            hover_name='produto',
            title="🫧 Acurácia vs Resolução (tamanho = nº de classes)",
            labels={
                'resolucao': 'Resolução Espacial (m)',
                'acuracia': 'Acurácia (%)',
                'num_classes': 'Número de Classes'
            }
        )
        fig_bubble.update_layout(height=500)
        st.plotly_chart(fig_bubble, use_container_width=True)

def run_disponibilidade_matrix_completo(df_teste, meta_geral, processar_disponibilidade_para_range):
    """Matrix de disponibilidade temporal completa"""
    st.subheader('📋 Matrix de Disponibilidade Temporal Completa')
    
    if meta_geral:
        # Criar matrix usando metadados
        all_years = set()
        availability_data = []
        
        for nome, meta in meta_geral.items():
            if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                for ano in meta['anos_disponiveis']:
                    all_years.add(ano)
                    availability_data.append({'nome': nome, 'ano': ano, 'disponivel': 1})
        
        if availability_data:
            avail_df = pd.DataFrame(availability_data)
            
            # Criar matrix completa
            all_names = sorted(meta_geral.keys())
            all_years_sorted = sorted(all_years)
            
            matrix_data = np.zeros((len(all_names), len(all_years_sorted)))
            
            for i, nome in enumerate(all_names):
                if 'anos_disponiveis' in meta_geral[nome]:
                    for ano in meta_geral[nome]['anos_disponiveis']:
                        j = all_years_sorted.index(ano)
                        matrix_data[i, j] = 1
            
            fig_matrix = px.imshow(
                matrix_data,
                x=all_years_sorted,
                y=all_names,
                color_continuous_scale=['white', 'green'],
                title='📋 Matrix de Disponibilidade Temporal (1985-2024)',
                labels=dict(x='Ano', y='Iniciativa', color='Disponível')
            )
            fig_matrix.update_layout(height=600)
            st.plotly_chart(fig_matrix, use_container_width=True)

# ==========================================
# NOVOS GRÁFICOS AVANÇADOS
# ==========================================

def run_area_empilhada_evolucao(df_teste, meta_geral):
    """Gráfico de área empilhada mostrando evolução por década"""
    st.subheader('📈 Evolução de Produtos LULC por Década (Área Empilhada)')
    
    if meta_geral:
        # Criar dados para evolução temporal
        evolution_data = []
        
        for nome, meta in meta_geral.items():
            if nome in df_teste['produto'].values:
                row = df_teste[df_teste['produto'] == nome].iloc[0]
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    primeiro_ano = min(meta['anos_disponiveis'])
                    
                    # Classificar resolução
                    resolucao = row.get('resolucao', 0)
                    if resolucao < 50:
                        cat_resolucao = '<50m'
                    elif resolucao <= 300:
                        cat_resolucao = '50-300m'
                    else:
                        cat_resolucao = '>300m'
                    
                    # Classificar escopo
                    escopo = str(row.get('escopo', 'N/A'))
                    if 'Global' in escopo or 'Mundial' in escopo:
                        cat_escopo = 'Global'
                    elif 'Nacional' in escopo or 'Brasil' in escopo:
                        cat_escopo = 'Nacional'
                    else:
                        cat_escopo = 'Regional'
                    
                    # Classificar década
                    decada = f"{(primeiro_ano//10)*10}s"
                    
                    evolution_data.append({
                        'produto': nome,
                        'ano': primeiro_ano,
                        'decada': decada,
                        'resolucao_cat': cat_resolucao,
                        'escopo_cat': cat_escopo
                    })
        
        if evolution_data:
            evo_df = pd.DataFrame(evolution_data)
            
            # Gráfico 1: Evolução por resolução
            resolution_decade = evo_df.groupby(['decada', 'resolucao_cat']).size().reset_index(name='count')
            resolution_pivot = resolution_decade.pivot(index='decada', columns='resolucao_cat', values='count').fillna(0)
            
            fig_res = go.Figure()
            colors_res = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            for i, col in enumerate(resolution_pivot.columns):
                fig_res.add_trace(go.Scatter(
                    x=resolution_pivot.index,
                    y=resolution_pivot[col],
                    stackgroup='one',
                    name=f'Resolução {col}',
                    fill='tonexty',
                    line=dict(color=colors_res[i % len(colors_res)])
                ))
            
            fig_res.update_layout(
                title='📊 Evolução por Categoria de Resolução Espacial',
                xaxis_title='Década',
                yaxis_title='Número de Produtos Lançados',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_res, use_container_width=True)
            
            # Gráfico 2: Evolução por escopo
            scope_decade = evo_df.groupby(['decada', 'escopo_cat']).size().reset_index(name='count')
            scope_pivot = scope_decade.pivot(index='decada', columns='escopo_cat', values='count').fillna(0)
            
            fig_scope = go.Figure()
            colors_scope = ['#96CEB4', '#FECA57', '#FF9FF3']
            
            for i, col in enumerate(scope_pivot.columns):
                fig_scope.add_trace(go.Scatter(
                    x=scope_pivot.index,
                    y=scope_pivot[col],
                    stackgroup='one',
                    name=f'Escopo {col}',
                    fill='tonexty',
                    line=dict(color=colors_scope[i % len(colors_scope)])
                ))
            
            fig_scope.update_layout(
                title='🌍 Evolução por Escopo Geográfico',
                xaxis_title='Década',
                yaxis_title='Número de Produtos Lançados',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_scope, use_container_width=True)
            
            # Estatísticas de evolução
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🎯 Década Mais Produtiva", evo_df['decada'].mode().iloc[0])
            with col2:
                st.metric("🔍 Resolução Dominante", evo_df['resolucao_cat'].mode().iloc[0])
            with col3:
                st.metric("🌍 Escopo Mais Comum", evo_df['escopo_cat'].mode().iloc[0])
        
        else:
            st.warning("Dados temporais insuficientes para análise de evolução.")
    else:
        st.error("Metadados não disponíveis.")

def run_mapa_hexagonal_cobertura(df_teste):
    """Mapa hexagonal simulado mostrando cobertura por região"""
    st.subheader('🗺️ Mapa Hexagonal de Cobertura Global LULC')
    
    # Simular dados de cobertura por região (hexágonos)
    regions_data = {
        'América do Norte': {'lat': 45, 'lon': -100, 'produtos': 8, 'hex_size': 30},
        'América do Sul': {'lat': -15, 'lon': -60, 'produtos': 12, 'hex_size': 25},
        'Europa': {'lat': 50, 'lon': 10, 'produtos': 15, 'hex_size': 20},
        'África': {'lat': 0, 'lon': 20, 'produtos': 6, 'hex_size': 35},
        'Ásia': {'lat': 30, 'lon': 100, 'produtos': 18, 'hex_size': 40},
        'Oceania': {'lat': -25, 'lon': 140, 'produtos': 4, 'hex_size': 15},
        'Ártico': {'lat': 75, 'lon': 0, 'produtos': 2, 'hex_size': 50},
        'Antártica': {'lat': -80, 'lon': 0, 'produtos': 1, 'hex_size': 30}
    }
    
    # Converter para DataFrame
    map_data = []
    for region, data in regions_data.items():
        map_data.append({
            'regiao': region,
            'latitude': data['lat'],
            'longitude': data['lon'],
            'produtos_disponiveis': data['produtos'],
            'tamanho_hex': data['hex_size']
        })
    
    map_df = pd.DataFrame(map_data)
    
    # Gráfico de mapa com pontos representando hexágonos
    fig_map = px.scatter_geo(
        map_df,
        lat='latitude',
        lon='longitude',
        color='produtos_disponiveis',
        size='tamanho_hex',
        hover_name='regiao',
        hover_data={'produtos_disponiveis': True, 'tamanho_hex': False},
        color_continuous_scale='RdYlBu_r',
        title='🌍 Cobertura Global de Produtos LULC por Região',
        labels={'produtos_disponiveis': 'Produtos Disponíveis'}
    )
    
    fig_map.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=600
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Tabela de cobertura por região
    st.markdown("#### 📊 Detalhes da Cobertura por Região")
    
    # Adicionar categorias de cobertura
    map_df['categoria_cobertura'] = pd.cut(
        map_df['produtos_disponiveis'],
        bins=[0, 5, 10, 15, 20],
        labels=['Baixa (1-5)', 'Média (6-10)', 'Alta (11-15)', 'Muito Alta (16+)']
    )
    
    st.dataframe(
        map_df[['regiao', 'produtos_disponiveis', 'categoria_cobertura']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "regiao": st.column_config.TextColumn("Região", width="large"),
            "produtos_disponiveis": st.column_config.NumberColumn("Produtos Disponíveis", format="%d"),
            "categoria_cobertura": st.column_config.TextColumn("Categoria de Cobertura", width="medium")
        }
    )
    
    # Insights de gaps
    st.markdown("#### 🚨 Gaps de Cobertura Identificados")
    low_coverage = map_df[map_df['produtos_disponiveis'] <= 5]
    
    if not low_coverage.empty:
        for _, region in low_coverage.iterrows():
            st.warning(f"⚠️ **{region['regiao']}**: Apenas {region['produtos_disponiveis']} produtos disponíveis - Gap de cobertura detectado!")
    
    # Distribuição de cobertura
    fig_dist = px.pie(
        map_df,
        values='produtos_disponiveis',
        names='regiao',
        title='🥧 Distribuição de Produtos por Região'
    )
    st.plotly_chart(fig_dist, use_container_width=True)

def run_rede_sensores_algoritmos(df_teste, df_original):
    """Rede de sensores e algoritmos"""
    st.subheader('🌐 Rede de Sensores e Algoritmos LULC')
    
    # Simular dados de sensores e algoritmos
    if 'metodologia' in df_teste.columns:
        # Extrair sensores e algoritmos dos dados
        sensores = ['Landsat', 'Sentinel', 'MODIS', 'AVHRR', 'SPOT']
        algoritmos = ['Random Forest', 'SVM', 'Deep Learning', 'Decision Tree', 'Neural Network']
        
        # Criar conexões simuladas
        connections = []
        sensor_counts = {}
        algo_counts = {}
        
        for _, row in df_teste.iterrows():
            produto = row['produto']
            metodologia = str(row.get('metodologia', ''))
            
            # Simular sensor baseado no produto
            sensor = np.random.choice(sensores)
            
            # Simular algoritmo baseado na metodologia
            if 'Machine Learning' in metodologia or 'ML' in metodologia:
                algoritmo = np.random.choice(['Random Forest', 'SVM', 'Neural Network'])
            elif 'Deep' in metodologia:
                algoritmo = 'Deep Learning'
            else:
                algoritmo = np.random.choice(algoritmos)
            
            connections.append({
                'produto': produto,
                'sensor': sensor,
                'algoritmo': algoritmo,
                'source': sensor,
                'target': algoritmo
            })
            
            sensor_counts[sensor] = sensor_counts.get(sensor, 0) + 1
            algo_counts[algoritmo] = algo_counts.get(algoritmo, 0) + 1
        
        conn_df = pd.DataFrame(connections)
        
        # Criar gráfico de rede usando scatter plot
        st.markdown("#### 📊 Frequência de Uso - Sensores")
        
        sensor_data = pd.DataFrame(list(sensor_counts.items()), columns=['Sensor', 'Frequencia'])
        fig_sensors = px.bar(
            sensor_data,
            x='Sensor',
            y='Frequencia',
            color='Frequencia',
            title='📡 Frequência de Uso por Sensor',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_sensors, use_container_width=True)
        
        st.markdown("#### 🧠 Frequência de Uso - Algoritmos")
        
        algo_data = pd.DataFrame(list(algo_counts.items()), columns=['Algoritmo', 'Frequencia'])
        fig_algos = px.bar(
            algo_data,
            x='Algoritmo',
            y='Frequencia',
            color='Frequencia',
            title='🤖 Frequência de Uso por Algoritmo',
            color_continuous_scale='plasma'
        )
        fig_algos.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_algos, use_container_width=True)
        
        # Matriz de combinações
        combination_matrix = conn_df.groupby(['sensor', 'algoritmo']).size().reset_index(name='count')
        
        if not combination_matrix.empty:
            fig_matrix = px.density_heatmap(
                combination_matrix,
                x='algoritmo',
                y='sensor',
                z='count',
                title='🔥 Matriz de Combinações Sensor-Algoritmo',
                color_continuous_scale='Blues'
            )
            fig_matrix.update_layout(height=400)
            st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Top combinações
        top_combinations = combination_matrix.nlargest(5, 'count')
        
        st.markdown("#### 🏆 Top 5 Combinações Mais Usadas")
        for _, combo in top_combinations.iterrows():
            st.info(f"📡 **{combo['sensor']}** + 🤖 **{combo['algoritmo']}**: {combo['count']} produtos")
    
    else:
        st.warning("Dados de metodologia não disponíveis para análise de rede.")

def run_timeline_melhorado_barras(meta_geral, df_original):
    """Timeline melhorado com barras por ano, análise comparativa e legenda"""
    st.subheader('⏰ Timeline Melhorado - Disponibilidade por Ano')
    
    if meta_geral:
        # Criar dados de disponibilidade ano a ano com informações adicionais
        timeline_data = []
        all_years = set()
        
        # Mapear produtos para obter características técnicas
        produto_info = {}
        if df_original is not None and not df_original.empty:
            for _, row in df_original.iterrows():
                produto_info[row['Nome']] = {
                    'metodologia': row.get('Metodologia', 'N/A'),
                    'escopo': row.get('Escopo', 'N/A'),
                    'acuracia': row.get('Acurácia (%)', 0),
                    'resolucao': row.get('Resolução (m)', 0)
                }
        
        # Coletar todos os anos de todas as iniciativas
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
                    all_years.add(ano)
        
        if timeline_data and all_years:
            timeline_df = pd.DataFrame(timeline_data)
            
            # Criar range completo de anos (1985-2024 para manter escala consistente)
            min_year, max_year = 1985, 2024
            all_years_range = list(range(min_year, max_year + 1))
            produtos_unicos = sorted(timeline_df['produto'].unique())
            
            # Criar matriz completa (produto x ano)
            matrix_data = []
            for produto in produtos_unicos:
                produto_anos = timeline_df[timeline_df['produto'] == produto]['ano'].tolist()
                produto_metodologia = timeline_df[timeline_df['produto'] == produto]['metodologia'].iloc[0]
                for ano in all_years_range:
                    matrix_data.append({
                        'produto': produto,
                        'ano': ano,
                        'disponivel': 1 if ano in produto_anos else 0,
                        'metodologia': produto_metodologia
                    })
            
            matrix_df = pd.DataFrame(matrix_data)            # Criar o gráfico de timeline como barras horizontais
            fig_timeline = go.Figure()
            
            # Usar cores Set1 (padrão do sistema) e mapear por produto/iniciativa
            colors = px.colors.qualitative.Set1
            metodologias_unicas = timeline_df['metodologia'].unique()  # Manter para análises posteriores
            color_map = {produto: colors[i % len(colors)] for i, produto in enumerate(produtos_unicos)}
            
            # Adicionar uma legenda personalizada para cada iniciativa
            legend_added = set()
            
            for i, produto in enumerate(produtos_unicos):
                produto_data = matrix_df[matrix_df['produto'] == produto]
                anos_disponiveis = produto_data[produto_data['disponivel'] == 1]['ano'].tolist()
                metodologia = produto_data['metodologia'].iloc[0]
                cor = color_map.get(produto, colors[0])
                
                if anos_disponiveis:
                    # Criar segmentos contínuos
                    segments = []
                    start = anos_disponiveis[0]
                    end = anos_disponiveis[0]
                    
                    for j in range(1, len(anos_disponiveis)):
                        if anos_disponiveis[j] == end + 1:
                            end = anos_disponiveis[j]                        
                        else:
                            segments.append((start, end))
                            start = anos_disponiveis[j]
                            end = anos_disponiveis[j]
                    
                    segments.append((start, end))
                    
                    # Plotar cada segmento
                    for seg_start, seg_end in segments:
                        # Adicionar legenda apenas uma vez por produto/iniciativa
                        show_legend = produto not in legend_added
                        if show_legend:
                            legend_added.add(produto)
                            
                        fig_timeline.add_trace(go.Scatter(
                            x=[seg_start, seg_end + 0.8],
                            y=[i, i],
                            mode='lines',
                            line=dict(
                                color=cor,
                                width=15
                            ),
                            name=produto if show_legend else None,
                            showlegend=show_legend,
                            legendgroup=produto,
                            hovertemplate=f"<b>{produto}</b><br>Metodologia: {metodologia}<br>Anos: {seg_start}-{seg_end}<extra></extra>"
                        ))
            
            # Configurar layout com legenda e escala fixa
            fig_timeline.update_layout(
                title='📅 Timeline de Disponibilidade das Iniciativas LULC (1985-2024)',
                xaxis_title='Ano',
                yaxis_title='Produtos LULC',
                height=max(500, len(produtos_unicos) * 25),
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(produtos_unicos))),
                    ticktext=produtos_unicos,
                    showgrid=True,
                    gridcolor='lightgray'
                ),
                xaxis=dict(
                    range=[1985, 2024],  # Manter escala fixa
                    dtick=5,  # Marcar a cada 5 anos
                    gridcolor='lightgray',
                    gridwidth=1,
                    showgrid=True
                ),
                hovermode='closest',
                showlegend=True,                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    title="Iniciativas LULC"
                )
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            safe_download_image(fig_timeline, "timeline_melhorado_barras.png", "⬇️ Baixar Timeline Melhorado (PNG)")
            
            # Análise comparativa por metodologia
            st.markdown("#### 📊 Análise Comparativa por Metodologia")
            
            # Estatísticas por metodologia
            metod_stats = timeline_df.groupby('metodologia').agg({
                'produto': 'nunique',
                'ano': ['min', 'max', 'count']
            }).round(1)
            metod_stats.columns = ['Produtos', 'Primeiro Ano', 'Último Ano', 'Total Anos-Produto']
            
            # Calcular período médio de cobertura
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
            
            # Ranking de Acurácia dos Produtos LULC
            st.markdown("#### 🏆 Ranking de Acurácia dos Produtos LULC")
            
            # Criar dados de ranking combinando informações do timeline com dados de acurácia
            ranking_data = []
            for produto in produtos_unicos:
                produto_timeline = timeline_df[timeline_df['produto'] == produto].iloc[0]
                metodologia = produto_timeline['metodologia']
                
                # Obter dados de acurácia do df_original se disponível
                acuracia = 0
                resolucao = 0
                if df_original is not None and not df_original.empty:
                    produto_row = df_original[df_original['Nome'] == produto]
                    if not produto_row.empty:
                        acuracia = produto_row['Acurácia (%)'].iloc[0] if 'Acurácia (%)' in produto_row.columns else 0
                        resolucao = produto_row['Resolução (m)'].iloc[0] if 'Resolução (m)' in produto_row.columns else 0
                
                # Calcular cobertura temporal
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
            
            # Gráfico de ranking horizontal por acurácia
            if ranking_df['acuracia'].sum() > 0:  # Se há dados de acurácia
                ranking_sorted = ranking_df.sort_values('acuracia', ascending=True)
                
                fig_ranking = px.bar(
                    ranking_sorted,
                    x='acuracia',
                    y='produto',
                    color='metodologia',
                    orientation='h',
                    title='🏆 Ranking de Acurácia dos Produtos LULC',
                    labels={'acuracia': 'Acurácia (%)', 'produto': 'Produto'},
                    color_discrete_sequence=colors,
                    text='acuracia'
                )
                
                fig_ranking.update_traces(
                    texttemplate='%{text:.1f}%', 
                    textposition='outside',
                    marker_line=dict(width=2, color='white')
                )
                
                fig_ranking.update_layout(
                    height=max(400, len(ranking_sorted) * 25),
                    xaxis_title='Acurácia (%)',
                    yaxis_title='Produtos LULC',
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        title="Metodologia"
                    )
                )
                
                st.plotly_chart(fig_ranking, use_container_width=True)
                safe_download_image(fig_ranking, "ranking_acuracia_lulc.png", "⬇️ Baixar Ranking (PNG)")
                
                # Top 5 e Bottom 5
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
                
                # Estatísticas do ranking
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
            
            # Estatísticas gerais do timeline
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
            # Gráfico de distribuição de metodologias ao longo do tempo
            st.markdown("#### ⏰ Evolução das Metodologias ao Longo do Tempo")
            
            # Criar dados para gráfico de área empilhada por metodologia
            timeline_pivot = timeline_df.groupby(['ano', 'metodologia']).size().reset_index(name='count')
            
            fig_metodologia_evolucao = px.area(
                timeline_pivot,
                x='ano',
                y='count',
                color='metodologia',
                title='📈 Evolução da Adoção de Metodologias LULC',
                labels={'ano': 'Ano', 'count': 'Número de Produtos', 'metodologia': 'Metodologia'},
                color_discrete_sequence=colors
            )
            
            fig_metodologia_evolucao.update_layout(
                height=400,
                xaxis=dict(range=[min(anos_reais), max(anos_reais)]),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_metodologia_evolucao, use_container_width=True)
        
        else:
            st.warning("Dados temporais insuficientes para criar timeline.")
    else:
        st.error("Metadados não disponíveis.")

def run_matriz_adequacao_uso(df_teste):
    """Matriz de adequação por caso de uso"""
    st.subheader('🎯 Matriz de Adequação por Caso de Uso')
    
    # Definir casos de uso e critérios
    casos_uso = ['Desmatamento', 'Agricultura', 'Urbano', 'Clima', 'Biodiversidade']
    
    if len(df_teste) > 0:
        # Simular scores de adequação baseados nas características
        adequacao_data = []
        
        for _, row in df_teste.iterrows():
            produto = row['produto']
            acuracia = row.get('acuracia', 0)
            resolucao = row.get('resolucao', 1000)
            num_classes = row.get('num_classes', 0)
            
            for caso in casos_uso:
                # Calcular score baseado nas características
                if caso == 'Desmatamento':
                    # Melhor com alta resolução e boa acurácia
                    score = (acuracia / 100) * 0.4 + (1 / max(resolucao, 1)) * 100000 * 0.4 + (min(num_classes, 20) / 20) * 0.2
                elif caso == 'Agricultura':
                    # Moderadamente sensível à resolução
                    score = (acuracia / 100) * 0.5 + (1 / max(resolucao, 1)) * 50000 * 0.3 + (min(num_classes, 15) / 15) * 0.2
                elif caso == 'Urbano':
                    # Muito sensível à resolução
                    score = (acuracia / 100) * 0.3 + (1 / max(resolucao, 1)) * 200000 * 0.6 + (min(num_classes, 25) / 25) * 0.1
                elif caso == 'Clima':
                    # Menos sensível à resolução, mais à cobertura temporal
                    score = (acuracia / 100) * 0.6 + (1 / max(resolucao, 1)) * 10000 * 0.2 + (min(num_classes, 10) / 10) * 0.2
                else:  # Biodiversidade
                    # Equilibrado
                    score = (acuracia / 100) * 0.4 + (1 / max(resolucao, 1)) * 80000 * 0.3 + (min(num_classes, 30) / 30) * 0.3
                
                # Normalizar para escala 1-5
                score_normalizado = max(1, min(5, score * 5))
                
                adequacao_data.append({
                    'produto': produto,
                    'caso_uso': caso,
                    'score': round(score_normalizado, 1)
                })
        
        adequacao_df = pd.DataFrame(adequacao_data)
        
        # Criar matriz pivot
        matriz_adequacao = adequacao_df.pivot(index='produto', columns='caso_uso', values='score')
        
        # Gráfico de heatmap da matriz
        fig_matrix = px.imshow(
            matriz_adequacao.values,
            x=matriz_adequacao.columns,
            y=matriz_adequacao.index,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title='🎯 Matriz de Adequação: Produtos vs Casos de Uso (1-5)',
            labels=dict(x='Caso de Uso', y='Produto', color='Score de Adequação')
        )
        
        # Adicionar valores na matriz
        for i in range(len(matriz_adequacao.index)):
            for j in range(len(matriz_adequacao.columns)):
                score = matriz_adequacao.iloc[i, j]
                if score >= 4:
                    stars = '★★★'
                elif score >= 3:
                    stars = '★★'
                else:
                    stars = '★'
                
                fig_matrix.add_annotation(
                    x=j,
                    y=i,
                    text=f"{score}<br>{stars}",
                    showarrow=False,
                    font=dict(color='white' if score < 3 else 'black', size=10)
                )
        
        fig_matrix.update_layout(height=max(400, len(matriz_adequacao.index) * 30))
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Recomendações por caso de uso
        st.markdown("#### 🏆 Produtos Mais Recomendados por Caso de Uso")
        
        for caso in casos_uso:
            top_produto = adequacao_df[adequacao_df['caso_uso'] == caso].nlargest(1, 'score')
            if not top_produto.empty:
                produto_nome = top_produto.iloc[0]['produto']
                score = top_produto.iloc[0]['score']
                stars = '★★★' if score >= 4 else '★★' if score >= 3 else '★'
                
                st.success(f"**{caso}**: {produto_nome} (Score: {score} {stars})")
        
        # Tabela detalhada
        st.markdown("#### 📊 Tabela Detalhada de Adequação")
        matriz_display = matriz_adequacao.round(1)
        st.dataframe(matriz_display, use_container_width=True)
        
        # Rankings
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🥇 Produtos Mais Versáteis (média geral)")
            versatilidade = adequacao_df.groupby('produto')['score'].mean().sort_values(ascending=False)
            for produto, score in versatilidade.head(5).items():
                st.write(f"• **{produto}**: {score:.1f}")
        
        with col2:
            st.markdown("##### 🎯 Casos de Uso Mais Atendidos")
            atendimento = adequacao_df.groupby('caso_uso')['score'].mean().sort_values(ascending=False)
            for caso, score in atendimento.items():
                st.write(f"• **{caso}**: {score:.1f}")
    
    else:
        st.warning("Dados insuficientes para análise de adequação.")

def run_analise_3d_gaps(df_teste, meta_geral):
    """Análise 3D para identificação de gaps"""
    st.subheader('🔍 Análise 3D de Gaps e Oportunidades')
    
    if meta_geral and len(df_teste) > 0:
        # Preparar dados 3D
        analise_3d_data = []
        
        for nome, meta in meta_geral.items():
            if nome in df_teste['produto'].values:
                row = df_teste[df_teste['produto'] == nome].iloc[0]
                
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                    cobertura_temporal = len(meta['anos_disponiveis'])
                    
                    analise_3d_data.append({
                        'produto': nome,
                        'cobertura_temporal': cobertura_temporal,
                        'resolucao_espacial': row.get('resolucao', 0),
                        'acuracia': row.get('acuracia', 0),
                        'escopo': str(row.get('escopo', 'N/A')),
                        'metodologia': str(row.get('metodologia', 'N/A'))
                    })
        
        if analise_3d_data:
            analise_3d_df = pd.DataFrame(analise_3d_data)
            
            # Classificar escopo para cores
            def classificar_escopo(escopo):
                if 'Global' in escopo or 'Mundial' in escopo:
                    return 'Global'
                elif 'Nacional' in escopo or 'Brasil' in escopo:
                    return 'Nacional'
                else:
                    return 'Regional'
            
            analise_3d_df['escopo_cat'] = analise_3d_df['escopo'].apply(classificar_escopo)
            
            # Gráfico 3D
            fig_3d = px.scatter_3d(
                analise_3d_df,
                x='cobertura_temporal',
                y='resolucao_espacial',
                z='acuracia',
                color='escopo_cat',
                size='acuracia',
                hover_name='produto',
                hover_data={'metodologia': True},
                title='🔍 Análise 3D: Cobertura Temporal × Resolução × Acurácia',
                labels={
                    'cobertura_temporal': 'Cobertura Temporal (anos)',
                    'resolucao_espacial': 'Resolução Espacial (m)',
                    'acuracia': 'Acurácia (%)',
                    'escopo_cat': 'Escopo Geográfico'
                }
            )
            
            # Usar escala logarítmica para resolução se necessário
            max_res = analise_3d_df['resolucao_espacial'].max()
            if max_res > 1000:
                fig_3d.update_layout(scene=dict(yaxis=dict(type='log')))
            
            fig_3d.update_layout(height=700)
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # Identificação de gaps
            st.markdown("#### 🕳️ Identificação de Gaps")
            
            gaps_identificados = []
            
            # Gap 1: Alta resolução + baixa cobertura temporal
            alta_res_baixa_temp = analise_3d_df[
                (analise_3d_df['resolucao_espacial'] <= 50) & 
                (analise_3d_df['cobertura_temporal'] <= 5)
            ]
            if not alta_res_baixa_temp.empty:
                gaps_identificados.append("🔍 **Gap de Continuidade Temporal**: Produtos com alta resolução mas pouca cobertura temporal")
            
            # Gap 2: Baixa acurácia + escopo global
            baixa_acc_global = analise_3d_df[
                (analise_3d_df['acuracia'] <= 70) & 
                (analise_3d_df['escopo_cat'] == 'Global')
            ]
            if not baixa_acc_global.empty:
                gaps_identificados.append("🌍 **Gap de Qualidade Global**: Produtos globais com acurácia limitada")
            
            # Gap 3: Espaços vazios no cubo 3D
            # Identificar regiões do espaço 3D com poucos produtos
            temp_bins = pd.cut(analise_3d_df['cobertura_temporal'], bins=3, labels=['Baixa', 'Média', 'Alta'])
            res_bins = pd.cut(analise_3d_df['resolucao_espacial'], bins=3, labels=['Fina', 'Média', 'Grossa'])
            acc_bins = pd.cut(analise_3d_df['acuracia'], bins=3, labels=['Baixa', 'Média', 'Alta'])
            
            space_analysis = pd.DataFrame({
                'temporal': temp_bins,
                'espacial': res_bins,
                'acuracia': acc_bins
            })
            
            # Mostrar gaps identificados
            if gaps_identificados:
                for gap in gaps_identificados:
                    st.warning(gap)
            else:
                st.success("✅ Nenhum gap crítico identificado na distribuição atual!")
            
            # Oportunidades de melhoria
            st.markdown("#### 💡 Oportunidades de Melhoria")
            
            oportunidades = []
            
            # Oportunidade 1: Melhorar produtos com baixa acurácia
            baixa_acuracia = analise_3d_df[analise_3d_df['acuracia'] < 80].sort_values('acuracia')
            if not baixa_acuracia.empty:
                produto_melhoria = baixa_acuracia.iloc[0]['produto']
                oportunidades.append(f"📈 **Melhoria de Acurácia**: {produto_melhoria} poderia se beneficiar de algoritmos mais avançados")
            
            # Oportunidade 2: Estender cobertura temporal
            baixa_temporal = analise_3d_df[analise_3d_df['cobertura_temporal'] < 10].sort_values('cobertura_temporal')
            if not baixa_temporal.empty:
                produto_temporal = baixa_temporal.iloc[0]['produto']
                oportunidades.append(f"⏰ **Extensão Temporal**: {produto_temporal} poderia expandir sua série histórica")
            
            # Oportunidade 3: Produtos candidatos a escopo global
            candidatos_global = analise_3d_df[
                (analise_3d_df['escopo_cat'] != 'Global') & 
                (analise_3d_df['acuracia'] >= 85)
            ].sort_values('acuracia', ascending=False)
            
            if not candidatos_global.empty:
                produto_global = candidatos_global.iloc[0]['produto']
                oportunidades.append(f"🌍 **Expansão Global**: {produto_global} tem potencial para cobertura global")
            
            for oportunidade in oportunidades:
                st.info(oportunidade)
            
            # Estatísticas do espaço 3D
            col1, col2, col3 = st.columns(3)
            
            with col1:
                densidade = len(analise_3d_df) / (
                    analise_3d_df['cobertura_temporal'].max() * 
                    analise_3d_df['resolucao_espacial'].max() * 
                    analise_3d_df['acuracia'].max()
                ) * 1000000
                st.metric("📊 Densidade do Espaço", f"{densidade:.2e}")
            
            with col2:
                melhor_equilibrio = analise_3d_df.loc[
                    (analise_3d_df['cobertura_temporal'] * analise_3d_df['acuracia'] / analise_3d_df['resolucao_espacial']).idxmax(),
                    'produto'
                ]
                st.metric("⚖️ Melhor Equilíbrio", melhor_equilibrio)
            
            with col3:
                correlacao = analise_3d_df[['cobertura_temporal', 'resolucao_espacial', 'acuracia']].corr().abs().mean().mean()
                st.metric("🔗 Correlação Média", f"{correlacao:.2f}")
        
        else:
            st.warning("Dados insuficientes para análise 3D.")
    else:
        st.error("Metadados ou dados não disponíveis.")

if __name__ == "__main__":
    main()
