"""
Agricultural Analysis Dashboard Orchestrator
===========================================

Dashboard orquestrador para análise agrícola brasileira baseado no menu do app.py.
Responde às páginas: Agriculture Overview, Crop Calendar, Agriculture Availability

Author: Agricultural Dashboard Team
Date: 2025-08-08
"""

import streamlit as st


def run():
    """
    Função principal que responde às páginas selecionadas no menu lateral do app.py.
    Verifica st.session_state.current_page para determinar qual página renderizar.
    """
    
    # Obter página atual do session state (definido pelo app.py)
    current_page = getattr(st.session_state, 'current_page', 'Agriculture Overview')
    
    # Renderizar página baseada na seleção do menu lateral
    if current_page == "Agriculture Overview":
        render_agriculture_overview_page()
    elif current_page == "Crop Calendar":
        render_crop_calendar_page()
    elif current_page == "Agriculture Availability":
        render_agriculture_availability_page()
    elif current_page == "CONAB Availability Analysis":
        render_conab_availability_analysis_page()
    else:
        # Fallback para página não encontrada
        st.error(f"❌ Página '{current_page}' não encontrada")
        st.info("Páginas disponíveis: Agriculture Overview, Crop Calendar, Agriculture Availability, CONAB Availability Analysis")


def render_agriculture_overview_page():
    """Renderiza página Agriculture Overview com 3 abas internas"""
    
    # Cabeçalho da página
    st.markdown("# 🌾 Agriculture Overview")
    st.markdown("**Portal Integrado de Dados Agrícolas - CONAB & IBGE**")
    
    # Informações contextuais
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📊 **Dados Mapeados**\nGeoespaciais e sensoriamento remoto")
        
        with col2:
            st.info("📈 **Estimativas CONAB**\nBoletins oficiais de safra")
        
        with col3:
            st.info("📋 **Estatísticas IBGE**\nDados censitários e amostrais")
    
    st.divider()
    
    # Sistema de abas INTERNAS do Overview
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Overview Geral (Mapeamentos)",
        "📊 Dados Estimados CONAB", 
        "📈 Dados Estimados IBGE"
    ])
    
    # Aba 1: Overview Geral com dados mapeados
    with tab1:
        st.markdown("## 🗺️ Overview Geral - Dados Mapeados")
        st.markdown("*Dados geoespaciais e de sensoriamento remoto da agricultura brasileira*")
        
        # Importar e renderizar componente de mapeamento
        try:
            from dashboard.components.agricultural_analysis.mapping_overview import render_mapping_overview
            render_mapping_overview()
        except ImportError as e:
            st.warning(f"⚠️ Componente de mapeamento: {e}")
            
            # Informações temporárias sobre mapeamentos
            st.markdown("""
            ### 📡 Fonte: Portal de Informações Agropecuárias - CONAB
            
            **Mapeamentos Disponíveis:**
            - 🌱 Soja (Sentinel-2, Landsat-8)
            - 🌽 Milho 1ª e 2ª Safra (MODIS, Sentinel-2)
            - 🌿 Algodão (Landsat-8, SPOT)
            - 🎋 Cana-de-açúcar (Multi-sensor)
            
            **Características Técnicas:**
            - Resolução: 10-30m
            - Cobertura: Nacional
            - Período: 2020-2024
            - Acurácia: 88-94%
            
            **Downloads:** [Portal CONAB](https://portaldeinformacoes.conab.gov.br/mapeamentos-agricolas-downloads.html)
            """)
    
    # Aba 2: Dados Estimados CONAB
    with tab2:
        st.markdown("## 📊 Dados Estimados CONAB")
        st.markdown("*Estimativas oficiais de produção, área e produtividade*")
        
        # Importar e renderizar componente CONAB
        try:
            from dashboard.conab_agricultural_data import render
            render()
        except ImportError as e:
            st.error(f"❌ Erro ao carregar dados CONAB: {e}")
    
    # Aba 3: Dados Estimados IBGE
    with tab3:
        st.markdown("## 📈 Dados Estimados IBGE")
        st.markdown("*Estatísticas oficiais da Produção Agrícola Municipal (PAM)*")
        
        # Importar e renderizar componente IBGE
        try:
            from dashboard.components.agricultural_analysis.ibge_estimates import render
            render()
        except ImportError as e:
            st.error(f"❌ Erro ao carregar dados IBGE: {e}")


def render_crop_calendar_page():
    """Renderiza página Crop Calendar com gráficos organizados do #file:calendar"""
    
    st.markdown("# 📅 Crop Calendar")
    st.markdown("**Análises Temporais do Calendário Agrícola Brasileiro**")
    
    # Carregar dados
    data = load_calendar_data()
    
    if not data:
        st.warning("⚠️ Dados de calendário agrícola não disponíveis")
        return
    
    # Filtros globais
    st.markdown("### 🎛️ Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        cultures = get_available_cultures(data)
        selected_culture = st.selectbox(
            "🌾 Selecionar Cultura:",
            options=['Todas'] + cultures,
            index=0
        )
    
    with col2:
        regions = get_available_regions(data)
        selected_region = st.selectbox(
            "🗺️ Selecionar Região:",
            options=['Todas'] + regions,
            index=0
        )
    
    # Filtrar dados
    filtered_data = filter_data(data, selected_culture, selected_region)
    
    st.divider()
    
    # Organizar gráficos em abas baseado nos arquivos em #file:calendar
    cal_tab1, cal_tab2, cal_tab3 = st.tabs([
        "🗓️ Heatmaps & Matrix",
        "📈 Timeline & Regional",
        "🌍 Spatial & Temporal"
    ])
    
    with cal_tab1:
        render_calendar_heatmaps_tab(filtered_data)

    with cal_tab2:
        render_timeline_regional_tab(filtered_data)
    
    with cal_tab3:
        render_spatial_temporal_tab(filtered_data)



def render_agriculture_availability_page():
    """Renderiza página Agriculture Availability com novos gráficos organizados em abas"""
    
    st.markdown("# 📊 Agriculture Availability")
    st.markdown("**Análise de Disponibilidade e Qualidade dos Dados Agrícolas**")
    
    # Carregar dados
    data = load_calendar_data()
    
    if not data:
        st.warning("⚠️ Dados para análise de disponibilidade não disponíveis")
        return
    
    # Filtros globais (mesmo do crop calendar)
    st.markdown("### 🎛️ Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        cultures = get_available_cultures(data)
        selected_culture = st.selectbox(
            "🌾 Selecionar Cultura:",
            options=['Todas'] + cultures,
            index=0,
            key="avail_culture"
        )
    
    with col2:
        regions = get_available_regions(data)
        selected_region = st.selectbox(
            "🗺️ Selecionar Região:",
            options=['Todas'] + regions,
            index=0,
            key="avail_region"
        )
    
    # Filtrar dados
    filtered_data = filter_data(data, selected_culture, selected_region)
    
    st.divider()
    
    # Organizar gráficos em abas
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "�️ Spatial Coverage",
        "🌱 Crop Diversity",
        "📅 Seasonal Patterns",
        "�️ Regional Activity",
        "� Activity Intensity",
        "📊 Overview"
    ])
    
    with tab1:
        render_spatial_coverage_tab(filtered_data)
    
    with tab2:
        render_crop_diversity_tab(filtered_data)
    
    with tab3:
        render_seasonal_patterns_tab(filtered_data)
    
    with tab4:
        render_regional_activity_tab(filtered_data)
    
    with tab5:
        render_activity_intensity_tab(filtered_data)
    
    with tab6:
        render_overview_tab(filtered_data)


