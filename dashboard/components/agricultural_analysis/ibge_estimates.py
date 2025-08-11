"""
Componente de Dashboard para Dados Agrícolas do IBGE
Integrado com o sistema de orchestração do agricultural_analysis.py
Version: 1.0 - Updated
"""

import streamlit as st

def render():
    """Renderiza dados específicos do IBGE"""
    
    st.markdown("### 📈 Dados Estimados IBGE")
    st.markdown("*Estatísticas oficiais da Produção Agrícola Municipal (PAM)*")
    
    # Tentar carregar dados do IBGE
    data = load_ibge_data()
    
    if not data:
        st.warning("⚠️ Dados do IBGE não disponíveis no momento")
        
        # Informações sobre o IBGE
        st.markdown("""
        ### 📊 Sobre o IBGE - PAM
        
        A **Produção Agrícola Municipal (PAM)** é uma pesquisa do IBGE que investiga 
        informações sobre área plantada, área colhida, quantidade produzida, rendimento 
        médio e valor da produção agrícola municipal.
        
        - 📋 **Abrangência**: Todos os municípios brasileiros
        - 🌾 **Culturas**: Mais de 60 produtos agrícolas
        - 📅 **Periodicidade**: Anual (dados desde 1974)
        - 📍 **Detalhamento**: Municipal, Estadual e Nacional
        
        ### 🎯 Principais Culturas Pesquisadas
        
        #### Cereais, Leguminosas e Oleaginosas
        - Soja, Milho, Arroz, Feijão
        - Trigo, Sorgo, Aveia, Centeio
        - Algodão herbáceo, Girassol, Amendoim
        - Mamona, Gergelim, Canola
        
        #### Frutas
        - Laranja, Banana, Uva, Maçã
        - Manga, Mamão, Abacaxi, Coco
        - Melancia, Melão, Goiaba
        
        #### Outras Culturas
        - Cana-de-açúcar, Café, Cacau
        - Fumo, Mandioca, Batata
        - Tomate, Cebola, Alho
        
        ### 📊 Variáveis Investigadas
        
        - **Área Plantada** (hectares)
        - **Área Colhida** (hectares)  
        - **Quantidade Produzida** (toneladas)
        - **Rendimento Médio** (kg/ha)
        - **Valor da Produção** (mil reais)
        
        ### 📈 Séries Históricas Disponíveis
        
        - **Dados Históricos**: 1974 até presente
        - **Última Atualização**: Dados de 2023
        - **Frequência**: Divulgação anual (setembro/outubro)
        
        **Fonte:** [IBGE - PAM - Produção Agrícola Municipal](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html)
        """)
        
        return
    
    # Se tiver dados, renderizar visualizações
    render_ibge_visualizations(data)


