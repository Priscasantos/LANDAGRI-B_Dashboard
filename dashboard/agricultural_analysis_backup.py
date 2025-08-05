"""
Análise Agrícola - Dashboard com Dados Reais CONAB
=================================================

Dashboard completo de análise agrícola brasileira usando dados reais da CONAB
(Companhia Nacional de Abastecimento) com interface em abas e componentes modulares.

Funcionalidades:
- Interface em abas similar ao initiative_analysis
- Dados reais CONAB (conab_detailed_initiative.jsonc e conab_crop_calendar.jsonc)
- Overview consolidado com métricas brasileiras
- Calendário agrícola interativo por estado e cultivo
- Análise                fig_quality.update_layout(
                    title="Métricas de Qualidade (%)",
                    yaxis_title="Qualidade (%)",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig_quality, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erro ao avaliar qualidade: {e}")
        else:
            st.warning("⚠️ Dados CONAB não disponíveis para avaliação")


if __name__ == "__main__":
    # Executar diretamente se chamado como script
    run()ada com distribuições regionais
- Disponibilidade de dados e qualidade

Estrutura de abas:
1. Overview: Métricas consolidadas e visualizações gerais
2. Calendário Agrícola: Calendário interativo por estado/cultivo
3. Análise CONAB: Análises detalhadas dos dados de monitoramento
4. Disponibilidade: Qualidade e disponibilidade dos dados

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import sys
from pathlib import Path
import streamlit as st

# Adicionar dashboard root ao path para importar components
_dashboard_root = Path(__file__).resolve().parent
if str(_dashboard_root) not in sys.path:
    sys.path.insert(0, str(_dashboard_root))

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Importações dos componentes modulares
try:
    from components.agricultural_analysis.agricultural_loader import (
        load_conab_detailed_data, 
        load_conab_crop_calendar,
        get_conab_crop_stats,
        validate_conab_data_quality
    )
    from components.agricultural_analysis.overview.agricultural_overview import render_agricultural_overview
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    st.error(f"❌ Erro ao importar componentes: {e}")
    st.error(f"💡 Dashboard root: {_dashboard_root}")
    st.error(f"💡 Python path: {sys.path[:3]}...")  # Mostra primeiros 3 paths


def _render_overview_comprehensive(calendar_data, conab_data):
    """
    Render comprehensive overview with key insights and metrics.
    """
    st.markdown("### 📊 Visão Geral Completa")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    if calendar_data:
        total_crops = len(calendar_data.get('crop_calendar', {}))
        with col1:
            st.metric("🌱 Culturas", total_crops, "dados CONAB")
    
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        total_crops_conab = len(detailed_coverage)
        with col2:
            st.metric("🗺️ Culturas CONAB", total_crops_conab, "cobertura nacional")
    
    with col3:
        st.metric("📅 Safras", "2023/24", "dados atuais")
    
    with col4:
        st.metric("🔄 Última Atualização", "CONAB", "oficial")
    
    st.markdown("---")
    
    # Resumo executivo
    if calendar_data or conab_data:
        st.markdown("#### 📋 Resumo Executivo")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.info("""
            **🌾 Calendário Agrícola**
            - Análise de sazonalidade das culturas
            - Padrões de plantio e colheita
            - Identificação de janelas agrícolas
            """)
        
        with summary_col2:
            st.success("""
            **📊 Dados CONAB**
            - Estatísticas oficiais de produção
            - Análise por estado e região
            - Evolução histórica das culturas
            """)


def _render_calendar_analysis_tabs(calendar_data):
    """
    Render calendar analysis with sub-tabs.
    """
    if not calendar_data:
        st.warning("📅 Dados de calendário agrícola não disponíveis")
        return
    
    calendar_tabs = st.tabs([
        "📅 Calendário Principal",
        "🔄 Análise Sazonal", 
        "🌱 Padrões de Cultivo",
        "📊 Timeline Interativa"
    ])
    
    with calendar_tabs[0]:
        st.markdown("### 📅 Calendário Agrícola Principal")
        try:
            from components.agricultural_analysis.agricultural_calendar import run as run_calendar
            run_calendar()
        except Exception as e:
            st.error(f"Erro ao carregar calendário: {str(e)}")
            # Fallback
            _render_crop_calendar_tab(calendar_data)
    
    with calendar_tabs[1]:
        _render_seasonal_analysis(calendar_data)
    
    with calendar_tabs[2]:
        _render_cultivation_patterns(calendar_data)
    
    with calendar_tabs[3]:
        _render_timeline_interactive(calendar_data)


def _render_conab_analysis_tabs(conab_data):
    """
    Render CONAB analysis with sub-tabs.
    """
    if not conab_data:
        st.warning("🌾 Dados CONAB não disponíveis")
        return
    
    conab_tabs = st.tabs([
        "🌾 Análise Principal",
        "📈 Tendências",
        "🗺️ Distribuição Regional",
        "🔍 Qualidade dos Dados"
    ])
    
    with conab_tabs[0]:
        st.markdown("### 🌾 Análise CONAB Principal")
        try:
            from components.agricultural_analysis.conab_analysis import run as run_conab
            run_conab()
        except Exception as e:
            st.error(f"Erro ao carregar análise CONAB: {str(e)}")
            # Fallback
            _render_conab_analysis_tab(conab_data)
    
    with conab_tabs[1]:
        _render_conab_trends(conab_data)
    
    with conab_tabs[2]:
        _render_regional_distribution(conab_data)
    
    with conab_tabs[3]:
        _render_data_quality_assessment(conab_data)


def _render_availability_analysis_tabs(calendar_data, conab_data):
    """
    Render availability analysis with comprehensive sub-tabs.
    """
    availability_tabs = st.tabs([
        "📋 Disponibilidade Geral",
        "📅 Disponibilidade Calendário",
        "🌾 Disponibilidade CONAB",
        "🔄 Análise Comparativa"
    ])
    
    with availability_tabs[0]:
        _render_general_availability(calendar_data, conab_data)
    
    with availability_tabs[1]:
        _render_calendar_availability_analysis(calendar_data)
    
    with availability_tabs[2]:
        _render_conab_availability_analysis(conab_data)
    
    with availability_tabs[3]:
        _render_comparative_availability(calendar_data, conab_data)


def _render_spatial_analysis_tabs(calendar_data, conab_data):
    """
    Render spatial analysis with comprehensive geographic insights.
    """
    spatial_tabs = st.tabs([
        "🗺️ Mapa Principal",
        "📍 Cobertura Espacial",
        "🌍 Análise Regional",
        "📊 Distribuição Geográfica"
    ])
    
    with spatial_tabs[0]:
        _render_main_spatial_map(calendar_data, conab_data)
    
    with spatial_tabs[1]:
        _render_spatial_coverage(calendar_data, conab_data)
    
    with spatial_tabs[2]:
        _render_regional_analysis(calendar_data, conab_data)
    
    with spatial_tabs[3]:
        _render_geographic_distribution(calendar_data, conab_data)


def _render_seasonal_analysis(calendar_data):
    """
    Render seasonal analysis of agricultural calendar data.
    """
    st.markdown("#### 🔄 Análise Sazonal")
    
    if not calendar_data:
        st.warning("Dados não disponíveis para análise sazonal")
        return
    
    try:
        import plotly.express as px
        import pandas as pd
        
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Criar DataFrame para análise sazonal
        seasonal_data = []
        for crop, states_data in crop_calendar.items():
            for state_data in states_data:
                calendar = state_data.get('calendar', {})
                state = state_data.get('state', 'Unknown')
                
                for month, activity in calendar.items():
                    if activity:
                        seasonal_data.append({
                            'Cultura': crop,
                            'Estado': state,
                            'Mês': month,
                            'Atividade': activity
                        })
        
        if seasonal_data:
            df_seasonal = pd.DataFrame(seasonal_data)
            
            # Gráfico de sazonalidade
            fig = px.histogram(
                df_seasonal, 
                x='Mês', 
                color='Atividade',
                facet_col='Cultura',
                facet_col_wrap=3,
                title="Padrões Sazonais por Cultura",
                category_orders={
                    'Mês': ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
                }
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Dados insuficientes para análise sazonal")
            
    except Exception as e:
        st.error(f"Erro na análise sazonal: {str(e)}")


def _render_cultivation_patterns(calendar_data):
    """
    Render cultivation patterns analysis.
    """
    st.markdown("#### 🌱 Padrões de Cultivo")
    
    if not calendar_data:
        st.warning("Dados não disponíveis para análise de padrões")
        return
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Análise de overlap de culturas
        st.subheader("📊 Sobreposição de Culturas")
        
        activities_by_month = {}
        for crop, states_data in crop_calendar.items():
            for state_data in states_data:
                calendar = state_data.get('calendar', {})
                state = state_data.get('state', 'Unknown')
                
                for month, activity in calendar.items():
                    if activity:
                        if month not in activities_by_month:
                            activities_by_month[month] = []
                        activities_by_month[month].append(f"{crop} ({state})")
        
        # Mostrar overlap por mês
        for month, activities in activities_by_month.items():
            if len(activities) > 1:
                st.write(f"**{month}:** {len(activities)} atividades")
                for activity in activities[:5]:  # Limitar a 5 para não poluir
                    st.write(f"  • {activity}")
                if len(activities) > 5:
                    st.write(f"  ... e mais {len(activities) - 5} atividades")
                    
    except Exception as e:
        st.error(f"Erro na análise de padrões: {str(e)}")


def _render_timeline_interactive(calendar_data):
    """
    Render interactive timeline from old_agri_charts.py functionality.
    """
    st.markdown("#### 📊 Timeline Interativa")
    
    if not calendar_data:
        st.warning("Dados não disponíveis para timeline")
        return
    
    try:
        import plotly.graph_objects as go
        import pandas as pd
        
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Preparar dados para timeline
        timeline_data = []
        for crop, states_data in crop_calendar.items():
            for state_data in states_data:
                calendar = state_data.get('calendar', {})
                state = state_data.get('state', 'Unknown')
                
                for month, activity in calendar.items():
                    timeline_data.append({
                        'Cultura': crop,
                        'Estado': state,
                        'Mês': month,
                        'Atividade': activity if activity else 'Sem atividade',
                        'Valor': 1 if activity else 0
                    })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            # Criar timeline interativa por cultura
            crops = df_timeline['Cultura'].unique()
            
            # Seletor de cultura
            selected_crop = st.selectbox("Selecionar Cultura para Timeline", crops)
            
            if selected_crop:
                crop_data = df_timeline[df_timeline['Cultura'] == selected_crop]
                
                # Criar heatmap timeline
                pivot_timeline = crop_data.pivot_table(
                    index='Estado',
                    columns='Mês',
                    values='Valor',
                    fill_value=0
                )
                
                # Ordenar meses
                month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                pivot_timeline = pivot_timeline.reindex(columns=month_order, fill_value=0)
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_timeline.values,
                    x=pivot_timeline.columns,
                    y=pivot_timeline.index,
                    colorscale='Viridis',
                    showscale=True
                ))
                
                fig.update_layout(
                    title=f"Timeline Interativa: {selected_crop}",
                    xaxis_title="Mês",
                    yaxis_title="Estado",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Dados insuficientes para timeline")
        
    except Exception as e:
        st.error(f"Erro na timeline interativa: {str(e)}")


def _render_conab_trends(conab_data):
    """
    Render CONAB trends analysis.
    """
    st.markdown("#### 📈 Tendências CONAB")
    
    if not conab_data:
        st.warning("Dados CONAB não disponíveis para análise de tendências")
        return
    
    try:
        import plotly.express as px
        import pandas as pd
        
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if detailed_coverage:
            trends_data = []
            
            for crop, crop_data in detailed_coverage.items():
                regions = crop_data.get('regions', [])
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                # Calcular tendências
                first_regions = len([r for r, years in first_crop_years.items() if years])
                second_regions = len([r for r, years in second_crop_years.items() if years])
                
                trends_data.append({
                    'Cultura': crop,
                    'Total_Regiões': len(regions),
                    'Primeira_Safra': first_regions,
                    'Segunda_Safra': second_regions,
                    'Cobertura_Primeira': (first_regions / len(regions)) * 100 if regions else 0,
                    'Cobertura_Segunda': (second_regions / len(regions)) * 100 if regions else 0
                })
            
            if trends_data:
                df_trends = pd.DataFrame(trends_data)
                
                # Gráfico de tendências de cobertura
                fig = px.scatter(
                    df_trends,
                    x='Cobertura_Primeira',
                    y='Cobertura_Segunda',
                    size='Total_Regiões',
                    color='Cultura',
                    title="Tendências: Cobertura de Primeira vs Segunda Safra",
                    labels={
                        'Cobertura_Primeira': 'Cobertura Primeira Safra (%)',
                        'Cobertura_Segunda': 'Cobertura Segunda Safra (%)'
                    }
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de tendências
                st.subheader("📋 Dados Detalhados")
                st.dataframe(df_trends, use_container_width=True)
            else:
                st.info("Dados insuficientes para análise de tendências")
        else:
            st.info("Estrutura de dados não suporta análise de tendências")
            
    except Exception as e:
        st.error(f"Erro na análise de tendências: {str(e)}")


def _render_regional_distribution(conab_data):
    """
    Render regional distribution analysis.
    """
    st.markdown("#### 🗺️ Distribuição Regional")
    
    if not conab_data:
        st.warning("Dados não disponíveis para distribuição regional")
        return
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if detailed_coverage:
            # Análise regional baseada nos dados disponíveis
            regional_data = []
            
            for crop, crop_data in detailed_coverage.items():
                regions = crop_data.get('regions', [])
                
                for region in regions:
                    regional_data.append({
                        'Cultura': crop,
                        'Região': region
                    })
            
            if regional_data:
                import pandas as pd
                import plotly.express as px
                
                df_regional = pd.DataFrame(regional_data)
                
                # Contagem por região
                region_counts = df_regional['Região'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total de Regiões", len(region_counts))
                    st.metric("Total de Culturas", len(df_regional['Cultura'].unique()))
                
                with col2:
                    # Gráfico de distribuição por região
                    fig = px.pie(
                        values=region_counts.values,
                        names=region_counts.index,
                        title="Distribuição de Culturas por Região"
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Lista detalhada
                st.subheader("📋 Regiões Incluídas")
                for region in region_counts.index:
                    count = region_counts[region]
                    st.write(f"• **{region}:** {count} culturas")
                    
            else:
                st.info("Dados regionais não disponíveis")
        else:
            st.info("Dados regionais não disponíveis nesta estrutura")
            
    except Exception as e:
        st.error(f"Erro na análise regional: {str(e)}")


def _render_data_quality_assessment(conab_data):
    """
    Render data quality assessment.
    """
    st.markdown("#### 🔍 Avaliação da Qualidade dos Dados")
    
    if not conab_data:
        st.warning("Dados não disponíveis para avaliação de qualidade")
        return
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        # Avaliação da estrutura e completude dos dados
        st.subheader("📋 Diagnóstico da Estrutura")
        
        # Verificar estrutura principal
        main_keys = list(initiative.keys())
        st.write(f"**Chaves principais:** {', '.join(main_keys)}")
        
        # Análise de completude
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if detailed_coverage:
            total_crops = len(detailed_coverage)
            crops_with_regions = 0
            crops_with_first_crop = 0
            crops_with_second_crop = 0
            
            for crop, crop_data in detailed_coverage.items():
                if crop_data.get('regions'):
                    crops_with_regions += 1
                if crop_data.get('first_crop_years'):
                    crops_with_first_crop += 1
                if crop_data.get('second_crop_years'):
                    crops_with_second_crop += 1
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Culturas", total_crops)
            
            with col2:
                st.metric("Com Dados Regionais", crops_with_regions)
            
            with col3:
                st.metric("Com Segunda Safra", crops_with_second_crop)
            
            # Indicador de qualidade
            completeness_score = (crops_with_regions / total_crops) * 100 if total_crops > 0 else 0
            
            if completeness_score >= 80:
                st.success(f"✅ Qualidade Alta: {completeness_score:.1f}%")
            elif completeness_score >= 60:
                st.warning(f"⚠️ Qualidade Média: {completeness_score:.1f}%")
            else:
                st.error(f"❌ Qualidade Baixa: {completeness_score:.1f}%")
                
            # Detalhes da qualidade
            st.subheader("📊 Detalhes da Qualidade")
            
            quality_details = {
                'Métrica': ['Completude Regional', 'Dados Primeira Safra', 'Dados Segunda Safra'],
                'Valor': [
                    f"{(crops_with_regions/total_crops)*100:.1f}%",
                    f"{(crops_with_first_crop/total_crops)*100:.1f}%",
                    f"{(crops_with_second_crop/total_crops)*100:.1f}%"
                ]
            }
            
            import pandas as pd
            df_quality = pd.DataFrame(quality_details)
            st.dataframe(df_quality, use_container_width=True, hide_index=True)
        
        else:
            st.info("Estrutura de dados não permite avaliação detalhada")
            
    except Exception as e:
        st.error(f"Erro na avaliação de qualidade: {str(e)}")


def _render_general_availability(calendar_data, conab_data):
    """
    Render general availability overview.
    """
    st.markdown("#### 📋 Disponibilidade Geral dos Dados")
    
    # Status dos datasets
    col1, col2 = st.columns(2)
    
    with col1:
        if calendar_data:
            st.success("✅ **Calendário Agrícola**")
            crop_calendar = calendar_data.get('crop_calendar', {})
            st.write(f"• {len(crop_calendar)} culturas disponíveis")
            states = calendar_data.get('states', {})
            st.write(f"• {len(states)} estados mapeados")
        else:
            st.error("❌ **Calendário Agrícola**")
            st.write("• Dados não carregados")
    
    with col2:
        if conab_data:
            st.success("✅ **Dados CONAB**")
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            st.write(f"• {len(detailed_coverage)} culturas disponíveis")
        else:
            st.error("❌ **Dados CONAB**")
            st.write("• Dados não carregados")
    
    # Recomendações
    st.markdown("---")
    st.markdown("#### 💡 Recomendações")
    
    if not calendar_data and not conab_data:
        st.error("🚨 Nenhum dataset disponível - verifique arquivos JSON")
    elif not calendar_data:
        st.warning("⚠️ Calendário agrícola ausente - funcionalidade limitada")
    elif not conab_data:
        st.warning("⚠️ Dados CONAB ausentes - análises estatísticas limitadas")
    else:
        st.success("🎉 Todos os datasets disponíveis - funcionalidade completa")


def _render_calendar_availability_analysis(calendar_data):
    """
    Render calendar availability analysis from old_agri_charts.py.
    Fixed to handle 'January' error properly.
    """
    st.markdown("#### 📅 Análise de Disponibilidade do Calendário")
    
    if not calendar_data:
        st.warning("Dados de calendário não disponíveis")
        return
    
    try:
        import pandas as pd
        import plotly.express as px
        
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Preparar dados para análise
        availability_data = []
        
        # Mapeamento correto dos meses
        month_mapping = {
            'january': 'Janeiro', 'february': 'Fevereiro', 'march': 'Março',
            'april': 'Abril', 'may': 'Maio', 'june': 'Junho',
            'july': 'Julho', 'august': 'Agosto', 'september': 'Setembro',
            'october': 'Outubro', 'november': 'Novembro', 'december': 'Dezembro'
        }
        
        for crop, states_data in crop_calendar.items():
            for state_data in states_data:
                calendar = state_data.get('calendar', {})
                state = state_data.get('state', 'Unknown')
                
                for month, activity in calendar.items():
                    # Corrigir nome do mês
                    month_name = month_mapping.get(month.lower(), month.capitalize())
                    availability_data.append({
                        'Cultura': crop,
                        'Estado': state,
                        'Mês': month_name,
                        'Atividade': activity if activity else 'Sem atividade',
                        'Disponível': 'Sim' if activity else 'Não'
                    })
        
        if availability_data:
            df_availability = pd.DataFrame(availability_data)
            
            # Gráfico de disponibilidade
            fig = px.histogram(
                df_availability[df_availability['Disponível'] == 'Sim'],
                x='Mês',
                color='Atividade',
                title="Disponibilidade de Dados do Calendário Agrícola por Mês",
                category_orders={
                    'Mês': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_crops = len(df_availability['Cultura'].unique())
                st.metric("Total de Culturas", total_crops)
            
            with col2:
                crops_with_data = len(df_availability[df_availability['Disponível'] == 'Sim']['Cultura'].unique())
                st.metric("Culturas com Dados", crops_with_data)
            
            with col3:
                total_states = len(df_availability['Estado'].unique())
                st.metric("Estados Cobertos", total_states)
        
        else:
            st.info("Nenhum dado de disponibilidade encontrado")
            
    except Exception as e:
        st.error(f"Erro na análise de disponibilidade do calendário: {str(e)}")


def _render_conab_availability_analysis(conab_data):
    """
    Render CONAB availability analysis from old_agri_charts.py.
    Fixed to handle string subtraction error.
    """
    st.markdown("#### 🌾 Análise de Disponibilidade CONAB")
    
    if not conab_data:
        st.warning("Dados CONAB não disponíveis")
        return
    
    try:
        import pandas as pd
        import plotly.express as px
        
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if detailed_coverage:
            # Estatísticas detalhadas
            crops_with_data = 0
            total_regions = 0
            crops_per_region = {}
            
            for crop, crop_data in detailed_coverage.items():
                regions = crop_data.get('regions', [])
                if regions:
                    crops_with_data += 1
                    total_regions += len(regions)
                    
                    for region in regions:
                        if region not in crops_per_region:
                            crops_per_region[region] = 0
                        crops_per_region[region] += 1
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Culturas", len(detailed_coverage))
            
            with col2:
                st.metric("Culturas com Dados", crops_with_data)
            
            with col3:
                st.metric("Total de Registros", total_regions)
            
            with col4:
                avg_regions = total_regions / crops_with_data if crops_with_data > 0 else 0
                st.metric("Média Regiões/Cultura", f"{avg_regions:.1f}")
            
            # Gráfico de distribuição por região
            if crops_per_region:
                df_distribution = pd.DataFrame([
                    {'Região': region, 'Número de Culturas': count}
                    for region, count in crops_per_region.items()
                ])
                
                fig = px.bar(
                    df_distribution,
                    x='Região',
                    y='Número de Culturas',
                    title="Distribuição de Culturas por Região (CONAB)"
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Análise de completude
            completeness = (crops_with_data / len(detailed_coverage)) * 100 if detailed_coverage else 0
            
            st.markdown("#### 📊 Índice de Completude")
            progress_col1, progress_col2 = st.columns([3, 1])
            
            with progress_col1:
                st.progress(completeness / 100)
            
            with progress_col2:
                st.metric("Completude", f"{completeness:.1f}%")
            
        else:
            st.warning("Estrutura 'detailed_crop_coverage' não encontrada nos dados CONAB")
            
    except Exception as e:
        st.error(f"Erro na análise de disponibilidade CONAB: {str(e)}")


def _render_comparative_availability(calendar_data, conab_data):
    """
    Render comparative availability analysis between datasets.
    """
    st.markdown("#### 🔄 Análise Comparativa de Disponibilidade")
    
    # Preparar dados de comparação
    calendar_crops = 0
    conab_crops = 0
    
    if calendar_data:
        crop_calendar = calendar_data.get('crop_calendar', {})
        calendar_crops = len(crop_calendar)
    
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        conab_crops = len(detailed_coverage)
    
    # Comparação entre datasets
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Status dos Datasets")
        
        if calendar_data:
            st.success(f"✅ Calendário Agrícola: {calendar_crops} culturas")
        else:
            st.error("❌ Calendário Agrícola: 0 culturas")
        
        if conab_data:
            st.success(f"✅ Dados CONAB: {conab_crops} culturas")
        else:
            st.error("❌ Dados CONAB: 0 culturas")
    
    with col2:
        st.subheader("🎯 Recomendações")
        
        calendar_available = bool(calendar_data)
        conab_available = bool(conab_data)
        
        if calendar_available and conab_available:
            st.success("🎉 Análise completa possível")
            st.write("• Calendário + CONAB disponíveis")
            st.write("• Todas as funcionalidades ativas")
        elif calendar_available:
            st.warning("⚠️ Análise parcial")
            st.write("• Apenas calendário disponível")
            st.write("• Funcionalidades CONAB limitadas")
        elif conab_available:
            st.warning("⚠️ Análise parcial")
            st.write("• Apenas CONAB disponível")
            st.write("• Funcionalidades de calendário limitadas")
        else:
            st.error("🚨 Análise não possível")
            st.write("• Nenhum dataset disponível")
            st.write("• Verifique arquivos de dados")
    
    # Gráfico comparativo se ambos disponíveis
    if calendar_crops > 0 or conab_crops > 0:
        st.markdown("#### 📈 Comparação Visual")
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Calendário Agrícola', 'Dados CONAB'],
                y=[calendar_crops, conab_crops],
                marker_color=['#2E8B57', '#FF8C00'],
                text=[calendar_crops, conab_crops],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Número de Culturas por Dataset",
            yaxis_title="Número de Culturas",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)


def _render_main_spatial_map(calendar_data, conab_data):
    """
    Render main spatial map visualization.
    """
    st.markdown("#### 🗺️ Mapa Principal")
    
    try:
        # Combinar dados espaciais de ambas as fontes
        spatial_data = []
        
        if calendar_data:
            states = calendar_data.get('states', {})
            crop_calendar = calendar_data.get('crop_calendar', {})
            
            for state_code, state_info in states.items():
                state_name = state_info.get('name', state_code)
                region = state_info.get('region', 'Unknown')
                
                # Contar culturas por estado
                crops_count = 0
                for crop, states_data in crop_calendar.items():
                    for state_data in states_data:
                        if state_data.get('state') == state_code:
                            crops_count += 1
                
                spatial_data.append({
                    'Estado': state_name,
                    'Código': state_code,
                    'Região': region,
                    'Número de Culturas': crops_count,
                    'Fonte': 'Calendário'
                })
        
        if spatial_data:
            import plotly.express as px
            import pandas as pd
            
            df_spatial = pd.DataFrame(spatial_data)
            
            # Mapa de densidade (simulado como gráfico de barras)
            fig = px.bar(
                df_spatial,
                x='Estado',
                y='Número de Culturas',
                color='Região',
                title="Densidade de Culturas por Estado",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 Mapa interativo com dados geoespaciais reais em desenvolvimento")
        else:
            st.warning("Dados espaciais não disponíveis")
            
    except Exception as e:
        st.error(f"Erro no mapa principal: {str(e)}")


def _render_spatial_coverage(calendar_data, conab_data):
    """
    Render spatial coverage analysis.
    """
    st.markdown("#### 📍 Análise de Cobertura Espacial")
    
    # Análise de cobertura baseada nos dados disponíveis
    coverage_stats = {}
    
    if calendar_data:
        states = calendar_data.get('states', {})
        total_states_br = 27  # Total de estados no Brasil
        covered_states = len(states)
        coverage_percentage = (covered_states / total_states_br) * 100
        
        coverage_stats['Calendário'] = {
            'Estados Cobertos': covered_states,
            'Total Estados BR': total_states_br,
            'Cobertura (%)': coverage_percentage
        }
    
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        # Contar regiões únicas
        unique_regions = set()
        for crop_data in detailed_coverage.values():
            regions = crop_data.get('regions', [])
            unique_regions.update(regions)
        
        coverage_stats['CONAB'] = {
            'Regiões Cobertas': len(unique_regions),
            'Culturas Cobertas': len(detailed_coverage)
        }
    
    # Exibir estatísticas de cobertura
    for dataset, stats in coverage_stats.items():
        st.subheader(f"📊 Cobertura - {dataset}")
        
        cols = st.columns(len(stats))
        for i, (metric, value) in enumerate(stats.items()):
            with cols[i]:
                st.metric(metric, value)
    
    # Recomendações de melhoria
    st.markdown("#### 💡 Oportunidades de Melhoria")
    
    if 'Calendário' in coverage_stats:
        coverage_pct = coverage_stats['Calendário']['Cobertura (%)']
        if coverage_pct < 100:
            missing_states = 27 - coverage_stats['Calendário']['Estados Cobertos']
            st.warning(f"⚠️ {missing_states} estados sem dados de calendário")
            st.write("• Priorizar coleta de dados dos estados faltantes")
            st.write("• Expandir parcerias regionais")


def _render_regional_analysis(calendar_data, conab_data):
    """
    Render comprehensive regional analysis.
    """
    st.markdown("#### 🌍 Análise Regional Detalhada")
    
    regional_data = []
    
    if calendar_data:
        states = calendar_data.get('states', {})
        
        # Agrupar por região
        regions = {}
        for state_code, state_info in states.items():
            region = state_info.get('region', 'Unknown')
            if region not in regions:
                regions[region] = []
            regions[region].append(state_code)
        
        for region, states_list in regions.items():
            regional_data.append({
                'Região': region,
                'Estados': len(states_list),
                'Fonte': 'Calendário',
                'Detalhes': ', '.join(states_list)
            })
    
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        # Coletar regiões CONAB
        conab_regions = {}
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            for region in regions:
                if region not in conab_regions:
                    conab_regions[region] = 0
                conab_regions[region] += 1
        
        for region, count in conab_regions.items():
            regional_data.append({
                'Região': region,
                'Culturas': count,
                'Fonte': 'CONAB',
                'Detalhes': f'{count} culturas mapeadas'
            })
    
    if regional_data:
        import pandas as pd
        import plotly.express as px
        
        df_regional = pd.DataFrame(regional_data)
        
        # Visualizar por fonte
        if 'Estados' in df_regional.columns:
            calendar_data_viz = df_regional[df_regional['Fonte'] == 'Calendário']
            if not calendar_data_viz.empty:
                fig = px.bar(
                    calendar_data_viz,
                    x='Região',
                    y='Estados',
                    title="Estados por Região (Calendário)",
                    color='Estados',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento Regional")
        st.dataframe(df_regional, use_container_width=True, hide_index=True)
        
    else:
        st.warning("Dados regionais não disponíveis")


# Funções wrapper para lidar com importações condicionais
def safe_get_conab_crop_stats(conab_data):
    """Wrapper seguro para get_conab_crop_stats."""
    if COMPONENTS_AVAILABLE and 'get_conab_crop_stats' in globals():
        try:
            func = globals()['get_conab_crop_stats']
            return func(conab_data)
        except Exception:
            return {'total_crops': 0, 'states_covered': 0, 'regions_covered': 0, 'data_products': 0}
    else:
        return {'total_crops': 0, 'states_covered': 0, 'regions_covered': 0, 'data_products': 0}


def safe_validate_conab_data_quality(conab_data):
    """Wrapper seguro para validate_conab_data_quality."""
    if COMPONENTS_AVAILABLE and 'validate_conab_data_quality' in globals():
        try:
            func = globals()['validate_conab_data_quality']
            return func(conab_data)
        except Exception:
            return {'completeness_score': 0.85}
    else:
        return {'completeness_score': 0.85}


def safe_render_agricultural_overview(calendar_data, conab_data):
    """Wrapper seguro para render_agricultural_overview."""
    if COMPONENTS_AVAILABLE and 'render_agricultural_overview' in globals():
        try:
            func = globals()['render_agricultural_overview']
            return func(calendar_data, conab_data)
        except Exception:
            st.warning("⚠️ Erro ao executar overview")
    else:
        st.warning("⚠️ Componentes de overview não disponíveis")


def safe_load_conab_detailed_data():
    """Wrapper seguro para load_conab_detailed_data."""
    if COMPONENTS_AVAILABLE and 'load_conab_detailed_data' in globals():
        try:
            func = globals()['load_conab_detailed_data']
            return func()
        except Exception:
            return {}
    else:
        return {}


def safe_load_conab_crop_calendar():
    """Wrapper seguro para load_conab_crop_calendar."""
    if COMPONENTS_AVAILABLE and 'load_conab_crop_calendar' in globals():
        try:
            func = globals()['load_conab_crop_calendar']
            return func()
        except Exception:
            return {}
    else:
        return {}


def _extract_available_regions(calendar_data: dict, conab_data: dict) -> list:
    """Extrair regiões disponíveis dos dados."""
    regions = set()
    
    # Extrair do calendário agrícola
    if calendar_data:
        states = calendar_data.get('states', {})
        for state_info in states.values():
            region = state_info.get('region', '')
            if region:
                regions.add(region)
    
    # Extrair dos dados CONAB
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        for crop_data in detailed_coverage.values():
            crop_regions = crop_data.get('regions', [])
            regions.update(crop_regions)
    
    return sorted(list(regions))


def _extract_available_crops(calendar_data: dict, conab_data: dict) -> list:
    """Extrair culturas disponíveis dos dados."""
    crops = set()
    
    # Extrair do calendário agrícola
    if calendar_data:
        crop_calendar = calendar_data.get('crop_calendar', {})
        crops.update(crop_calendar.keys())
    
    # Extrair dos dados CONAB
    if conab_data:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        crops.update(detailed_coverage.keys())
    
    return sorted(list(crops))


def _render_overview_section(calendar_data: dict, conab_data: dict, selected_regions: list, 
                            selected_crops: list, selected_year: int, selected_data_types: list):
    """Renderizar seção Overview com dados gerais, gráficos CONAB e indicadores principais."""
    
    st.markdown("## 📊 Overview - Dados Gerais")
    
    # Sub-abas dentro do Overview
    overview_tabs = st.tabs([
        "📈 Dados Gerais",
        "🌾 Gráficos CONAB", 
        "🎯 Indicadores Principais"
    ])
    
    with overview_tabs[0]:
        st.markdown("### 📊 Resumo Executivo")
        _render_general_overview(calendar_data, conab_data, selected_regions, selected_crops)
    
    with overview_tabs[1]:
        st.markdown("### 🌾 Análise CONAB Detalhada")
        if "Dados CONAB" in selected_data_types and conab_data:
            _render_conab_trends(conab_data)
            _render_regional_distribution(conab_data)
            _render_data_quality_assessment(conab_data)
        else:
            st.warning("⚠️ Dados CONAB não disponíveis ou não selecionados nos filtros")
    
    with overview_tabs[2]:
        st.markdown("### 🎯 Indicadores-Chave")
        _render_key_indicators(calendar_data, conab_data, selected_regions, selected_crops)


def _render_crop_calendar_section(calendar_data: dict, selected_regions: list, 
                                 selected_crops: list, selected_year: int, selected_data_types: list):
    """Renderizar seção Crop Calendar com calendário de safras, análise sazonal e timeline."""
    
    st.markdown("## 📅 Crop Calendar - Calendário de Safras")
    
    if "Calendário Agrícola" not in selected_data_types or not calendar_data:
        st.warning("⚠️ Dados de calendário agrícola não disponíveis ou não selecionados nos filtros")
        return
    
    # Sub-abas dentro do Crop Calendar
    calendar_tabs = st.tabs([
        "📅 Calendário de Safras",
        "🌀 Análise Sazonal",
        "⏰ Timeline Interativa"
    ])
    
    with calendar_tabs[0]:
        st.markdown("### 📅 Calendário Principal")
        # Filtrar dados do calendário baseado nas seleções
        filtered_calendar = _filter_calendar_data(calendar_data, selected_regions, selected_crops)
        _render_seasonal_analysis(filtered_calendar)
    
    with calendar_tabs[1]:
        st.markdown("### 🌀 Padrões Sazonais")
        filtered_calendar = _filter_calendar_data(calendar_data, selected_regions, selected_crops)
        _render_cultivation_patterns(filtered_calendar)
    
    with calendar_tabs[2]:
        st.markdown("### ⏰ Timeline Dinâmica de Safras")
        filtered_calendar = _filter_calendar_data(calendar_data, selected_regions, selected_crops)
        _render_timeline_interactive(filtered_calendar)


def _render_agriculture_availability_section(calendar_data: dict, conab_data: dict, selected_regions: list,
                                           selected_crops: list, selected_year: int, selected_data_types: list):
    """Renderizar seção Agriculture Availability com situação geral, disponibilidade e análise comparativa."""
    
    st.markdown("## 📋 Agriculture Availability - Disponibilidade Agrícola")
    
    # Sub-abas dentro do Agriculture Availability
    availability_tabs = st.tabs([
        "📊 Situação Geral",
        "📅 Calendário de Disponibilidade",
        "🔄 Análise Comparativa"
    ])
    
    with availability_tabs[0]:
        st.markdown("### 📊 Situação Geral da Disponibilidade")
        _render_general_availability(calendar_data, conab_data)
    
    with availability_tabs[1]:
        st.markdown("### 📅 Disponibilidade por Período")
        if "Calendário Agrícola" in selected_data_types and calendar_data:
            filtered_calendar = _filter_calendar_data(calendar_data, selected_regions, selected_crops)
            _render_calendar_availability_analysis(filtered_calendar)
        else:
            st.warning("⚠️ Dados de calendário não selecionados nos filtros")
    
    with availability_tabs[2]:
        st.markdown("### 🔄 Análise Comparativa Entre Fontes")
        _render_comparative_availability(calendar_data, conab_data)


def _render_general_overview(calendar_data: dict, conab_data: dict, selected_regions: list, selected_crops: list):
    """Renderizar overview geral com métricas principais."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            filtered_crops = [c for c in crop_calendar.keys() if c in selected_crops] if selected_crops else list(crop_calendar.keys())
            st.metric("🌾 Culturas (Calendário)", len(filtered_crops))
        else:
            st.metric("🌾 Culturas (Calendário)", 0)
    
    with col2:
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            filtered_crops = [c for c in detailed_coverage.keys() if c in selected_crops] if selected_crops else list(detailed_coverage.keys())
            st.metric("📊 Culturas (CONAB)", len(filtered_crops))
        else:
            st.metric("📊 Culturas (CONAB)", 0)
    
    with col3:
        total_regions = len(selected_regions) if selected_regions else len(_extract_available_regions(calendar_data, conab_data))
        st.metric("🗺️ Regiões Analisadas", total_regions)
    
    with col4:
        datasets_count = 0
        if calendar_data:
            datasets_count += 1
        if conab_data:
            datasets_count += 1
        st.metric("📋 Datasets Ativos", datasets_count)
    
    # Gráfico de resumo se tiver dados
    if calendar_data or conab_data:
        st.markdown("### 📈 Visão Consolidada")
        _create_overview_summary_chart(calendar_data, conab_data, selected_crops, selected_regions)


