#!/usr/bin/env python3
"""
Implementação Prática - Fase 1: Melhorias Imediatas
===================================================

Script para implementar as melhorias de alta prioridade:
1. Streamlit Extras - Metric cards
2. AgGrid - Tabelas interativas
3. Otimizar Folium existente

Author: GitHub Copilot
Date: 2025-07-22
"""

import subprocess
import sys
from pathlib import Path

def install_packages():
    """Instala os pacotes necessários para a Fase 1"""
    packages = [
        "streamlit-extras",
        "streamlit-aggrid",
        "folium-plugins"  # Para funcionalidades avançadas do Folium
    ]
    
    print("📦 INSTALANDO PACOTES DA FASE 1:")
    print("=" * 50)
    
    for package in packages:
        print(f"🔄 Instalando {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} instalado com sucesso!")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {package}")
    print()

def update_requirements():
    """Atualiza o arquivo requirements.txt"""
    requirements_file = Path("requirements.txt")
    
    new_packages = [
        "streamlit-extras",
        "streamlit-aggrid", 
        "folium-plugins"
    ]
    
    print("📝 ATUALIZANDO REQUIREMENTS.TXT:")
    print("=" * 50)
    
    # Ler requirements existentes
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            existing = f.read().strip().split('\\n')
    else:
        existing = []
    
    # Adicionar novos pacotes se não existirem
    for package in new_packages:
        if package not in existing:
            existing.append(package)
            print(f"➕ Adicionado: {package}")
    
    # Escrever arquivo atualizado
    with open(requirements_file, 'w') as f:
        f.write('\\n'.join(existing) + '\\n')
    
    print("✅ Requirements.txt atualizado!")
    print()