# Funções auxiliares
def load_calendar_data():
    """Carrega dados de calendário agrícola"""
    try:
        from dashboard.components.agricultural_analysis.agricultural_loader import load_agricultural_data
        return load_agricultural_data()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None


def get_available_cultures(data):
    """Extrai culturas disponíveis dos dados"""
    if not data or 'crop_calendar' not in data:
        return []
    return list(data['crop_calendar'].keys())


def get_available_regions(data):
    """Extrai regiões disponíveis dos dados"""
    if not data or 'crop_calendar' not in data:
        return []
    
    regions = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            regions.add(state_info.get('region', 'Unknown'))
    return sorted(list(regions))


def filter_data(data, selected_culture, selected_region):
    """Filtra dados baseado na seleção"""
    if not data or 'crop_calendar' not in data:
        return data
    
    filtered_data = {'crop_calendar': {}}
    
    for crop_name, crop_data in data['crop_calendar'].items():
        # Filtro por cultura
        if selected_culture != 'Todas' and crop_name != selected_culture:
            continue
        
        # Filtro por região
        filtered_states = []
        for state_info in crop_data:
            if selected_region == 'Todas' or state_info.get('region') == selected_region:
                filtered_states.append(state_info)
        
        if filtered_states:
            filtered_data['crop_calendar'][crop_name] = filtered_states
    
    return filtered_data