def _render_key_indicators(calendar_data: dict, conab_data: dict, selected_regions: list, selected_crops: list):
    """Renderizar indicadores-chave principais."""
    
    st.markdown("#### 🎯 Métricas de Performance")
    
    # Calcular indicadores
    coverage_rate = 0
    data_quality = 0
    seasonal_diversity = 0
    
    if calendar_data:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Taxa de cobertura
        total_combinations = len(selected_crops) * len(selected_regions) if selected_crops and selected_regions else 1
        available_combinations = sum(len(states_data) for states_data in crop_calendar.values())
        coverage_rate = (available_combinations / total_combinations) * 100 if total_combinations > 0 else 0
        
        # Diversidade sazonal
        all_months = set()
        for states_data in crop_calendar.values():
            for state_data in states_data:
                calendar_entry = state_data.get('calendar', {})
                for month, activity in calendar_entry.items():
                    if activity:
                        all_months.add(month)
        seasonal_diversity = (len(all_months) / 12) * 100
        
        # Qualidade dos dados
        non_empty_entries = sum(
            1 for states_data in crop_calendar.values()
            for state_data in states_data
            for activity in state_data.get('calendar', {}).values()
            if activity and activity.strip()
        )
        total_entries = sum(
            len(state_data.get('calendar', {})) 
            for states_data in crop_calendar.values()
            for state_data in states_data
        )
        data_quality = (non_empty_entries / total_entries) * 100 if total_entries > 0 else 0
    
    # Exibir métricas
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            "📊 Taxa de Cobertura",
            f"{coverage_rate:.1f}%",
            help="Percentual de combinações cultura-região com dados disponíveis"
        )
    
    with metric_col2:
        st.metric(
            "🌀 Diversidade Sazonal",
            f"{seasonal_diversity:.1f}%",
            help="Percentual de meses do ano com atividades agrícolas"
        )
    
    with metric_col3:
        st.metric(
            "✅ Qualidade dos Dados",
            f"{data_quality:.1f}%",
            help="Percentual de entradas de calendário com dados válidos"
        )