def create_enhanced_overview_module():
    """Cria uma versão melhorada do módulo overview com novos componentes"""
    
    enhanced_code = '''#!/usr/bin/env python3
"""
Enhanced Overview Module - com Streamlit Extras e AgGrid
========================================================

Versão melhorada do módulo overview com:
- Metric cards modernas
- Tabelas interativas AgGrid
- Interface aprimorada

Author: GitHub Copilot
Date: 2025-07-22
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Novos imports para componentes melhorados
try:
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.add_vertical_space import add_vertical_space
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    ENHANCED_COMPONENTS = True
except ImportError:
    ENHANCED_COMPONENTS = False
    st.warning("⚠️ Componentes aprimorados não instalados. Execute: pip install streamlit-extras streamlit-aggrid")

def create_enhanced_metrics(df):
    """Cria cards de métricas modernas"""
    if not ENHANCED_COMPONENTS:
        return create_basic_metrics(df)
    
    colored_header(
        label="📊 Estatísticas Principais",
        description="Visão geral dos dados LULC",
        color_name="blue-70"
    )
    
    # Calcular métricas
    total_initiatives = len(df)
    avg_resolution = df['resolucao_espacial'].mean() if 'resolucao_espacial' in df.columns else 0
    avg_accuracy = df['acuracia'].mean() if 'acuracia' in df.columns else 0
    temporal_coverage = df['ano_final'].max() - df['ano_inicial'].min() if 'ano_inicial' in df.columns else 0
    
    # Criar colunas para métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌍 Total de Iniciativas",
            value=total_initiatives,
            delta="↗️ Ativo"
        )
    
    with col2:
        st.metric(
            label="📏 Resolução Média",
            value=f"{avg_resolution:.1f}m" if avg_resolution > 0 else "N/A",
            delta="🎯 Espacial"
        )
    
    with col3:
        st.metric(
            label="🎯 Acurácia Média", 
            value=f"{avg_accuracy:.1f}%" if avg_accuracy > 0 else "N/A",
            delta="📈 Performance"
        )
    
    with col4:
        st.metric(
            label="📅 Cobertura Temporal",
            value=f"{temporal_coverage} anos" if temporal_coverage > 0 else "N/A",
            delta="⏱️ Histórico"
        )
    
    # Aplicar estilo dos cards
    style_metric_cards(
        background_color="#FFFFFF",
        border_left_color="#686664",
        border_color="#000000",
        box_shadow="#F71938"
    )
    
    add_vertical_space(2)

def create_basic_metrics(df):
    """Versão básica das métricas (fallback)"""
    st.subheader("📊 Estatísticas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Iniciativas", len(df))
    with col2:
        avg_res = df['resolucao_espacial'].mean() if 'resolucao_espacial' in df.columns else 0
        st.metric("Resolução Média", f"{avg_res:.1f}m" if avg_res > 0 else "N/A")
    with col3:
        avg_acc = df['acuracia'].mean() if 'acuracia' in df.columns else 0
        st.metric("Acurácia Média", f"{avg_acc:.1f}%" if avg_acc > 0 else "N/A")
    with col4:
        temp_cov = df['ano_final'].max() - df['ano_inicial'].min() if 'ano_inicial' in df.columns else 0
        st.metric("Cobertura Temporal", f"{temp_cov} anos" if temp_cov > 0 else "N/A")

def create_enhanced_dataframe(df):
    """Cria tabela interativa com AgGrid"""
    if not ENHANCED_COMPONENTS:
        return create_basic_dataframe(df)
    
    colored_header(
        label="📋 Dados das Iniciativas LULC",
        description="Tabela interativa com filtros e ordenação",
        color_name="green-70"
    )
    
    # Configurar AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Configurações básicas
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()  # Adiciona sidebar com filtros
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    
    # Configurar colunas específicas
    if 'nome_iniciativa' in df.columns:
        gb.configure_column("nome_iniciativa", pinned="left", width=200)
    
    if 'acuracia' in df.columns:
        gb.configure_column("acuracia", type=["numericColumn", "numberColumnFilter"], precision=1)
    
    if 'resolucao_espacial' in df.columns:
        gb.configure_column("resolucao_espacial", type=["numericColumn", "numberColumnFilter"], precision=1)
    
    # Configurações avançadas
    gb.configure_grid_options(
        domLayout='normal',
        suppressRowClickSelection=False,
        rowSelection='multiple',
        enableRangeSelection=True,
        enableColResize=True,
        enableSorting=True,
        enableFilter=True
    )
    
    gridOptions = gb.build()
    
    # Exibir tabela
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
        theme='streamlit',  # Tema Streamlit
        enable_enterprise_modules=True,
        height=400,
        width='100%',
        reload_data=False
    )
    
    # Mostrar seleção
    if grid_response['selected_rows']:
        st.info(f"📌 {len(grid_response['selected_rows'])} linha(s) selecionada(s)")
        
        if st.button("📊 Analisar Selecionados"):
            selected_df = pd.DataFrame(grid_response['selected_rows'])
            st.subheader("🔍 Análise dos Itens Selecionados")
            
            # Métricas da seleção
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Itens Selecionados", len(selected_df))
            with col2:
                if 'acuracia' in selected_df.columns:
                    avg_acc_selected = selected_df['acuracia'].mean()
                    st.metric("Acurácia Média Seleção", f"{avg_acc_selected:.1f}%")
    
    add_vertical_space(2)
    return grid_response

def create_basic_dataframe(df):
    """Versão básica da tabela (fallback)"""
    st.subheader("📋 Dados das Iniciativas")
    st.dataframe(df, use_container_width=True, height=400)
    return None

def run_enhanced_overview():
    """Função principal do overview melhorado"""
    
    # Tentar carregar dados do cache
    try:
        from utilities.cache_system import load_optimized_data
        metadata, df, cache_info = load_optimized_data()
        
        if df is not None and not df.empty:
            st.success(f"✅ Dados carregados: {len(df)} iniciativas")
        else:
            st.error("❌ Erro ao carregar dados")
            return
            
    except Exception as e:
        st.error(f"❌ Erro no sistema de cache: {e}")
        return
    
    # Header principal
    if ENHANCED_COMPONENTS:
        colored_header(
            label="🌍 Dashboard LULC - Visão Geral Aprimorada",
            description="Análise de iniciativas de mapeamento de uso e cobertura da terra",
            color_name="violet-70"
        )
    else:
        st.title("🌍 Dashboard LULC - Visão Geral")
        st.markdown("Análise de iniciativas de mapeamento de uso e cobertura da terra")
    
    # Métricas principais
    create_enhanced_metrics(df)
    
    # Tabela interativa
    grid_response = create_enhanced_dataframe(df)
    
    # Gráficos existentes (manter Plotly)
    if ENHANCED_COMPONENTS:
        colored_header(
            label="📈 Visualizações",
            description="Gráficos interativos dos dados",
            color_name="orange-70"
        )
    else:
        st.subheader("📈 Visualizações")
    
    # Exemplo de gráfico com dados
    if 'ano_inicial' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribuição por Ano")
            fig_year = px.histogram(df, x='ano_inicial', title="Iniciativas por Ano de Início")
            st.plotly_chart(fig_year, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Acurácia vs Resolução")
            if 'acuracia' in df.columns and 'resolucao_espacial' in df.columns:
                fig_scatter = px.scatter(
                    df, 
                    x='resolucao_espacial', 
                    y='acuracia',
                    title="Acurácia vs Resolução Espacial",
                    hover_data=['nome_iniciativa'] if 'nome_iniciativa' in df.columns else None
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Informações de cache
    if ENHANCED_COMPONENTS:
        add_vertical_space(2)
        with st.expander("🔧 Informações Técnicas"):
            st.json(cache_info)
    else:
        with st.expander("ℹ️ Cache Info"):
            st.json(cache_info)

# Função para compatibilidade
def run():
    """Função principal para compatibilidade com o sistema existente"""
    run_enhanced_overview()

if __name__ == "__main__":
    run_enhanced_overview()
'''
    
    output_file = Path("dashboard/overview_enhanced.py")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_code)
    
    print(f"✅ Módulo melhorado criado: {output_file}")
    print()