# Funções de renderização de abas do Crop Calendar
def render_calendar_heatmaps_tab(data):
    """Renderiza aba de heatmaps e matrizes"""
    st.markdown("#### 🗓️ Heatmaps & Calendar Matrix")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🌡️ Enhanced Calendar Heatmap")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.enhanced_calendar_heatmap import create_enhanced_calendar_heatmap
            create_enhanced_calendar_heatmap(data)
        except Exception as e:
            st.warning(f"⚠️ Enhanced Calendar Heatmap: {e}")
    
    with col2:
        st.markdown("##### 📊 National Calendar Matrix")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.national_calendar_matrix import create_calendar_heatmap_chart
            fig = create_calendar_heatmap_chart(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ National Calendar Matrix: {e}")


def render_monthly_seasonal_tab(data):
    """Renderiza aba de análises mensais e sazonais com sub-abas para cada gráfico"""
    st.markdown("#### 📊 Monthly & Seasonal Analysis")
    
    # Criar sub-abas para organizar melhor os gráficos
    monthly_tab1, monthly_tab2, monthly_tab3 = st.tabs([
        "🔄 Seasonality & Monthly",
        "🎯 Polar Activity",
        "🌾 Crop Distribution"
    ])
    
    with monthly_tab1:
        # Monthly Activity Charts e Seasonality Analysis ficam juntos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔄 Seasonality Analysis")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                create_seasonality_index_chart(data, "seasonality_monthly_seasonal_tab")
            except Exception as e:
                st.warning(f"⚠️ Seasonality Analysis: {e}")
        
        with col2:
            st.markdown("##### 📊 Monthly Overview")
            # Placeholder para análises mensais adicionais se necessário
            st.info("📊 Additional monthly analysis can be added here")
    
    with monthly_tab2:
        # Polar Activity Chart em sua própria aba
        st.markdown("##### 🎯 Polar Activity Distribution")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.polar_activity_chart import create_polar_activity_chart
            fig = create_polar_activity_chart(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Polar Activity Chart: {e}")
    
    with monthly_tab3:
        # Crop Distribution em sua própria aba
        st.markdown("##### 🌾 Crop Distribution")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import render_crop_distribution_charts
            render_crop_distribution_charts(data)
        except Exception as e:
            st.warning(f"⚠️ Crop Distribution: {e}")


def render_timeline_regional_tab(data):
    """Renderiza aba de timeline e análise regional com sub-abas para cada gráfico"""
    st.markdown("#### 📈 Timeline & Regional Analysis")
    
    # Criar sub-abas para organizar melhor os gráficos
    timeline_tab1, timeline_tab2, timeline_tab3 = st.tabs([
        "📅 Monthly & Seasonality",
        "🗓️ Gantt Chart",
        "🔄 Polar Seasonality"
    ])
    
    with timeline_tab1:
        # Monthly Activity Charts e Seasonality ficam lado a lado
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📅 Monthly Activity Charts")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.monthly_activity_charts import create_total_activities_per_month_chart
                fig = create_total_activities_per_month_chart(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Monthly Activity Charts: {e}")
        
        with col2:
            st.markdown("##### 🔄 Seasonality Analysis")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                create_seasonality_index_chart(data, "seasonality_timeline_regional_tab")
            except Exception as e:
                st.warning(f"⚠️ Seasonality Analysis: {e}")
        
        # Interactive Timeline abaixo dos dois gráficos acima
        st.markdown("##### ⏰ Interactive Timeline")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.interactive_timeline import create_interactive_timeline
            fig = create_interactive_timeline(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Interactive Timeline: {e}")
    
    
    with timeline_tab2:
        # Gantt Chart em sua própria aba
        st.markdown("##### 🗓️ Gantt Chart - Crop Cultivation Periods")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.crop_gantt_chart import render_crop_gantt_chart
            
            # Usar dados já filtrados da aba para o Gantt
            crop_calendar = data.get('crop_calendar', {})
            
            if crop_calendar:
                # Renderizar o diagrama de Gantt sem filtros adicionais (usa filtros da aba)
                render_crop_gantt_chart(crop_calendar, "Brasil")
            else:
                st.info("📊 Nenhum dado de calendário disponível para o diagrama de Gantt")
                
        except Exception as e:
            st.warning(f"⚠️ Gantt Chart: {e}")
    
    with timeline_tab3:
        # Polar Seasonality Analysis em sua própria sub-aba
        st.markdown("##### 🔄 Polar Seasonality Analysis")
        st.markdown("**Análise polar das atividades agrícolas ao longo do ano**")
        
        try:
            # Importar e usar a função de análise polar criada anteriormente
            from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_polar_seasonality_analysis
            
            # Criar o gráfico polar de sazonalidade
            create_polar_seasonality_analysis(data, "timeline_polar_seasonality_chart")
            
            
        except Exception as e:
            st.error(f"❌ Erro na análise polar de sazonalidade: {str(e)}")
            st.info("📊 Verifique se os dados de calendário estão disponíveis")
    


def render_statistics_analysis_tab(data):
    """Renderiza aba de estatísticas e análises avançadas"""
    st.markdown("#### 🎯 Statistics & Advanced Analysis")
    
    # Estatísticas básicas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Culturas", len(data.get('crop_calendar', {})))
    
    with col2:
        total_states = sum(len(crops) for crops in data.get('crop_calendar', {}).values())
        st.metric("Total de Estados", total_states)
    
    with col3:
        # Calculate average calendar span
        calendar_spans = []
        for crop_data in data.get('crop_calendar', {}).values():
            for state_info in crop_data:
                if 'planting_months' in state_info and 'harvesting_months' in state_info:
                    planting = len(state_info.get('planting_months', []))
                    harvesting = len(state_info.get('harvesting_months', []))
                    calendar_spans.append(planting + harvesting)
        
        avg_span = sum(calendar_spans) / len(calendar_spans) if calendar_spans else 0
        st.metric("Média Extensão Calendário", f"{avg_span:.1f} meses")
    
    # Enhanced Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Enhanced Statistics")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.enhanced_statistics import create_enhanced_statistics
            selected_crops = list(data.get('crop_calendar', {}).keys())[:5]  # Top 5 crops
            selected_states = ['SP', 'MG', 'MT', 'GO', 'RS']  # Main agricultural states
            create_enhanced_statistics(data, selected_crops, selected_states)
        except Exception as e:
            st.info("📊 Enhanced statistics chart será implementado")
    
    with col2:
        st.markdown("##### 📈 Additional Analysis")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.additional_analysis import render_seasonality_analysis
            render_seasonality_analysis(data)
        except Exception as e:
            st.info("📈 Additional analysis chart será implementado")


# Funções de renderização de abas do Availability
def render_availability_analysis_tab(data):
    """Renderiza aba de análise geral de disponibilidade"""
    st.markdown("#### 📈 General Availability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Calendar Availability Analysis")
        try:
            from dashboard.components.agricultural_analysis.charts.availability.calendar_availability_analysis import render_calendar_availability_analysis
            render_calendar_availability_analysis(data)
        except Exception as e:
            st.warning(f"⚠️ Calendar Availability Analysis: {e}")
    
    with col2:
        st.markdown("##### 📋 Data Quality Metrics")
        try:
            # Adicionar métricas de qualidade de dados aqui
            st.info("📊 Data quality metrics will be displayed here")
        except Exception as e:
            st.warning(f"⚠️ Data Quality Metrics: {e}")
    


def render_conab_specific_tab(data):
    """Renderiza aba específica do CONAB com gráficos migrados do overview"""
    st.markdown("#### 🎯 CONAB Specific Analysis")
    
    # Load CONAB detailed data for charts
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        st.warning("⚠️ Dados CONAB detalhados não disponíveis")
        return
    
    # CONAB Spatial and Temporal Distribution
    st.markdown("##### 🗺️ Spatial and Temporal Distribution")
    try:
        fig = plot_conab_spatial_temporal_distribution(conab_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ CONAB Spatial Temporal Distribution: {e}")
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📈 Temporal Coverage")
        try:
            fig = plot_conab_temporal_coverage(conab_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ CONAB Temporal Coverage: {e}")
    
    with col2:
        st.markdown("##### 🗺️ Spatial Coverage")
        try:
            fig = plot_conab_spatial_coverage(conab_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ CONAB Spatial Coverage: {e}")
    
    # Crop Diversity Chart
    st.markdown("##### 🌾 Crop Diversity")
    try:
        fig = plot_conab_crop_diversity(conab_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ CONAB Crop Diversity: {e}")
    
    # CONAB Availability Matrix
    st.markdown("##### 📊 CONAB Availability Matrix")
    try:
        from dashboard.components.agricultural_analysis.charts.availability.conab_availability_matrix import create_conab_availability_matrix
        create_conab_availability_matrix(data)
    except Exception as e:
        st.warning(f"⚠️ CONAB Availability Matrix: {e}")


def render_crop_availability_detailed_tab(data):
    """Renderiza aba detalhada de disponibilidade por cultura"""
    st.markdown("#### 📊 Detailed Crop Availability")
    
    # Tab selector for detailed analysis
    cultures = get_available_cultures(data)
    
    if not cultures:
        st.info("Nenhuma cultura disponível para análise detalhada")
        return
    
    # Create subtabs for each culture
    if len(cultures) <= 5:
        # If few cultures, create tabs for each
        culture_tabs = st.tabs([f"🌾 {culture}" for culture in cultures])
        
        for i, culture in enumerate(cultures):
            with culture_tabs[i]:
                render_individual_crop_analysis(data, culture)
    else:
        # If many cultures, use selectbox
        selected_culture = st.selectbox("Selecionar Cultura para Análise Detalhada:", cultures)
        render_individual_crop_analysis(data, selected_culture)


def render_individual_crop_analysis(data, culture):
    """Renderiza análise individual de uma cultura"""
    st.markdown(f"##### 📊 Análise de Disponibilidade: {culture}")
    
    # Extract culture-specific data
    culture_data = data.get('crop_calendar', {}).get(culture, [])
    
    if not culture_data:
        st.info(f"Dados não disponíveis para {culture}")
        return
    
    # Basic metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estados com Dados", len(culture_data))
    
    with col2:
        regions = set()
        for state_info in culture_data:
            regions.add(state_info.get('region', 'Unknown'))
        st.metric("Regiões Cobertas", len(regions))
    
    with col3:
        total_months = set()
        for state_info in culture_data:
            total_months.update(state_info.get('planting_months', []))
            total_months.update(state_info.get('harvesting_months', []))
        st.metric("Meses de Atividade", len(total_months))
    
    # Individual crop availability analysis
    # TODO: Implement detailed crop analysis
    st.info(f"Análise detalhada para {culture} será implementada")


# === MIGRATED CONAB FUNCTIONS FROM OVERVIEW ===

def load_conab_detailed_data():
    """Load CONAB detailed data from JSON file."""
    try:
        from pathlib import Path
        import json
        
        current_dir = Path(__file__).parent.parent.parent
        file_path = current_dir / "data" / "conab_detailed_initiative.jsonc"
        
        if not file_path.exists():
            # Try alternative path
            file_path = current_dir / "data" / "json" / "conab_detailed_initiative.jsonc"
        
        if not file_path.exists():
            st.warning("Arquivo de dados CONAB detalhados não encontrado")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Clean the JSONC content
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove control characters and clean the line
                cleaned_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t\n\r')
                
                # Remove comments but keep the line if it has valid JSON
                if '//' in cleaned_line:
                    json_part = cleaned_line.split('//')[0].strip()
                    if json_part:
                        cleaned_lines.append(json_part)
                else:
                    if cleaned_line.strip():
                        cleaned_lines.append(cleaned_line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # Additional cleanup for common JSON issues
            cleaned_content = cleaned_content.replace('\r', '').replace('\x00', '')
            
            return json.loads(cleaned_content)
            
    except Exception as e:
        st.warning(f"Error loading CONAB detailed data: {e}")
        return {}


def plot_conab_spatial_temporal_distribution(conab_data):
    """Create a spatial and temporal distribution chart for CONAB mapping initiatives."""
    import plotly.graph_objects as go
    import plotly.express as px
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No data available)")
    
    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Prepare data for timeline chart
    timeline_data = []
    all_states = set()
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        second_crop_years = crop_info.get("second_crop_years", {})
        
        # Process first and second semester data
        for state, years in first_crop_years.items():
            if state in regions:
                all_states.add(state)
                for year_range in years:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    
                    for year in range(start_year, end_year + 1):
                        timeline_data.append({
                            'State': state,
                            'Year': year,
                            'Crop': crop,
                            'Semester': 'First',
                            'Coverage': 1                        
                        })
    
    if not timeline_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No timeline data)")
    
    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(timeline_data)
    
    # Create figure
    fig = go.Figure()
    
    # Get unique crop types and assign colors
    crop_types = sorted(df['Crop'].unique())
    colors = px.colors.qualitative.Set3
    crop_colors = {crop: colors[i % len(colors)] for i, crop in enumerate(crop_types)}
    
    states_list = sorted(list(all_states), reverse=True)
    states_list.append("Brazil")
    
    legend_added = set()
    
    # Add traces for each state
    for state in states_list:
        if state == "Brazil":
            continue
        
        state_data = df[df['State'] == state]
        if not state_data.empty:
            for crop in crop_types:
                crop_state_data = state_data[state_data['Crop'] == crop]
                if not crop_state_data.empty:
                    years = sorted(crop_state_data['Year'].unique())
                    
                    if years:
                        start_year = years[0]
                        end_year = years[-1]
                        
                        show_in_legend = crop not in legend_added
                        if show_in_legend:
                            legend_added.add(crop)
                        
                        fig.add_trace(go.Scatter(
                            x=[start_year, end_year],
                            y=[state, state],
                            mode='lines',
                            line=dict(width=15, color=crop_colors[crop]),
                            name=crop,
                            legendgroup=crop,
                            showlegend=show_in_legend,
                            hovertemplate=f"<b>{state}</b><br>Crop: {crop}<br>Period: {start_year}-{end_year}<br><extra></extra>"
                        ))
    
    # Add Brazil trace
    if timeline_data:
        all_years = sorted(df['Year'].unique())
        if all_years:
            brazil_start = min(all_years)
            brazil_end = max(all_years)
            
            fig.add_trace(go.Scatter(
                x=[brazil_start, brazil_end],
                y=["Brazil", "Brazil"],
                mode='lines',
                line=dict(width=15, color='#808080'),
                name='Overall Coverage',
                showlegend=True,
                hovertemplate=f"<b>Brazil</b><br>Overall Period: {brazil_start}-{brazil_end}<br><extra></extra>"
            ))
    
    # Update layout
    fig.update_layout(
        title="CONAB Spatial and Temporal Distribution",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Region</b>",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title=dict(text="<b>Crop Type</b>")
        ),   
        yaxis=dict(
            categoryorder='array',
            categoryarray=states_list,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            tickfont=dict(size=14),
            showline=True,
            linewidth=0,
            zeroline=False
        ),
        xaxis=dict(
            dtick=1,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            showline=True,
            linewidth=0,
            zeroline=False
        )
    )
    
    return fig


def plot_conab_temporal_coverage(conab_data):
    """Create a temporal coverage chart showing percentage of states covered over time."""
    import plotly.graph_objects as go
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No data available)")
    
    # Extract data and calculate coverage percentages
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    year_coverage = {}
    TOTAL_STATES_PLUS_DF = 27
    
    for crop, crop_info in crop_coverage.items():
        first_crop_years = crop_info.get("first_crop_years", {})
        
        for state, years in first_crop_years.items():
            for year_range in years:
                start_year = int(year_range.split('-')[0])
                end_year = int(year_range.split('-')[1])
                
                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)
    
    if not year_coverage:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No coverage data)")
    
    years = sorted(year_coverage.keys())
    coverage_percentages = []
    
    for year in years:
        num_states = len(year_coverage[year])
        percentage = (num_states / TOTAL_STATES_PLUS_DF) * 100
        coverage_percentages.append(percentage)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=coverage_percentages,
        mode='lines+markers',
        line=dict(width=3, color='#17a2b8'),
        marker=dict(size=8, color='#17a2b8'),
        name='Coverage %',
        hovertemplate="<b>Year:</b> %{x}<br><b>Coverage:</b> %{y:.1f}%<br><extra></extra>"
    ))
    
    fig.update_layout(
        title="CONAB Temporal Coverage",
        xaxis_title="Year",
        yaxis_title="Percentage of States",
        height=400,
        yaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    return fig


def plot_conab_spatial_coverage(conab_data):
    """Create a spatial coverage chart showing percentage coverage by state."""
    import plotly.graph_objects as go
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No data available)")
    
    # Extract and process data
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    state_coverage = {}
    total_years = 24  # 2000-2023
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        
        for state in regions:
            if state not in state_coverage:
                state_coverage[state] = set()
            
            if state in first_crop_years:
                for year_range in first_crop_years[state]:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)
    
    if not state_coverage:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No coverage data)")
    
    states = []
    coverages = []
    
    for state, years in state_coverage.items():
        coverage_percent = (len(years) / total_years) * 100
        states.append(state)
        coverages.append(coverage_percent)
    
    # Sort by coverage percentage
    sorted_data = sorted(zip(states, coverages), key=lambda x: x[1])
    states, coverages = zip(*sorted_data)
    
    # Color gradient based on coverage
    colors = ['#ffcccc' if c < 25 else '#ffeb99' if c < 50 else '#ccffcc' if c < 75 else '#99ccff' for c in coverages]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=coverages,
        y=states,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<br><extra></extra>"
    ))
    
    fig.update_layout(
        title="CONAB Spatial Coverage (2000-2023)",
        xaxis_title="Coverage (%)",
        yaxis_title="State/Area",
        height=500,
        showlegend=False
    )
    
    return fig


