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
        page_title="🧪 Testes Gráficos LULC",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧪 Testes de Visualizações LULC")
    st.markdown("### Sistema de Teste para Avaliação de Novos Gráficos Comparativos")
    
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

    # Menu de seleção de exemplos de gráficos
    st.markdown("### 🖼️ Exemplos de Gráficos LULC Avançados")
    example_tabs = st.tabs([
        "🔬 Performance Metodológica",
        "🌍 Densidade Temporal",
        "⚖️ Escopo vs Qualidade", 
        "🧮 Análise Classes",
        "📅 Evolução Tecnológica",
        "🇧🇷 Brasil vs Global",
        "🔗 Ecossistema Provedores",
        "📊 Gráficos Clássicos"
    ])

    with example_tabs[0]:
        run_lulc_performance_metodologica(df_teste, df_geral_original)
    
    with example_tabs[1]:
        run_lulc_densidade_temporal(df_teste, meta_geral, processar_disponibilidade_para_range)
    
    with example_tabs[2]:
        run_lulc_escopo_qualidade(df_teste)
    
    with example_tabs[3]:
        run_lulc_analise_classes(df_teste)
    
    with example_tabs[4]:
        run_lulc_evolucao_tecnologica(df_teste, meta_geral)
    
    with example_tabs[5]:
        run_lulc_brasil_vs_global(df_teste)
    
    with example_tabs[6]:
        run_lulc_ecossistema_provedores(df_teste, df_geral_original)
    
    with example_tabs[7]:
        # Gráficos clássicos existentes
        classic_subtabs = st.tabs([
            "Scatter Plot",
            "Ranking Acurácia", 
            "Box Plot",
            "Timeline"
        ])
        
        with classic_subtabs[0]:
            st.subheader('Scatter Plot: Acurácia vs Resolução')
            if 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
                fig_scatter = px.scatter(
                    df_teste,
                    x='resolucao',
                    y='acuracia',
                    color='metodologia' if 'metodologia' in df_teste.columns else None,
                    size='num_classes' if 'num_classes' in df_teste.columns else None,
                    hover_name='produto',
                    title="Acurácia vs Resolução Espacial",
                    labels={'resolucao': 'Resolução (m)', 'acuracia': 'Acurácia (%)'},
                    height=500
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                safe_download_image(fig_scatter, "exemplo_scatter.png", "⬇️ Baixar Scatter (PNG)")
            else:
                st.info("Colunas necessárias não encontradas.")
        
        with classic_subtabs[1]:
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
                safe_download_image(fig_ranking, "exemplo_ranking.png", "⬇️ Baixar Ranking (PNG)")
            else:
                st.info("Coluna 'acuracia' não encontrada.")
        
        with classic_subtabs[2]:
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
                safe_download_image(fig_box, "exemplo_boxplot.png", "⬇️ Baixar Box Plot (PNG)")
            else:
                st.info("Colunas 'acuracia' e/ou 'metodologia' não encontradas.")
        
        with classic_subtabs[3]:
            st.subheader('Timeline Geral das Iniciativas')
            from plots import plot_timeline
            if 'metadata' in st.session_state:
                meta = st.session_state['metadata']
                df_original = st.session_state['df_original']
                fig_timeline = plot_timeline(meta, df_original)
                st.plotly_chart(fig_timeline, use_container_width=True)
                safe_download_image(fig_timeline, "exemplo_timeline.png", "⬇️ Baixar Timeline (PNG)")
            else:
                st.info("Metadados não carregados para timeline.")

# ==========================================
# ANÁLISES LULC ESPECÍFICAS
# ==========================================

def run_lulc_performance_metodologica(df_teste, df_original):
    """Análise avançada de performance por metodologia LULC"""
    st.subheader('🔬 Performance Metodológica Avançada')
    
    if 'metodologia' in df_teste.columns and 'acuracia' in df_teste.columns and 'resolucao' in df_teste.columns:
        # Gráfico de violin plot para distribuição de acurácia por metodologia
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
        safe_download_image(fig_violin, "lulc_performance_metodologica.png", "⬇️ Baixar Gráfico (PNG)")
        
        # Scatter com tendências por metodologia
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
        
        # Estatísticas por metodologia
        stats_metod = df_teste.groupby('metodologia').agg({
            'acuracia': ['mean', 'std', 'count'],
            'resolucao': ['mean', 'min', 'max']
        }).round(2)
        
        st.markdown("### 📊 Estatísticas por Metodologia")
        st.dataframe(stats_metod, use_container_width=True)
    else:
        st.info("Dados insuficientes para análise de performance metodológica.")

def run_lulc_densidade_temporal(df_teste, meta_geral, processar_disponibilidade_para_range):
    """Análise de densidade e cobertura temporal das iniciativas LULC"""
    st.subheader('🌍 Densidade de Cobertura Temporal')
    
    if meta_geral and 'disponibilidade' in df_teste.columns:
        # Criar dados de densidade temporal
        all_years = []
        year_counts = {}
        
        for idx, row in df_teste.iterrows():
            if pd.notna(row['disponibilidade']):
                years = processar_disponibilidade_para_range(row['disponibilidade'])
                all_years.extend(years)
                for year in years:
                    year_counts[year] = year_counts.get(year, 0) + 1
        
        if year_counts:
            # Gráfico de densidade por ano
            years_sorted = sorted(year_counts.keys())
            counts = [year_counts[year] for year in years_sorted]
            
            fig_density = go.Figure()
            fig_density.add_trace(go.Scatter(
                x=years_sorted,
                y=counts,
                mode='lines+markers',
                fill='tonexty',
                name='Número de Iniciativas',
                line=dict(color='rgba(0,100,80,0.8)', width=3),
                marker=dict(size=8)
            ))
            
            fig_density.update_layout(
                title='📊 Densidade Temporal: Número de Iniciativas por Ano',
                xaxis_title='Ano',
                yaxis_title='Número de Iniciativas Ativas',
                height=500,
                hovermode='x'
            )
            st.plotly_chart(fig_density, use_container_width=True)
            safe_download_image(fig_density, "lulc_densidade_temporal.png", "⬇️ Baixar Gráfico (PNG)")
            
            # Heatmap de períodos de maior atividade
            periods = {
                '1980-1989': sum(1 for y in years_sorted if 1980 <= y <= 1989),
                '1990-1999': sum(1 for y in years_sorted if 1990 <= y <= 1999),
                '2000-2009': sum(1 for y in years_sorted if 2000 <= y <= 2009),
                '2010-2019': sum(1 for y in years_sorted if 2010 <= y <= 2019),
                '2020-2024': sum(1 for y in years_sorted if 2020 <= y <= 2024)
            }
            
            fig_periods = go.Figure(data=go.Bar(
                x=list(periods.keys()),
                y=list(periods.values()),
                marker_color='lightseagreen'
            ))
            fig_periods.update_layout(
                title='📅 Concentração de Iniciativas por Década',
                xaxis_title='Período',
                yaxis_title='Anos com Dados Disponíveis',
                height=400
            )
            st.plotly_chart(fig_periods, use_container_width=True)
            
            # Métricas de cobertura
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🗓️ Período Total", f"{min(years_sorted)}-{max(years_sorted)}")
            with col2:
                st.metric("📈 Pico de Atividade", f"{max(counts)} iniciativas")
            with col3:
                st.metric("📊 Cobertura Média", f"{np.mean(counts):.1f} iniciativas/ano")
    else:
        st.info("Metadados temporais não disponíveis.")

def run_lulc_escopo_qualidade(df_teste):
    """Análise da relação entre escopo geográfico e qualidade técnica"""
    st.subheader('⚖️ Escopo Geográfico vs Qualidade Técnica')
    
    if all(col in df_teste.columns for col in ['escopo', 'acuracia', 'resolucao']):
        # Gráfico de dispersão com escopo como cor
        fig_scope = px.scatter(
            df_teste,
            x='resolucao',
            y='acuracia',
            color='escopo',
            size=[20] * len(df_teste),
            hover_name='produto',
            title='🌍 Trade-off: Qualidade Técnica vs Escopo Geográfico',
            labels={
                'resolucao': 'Resolução Espacial (m)',
                'acuracia': 'Acurácia (%)',
                'escopo': 'Escopo'
            }
        )
        fig_scope.update_traces(marker=dict(line=dict(width=2, color='white')))
        fig_scope.update_layout(height=500)
        st.plotly_chart(fig_scope, use_container_width=True)
        safe_download_image(fig_scope, "lulc_escopo_qualidade.png", "⬇️ Baixar Gráfico (PNG)")
        
        # Box plot comparativo por escopo
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
            size='resolucao',
            hover_name='produto',
            title='🎯 Número de Classes vs Acurácia',
            labels={
                'num_classes': 'Número de Classes',
                'acuracia': 'Acurácia (%)',
                'resolucao': 'Resolução (m)'
            },
            trendline='ols'
        )
        fig_classes.update_layout(height=500)
        st.plotly_chart(fig_classes, use_container_width=True)
        safe_download_image(fig_classes, "lulc_analise_classes.png", "⬇️ Baixar Gráfico (PNG)")
        
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
            
            # Gráfico temporal de evolução da acurácia
            fig_evo_acc = px.scatter(
                evo_df,
                x='primeiro_ano',
                y='acuracia',
                color='metodologia',
                size='num_classes',
                hover_name='produto',
                title='📈 Evolução da Acurácia ao Longo do Tempo',
                labels={
                    'primeiro_ano': 'Ano de Início',
                    'acuracia': 'Acurácia (%)',
                    'num_classes': 'Nº Classes'
                },
                trendline='ols'
            )
            fig_evo_acc.update_layout(height=500)
            st.plotly_chart(fig_evo_acc, use_container_width=True)
            safe_download_image(fig_evo_acc, "lulc_evolucao_acuracia.png", "⬇️ Baixar Gráfico (PNG)")
            
            # Evolução da resolução espacial
            fig_evo_res = px.scatter(
                evo_df,
                x='primeiro_ano',
                y='resolucao',
                color='metodologia',
                hover_name='produto',
                title='🔍 Evolução da Resolução Espacial',
                labels={
                    'primeiro_ano': 'Ano de Início',
                    'resolucao': 'Resolução Espacial (m)'
                },
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
            safe_download_image(fig_comparison, "lulc_brasil_vs_global.png", "⬇️ Baixar Gráfico (PNG)")
            
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
            safe_download_image(fig_providers, "lulc_ecossistema_provedores.png", "⬇️ Baixar Gráfico (PNG)")
            
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
                    'resolucao': ['mean', 'min', 'max'],
                    'num_classes': 'mean'
                }).round(2)
                
                st.markdown("### 🎯 Performance por Provedor")
                st.dataframe(provider_performance, use_container_width=True)
    else:
        st.info("Dados de provedor não disponíveis no dataset original.")

if __name__ == "__main__":
    main()