def load_ibge_data():
    """Carrega dados agrícolas do IBGE"""
    try:
        import json
        import os
        
        # Primeiro tenta carregar o arquivo de dados IBGE específico
        data_path = os.path.join('data', 'brazilian_ibge_agricultural_data.json')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Fallback para arquivo alternativo
        alt_data_path = os.path.join('data', 'ibge_agricultural_data.json')
        if os.path.exists(alt_data_path):
            with open(alt_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados IBGE: {e}")
        return None


def render_ibge_visualizations(data):
    """Renderiza visualizações dos dados IBGE"""
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Extrair dados do JSON real
        producao_data = data.get('data', {}).get('producao_agricola', {})
        latest_year = "2023"  # Ano mais recente nos dados
        
        with col1:
            total_crops = len(producao_data)
            st.metric("🌾 Culturas", total_crops)
        
        with col2:
            st.metric("📅 Ano Referência", latest_year)
        
        with col3:
            # Calcular produção total do ano mais recente
            total_production = 0
            for crop_name, crop_data in producao_data.items():
                producao_toneladas = crop_data.get('quantidade_produzida_toneladas', {})
                if latest_year in producao_toneladas:
                    total_production += producao_toneladas[latest_year]
            
            st.metric("📈 Produção Total", f"{total_production/1000000:.1f}M ton")
        
        with col4:
            # Calcular área total colhida do ano mais recente
            total_area = 0
            for crop_name, crop_data in producao_data.items():
                area_colhida = crop_data.get('area_colhida_hectares', {})
                if latest_year in area_colhida:
                    total_area += area_colhida[latest_year]
            
            st.metric("🌍 Área Total", f"{total_area/1000000:.1f}M ha")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar métricas IBGE: {e}")
    
    st.divider()
    
    # Abas de análise
    tab1, tab2, tab3 = st.tabs([
        "📊 Produção por Cultura",
        "🗺️ Distribuição Regional", 
        "📈 Série Histórica"
    ])
    
    with tab1:
        render_ibge_production_tab(data)
    
    with tab2:
        render_ibge_regional_tab(data)
        
    with tab3:
        render_ibge_historical_tab(data)


def render_ibge_production_tab(data):
    """Renderiza aba de produção por cultura"""
    st.markdown("#### 🌾 Produção por Cultura - IBGE PAM 2023")
    
    # Gráfico de barras das principais culturas
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extrair dados reais do JSON
        producao_data = data.get('data', {}).get('producao_agricola', {})
        latest_year = "2023"
        
        crops_data = []
        for crop_key, crop_info in producao_data.items():
            nome = crop_info.get('nome', crop_key.title())
            producao = crop_info.get('quantidade_produzida_toneladas', {}).get(latest_year, 0)
            area = crop_info.get('area_colhida_hectares', {}).get(latest_year, 0)
            
            # Calcular produtividade
            produtividade = (producao * 1000 / area) if area > 0 else 0  # kg/ha
            
            crops_data.append({
                'Cultura': nome,
                'Produção (mil t)': producao / 1000,
                'Área (mil ha)': area / 1000,
                'Produtividade (t/ha)': produtividade / 1000
            })
        
        # Criar DataFrame e ordenar por produção
        df = pd.DataFrame(crops_data)
        df = df.sort_values('Produção (mil t)', ascending=False)
        
        # Gráfico de produção
        fig1 = px.bar(
            df.head(10), 
            x='Cultura', 
            y='Produção (mil t)',
            title="📊 Produção por Cultura - Dados IBGE PAM 2023",
            color='Produção (mil t)',
            color_continuous_scale='Greens'
        )
        fig1.update_layout(height=400)
        fig1.update_xaxes(tickangle=45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de área colhida
        fig2 = px.bar(
            df.head(10), 
            x='Cultura', 
            y='Área (mil ha)',
            title="🌍 Área Colhida por Cultura - IBGE PAM 2023",
            color='Área (mil ha)',
            color_continuous_scale='Blues'
        )
        fig2.update_layout(height=400)
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("##### 📋 Dados Detalhados IBGE PAM 2023")
        st.dataframe(df.round(2), use_container_width=True)
        
        # Fonte dos dados
        st.markdown("**Fonte:** IBGE - Produção Agrícola Municipal (PAM)")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar gráficos de produção: {e}")


def render_ibge_regional_tab(data):
    """Renderiza aba de análise regional"""
    st.markdown("#### 🗺️ Análise Regional - IBGE PAM")
    
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extrair dados regionais reais
        producao_data = data.get('data', {}).get('producao_agricola', {})
        resumo_regional = data.get('data', {}).get('resumo_regional', {})
        
        # Mapeamento de regiões para cálculo consolidado
        regional_data = {}
        
        # Processar dados por cultura para extrair informações regionais
        for crop_key, crop_info in producao_data.items():
            crop_name = crop_info.get('nome', crop_key.title())
            
            # Pegar dados mais recentes (2023)
            producao_2023 = crop_info.get('quantidade_produzida_toneladas', {}).get('2023', 0)
            area_2023 = crop_info.get('area_colhida_hectares', {}).get('2023', 0)
            
            # Calcular produtividade
            produtividade = (producao_2023 / area_2023) if area_2023 > 0 else 0
            
            regional_data[crop_name] = {
                'Produção (t)': producao_2023,
                'Área (ha)': area_2023,
                'Produtividade (t/ha)': produtividade
            }
        
        # Se temos dados regionais específicos, usá-los
        if resumo_regional:
            region_summary = {}
            for region, region_data in resumo_regional.items():
                total_prod = sum(region_data.get('culturas', {}).values())
                region_summary[region] = total_prod
            
            # Criar gráfico de barras por região
            regions = list(region_summary.keys())
            productions = [region_summary[r] / 1000000 for r in regions]  # Milhões de toneladas
            
            df_regions = pd.DataFrame({
                'Região': regions,
                'Produção (M ton)': productions
            })
            
            fig_regions = px.bar(
                df_regions,
                x='Região',
                y='Produção (M ton)',
                title="🗺️ Produção Agrícola por Região (2023)",
                color='Produção (M ton)',
                color_continuous_scale='Greens'
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        
        else:
            # Simulação de distribuição regional baseada nos dados reais
            crops_by_region = {
                'Sudeste': ['soja', 'milho', 'cana_de_acucar', 'cafe', 'laranja'],
                'Sul': ['soja', 'milho', 'arroz', 'fumo'],
                'Centro-Oeste': ['soja', 'milho', 'algodao'],
                'Nordeste': ['cana_de_acucar', 'mandioca', 'feijao'],
                'Norte': ['mandioca', 'cacau', 'acai']
            }
            
            region_totals = {}
            for region, main_crops in crops_by_region.items():
                total_production = 0
                for crop in main_crops:
                    for crop_key, crop_data in regional_data.items():
                        if any(crop_word in crop_key.lower() for crop_word in crop.split('_')):
                            # Distribuição estimada por região
                            region_factor = {
                                'Sudeste': 0.3, 'Sul': 0.25, 'Centro-Oeste': 0.25,
                                'Nordeste': 0.15, 'Norte': 0.05
                            }
                            total_production += crop_data['Produção (t)'] * region_factor.get(region, 0.2)
                
                region_totals[region] = total_production / 1000000  # Milhões de toneladas
            
            # Gráfico de barras por região
            df_regions = pd.DataFrame([
                {'Região': region, 'Produção (M ton)': production}
                for region, production in region_totals.items()
            ])
            
            fig_regions = px.bar(
                df_regions,
                x='Região',
                y='Produção (M ton)',
                title="🗺️ Distribuição da Produção Agrícola por Região (2023)",
                color='Produção (M ton)',
                color_continuous_scale='Greens'
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        
        # Análise de concentração por cultura
        st.markdown("##### 🌾 Principais Culturas por Região")
        
        # Preparar dados das principais culturas
        top_crops = sorted(regional_data.items(), key=lambda x: x[1]['Produção (t)'], reverse=True)[:8]
        
        crops_data = []
        for crop_name, crop_data in top_crops:
            crops_data.append({
                'Cultura': crop_name,
                'Produção (M ton)': crop_data['Produção (t)'] / 1000000,
                'Área (M ha)': crop_data['Área (ha)'] / 1000000,
                'Produtividade (t/ha)': crop_data['Produtividade (t/ha)']
            })
        
        df_crops = pd.DataFrame(crops_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras - Produção por cultura
            fig_crops = px.bar(
                df_crops.head(6),
                x='Cultura',
                y='Produção (M ton)',
                title="📊 Principais Culturas - Produção",
                color='Produção (M ton)',
                color_continuous_scale='Blues'
            )
            fig_crops.update_xaxes(tickangle=45)
            st.plotly_chart(fig_crops, use_container_width=True)
        
        with col2:
            # Gráfico de barras - Área por cultura
            fig_area = px.bar(
                df_crops.head(6),
                x='Cultura',
                y='Área (M ha)',
                title="🌍 Principais Culturas - Área",
                color='Área (M ha)',
                color_continuous_scale='Oranges'
            )
            fig_area.update_xaxes(tickangle=45)
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Métricas regionais
        st.markdown("##### � Indicadores Regionais")
        
        total_production = sum(crop_data['Produção (t)'] for crop_data in regional_data.values()) / 1000000
        total_area = sum(crop_data['Área (ha)'] for crop_data in regional_data.values()) / 1000000
        avg_productivity = total_production * 1000 / total_area if total_area > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌾 Produção Total", f"{total_production:.1f} M ton")
        
        with col2:
            st.metric("🌍 Área Total", f"{total_area:.1f} M ha")
        
        with col3:
            st.metric("📊 Produtividade Média", f"{avg_productivity:.2f} t/ha")
        
        with col4:
            st.metric("🔢 Número de Culturas", len(regional_data))
        
        # Tabela detalhada por cultura
        st.markdown("##### 📋 Dados Detalhados por Cultura")
        st.dataframe(df_crops.round(2), use_container_width=True)
        
        # Fonte dos dados
        st.markdown("**Fonte:** IBGE - Produção Agrícola Municipal (PAM)")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar análise regional: {e}")


def render_ibge_historical_tab(data):
    """Renderiza aba de série histórica"""
    st.markdown("#### 📈 Série Histórica - IBGE PAM (2018-2023)")
    
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extrair dados históricos reais
        producao_data = data.get('data', {}).get('producao_agricola', {})
        resumo_anual = data.get('data', {}).get('resumo_anual', {})
        
        # Preparar dados históricos de produção total
        years = ['2018', '2019', '2020', '2021', '2022', '2023']
        total_production_by_year = []
        total_area_by_year = []
        
        for year in years:
            year_production = 0
            year_area = 0
            
            for crop_key, crop_info in producao_data.items():
                producao = crop_info.get('quantidade_produzida_toneladas', {}).get(year, 0)
                area = crop_info.get('area_colhida_hectares', {}).get(year, 0)
                
                year_production += producao
                year_area += area
            
            total_production_by_year.append(year_production / 1000000)  # Milhões de toneladas
            total_area_by_year.append(year_area / 1000000)  # Milhões de hectares
        
        # Calcular produtividade média
        productivity_by_year = [
            (prod * 1000 / area) if area > 0 else 0 
            for prod, area in zip(total_production_by_year, total_area_by_year)
        ]
        
        # Criar DataFrame histórico
        df_hist = pd.DataFrame({
            'Ano': [int(y) for y in years],
            'Produção Total (M ton)': total_production_by_year,
            'Área Total (M ha)': total_area_by_year,
            'Produtividade (t/ha)': productivity_by_year
        })
        
        # Gráfico de linha para produção total
        fig_line = px.line(
            df_hist, 
            x='Ano', 
            y='Produção Total (M ton)',
            title="📈 Evolução da Produção Agrícola Total IBGE (2018-2023)",
            markers=True
        )
        fig_line.update_traces(line_color='green', line_width=3)
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de área
            fig_area = px.line(
                df_hist, 
                x='Ano', 
                y='Área Total (M ha)',
                title="🌍 Evolução da Área Colhida Total",
                markers=True
            )
            fig_area.update_traces(line_color='blue')
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            # Gráfico de produtividade
            fig_prod = px.line(
                df_hist, 
                x='Ano', 
                y='Produtividade (t/ha)',
                title="📊 Evolução da Produtividade Média",
                markers=True
            )
            fig_prod.update_traces(line_color='orange')
            st.plotly_chart(fig_prod, use_container_width=True)
        
        # Análise de tendências
        st.markdown("##### 📊 Análise de Tendências (2018-2023)")
        
        growth_production = ((df_hist['Produção Total (M ton)'].iloc[-1] / df_hist['Produção Total (M ton)'].iloc[0]) - 1) * 100
        growth_area = ((df_hist['Área Total (M ha)'].iloc[-1] / df_hist['Área Total (M ha)'].iloc[0]) - 1) * 100
        growth_productivity = ((df_hist['Produtividade (t/ha)'].iloc[-1] / df_hist['Produtividade (t/ha)'].iloc[0]) - 1) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📈 Crescimento Produção", 
                f"{growth_production:.1f}%",
                delta=f"{growth_production:.1f}%"
            )
        
        with col2:
            st.metric(
                "🌍 Crescimento Área", 
                f"{growth_area:.1f}%",
                delta=f"{growth_area:.1f}%"
            )
        
        with col3:
            st.metric(
                "📊 Crescimento Produtividade", 
                f"{growth_productivity:.1f}%",
                delta=f"{growth_productivity:.1f}%"
            )
        
        # Gráfico de evolução das principais culturas
        st.markdown("##### 🌾 Evolução das Principais Culturas")
        
        # Selecionar as 5 principais culturas por produção em 2023
        main_crops = {}
        for crop_key, crop_info in producao_data.items():
            producao_2023 = crop_info.get('quantidade_produzida_toneladas', {}).get('2023', 0)
            main_crops[crop_key] = {
                'nome': crop_info.get('nome', crop_key.title()),
                'producao_2023': producao_2023
            }
        
        # Ordenar e pegar top 5
        top_crops = sorted(main_crops.items(), key=lambda x: x[1]['producao_2023'], reverse=True)[:5]
        
        # Preparar dados para gráfico de linhas múltiplas
        evolution_data = []
        for year in years:
            for crop_key, crop_data in top_crops:
                crop_info = producao_data[crop_key]
                producao = crop_info.get('quantidade_produzida_toneladas', {}).get(year, 0) / 1000000
                evolution_data.append({
                    'Ano': int(year),
                    'Cultura': crop_data['nome'],
                    'Produção (M ton)': producao
                })
        
        df_evolution = pd.DataFrame(evolution_data)
        
        fig_evolution = px.line(
            df_evolution,
            x='Ano',
            y='Produção (M ton)',
            color='Cultura',
            title="📈 Evolução das 5 Principais Culturas (2018-2023)",
            markers=True
        )
        fig_evolution.update_layout(height=400)
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Tabela histórica completa
        st.markdown("##### 📋 Dados Históricos Completos")
        st.dataframe(df_hist.round(2), use_container_width=True)
        
        # Fonte dos dados
        st.markdown("**Fonte:** IBGE - Produção Agrícola Municipal (PAM)")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar série histórica: {e}")