def create_folium_enhanced_example():
    """Cria exemplo de uso avançado do Folium"""
    
    folium_code = '''#!/usr/bin/env python3
"""
Enhanced Folium Maps - Exemplo de Uso Avançado
==============================================

Demonstração de funcionalidades avançadas do Folium:
- Heatmaps
- Clustering
- Layers interativos
- Popups customizados

Author: GitHub Copilot
Date: 2025-07-22
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np

# Plugins avançados do Folium
try:
    from folium.plugins import HeatMap, MarkerCluster, Draw, MeasureControl
    from folium.plugins import FloatImage, MiniMap, ScrollZoomToggler
    FOLIUM_PLUGINS = True
except ImportError:
    FOLIUM_PLUGINS = False
    st.warning("⚠️ Plugins do Folium não disponíveis. Execute: pip install folium")

def create_enhanced_map(df_geo):
    """Cria mapa interativo avançado com múltiplas funcionalidades"""
    
    if df_geo is None or df_geo.empty:
        st.warning("⚠️ Dados geoespaciais não disponíveis")
        return None
    
    # Configurar centro do mapa (Brasil)
    center_lat = -15.77
    center_lon = -47.92
    
    # Criar mapa base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Adicionar tiles alternativos
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Positron',
        overlay=False,
        control=True
    ).add_to(m)
    
    if FOLIUM_PLUGINS:
        # 1. HEATMAP - Densidade de iniciativas
        if 'latitude' in df_geo.columns and 'longitude' in df_geo.columns:
            heat_data = []
            for _, row in df_geo.iterrows():
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    # Adicionar peso baseado na acurácia se disponível
                    weight = row.get('acuracia', 50) / 100.0
                    heat_data.append([row['latitude'], row['longitude'], weight])
            
            if heat_data:
                heat_map = HeatMap(
                    heat_data,
                    name='Densidade de Iniciativas',
                    radius=15,
                    blur=10,
                    max_zoom=10,
                    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
                )
                heat_map.add_to(m)
        
        # 2. MARKER CLUSTER - Agrupamento de pontos
        marker_cluster = MarkerCluster(
            name='Iniciativas (Clustered)',
            overlay=True,
            control=True,
            icon_create_function=None
        ).add_to(m)
        
        # Adicionar marcadores ao cluster
        for idx, row in df_geo.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                # Criar popup customizado
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="color: #2E86AB; margin-bottom: 10px;">
                        {row.get('nome_iniciativa', 'Iniciativa')}
                    </h4>
                    <p><b>Acurácia:</b> {row.get('acuracia', 'N/A')}%</p>
                    <p><b>Resolução:</b> {row.get('resolucao_espacial', 'N/A')}m</p>
                    <p><b>Período:</b> {row.get('ano_inicial', 'N/A')} - {row.get('ano_final', 'N/A')}</p>
                    <p><b>Classes:</b> {row.get('numero_classes', 'N/A')}</p>
                </div>
                """
                
                # Cor do marcador baseada na acurácia
                accuracy = row.get('acuracia', 50)
                if accuracy >= 90:
                    color = 'green'
                elif accuracy >= 75:
                    color = 'orange'
                else:
                    color = 'red'
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=row.get('nome_iniciativa', 'Clique para detalhes'),
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(marker_cluster)
        
        # 3. CONTROLES AVANÇADOS
        # Ferramenta de desenho
        draw = Draw(
            export=True,
            filename='lulc_selection.geojson',
            position='topleft',
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': True,
                'rectangle': True,
                'marker': True,
                'circlemarker': False,
            },
            edit_options={'edit': True}
        )
        draw.add_to(m)
        
        # Controle de medição
        measure_control = MeasureControl(
            position='bottomleft',
            primary_length_unit='kilometers',
            secondary_length_unit='miles',
            primary_area_unit='sqkilometers',
            secondary_area_unit='acres'
        )
        measure_control.add_to(m)
        
        # Minimapa
        minimap = MiniMap(
            tile_layer='OpenStreetMap',
            position='bottomright',
            width=150,
            height=150,
            collapsed_width=25,
            collapsed_height=25,
            zoom_level_offset=-5,
            zoom_animation=True
        )
        minimap.add_to(m)
        
        # Toggle de zoom com scroll
        ScrollZoomToggler().add_to(m)
    
    # Adicionar controle de layers
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Adicionar escala
    folium.plugins.MeasureControl().add_to(m)
    
    return m

def create_choropleth_map(df_states):
    """Cria mapa coroplético por estados"""
    # Exemplo de mapa coroplético (necessita dados de geometria dos estados)
    m = folium.Map(location=[-15.77, -47.92], zoom_start=4)
    
    # Aqui você adicionaria o choropleth com dados por estado
    # folium.Choropleth(...).add_to(m)
    
    return m

def run_enhanced_maps():
    """Demonstração dos mapas aprimorados"""
    
    st.title("🗺️ Mapas Interativos Avançados - LULC")
    st.markdown("Demonstração de funcionalidades avançadas do Folium")
    
    # Tentar carregar dados
    try:
        from utilities.cache_system import load_optimized_data
        metadata, df, cache_info = load_optimized_data()
        
        if df is not None and not df.empty:
            st.success(f"✅ Dados carregados: {len(df)} iniciativas")
            
            # Simular dados geográficos (substitua pela sua lógica)
            df_geo = df.copy()
            if 'latitude' not in df_geo.columns:
                # Simular coordenadas no Brasil
                np.random.seed(42)
                df_geo['latitude'] = np.random.uniform(-35, 5, len(df))
                df_geo['longitude'] = np.random.uniform(-75, -35, len(df))
            
        else:
            st.error("❌ Erro ao carregar dados")
            return
            
    except Exception as e:
        st.error(f"❌ Erro no sistema: {e}")
        return
    
    # Configurações do mapa
    st.sidebar.subheader("🎛️ Configurações do Mapa")
    
    show_heatmap = st.sidebar.checkbox("🔥 Mostrar Heatmap", value=True)
    show_clusters = st.sidebar.checkbox("📍 Mostrar Clusters", value=True) 
    show_controls = st.sidebar.checkbox("🛠️ Controles Avançados", value=True)
    
    # Criar e exibir mapa
    with st.spinner("🗺️ Criando mapa interativo..."):
        enhanced_map = create_enhanced_map(df_geo)
        
        if enhanced_map:
            st.subheader("🌍 Mapa Interativo das Iniciativas LULC")
            
            # Exibir mapa
            map_data = st_folium(
                enhanced_map,
                width=700,
                height=500,
                returned_objects=["last_object_clicked", "last_clicked", "bounds"]
            )
            
            # Mostrar informações de interação
            if map_data['last_object_clicked']:
                st.subheader("📊 Última Seleção")
                st.json(map_data['last_object_clicked'])
            
            # Estatísticas do mapa
            st.subheader("📈 Estatísticas do Mapa")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Iniciativas Plotadas", len(df_geo))
            with col2:
                if 'acuracia' in df_geo.columns:
                    avg_accuracy = df_geo['acuracia'].mean()
                    st.metric("Acurácia Média", f"{avg_accuracy:.1f}%")
            with col3:
                if 'resolucao_espacial' in df_geo.columns:
                    avg_resolution = df_geo['resolucao_espacial'].mean()
                    st.metric("Resolução Média", f"{avg_resolution:.1f}m")

if __name__ == "__main__":
    run_enhanced_maps()
'''
    
    output_file = Path("examples/folium_enhanced_demo.py")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(folium_code)
    
    print(f"✅ Exemplo Folium avançado criado: {output_file}")
    print()