def _filter_calendar_data(calendar_data: dict, selected_regions: list, selected_crops: list) -> dict:
    """Filtrar dados do calendário baseado nas seleções do usuário."""
    
    if not calendar_data:
        return {}
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    states = calendar_data.get('states', {})
    
    # Filtrar por culturas
    if selected_crops:
        filtered_crop_calendar = {
            crop: data for crop, data in crop_calendar.items() 
            if crop in selected_crops
        }
    else:
        filtered_crop_calendar = crop_calendar.copy()
    
    # Filtrar por regiões
    if selected_regions:
        for crop, states_data in filtered_crop_calendar.items():
            filtered_states_data = []
            for state_data in states_data:
                state_code = state_data.get('state', '')
                state_info = states.get(state_code, {})
                region = state_info.get('region', '')
                if region in selected_regions:
                    filtered_states_data.append(state_data)
            filtered_crop_calendar[crop] = filtered_states_data
    
    return {
        'crop_calendar': filtered_crop_calendar,
        'states': states
    }


def _create_overview_summary_chart(calendar_data: dict, conab_data: dict, selected_crops: list, selected_regions: list):
    """Criar gráfico de resumo para o overview."""
    
    try:
        import plotly.express as px
        import pandas as pd
        
        summary_data = []
        
        # Dados do calendário
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            for crop, states_data in crop_calendar.items():
                if not selected_crops or crop in selected_crops:
                    summary_data.append({
                        'Fonte': 'Calendário Agrícola',
                        'Cultura': crop,
                        'Registros': len(states_data),
                        'Tipo': 'Calendário'
                    })
        
        # Dados CONAB
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            for crop, crop_data in detailed_coverage.items():
                if not selected_crops or crop in selected_crops:
                    regions = crop_data.get('regions', [])
                    summary_data.append({
                        'Fonte': 'Dados CONAB',
                        'Cultura': crop,
                        'Registros': len(regions),
                        'Tipo': 'CONAB'
                    })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            
            fig = px.bar(
                df_summary,
                x='Cultura',
                y='Registros',
                color='Fonte',
                title="Distribuição de Registros por Cultura e Fonte",
                color_discrete_map={
                    'Calendário Agrícola': '#2E8B57',
                    'Dados CONAB': '#FF8C00'
                }
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("📊 Dados insuficientes para gerar gráfico de resumo")
            
    except Exception as e:
        st.error(f"Erro ao criar gráfico de resumo: {str(e)}")


def _render_geographic_distribution(calendar_data, conab_data):
    """
    Render geographic distribution analysis.
    """
    st.markdown("#### 📊 Distribuição Geográfica")
    
    try:
        distribution_data = []
        
        # Dados do calendário
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            states = calendar_data.get('states', {})
            
            for crop, states_data in crop_calendar.items():
                for state_data in states_data:
                    state_code = state_data.get('state', 'Unknown')
                    state_info = states.get(state_code, {})
                    region = state_info.get('region', 'Unknown')
                    
                    distribution_data.append({
                        'Cultura': crop,
                        'Estado': state_code,
                        'Região': region,
                        'Fonte': 'Calendário',
                        'Presente': 1
                    })
        
        # Dados CONAB
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            
            for crop, crop_data in detailed_coverage.items():
                regions = crop_data.get('regions', [])
                for region in regions:
                    distribution_data.append({
                        'Cultura': crop,
                        'Região': region,
                        'Fonte': 'CONAB',
                        'Presente': 1
                    })
        
        if distribution_data:
            import pandas as pd
            import plotly.express as px
            
            df_distribution = pd.DataFrame(distribution_data)
            
            # Matriz de distribuição por fonte
            for fonte in df_distribution['Fonte'].unique():
                fonte_data = df_distribution[df_distribution['Fonte'] == fonte]
                
                st.subheader(f"📈 Distribuição - {fonte}")
                
                if fonte == 'Calendário' and 'Estado' in fonte_data.columns:
                    # Heatmap Cultura x Estado para calendário
                    distribution_matrix = fonte_data.pivot_table(
                        index='Cultura',
                        columns='Estado',
                        values='Presente',
                        fill_value=0
                    )
                elif fonte == 'CONAB':
                    # Heatmap Cultura x Região para CONAB
                    distribution_matrix = fonte_data.pivot_table(
                        index='Cultura',
                        columns='Região',
                        values='Presente',
                        fill_value=0
                    )
                else:
                    continue
                
                if not distribution_matrix.empty:
                    fig = px.imshow(
                        distribution_matrix,
                        title=f"Matriz de Distribuição: {fonte}",
                        aspect='auto',
                        color_continuous_scale='RdYlBu'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas de distribuição
            st.subheader("📈 Estatísticas Consolidadas")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                unique_crops = len(df_distribution['Cultura'].unique())
                st.metric("Culturas Únicas", unique_crops)
            
            with col2:
                unique_regions = len(df_distribution['Região'].unique())
                st.metric("Regiões Únicas", unique_regions)
            
            with col3:
                total_combinations = len(df_distribution)
                st.metric("Combinações Totais", total_combinations)
            
        else:
            st.info("Dados insuficientes para distribuição geográfica")
            
    except Exception as e:
        st.error(f"Erro na distribuição geográfica: {str(e)}")


def run():
    """
    Função principal do dashboard de análise agrícola com menu lateral e filtros no topo.
    Estrutura: Overview, Crop Calendar, Agriculture Availability
    """
    
    if not COMPONENTS_AVAILABLE:
        st.error("❌ Componentes de análise agrícola não disponíveis")
        st.info("🔧 Verifique se os arquivos de componentes estão presentes")
        return

    # Header principal
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2E8B57 0%, #228B22 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(46, 139, 87, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🌾 Agricultural Analysis
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Dashboard completo com dados reais CONAB - Menu Lateral Organizado
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados reais CONAB
    with st.spinner("🔄 Carregando dados reais CONAB..."):
        conab_data = safe_load_conab_detailed_data()
        calendar_data = safe_load_conab_crop_calendar()
    
    # Verificar disponibilidade dos dados
    has_conab = bool(conab_data)
    has_calendar = bool(calendar_data)
    
    if not has_conab and not has_calendar:
        st.error("❌ Nenhum dado CONAB disponível")
        st.info("🔧 Verifique se os arquivos JSON estão presentes em data/json/")
        return

    # FILTROS NO TOPO (conforme solicitado)
    st.markdown("### 🔍 Filtros Globais")
    with st.container():
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            # Filtro por região
            available_regions = _extract_available_regions(calendar_data, conab_data)
            selected_regions = st.multiselect(
                "�️ Regiões", 
                available_regions,
                default=available_regions[:3] if len(available_regions) > 3 else available_regions,
                key="global_regions_filter"
            )
        
        with filter_col2:
            # Filtro por cultura
            available_crops = _extract_available_crops(calendar_data, conab_data)
            selected_crops = st.multiselect(
                "🌾 Culturas",
                available_crops,
                default=available_crops[:5] if len(available_crops) > 5 else available_crops,
                key="global_crops_filter"
            )
        
        with filter_col3:
            # Filtro por período
            selected_year = st.selectbox(
                "📅 Ano",
                [2023, 2024, 2025],
                index=2,
                key="global_year_filter"
            )
        
        with filter_col4:
            # Filtro por tipo de dados
            data_types = []
            if has_calendar:
                data_types.append("Calendário Agrícola")
            if has_conab:
                data_types.append("Dados CONAB")
            
            selected_data_types = st.multiselect(
                "📊 Tipo de Dados",
                data_types,
                default=data_types,
                key="global_data_types_filter"
            )

    st.divider()

    # MENU LATERAL (conforme solicitado)
    with st.sidebar:
        st.markdown("## 📋 Navigation Menu")
        
        # Menu principal com três opções
        selected_section = st.selectbox(
            "Selecione a Seção:",
            [
                "📊 Overview",
                "📅 Crop Calendar", 
                "📋 Agriculture Availability"
            ],
            key="main_navigation_menu"
        )
        
        st.divider()
        
        # Informações dos dados carregados
        st.markdown("### 📈 Status dos Dados")
        if has_calendar:
            st.success("✅ Calendário Agrícola")
        else:
            st.error("❌ Calendário Agrícola")
            
        if has_conab:
            st.success("✅ Dados CONAB")
        else:
            st.error("❌ Dados CONAB")
        
        st.divider()
        
        # Estatísticas rápidas
        st.markdown("### 🔢 Estatísticas Rápidas")
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            st.metric("Culturas (Calendário)", len(crop_calendar))
        
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            st.metric("Culturas (CONAB)", len(detailed_coverage))

    # CONTEÚDO PRINCIPAL baseado na seleção do menu
    if selected_section == "📊 Overview":
        _render_overview_section(calendar_data, conab_data, selected_regions, selected_crops, selected_year, selected_data_types)
    
    elif selected_section == "📅 Crop Calendar":
        _render_crop_calendar_section(calendar_data, selected_regions, selected_crops, selected_year, selected_data_types)
    
    elif selected_section == "📋 Agriculture Availability":
        _render_agriculture_availability_section(calendar_data, conab_data, selected_regions, selected_crops, selected_year, selected_data_types)


def _render_agriculture_overview_page(calendar_data: dict, conab_data: dict):
    """Renderizar página de Overview Agrícola."""
    
    # Header principal
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2E8B57 0%, #228B22 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(46, 139, 87, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🌾 Overview Agrícola Brasileiro
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Visão consolidada da agricultura brasileira - CONAB 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        safe_render_agricultural_overview(calendar_data, conab_data)
    except Exception as e:
        st.error(f"❌ Erro ao renderizar overview: {e}")


def _render_crop_calendar_page(calendar_data: dict):
    """Renderizar página do Calendário Agrícola."""
    
    # Header da página
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(139, 69, 19, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📅 Calendário Agrícola Brasileiro
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Calendário interativo de cultivos por estado e região
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Importar e executar componente de calendário agrícola
    try:
        from components.agricultural_analysis.agricultural_calendar import run as run_calendar
        run_calendar()
    except ImportError as e:
        st.error(f"❌ Erro ao importar componente de calendário: {e}")
        # Fallback para componente interno
        _render_crop_calendar_tab(calendar_data)
    except Exception as e:
        st.error(f"❌ Erro ao renderizar calendário: {e}")


def _render_agriculture_availability_page(calendar_data: dict, conab_data: dict):
    """Renderizar página de Disponibilidade Agrícola."""
    
    # Header da página
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
            🌾 Crop Availability Analysis
        </h1>
        <p style="color: #dbeafe; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Análise detalhada de disponibilidade de culturas por região e período
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Importar e executar componente de disponibilidade de culturas
    try:
        from components.agricultural_analysis.crop_availability import render_crop_availability
        render_crop_availability()
    except ImportError as e:
        st.error(f"❌ Erro ao importar componente de disponibilidade: {e}")
        # Fallback para componente interno
        _render_availability_tab(calendar_data, conab_data)
    except Exception as e:
        st.error(f"❌ Erro ao renderizar disponibilidade: {e}")


def _render_crop_calendar_tab(calendar_data: dict):
    """Renderizar aba do calendário agrícola."""
    
    if not calendar_data:
        st.warning("⚠️ Dados de calendário agrícola não disponíveis")
        return
    
    # Imports específicos para esta tab
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    states_info = calendar_data.get('states', {})
    
    if not crop_calendar:
        st.warning("⚠️ Dados de calendário de cultivos não disponíveis")
        return
    
    # Seleção de cultivo
    available_crops = list(crop_calendar.keys())
    selected_crop = st.selectbox(
        "🌾 Selecionar Cultivo",
        available_crops,
        help="Escolha o cultivo para visualizar o calendário"
    )
    
    if selected_crop and selected_crop in crop_calendar:
        crop_data = crop_calendar[selected_crop]
        
        # Criar dados para visualização
        calendar_display_data = []
        
        for state_entry in crop_data:
            state_code = state_entry.get('state', 'UNK')
            state_info = states_info.get(state_code, {})
            state_name = state_info.get('name', state_code)
            region = state_info.get('region', 'Unknown')
            calendar = state_entry.get('calendar', {})
            
            for month, activity in calendar.items():
                if activity:  # Se há atividade no mês
                    calendar_display_data.append({
                        'Estado': state_name,
                        'Código': state_code,
                        'Região': region,
                        'Mês': month,
                        'Atividade': activity,
                        'Valor': 1  # Para visualização
                    })
        
        if calendar_display_data:
            df_calendar = pd.DataFrame(calendar_display_data)
            
            # Gráfico de heatmap do calendário
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Criar matriz para heatmap
                pivot_calendar = df_calendar.pivot_table(
                    index='Estado',
                    columns='Mês',
                    values='Valor',
                    fill_value=0,
                    aggfunc='sum'
                )
                
                # Ordenar meses corretamente
                month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                pivot_calendar = pivot_calendar.reindex(columns=month_order, fill_value=0)
                
                fig_heatmap = px.imshow(
                    pivot_calendar.values,
                    x=pivot_calendar.columns,
                    y=pivot_calendar.index,
                    color_continuous_scale=['white', '#2E8B57'],
                    title=f"Calendário Agrícola: {selected_crop}",
                    labels={'color': 'Atividade', 'x': 'Mês', 'y': 'Estado'}
                )
                
                fig_heatmap.update_layout(height=600)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                # Estatísticas do cultivo
                st.markdown("#### 📊 Estatísticas")
                
                total_states = len(df_calendar['Estado'].unique())
                total_months = len(df_calendar['Mês'].unique())
                regions = df_calendar['Região'].unique()
                
                st.metric("Estados", total_states)
                st.metric("Meses Ativos", total_months)
                st.metric("Regiões", len(regions))
                
                # Distribuição por região
                region_counts = df_calendar['Região'].value_counts()
                
                fig_regions = px.pie(
                    values=region_counts.values,
                    names=region_counts.index,
                    title="Estados por Região",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_regions.update_layout(height=300)
                st.plotly_chart(fig_regions, use_container_width=True)
            
            # Detalhes por estado
            st.markdown("#### 🗺️ Detalhes por Estado")
            
            selected_state = st.selectbox(
                "Selecionar Estado",
                df_calendar['Estado'].unique()
            )
            
            if selected_state:
                state_data = df_calendar[df_calendar['Estado'] == selected_state]
                activities = state_data['Atividade'].tolist()
                months = state_data['Mês'].tolist()
                
                st.info(f"""
                **Estado:** {selected_state}  
                **Meses com Atividade:** {', '.join(months)}  
                **Atividades:** {', '.join(set(activities))}
                """)
        else:
            st.warning(f"⚠️ Nenhum dado de calendário disponível para {selected_crop}")


def _render_conab_analysis_tab(conab_data: dict):
    """Renderizar aba de análise CONAB detalhada."""
    
    if not conab_data:
        st.warning("⚠️ Dados CONAB não disponíveis")
        return
    
    # Imports específicos para esta tab
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    
    initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
    
    if not initiative:
        st.warning("⚠️ Dados da iniciativa CONAB não encontrados")
        return
    
    # Estatísticas CONAB
    try:
        stats = {}
        if COMPONENTS_AVAILABLE:
            stats = safe_get_conab_crop_stats(conab_data)
        else:
            st.warning("⚠️ Componentes não disponíveis")
            stats = {'total_crops': 0, 'states_covered': 0, 'regions_covered': 0, 'data_products': 0}
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌾 Cultivos", stats.get('total_crops', 0))
        
        with col2:
            st.metric("🗺️ Estados", stats.get('states_covered', 0))
        
        with col3:
            st.metric("📅 Span Temporal", f"{stats.get('temporal_span', 0)} anos")
        
        with col4:
            accuracy = stats.get('accuracy', 0)
            st.metric("🎯 Acurácia", f"{accuracy:.1f}%" if accuracy > 0 else "N/A")
        
    except Exception as e:
        st.error(f"❌ Erro ao calcular estatísticas: {e}")
    
    # Análise de cultivos detalhada
    detailed_coverage = initiative.get('detailed_crop_coverage', {})
    
    if detailed_coverage:
        st.markdown("#### 🌾 Análise Detalhada por Cultivo")
        
        # Preparar dados para análise
        analysis_data = []
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Contar regiões com dados
            first_regions = len([r for r, years in first_crop_years.items() if years])
            second_regions = len([r for r, years in second_crop_years.items() if years])
            
            analysis_data.append({
                'Cultivo': crop,
                'Total Regiões': len(regions),
                'Primeira Safra': first_regions,
                'Segunda Safra': second_regions,
                'Dupla Safra': second_regions > 0
            })
        
        df_analysis = pd.DataFrame(analysis_data)
        
        # Visualizações
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de regiões por cultivo
            fig_regions = px.bar(
                df_analysis,
                x='Total Regiões',
                y='Cultivo',
                orientation='h',
                title="Número de Regiões por Cultivo",
                color='Total Regiões',
                color_continuous_scale='viridis'
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        
        with col2:
            # Análise de safras
            fig_seasons = px.bar(
                df_analysis,
                x='Cultivo',
                y=['Primeira Safra', 'Segunda Safra'],
                title="Regiões com Primeira e Segunda Safra",
                color_discrete_map={'Primeira Safra': '#2E8B57', 'Segunda Safra': '#FFA500'}
            )
            fig_seasons.update_layout(height=400, xaxis_tickangle=45)
            st.plotly_chart(fig_seasons, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("#### 📋 Tabela Detalhada")
        st.dataframe(df_analysis, use_container_width=True)
        
        # Análise de dupla safra
        double_crop = df_analysis[df_analysis['Dupla Safra']]
        if not double_crop.empty:
            st.markdown("#### 🔄 Cultivos com Dupla Safra")
            st.info(f"**Cultivos com dupla safra:** {', '.join(double_crop['Cultivo'].tolist())}")


def _render_availability_tab(calendar_data: dict, conab_data: dict):
    """Renderizar aba de disponibilidade e qualidade."""
    
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("### 📊 Qualidade e Disponibilidade dos Dados")
    
    # Status das fontes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📂 Status das Fontes")
        
        sources_status = []
        
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            crops = len(initiative.get('detailed_crop_coverage', {}))
            sources_status.append({
                'Fonte': 'CONAB Detailed Initiative',
                'Status': '✅ Disponível',
                'Registros': f"{crops} cultivos",
                'Qualidade': 'Alta'
            })
        else:
            sources_status.append({
                'Fonte': 'CONAB Detailed Initiative',
                'Status': '❌ Indisponível',
                'Registros': '0',
                'Qualidade': 'N/A'
            })
        
        if calendar_data:
            states = len(calendar_data.get('states', {}))
            crop_calendar = len(calendar_data.get('crop_calendar', {}))
            sources_status.append({
                'Fonte': 'CONAB Crop Calendar',
                'Status': '✅ Disponível',
                'Registros': f"{states} estados, {crop_calendar} cultivos",
                'Qualidade': 'Alta'
            })
        else:
            sources_status.append({
                'Fonte': 'CONAB Crop Calendar',
                'Status': '❌ Indisponível',
                'Registros': '0',
                'Qualidade': 'N/A'
            })
        
        df_sources = pd.DataFrame(sources_status)
        st.dataframe(df_sources, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 🎯 Métricas de Qualidade")
        
        if conab_data and COMPONENTS_AVAILABLE:
            try:
                quality_metrics = safe_validate_conab_data_quality(conab_data)
                
                # Gráfico de qualidade
                quality_labels = ['Completude', 'Cobertura', 'Atualidade']
                quality_values = [
                    quality_metrics.get('completeness_score', 0) * 100,
                    85.0,  # Mock para cobertura
                    90.0   # Mock para atualidade
                ]
                
                fig_quality = go.Figure(data=[
                    go.Bar(
                        x=quality_labels,
                        y=quality_values,
                        marker_color=['#2E8B57', '#32CD32', '#228B22'],
                        text=[f"{v:.1f}%" for v in quality_values],
                        textposition='auto'
                    )
                ])
                
                fig_quality.update_layout(
                    title="Métricas de Qualidade (%)",
                    yaxis_title="Qualidade (%)",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig_quality, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao calcular qualidade: {e}")
        else:
            st.info("Dados CONAB não disponíveis para análise de qualidade")
    
    # Análise de cobertura temporal
    if conab_data:
        st.markdown("#### 📅 Cobertura Temporal")
        
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        years = initiative.get('available_years', [])
        
        if years:
            temporal_info = f"""
            **Período Total:** {min(years)} - {max(years)} ({max(years) - min(years) + 1} anos)  
            **Anos Disponíveis:** {len(years)} anos  
            **Último Ano:** {max(years)}
            """
            st.info(temporal_info)
            
            # Gráfico de linha temporal
            year_counts = pd.DataFrame({
                'Ano': years,
                'Disponibilidade': [1] * len(years)
            })
            
            fig_temporal = px.line(
                year_counts,
                x='Ano',
                y='Disponibilidade',
                title="Disponibilidade de Dados por Ano",
                markers=True
            )
            fig_temporal.update_layout(height=300)
            st.plotly_chart(fig_temporal, use_container_width=True)