def plot_conab_crop_diversity(conab_data):
    """Create a crop type diversity chart showing crop types by state."""
    import plotly.graph_objects as go
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Crop Diversity (No data available)")
    
    # Extract and process data
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    state_crops = {}
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        
        for state in regions:
            if state not in state_crops:
                state_crops[state] = []
            state_crops[state].append(crop)
    
    if not state_crops:
        return go.Figure().update_layout(title="CONAB Crop Diversity (No crop data)")
    
    states = sorted(state_crops.keys())
    crop_types = list(set([crop for crops in state_crops.values() for crop in crops]))
    
    # Color map for different crops
    color_map = {
        'Cotton': '#8B4513',
        'Irrigated Rice': '#4682B4',
        'Coffee': '#6B4423',
        'Sugar cane': '#32CD32',
        'Other winter crops': '#FFD700',
        'Other summer crops': '#FFA500',
        'Corn': '#FFFF00',
        'Soybean': '#8B0000',
        'Sugar cane mill': '#228B22'
    }
    
    fig = go.Figure()
    
    # Count crops per state
    for crop in crop_types:
        crop_counts = []
        for state in states:
            count = state_crops[state].count(crop) if state in state_crops else 0
            crop_counts.append(count)
        
        fig.add_trace(go.Bar(
            x=crop_counts,
            y=states,
            orientation='h',
            name=crop,
            marker=dict(color=color_map.get(crop, '#808080')),
            hovertemplate=f"<b>{crop}</b><br>State: %{{y}}<br>Count: %{{x}}<br><extra></extra>"
        ))
    
    fig.update_layout(
        title="CONAB Crop Type Diversity by State (2000-2023)",
        xaxis_title="Crop Type Count",
        yaxis_title="State/Area",
        height=500,
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig


# Funções de renderização das abas da Agriculture Availability
def render_spatial_coverage_tab(data):
    """Renders spatial coverage tab with subtabs by state and region"""
    st.markdown("### 🗺️ Spatial Coverage Analysis")
    st.markdown("Analysis of agricultural data spatial coverage across Brazilian states and regions.")
    
    # Create subtabs for state and region
    subtab1, subtab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with subtab1:
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_conab_spatial_coverage_by_state
            fig = plot_conab_spatial_coverage_by_state(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Coverage percentage by state, showing data availability across Brazilian states using acronyms.")
            else:
                st.warning("⚠️ Unable to generate spatial coverage chart by state")
        except Exception as e:
            st.error(f"❌ Error loading spatial coverage chart by state: {e}")
    
    with subtab2:
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_conab_spatial_coverage_by_region
            fig = plot_conab_spatial_coverage_by_region(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Coverage percentage by Brazilian region (North, Northeast, Central-West, Southeast, South).")
            else:
                st.warning("⚠️ Unable to generate spatial coverage chart by region")
        except Exception as e:
            st.error(f"❌ Error loading spatial coverage chart by region: {e}")


def render_crop_diversity_tab(data):
    """Renders crop diversity tab with subtabs by state and region"""
    st.markdown("### 🌱 Crop Diversity Analysis")
    st.markdown("Analysis of crop type diversity across Brazilian states and regions.")
    
    # Create subtabs for state and region
    subtab1, subtab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with subtab1:
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_conab_crop_diversity_by_state
            fig = plot_conab_crop_diversity_by_state(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Number and types of crops cultivated in each state, showing agricultural diversity by state acronym.")
            else:
                st.warning("⚠️ Unable to generate crop diversity chart by state")
        except Exception as e:
            st.error(f"❌ Error loading crop diversity chart by state: {e}")
    
    with subtab2:
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_conab_crop_diversity_by_region
            fig = plot_conab_crop_diversity_by_region(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Crop diversity patterns across Brazilian regions, highlighting regional agricultural specialization.")
            else:
                st.warning("⚠️ Unable to generate crop diversity chart by region")
        except Exception as e:
            st.error(f"❌ Error loading crop diversity chart by region: {e}")


def render_seasonal_patterns_tab(data):
    """Renderiza aba de padrões sazonais com subtabs por estado e região"""
    st.markdown("### 📅 Seasonal Patterns Analysis")
    st.markdown("Analysis of seasonal agricultural activity patterns throughout the year.")
    
    # Primeiro nível: Estado vs Região
    main_tab1, main_tab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with main_tab1:
        st.markdown("**Seasonal patterns at state level**")
        # Sub-abas para diferentes visualizações de padrões sazonais por estado
        seasonal_tab1, seasonal_tab2, seasonal_tab3 = st.tabs([
            "🌞 Seasonal Overview",
            "📊 Crop Distribution", 
            "📈 Monthly Intensity"
        ])
        
        with seasonal_tab1:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_seasonal_patterns
                fig = plot_seasonal_patterns(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Overview of seasonal planting and harvest patterns across states.")
                else:
                    st.warning("⚠️ Unable to generate seasonal patterns chart")
            except Exception as e:
                st.error(f"❌ Error loading seasonal patterns chart: {e}")
        
        with seasonal_tab2:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_crop_seasonal_distribution
                fig = plot_crop_seasonal_distribution(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Seasonal distribution heatmap showing when different crops are active in each state.")
                else:
                    st.warning("⚠️ Unable to generate seasonal distribution heatmap")
            except Exception as e:
                st.error(f"❌ Error loading seasonal distribution heatmap: {e}")
        
        with seasonal_tab3:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_monthly_activity_intensity
                fig = plot_monthly_activity_intensity(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Monthly activity intensity showing peak agricultural periods by state.")
                else:
                    st.warning("⚠️ Unable to generate monthly intensity chart")
            except Exception as e:
                st.error(f"❌ Error loading monthly intensity chart: {e}")
    
    with main_tab2:
        st.markdown("**Seasonal patterns at regional level**")
        st.info("🔄 Regional-level seasonal analysis - aggregating state data by Brazilian regions.")
        # Para região, podemos reutilizar os mesmos gráficos mas com dados agregados por região
        # Por enquanto, vamos mostrar uma mensagem indicando que será implementado
        st.markdown("*Regional seasonal analysis will aggregate data from states within each Brazilian region (North, Northeast, Central-West, Southeast, South).*")


def render_regional_activity_tab(data):
    """Renderiza aba de atividade regional com subtabs por estado e região"""
    st.markdown("### � Regional Activity Analysis")
    st.markdown("Analysis of agricultural activities across Brazilian states and regions.")
    
    # Primeiro nível: Estado vs Região
    main_tab1, main_tab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with main_tab1:
        st.markdown("**Regional activity analysis at state level**")
        # Sub-abas para diferentes análises regionais por estado
        regional_tab1, regional_tab2, regional_tab3, regional_tab4 = st.tabs([
            "📊 State Comparison",
            "🗺️ Activity Heatmap",
            "🌾 Crop Specialization",
            "⏰ Activity Timeline"
        ])
        
        with regional_tab1:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_regional_activity_comparison
                fig = plot_regional_activity_comparison(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Comparison of agricultural activity levels between states.")
                else:
                    st.warning("⚠️ Unable to generate state comparison chart")
            except Exception as e:
                st.error(f"❌ Error loading state comparison chart: {e}")
        
        with regional_tab2:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_heatmap
                fig = plot_state_activity_heatmap(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Heatmap showing activity intensity across states and months.")
                else:
                    st.warning("⚠️ Unable to generate state activity heatmap")
            except Exception as e:
                st.error(f"❌ Error loading state activity heatmap: {e}")
        
        with regional_tab3:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_regional_crop_specialization
                fig = plot_regional_crop_specialization(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Crop specialization patterns showing which crops dominate in each state.")
                else:
                    st.warning("⚠️ Unable to generate crop specialization chart")
            except Exception as e:
                st.error(f"❌ Error loading crop specialization chart: {e}")
        
        with regional_tab4:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_activity_timeline_by_region
                fig = plot_activity_timeline_by_region(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Timeline of agricultural activities showing seasonal progression by state.")
                else:
                    st.warning("⚠️ Unable to generate activity timeline")
            except Exception as e:
                st.error(f"❌ Error loading activity timeline: {e}")
    
    with main_tab2:
        st.markdown("**Regional activity analysis at Brazilian region level**")
        st.info("🔄 Regional-level activity analysis - aggregating state data by Brazilian regions.")
        # Para região, podemos reutilizar os mesmos gráficos mas com dados agregados por região
        st.markdown("*Regional activity analysis will show patterns for North, Northeast, Central-West, Southeast, and South regions.*")


def render_activity_intensity_tab(data):
    """Renderiza aba de intensidade de atividades com subtabs por estado e região"""
    st.markdown("### ⚡ Activity Intensity Analysis")
    st.markdown("Analysis of agricultural activity intensity patterns across time and space.")
    
    # Primeiro nível: Estado vs Região
    main_tab1, main_tab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with main_tab1:
        st.markdown("**Activity intensity analysis at state level**")
        # Sub-abas para diferentes análises de intensidade por estado
        intensity_tab1, intensity_tab2, intensity_tab3, intensity_tab4 = st.tabs([
            "🗓️ Intensity Matrix",
            "⚡ Peak Activity",
            "🎯 Density Map",
            "📊 Concentration Index"
        ])
        
        with intensity_tab1:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_activity_intensity_matrix
                fig = plot_activity_intensity_matrix(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Matrix showing activity intensity across crops and months at state level.")
                else:
                    st.warning("⚠️ Unable to generate intensity matrix")
            except Exception as e:
                st.error(f"❌ Error loading intensity matrix: {e}")
        
        with intensity_tab2:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_peak_activity_analysis
                fig = plot_peak_activity_analysis(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Peak activity periods throughout the year showing planting and harvest peaks by state.")
                else:
                    st.warning("⚠️ Unable to generate peak activity analysis")
            except Exception as e:
                st.error(f"❌ Error loading peak activity analysis: {e}")
        
        with intensity_tab3:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_activity_density_map
                fig = plot_activity_density_map(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Density map showing activity concentration across states and months.")
                else:
                    st.warning("⚠️ Unable to generate density map")
            except Exception as e:
                st.error(f"❌ Error loading density map: {e}")
        
        with intensity_tab4:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_activity_concentration_index
                fig = plot_activity_concentration_index(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Concentration index showing temporal distribution of activities by crop and state.")
                else:
                    st.warning("⚠️ Unable to generate concentration index")
            except Exception as e:
                st.error(f"❌ Error loading concentration index: {e}")
    
    with main_tab2:
        st.markdown("**Activity intensity analysis at regional level**")
        st.info("🔄 Regional-level intensity analysis - aggregating state data by Brazilian regions.")
        st.markdown("*Regional intensity analysis will show activity patterns for North, Northeast, Central-West, Southeast, and South regions.*")


def render_overview_tab(data):
    """Renderiza aba de overview geral"""
    st.markdown("### 📊 General Overview")
    st.markdown("Visão geral dos dados e estatísticas principais.")
    
    if not data or 'crop_calendar' not in data:
        st.warning("⚠️ Dados não disponíveis para análise")
        return
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    total_crops = len(data['crop_calendar'])
    total_states = len(set(
        state_info.get('state_code', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('state_code')
    ))
    total_regions = len(set(
        state_info.get('region', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('region')
    ))
    total_activities = sum(
        sum(1 for activity in state_info.get('calendar', {}).values() if activity and activity.strip())
        for crop_data in data['crop_calendar'].values()
        for state_info in crop_data
    )
    
    with col1:
        st.metric("🌾 Total Crops", total_crops)
    
    with col2:
        st.metric("🗺️ States Covered", total_states)
    
    with col3:
        st.metric("🌍 Regions", total_regions)
    
    with col4:
        st.metric("📊 Total Activities", total_activities)
    
    st.markdown("---")
    
    # Informações sobre os dados
    st.markdown("#### 📋 Data Summary")
    
    # Lista de culturas
    st.markdown("**Culturas disponíveis:**")
    crops_list = ", ".join(sorted(data['crop_calendar'].keys()))
    st.markdown(f"- {crops_list}")
    
    # Lista de regiões
    regions_list = sorted(set(
        state_info.get('region', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('region')
    ))
    st.markdown("**Regiões cobertas:**")
    st.markdown(f"- {', '.join(regions_list)}")
    
    # Data source info
    st.markdown("---")
    st.markdown("#### 📊 Data Source")
    st.info("""
    **Fonte:** CONAB (Companhia Nacional de Abastecimento)
    
    **Descrição:** Calendário agrícola mostrando períodos de plantio e colheita por estado e tipo de cultura
    
    **Legenda:**
    - P = Plantio (Planting)
    - H = Colheita (Harvest)  
    - PH = Plantio e Colheita (Planting and Harvest)
    """)


def render_conab_availability_analysis_page():
    """Renderiza página dedicada e independente para CONAB Availability Analysis"""
    
    # Cabeçalho da página
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🎯 CONAB Availability Analysis
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            📊 Análise de Disponibilidade CONAB - Análise baseada em dados oficiais CONAB por região e estado
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados CONAB
    data = load_calendar_data()
    
    if not data:
        st.error("❌ Dados CONAB não disponíveis para análise")
        st.info("Esta página requer dados do calendário agrícola CONAB para funcionar.")
        return
    
    # Informações contextuais sobre dados CONAB
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📈 **Estimativas de Safra**\nBoletins mensais oficiais")
        
        with col2:
            st.info("🗺️ **Mapeamentos**\nDados geoespaciais por satélite")
        
        with col3:
            st.info("📅 **Calendário Agrícola**\nPeriodos de plantio e colheita")
    
    st.divider()
    
    # Sistema de abas para análises CONAB organizadas
    tab1, tab2, tab3, tab4 = st.tabs([
        "�️ Análise Regional",
        "� Sazonalidade", 
        "⏰ Timeline",
        "📈 Tendências"
    ])
    
    # Aba 1: Análise Regional
    with tab1:
        st.markdown("## �️ Análise Regional")
        st.markdown("*Análise de disponibilidade de dados CONAB por região e estado*")
        
        # Subabas para diferentes tipos de análise regional
        subtab1, subtab2, subtab3 = st.tabs([
            "📊 Distribuição Regional",
            "🗾 Matriz Nacional", 
            "📈 Intensidade de Atividades"
        ])
        
        with subtab1:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import create_crop_type_distribution_chart, create_crop_diversity_by_region_chart
                
                st.markdown("### 📊 Distribuição de Culturas por Região")
                
                # Filtros específicos
                col1, col2 = st.columns(2)
                with col1:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "🗺️ Região:",
                        options=['Todas'] + regions,
                        key="regional_distribution_region"
                    )
                
                with col2:
                    chart_type = st.selectbox(
                        "� Tipo de Análise:",
                        options=['Distribuição por Cultura', 'Diversidade Regional'],
                        key="regional_distribution_type"
                    )
                
                # Preparar dados filtrados
                filtered_data = data.copy()
                
                # Gerar gráfico baseado na seleção
                if chart_type == 'Distribuição por Cultura':
                    fig = create_crop_type_distribution_chart(filtered_data)
                else:
                    fig = create_crop_diversity_by_region_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Não foi possível gerar a análise de distribuição")
                    
            except ImportError as e:
                st.error(f"❌ Erro ao carregar componente: {e}")
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar distribuição: {e}")
        
        with subtab2:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.national_calendar_matrix import create_calendar_heatmap_chart, create_consolidated_calendar_matrix_chart
                
                st.markdown("### � Matriz Nacional do Calendário")
                
                # Filtros específicos
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Cultura:",
                        options=['Todas'] + cultures,
                        key="regional_matrix_culture"
                    )
                
                with col2:
                    chart_type = st.selectbox(
                        "📊 Tipo de Visualização:",
                        options=['Heatmap', 'Matriz Consolidada'],
                        key="regional_matrix_type"
                    )
                
                # Preparar dados filtrados
                filtered_data = data.copy()
                
                # Gerar gráfico baseado na seleção
                if chart_type == 'Heatmap':
                    fig = create_calendar_heatmap_chart(filtered_data)
                else:
                    fig = create_consolidated_calendar_matrix_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Não foi possível gerar a matriz do calendário")
                    
            except ImportError as e:
                st.error(f"❌ Erro ao carregar componente: {e}")
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar matriz: {e}")
        
        with subtab3:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.activity_intensity import create_intensity_heatmap
                
                st.markdown("### 📈 Intensidade de Atividades por Região")
                
                # Filtros específicos
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Cultura:",
                        options=['Todas'] + cultures,
                        key="regional_intensity_culture"
                    )
                
                with col2:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "�️ Região:",
                        options=['Todas'] + regions,
                        key="regional_intensity_region"
                    )
                
                # Preparar dados filtrados
                filtered_data = data.copy()
                
                # Renderizar gráfico
                create_intensity_heatmap(filtered_data)
                    
            except ImportError as e:
                st.error(f"❌ Erro ao carregar componente: {e}")
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar gráfico de intensidade: {e}")
    
    # Aba 2: Sazonalidade
    with tab2:
        st.markdown("## � Sazonalidade")
        st.markdown("*Análise de padrões sazonais da agricultura brasileira*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
            
            # Filtros específicos
            st.markdown("### 🎛️ Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                cultures = get_available_cultures(data)
                selected_culture = st.selectbox(
                    "🌾 Cultura:",
                    options=['Todas'] + cultures,
                    key="seasonal_culture"
                )
            
            with col2:
                activity_types = ['Todas', 'Plantio', 'Colheita', 'Plantio/Colheita']
                selected_activity = st.selectbox(
                    "� Atividade:",
                    options=activity_types,
                    key="seasonal_activity"
                )
            
            # Preparar dados filtrados
            filtered_data = data.copy()
            
            # Renderizar análise
            create_seasonality_index_chart(filtered_data, "seasonality_monthly_seasonal_subsection")
            
            # Informações adicionais sobre sazonalidade
            st.markdown("""
            ### 📋 Interpretação da Sazonalidade
            - **Alta sazonalidade**: Atividades concentradas em períodos específicos
            - **Baixa sazonalidade**: Atividades distribuídas ao longo do ano
            - **Padrões regionais**: Variações climáticas influenciam a sazonalidade
            """)
                
        except ImportError as e:
            st.error(f"❌ Erro ao carregar componente: {e}")
        except Exception as e:
            st.warning(f"⚠️ Erro ao gerar análise sazonal: {e}")
    
    # Aba 3: Timeline
    with tab3:
        st.markdown("## ⏰ Timeline")
        st.markdown("*Timeline interativa de atividades agrícolas ao longo do ano*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.timeline_charts import create_timeline_activities_chart
            
            # Filtros específicos
            st.markdown("### 🎛️ Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                cultures = get_available_cultures(data)
                selected_culture = st.selectbox(
                    "🌾 Cultura:",
                    options=['Todas'] + cultures,
                    key="timeline_culture"
                )
            
            with col2:
                regions = get_available_regions(data)
                selected_region = st.selectbox(
                    "�️ Região:",
                    options=['Todas'] + regions,
                    key="timeline_region"
                )
            
            # Gerar timeline
            fig = create_timeline_activities_chart(data)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Adicionar informações explicativas
                st.markdown("""
                ### 📋 Como interpretar a timeline
                - 🟢 **Pontos verdes**: Atividades de plantio
                - 🟡 **Pontos amarelos**: Atividades de colheita  
                - 🔵 **Pontos azuis**: Atividades combinadas (plantio/colheita)
                - **Linha**: Tendência temporal das atividades
                - **Interatividade**: Clique nos pontos para detalhes
                """)
            else:
                st.warning("⚠️ Não foi possível gerar a timeline de atividades")
                
        except ImportError as e:
            st.error(f"❌ Erro ao carregar componente: {e}")
        except Exception as e:
            st.warning(f"⚠️ Erro ao gerar timeline: {e}")
    
    # Aba 4: Tendências
    with tab4:
        st.markdown("## 📈 Tendências")
        st.markdown("*Análise de tendências e evolução temporal dos dados CONAB*")
        
        # Subabas para diferentes tipos de tendências
        trend_tab1, trend_tab2, trend_tab3 = st.tabs([
            "📊 Tendências Anuais",
            "🔄 Comparativo Temporal",
            "📈 Projeções"
        ])
        
        with trend_tab1:
            st.markdown("### 📊 Tendências Anuais das Atividades")
            
            try:
                # Usar componentes existentes para análise de tendências
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Cultura:",
                        options=['Todas'] + cultures,
                        key="trends_annual_culture"
                    )
                
                with col2:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "🗺️ Região:",
                        options=['Todas'] + regions,
                        key="trends_annual_region"
                    )
                
                filtered_data = data.copy()
                create_seasonality_index_chart(filtered_data, "seasonality_monthly_seasonal_trends")
                
                st.info("📊 **Análise**: Tendências baseadas em padrões sazonais identificados nos dados CONAB")
                
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar tendências anuais: {e}")
        
        with trend_tab2:
            st.markdown("### 🔄 Comparativo Temporal entre Regiões")
            
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import create_crop_diversity_by_region_chart
                
                filtered_data = data.copy()
                fig = create_crop_diversity_by_region_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                st.info("🔄 **Análise**: Comparação da diversidade de culturas entre diferentes regiões ao longo do tempo")
                
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar comparativo temporal: {e}")
        
        with trend_tab3:
            st.markdown("### 📈 Projeções e Insights")
            
            # Insights baseados nos dados
            st.markdown("""
            #### 🎯 Insights dos Dados CONAB
            
            **📊 Disponibilidade Regional:**
            - Regiões com maior cobertura de dados
            - Estados com calendários mais completos
            - Culturas com melhor mapeamento temporal
            
            **📅 Padrões Sazonais:**
            - Identificação de picos de plantio e colheita
            - Variações regionais nos calendários
            - Sobreposições de atividades agrícolas
            
            **⏰ Evolução Temporal:**
            - Tendências de expansão de culturas
            - Mudanças nos padrões regionais
            - Adaptações climáticas refletidas no calendário
            """)
            
            # Métricas resumo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if data and 'crop_calendar' in data:
                    total_cultures = len(data['crop_calendar'])
                    st.metric("🌾 Total de Culturas", total_cultures)
            
            with col2:
                if data and 'crop_calendar' in data:
                    total_regions = len(get_available_regions(data))
                    st.metric("🗺️ Regiões Cobertas", total_regions)
            
            with col3:
                if data and 'crop_calendar' in data:
                    # Calcular total de estados com dados
                    total_states = 0
                    for crop_data in data['crop_calendar'].values():
                        total_states += len(crop_data)
                    st.metric("🏛️ Estados com Dados", total_states)


def render_spatial_temporal_tab(data):
    """Renderiza aba de distribuição espacial e temporal CONAB"""
    st.markdown("#### 🌍 Spatial & Temporal Distribution")
    st.markdown("**Análise de Distribuição Espacial e Temporal dos Dados CONAB**")
    
    # Carregar dados CONAB
    conab_data = load_conab_data()
    
    if not conab_data:
        st.warning("⚠️ Dados CONAB não disponíveis para análise espacial e temporal")
        return
    
    # Importar e usar a função de plotagem
    try:
        from dashboard.components.agricultural_analysis.charts.calendar.spatial_temporal import (
            plot_conab_spatial_temporal_distribution
        )
        
        # Criar o gráfico
        fig = plot_conab_spatial_temporal_distribution(conab_data)
        
        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar informações adicionais
        st.markdown("---")
        st.markdown("### 📋 Informações do Gráfico")
        
        # Informações sobre os dados
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        if crop_coverage:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_crops = len(crop_coverage)
                st.metric("🌾 Culturas Mapeadas", total_crops)
            
            with col2:
                # Contar estados únicos
                all_states = set()
                for crop_info in crop_coverage.values():
                    regions = crop_info.get("regions", [])
                    all_states.update(regions)
                st.metric("🗺️ Estados/Regiões", len(all_states))
            
            with col3:
                # Calcular período temporal
                all_years = set()
                for crop_info in crop_coverage.values():
                    first_years = crop_info.get("first_crop_years", {})
                    second_years = crop_info.get("second_crop_years", {})
                    
                    for years_list in first_years.values():
                        for year_range in years_list:
                            start_year = int(year_range.split('-')[0])
                            end_year = int(year_range.split('-')[1])
                            all_years.update(range(start_year, end_year + 1))
                    
                    for years_list in second_years.values():
                        for year_range in years_list:
                            start_year = int(year_range.split('-')[0])
                            end_year = int(year_range.split('-')[1])
                            all_years.update(range(start_year, end_year + 1))
                
                if all_years:
                    period = f"{min(all_years)}-{max(all_years)}"
                    st.metric("📅 Período Temporal", period)
                else:
                    st.metric("📅 Período Temporal", "N/A")
        
        # Descrição do gráfico
        st.markdown("""
        **Sobre este gráfico:**
        - Mostra a distribuição espacial (estados/regiões) e temporal (anos) da cobertura CONAB
        - Cada linha representa um estado/região
        - As cores representam diferentes tipos de culturas
        - O comprimento das linhas indica o período de cobertura
        - Brasil (linha inferior) mostra o período geral de cobertura
        """)
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar gráfico espacial e temporal: {str(e)}")
        st.markdown("```python")
        st.markdown(f"Erro: {e}")
        st.markdown("```")


def load_conab_data():
    """Carrega dados CONAB para análise espacial e temporal"""
    try:
        import json
        from pathlib import Path
        
        # Tentar carregar de diferentes fontes
        data_paths = [
            Path("data/json/conab_detailed_initiative.jsonc"),
            Path("data/conab_mapping_data.json"),
            Path("data/conab_agricultural_data.json")
        ]
        
        for path in data_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    # Para arquivos .jsonc, remover comentários simples
                    content = f.read()
                    if path.suffix == '.jsonc':
                        lines = content.split('\n')
                        lines = [line for line in lines if not line.strip().startswith('//')]
                        content = '\n'.join(lines)
                    
                    data = json.loads(content)
                    return data
        
        # Se não encontrar arquivos, retornar dados mockados para demonstração
        return create_mock_conab_data()
        
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar dados CONAB: {e}")
        return create_mock_conab_data()


def create_mock_conab_data():
    """Cria dados mockados para demonstração do gráfico espacial e temporal"""
    return {
        "CONAB Crop Monitoring Initiative": {
            "detailed_crop_coverage": {
                "Soja": {
                    "regions": ["MT", "GO", "PR", "RS", "MS", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "PR": ["2018-2019", "2019-2020", "2020-2021", "2021-2022"],
                        "RS": ["2020-2021", "2021-2022", "2022-2023"],
                        "MS": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2019-2020", "2020-2021", "2021-2022"],
                        "GO": ["2020-2021", "2021-2022", "2022-2023"],
                        "MS": ["2020-2021", "2021-2022"]
                    }
                },
                "Milho": {
                    "regions": ["MT", "GO", "PR", "MG", "SP", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2020-2021", "2021-2022", "2022-2023"],
                        "PR": ["2018-2019", "2019-2020", "2020-2021"],
                        "MG": ["2019-2020", "2020-2021", "2021-2022"],
                        "SP": ["2020-2021", "2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2021-2022", "2022-2023"],
                        "PR": ["2019-2020", "2020-2021"]
                    }
                },
                "Algodão": {
                    "regions": ["MT", "BA", "GO", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2020-2021", "2021-2022", "2022-2023"],
                        "BA": ["2019-2020", "2020-2021", "2021-2022"],
                        "GO": ["2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2021-2022", "2022-2023"],
                        "BA": ["2020-2021", "2021-2022"]
                    }
                }
            }
        }
    }


# Ensure functions are available when imported
__all__ = ['run', 'render_agriculture_overview_page', 'render_crop_calendar_page', 'render_agriculture_availability_page', 'render_conab_availability_analysis_page']


if __name__ == "__main__":
    # Para testes diretos
    st.set_page_config(page_title="Agricultural Analysis Test")
    run()
