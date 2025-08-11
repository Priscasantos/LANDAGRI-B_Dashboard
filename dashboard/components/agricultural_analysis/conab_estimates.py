"""
Componente de Dashboard para Dados Agrícolas da CONAB
Exibe dados de produção agrícola brasileira da Companhia Nacional de Abastecimento (CONAB)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

def load_conab_data():
    """Carrega dados agrícolas da CONAB do arquivo JSON"""
    try:
        data_path = os.path.join('data', 'conab_agricultural_data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Arquivo de dados da CONAB não encontrado!")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados da CONAB: {e}")
        return None

def create_conab_production_chart(data):
    """Cria gráfico de produção total por safra"""
    # Preparar dados para o gráfico
    years = []
    productions = []
    
    for crop_key, crop_data in data['crops'].items():
        for year, values in crop_data['production_data'].items():
            years.append(year)
            productions.append(values['production'])
    
    # Criar DataFrame agregado por ano
    df = pd.DataFrame({'Safra': years, 'Producao': productions})
    df_grouped = df.groupby('Safra')['Producao'].sum().reset_index()
    df_grouped['Producao_MT'] = df_grouped['Producao'] / 1000  # Converter para milhões de toneladas
    
    # Criar gráfico
    fig = px.line(df_grouped, x='Safra', y='Producao_MT',
                  title='Evolução da Produção Total de Grãos - CONAB',
                  labels={'Producao_MT': 'Produção (Milhões de Toneladas)', 'Safra': 'Safra'},
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Safra",
        yaxis_title="Produção (Milhões de Toneladas)",
        hovermode='x unified'
    )
    
    return fig

def create_conab_crop_comparison_chart(data):
    """Cria gráfico de comparação entre culturas"""
    # Preparar dados da safra mais recente
    crop_names = []
    productions = []
    areas = []
    
    for crop_key, crop_data in data['crops'].items():
        # Pegar dados da safra 2023/24 (mais recente)
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            productions.append(latest_data['production'] / 1000)  # Converter para milhões
            areas.append(latest_data['area'] / 1000)  # Converter para milhões
    
    # Criar gráfico de barras
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Produção (Milhões de t)',
        x=crop_names,
        y=productions,
        yaxis='y',
        offsetgroup=1,
        marker_color='#2E8B57'
    ))
    
    fig.add_trace(go.Bar(
        name='Área (Milhões de ha)',
        x=crop_names,
        y=areas,
        yaxis='y2',
        offsetgroup=2,
        marker_color='#FF6B35'
    ))
    
    fig.update_layout(
        title='Produção e Área por Cultura - Safra 2023/24 (CONAB)',
        xaxis_title="Culturas",
        yaxis=dict(
            title="Produção (Milhões de toneladas)",
            side="left"
        ),
        yaxis2=dict(
            title="Área (Milhões de hectares)",
            side="right",
            overlaying="y"
        ),
        barmode='group'
    )
    
    return fig

def create_conab_productivity_chart(data):
    """Cria gráfico de evolução da produtividade"""
    productivity_data = []
    
    # Focar em soja e milho (principais culturas)
    main_crops = ['soja', 'milho_total']
    crop_names = {'soja': 'Soja', 'milho_total': 'Milho'}
    
    for crop_key in main_crops:
        if crop_key in data['crops']:
            crop_data = data['crops'][crop_key]
            for year, values in crop_data['production_data'].items():
                productivity_data.append({
                    'Safra': year,
                    'Cultura': crop_names[crop_key],
                    'Produtividade': values['productivity']
                })
    
    df = pd.DataFrame(productivity_data)
    
    fig = px.line(df, x='Safra', y='Produtividade', color='Cultura',
                  title='Evolução da Produtividade - CONAB',
                  labels={'Produtividade': 'Produtividade (kg/ha)', 'Safra': 'Safra'},
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Safra",
        yaxis_title="Produtividade (kg/ha)",
        hovermode='x unified'
    )
    
    return fig

def create_conab_area_chart(data):
    """Cria gráfico de pizza da distribuição de área"""
    # Dados da safra 2023/24
    crop_names = []
    areas = []
    
    for crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            areas.append(latest_data['area'])
    
    fig = px.pie(
        values=areas,
        names=crop_names,
        title='Distribuição de Área Plantada por Cultura - Safra 2023/24 (CONAB)'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_conab_all_crops_chart(data):
    """Cria gráfico de barras com todas as culturas CONAB"""
    # Dados da safra 2023/24
    crop_names = []
    productions = []
    
    for crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            productions.append(latest_data['production'])
    
    # Criar DataFrame e ordenar por produção
    df = pd.DataFrame({'Cultura': crop_names, 'Produção': productions})
    df = df.sort_values('Produção', ascending=True)
    
    fig = px.bar(
        df,
        x='Produção',
        y='Cultura',
        orientation='h',
        title='Produção por Cultura - Safra 2023/24 (CONAB)',
        labels={'Produção': 'Produção (mil toneladas)', 'Cultura': 'Cultura'},
        color='Produção',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=600)
    
    return fig

def create_conab_regional_chart(data):
    """Cria gráfico de produção regional CONAB"""
    if 'regional_production' not in data:
        return None
    
    regional_data = data['regional_production']
    chart_data = []
    
    for region_key, region_info in regional_data.items():
        region_name = region_info['name']
        production_data = region_info.get('production_2023_24', {})
        
        for crop, production in production_data.items():
            # Converter nomes das culturas
            crop_display = crop.replace('_', ' ').replace('total', '').title()
            chart_data.append({
                'Região': region_name,
                'Cultura': crop_display,
                'Produção': production
            })
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    
    fig = px.bar(
        df,
        x='Região',
        y='Produção',
        color='Cultura',
        title='Produção Regional por Cultura - Safra 2023/24 (CONAB)',
        labels={'Produção': 'Produção (mil toneladas)', 'Região': 'Região'},
        barmode='group'
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_conab_crops_evolution_chart(data):
    """Cria gráfico de evolução de todas as culturas CONAB"""
    crops_data = []
    
    # Incluir todas as culturas
    for crop_key, crop_data in data['crops'].items():
        crop_name = crop_data['name']
        
        for year, values in crop_data['production_data'].items():
            crops_data.append({
                'Safra': year,
                'Cultura': crop_name,
                'Produção': values['production']
            })
    
    df = pd.DataFrame(crops_data)
    
    fig = px.line(
        df,
        x='Safra',
        y='Produção',
        color='Cultura',
        title='Evolução da Produção por Cultura - CONAB (2018/19 - 2023/24)',
        labels={'Produção': 'Produção (mil toneladas)', 'Safra': 'Safra'},
        markers=True
    )
    
    fig.update_layout(
        height=600,
        hovermode='x unified'
    )
    
    return fig

def render_conab_production_overview(data):
    """Renderiza visão geral da produção CONAB"""
    st.subheader("📊 Visão Geral da Produção - CONAB")
    
    # Métricas principais da safra 2023/24
    latest_year = '2023/24'
    total_production = 0
    total_area = 0
    main_crops_count = len(data['crops'])
    
    for crop_data in data['crops'].values():
        if latest_year in crop_data['production_data']:
            production_data = crop_data['production_data'][latest_year]
            total_production += production_data['production']
            total_area += production_data['area']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Produção Total 2023/24",
            f"{total_production/1000:.1f} milhões t",
            delta=f"{main_crops_count} culturas principais"
        )
    
    with col2:
        st.metric(
            "Área Total Plantada",
            f"{total_area/1000:.1f} milhões ha",
            delta="Safra 2023/24"
        )
    
    with col3:
        avg_productivity = (total_production / total_area) if total_area > 0 else 0
        st.metric(
            "Produtividade Média",
            f"{avg_productivity:.0f} kg/ha",
            delta="Média ponderada"
        )

def render_conab_charts(data):
    """Renderiza gráficos dos dados CONAB"""
    st.subheader("📈 Análises Detalhadas - CONAB")
    
    # Primeira linha: Produção total e distribuição de área
    col1, col2 = st.columns(2)
    
    with col1:
        fig_production = create_conab_production_chart(data)
        st.plotly_chart(fig_production, use_container_width=True)
    
    with col2:
        fig_area = create_conab_area_chart(data)
        st.plotly_chart(fig_area, use_container_width=True)
    
    # Segunda linha: Comparação entre culturas
    fig_comparison = create_conab_crop_comparison_chart(data)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Terceira linha: Todas as culturas (barras horizontais)
    fig_all_crops = create_conab_all_crops_chart(data)
    st.plotly_chart(fig_all_crops, use_container_width=True)
    
    # Quarta linha: Evolução temporal de todas as culturas
    fig_evolution = create_conab_crops_evolution_chart(data)
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Quinta linha: Dados regionais (se disponível)
    fig_regional = create_conab_regional_chart(data)
    if fig_regional:
        st.plotly_chart(fig_regional, use_container_width=True)
    
    # Sexta linha: Produtividade
    fig_productivity = create_conab_productivity_chart(data)
    st.plotly_chart(fig_productivity, use_container_width=True)

def render_conab_data_table(data):
    """Renderiza tabela com dados detalhados da CONAB"""
    st.subheader("📋 Dados Detalhados por Cultura - CONAB")
    
    # Informações sobre Portal 360° (se disponível)
    if 'portal_360_info' in data:
        portal_info = data['portal_360_info']
        st.info(f"ℹ️ **{portal_info['description']}**")
        
        # Exibir características do portal em colunas
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Funcionalidades disponíveis:**")
            for feature in portal_info.get('features', []):
                st.markdown(f"• {feature}")
        
        with col2:
            if 'products_covered' in portal_info:
                st.markdown("**Produtos cobertos:**")
                products_text = ", ".join(portal_info['products_covered'])
                st.markdown(products_text)
    
    # Preparar dados para a tabela
    table_data = []
    
    for crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            table_data.append({
                'Cultura': crop_data['name'],
                'Nome Científico': crop_data.get('scientific_name', 'N/A'),
                'Produção (mil t)': f"{latest_data['production']:,}",
                'Área (mil ha)': f"{latest_data['area']:,}",
                'Produtividade (kg/ha)': f"{latest_data['productivity']:,}"
            })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    # Adicionar informações regionais se disponível
    if 'regional_production' in data:
        st.subheader("🗺️ Informações Regionais - CONAB")
        regional_data = data['regional_production']
        
        for region_key, region_info in regional_data.items():
            with st.expander(f"📍 {region_info['name']}"):
                st.markdown(f"**Estados:** {', '.join(region_info['states'])}")
                st.markdown(f"**Características:** {region_info['characteristics']}")
                
                if 'production_2023_24' in region_info:
                    st.markdown("**Principais produções (safra 2023/24):**")
                    prod_data = region_info['production_2023_24']
                    for crop, production in prod_data.items():
                        crop_name = crop.replace('_', ' ').title()
                        st.markdown(f"• {crop_name}: {production:,} mil toneladas")

def render():
    """Função principal para renderizar o componente CONAB"""
    # Carregar dados
    data = load_conab_data()
    
    if data is None:
        return
    
    # Renderizar componentes
    render_conab_production_overview(data)
    st.divider()
    
    render_conab_charts(data)
    st.divider()
    
    render_conab_data_table(data)
    
    # Rodapé com fonte dos dados
    st.markdown("---")
    st.markdown("### 📋 Sobre os Dados CONAB")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            "**🏢 CONAB - Companhia Nacional de Abastecimento**  \n"
            "Empresa pública vinculada ao Ministério da Agricultura,  \n"
            "responsável pela gestão das políticas agrícolas brasileiras.  \n\n"
            "**🌐 Website Oficial:** https://www.gov.br/conab/pt-br  \n"
            "**📊 Portal de Informações:** [Produtos 360°](https://portaldeinformacoes.conab.gov.br/produtos-360.html)  \n"
            "**📈 Boletins da Safra:** Levantamentos mensais de grãos"
        )
    
    with col2:
        st.markdown(
            f"**📅 Período dos Dados:** Safras 2018/19 a 2023/24  \n"
            f"**🌾 Total de Culturas:** {len(data['crops'])} culturas principais  \n"
            f"**🗺️ Cobertura:** Todo território nacional brasileiro  \n"
            f"**📊 Dados Regionais:** {len(data.get('regional_production', {}))} regiões  \n\n"
            "**🔗 Portal 360°:** Informações detalhadas por produto,  \n"
            "séries históricas, custos de produção e análises regionais."
        )

# Função para testes
if __name__ == "__main__":
    st.set_page_config(page_title="Dados CONAB", layout="wide")
    st.title("🌾 Dados Agrícolas CONAB")
    render()