def main():
    """Função principal de implementação"""
    print("🚀 IMPLEMENTAÇÃO FASE 1 - MELHORIAS IMEDIATAS")
    print("=" * 60)
    print("Esta implementação inclui:")
    print("1. 📦 Instalação de pacotes necessários")
    print("2. 📝 Atualização do requirements.txt")
    print("3. 🎨 Módulo overview aprimorado")
    print("4. 🗺️ Exemplo Folium avançado")
    print()
    
    # Perguntar se deve prosseguir
    response = input("Deseja prosseguir com a implementação? (s/n): ").lower().strip()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("\\n🔄 Iniciando implementação...")
        
        # 1. Instalar pacotes
        install_packages()
        
        # 2. Atualizar requirements
        update_requirements()
        
        # 3. Criar módulos aprimorados
        create_enhanced_overview_module()
        
        # 4. Criar exemplo Folium
        create_folium_enhanced_example()
        
        print("✅ IMPLEMENTAÇÃO FASE 1 CONCLUÍDA!")
        print("=" * 60)
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Teste o módulo overview_enhanced.py")
        print("2. Execute o exemplo folium_enhanced_demo.py")
        print("3. Integre os novos componentes ao dashboard principal")
        print("4. Considere implementar a Fase 2 (Pygwalker, etc.)")
        print()
        print("🌐 Para testar: streamlit run dashboard/overview_enhanced.py")
        print("🗺️ Para mapas: streamlit run examples/folium_enhanced_demo.py")
        
    else:
        print("❌ Implementação cancelada pelo usuário")

if __name__ == "__main__":
    main()
