"""
Análise Agrícola - Dashboard com Dados Reais CONAB
=================================================

Dashboard completo de análise agrícola brasileira usando dados reais da CONAB
(Companhia Nacional de Abastecimento) integrado ao sistema de menu do app principal.

Funcionalidades:
- Integração com menu lateral do app.py (Agriculture Overview, Crop Calendar, Agriculture Availability)
- Dados reais CONAB (conab_detailed_initiative.jsonc e conab_crop_calendar.jsonc)
- Overview consolidado com métricas brasileiras
- Calendário agrícola interativo por estado e cultivo
- Análise de disponibilidade e qualidade dos dados

Estrutura seguindo app.py:
- Agriculture Overview: Métricas consolidadas e visualizações gerais
- Crop Calendar: Calendário interativo por estado/cultivo  
- Agriculture Availability: Qualidade e disponibilidade dos dados

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
from components.agricultural_analysis.agricultural_loader import (
    load_conab_detailed_data, 
    load_conab_crop_calendar,
    get_conab_crop_stats,
    validate_conab_data_quality
)
from components.agricultural_analysis.overview.agricultural_overview import render_agricultural_overview


def run():
    """
    Função principal que responde às páginas selecionadas no menu lateral do app.py.
    Verifica st.session_state.current_page para determinar qual página renderizar.
    """
    
    # Carregar dados reais CONAB
    with st.spinner("🔄 Carregando dados reais CONAB..."):
        try:
            conab_data = load_conab_detailed_data()
            calendar_data = load_conab_crop_calendar()
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
            conab_data = {}
            calendar_data = {}
    
    # Verificar disponibilidade dos dados
    has_conab = bool(conab_data)
    has_calendar = bool(calendar_data)
    
    if not has_conab and not has_calendar:
        st.error("❌ Nenhum dado CONAB disponível")
        st.info("🔧 Verifique se os arquivos JSON estão presentes em data/json/")
        return
    
    # Obter página atual do session state (definida pelo app.py)
    current_page = getattr(st.session_state, 'current_page', 'Agriculture Overview')
    
    # Renderizar página baseada na seleção do menu lateral
    if current_page == "Agriculture Overview":
        _render_agriculture_overview_page(calendar_data, conab_data)
    
    elif current_page == "Crop Calendar":
        _render_crop_calendar_page(calendar_data, conab_data)
    
    elif current_page == "Agriculture Availability":
        _render_agriculture_availability_page(calendar_data, conab_data)
    
    else:
        # Fallback para página padrão
        _render_agriculture_overview_page(calendar_data, conab_data)


def _render_agriculture_overview_page(calendar_data: dict, conab_data: dict):
    """Renderizar página Agriculture Overview - overview consolidado com métricas."""
    
    # Header da página
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
            📊 Agriculture Overview
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Visão consolidada da agricultura brasileira com dados CONAB
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais no topo
    _render_main_metrics(calendar_data, conab_data)
    
    st.markdown("---")
    
    # Overview consolidado usando o componente existente
    render_agricultural_overview(calendar_data, conab_data)
    
    # Gráficos adicionais de distribuição
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ Distribuição Regional")
        _render_regional_distribution_chart(conab_data)
    
    with col2:
        st.markdown("### 🌾 Diversidade de Culturas")
        _render_crop_diversity_chart(conab_data, calendar_data)


def _render_crop_calendar_page(calendar_data: dict, conab_data: dict):
    """Renderizar página Crop Calendar - calendário interativo."""
    
    # Header da página
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4A90E2 0%, #2E5984 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(74, 144, 226, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📅 Crop Calendar
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Calendário interativo de safras por estado e região
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not calendar_data:
        st.warning("⚠️ Dados de calendário agrícola não disponíveis")
        return
    
    # Filtros específicos para calendário
    _render_calendar_filters(calendar_data)
    
    st.markdown("---")
    
    # Usar o componente de calendário existente
    try:
        from components.agricultural_analysis.agricultural_calendar import run as run_calendar
        run_calendar()
    except ImportError:
        st.warning("⚠️ Componente de calendário não disponível")
        _render_basic_calendar_view(calendar_data)
    except Exception as e:
        st.error(f"❌ Erro ao renderizar calendário: {e}")


def _render_agriculture_availability_page(calendar_data: dict, conab_data: dict):
    """Renderizar página Agriculture Availability - disponibilidade e qualidade."""
    
    # Header da página
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #E2A857 0%, #B8860B 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(226, 168, 87, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📋 Agriculture Availability
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Análise de disponibilidade e qualidade dos dados agrícolas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Análise de disponibilidade de dados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Fontes de Dados")
        _render_data_sources_info(calendar_data, conab_data)
    
    with col2:
        st.markdown("### 🎯 Métricas de Qualidade")
        _render_data_quality_metrics(calendar_data, conab_data)
    
    st.markdown("---")
    
    # Análise temporal de disponibilidade
    st.markdown("### 📈 Disponibilidade Temporal")
    _render_temporal_availability(conab_data)
    
    # Análise geográfica de cobertura
    st.markdown("### 🗺️ Cobertura Geográfica")
    _render_geographic_coverage(calendar_data, conab_data)


def _render_main_metrics(calendar_data: dict, conab_data: dict):
    """Renderizar métricas principais no topo da página."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Número de culturas no calendário
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            total_calendar_crops = len(crop_calendar)
        else:
            total_calendar_crops = 0
        st.metric("🌾 Culturas (Calendário)", total_calendar_crops)
    
    with col2:
        # Número de culturas CONAB
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            total_conab_crops = len(detailed_coverage)
        else:
            total_conab_crops = 0
        st.metric("📊 Culturas (CONAB)", total_conab_crops)
    
    with col3:
        # Número de estados/regiões
        if calendar_data:
            states = calendar_data.get('states', {})
            total_states = len(states)
        else:
            total_states = 0
        st.metric("🗺️ Estados", total_states)
    
    with col4:
        # Anos de dados disponíveis
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            available_years = initiative.get('available_years', [])
            total_years = len(available_years)
        else:
            total_years = 0
        st.metric("📅 Anos de Dados", total_years)


def _render_regional_distribution_chart(conab_data: dict):
    """Renderizar gráfico de distribuição regional."""
    
    try:
        import plotly.express as px
        import pandas as pd
        
        if not conab_data:
            st.warning("⚠️ Dados CONAB não disponíveis")
            return
        
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            st.warning("⚠️ Dados detalhados de cobertura não encontrados")
            return
        
        # Contar culturas por região
        region_data = []
        for crop, crop_info in detailed_coverage.items():
            regions = crop_info.get('regions', [])
            for region in regions:
                region_data.append({
                    'Região': region,
                    'Cultura': crop,
                    'Contagem': 1
                })
        
        if region_data:
            df_regions = pd.DataFrame(region_data)
            region_summary = df_regions.groupby('Região')['Contagem'].sum().reset_index()
            
            fig_regions = px.pie(
                region_summary,
                values='Contagem',
                names='Região',
                title="Distribuição de Culturas por Região"
            )
            st.plotly_chart(fig_regions, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para gráfico regional")
        
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico regional: {e}")


def _render_crop_diversity_chart(conab_data: dict, calendar_data: dict):
    """Renderizar gráfico de diversidade de culturas."""
    
    try:
        import plotly.express as px
        import pandas as pd
        
        crops_data = []
        
        # Dados do calendário
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            for crop in crop_calendar.keys():
                crops_data.append({
                    'Cultura': crop,
                    'Fonte': 'Calendário Agrícola',
                    'Disponível': 1
                })
        
        # Dados CONAB
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            for crop in detailed_coverage.keys():
                crops_data.append({
                    'Cultura': crop,
                    'Fonte': 'Dados CONAB',
                    'Disponível': 1
                })
        
        if crops_data:
            df_crops = pd.DataFrame(crops_data)
            
            fig_crops = px.bar(
                df_crops,
                x='Cultura',
                y='Disponível',
                color='Fonte',
                title="Diversidade de Culturas por Fonte",
                color_discrete_map={
                    'Calendário Agrícola': '#2E8B57',
                    'Dados CONAB': '#FF8C00'
                }
            )
            fig_crops.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_crops, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para gráfico de diversidade")
        
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de diversidade: {e}")


def _render_calendar_filters(calendar_data: dict):
    """Renderizar filtros específicos para calendário."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro de estados
        states = calendar_data.get('states', {})
        state_options = [f"{code} - {info.get('name', code)}" for code, info in states.items()]
        selected_states = st.multiselect(
            "🏛️ Estados",
            options=state_options,
            default=state_options[:5] if len(state_options) > 5 else state_options,
            help="Selecione os estados para análise"
        )
    
    with col2:
        # Filtro de regiões
        regions = set()
        for state_info in states.values():
            region = state_info.get('region', '')
            if region:
                regions.add(region)
        
        selected_regions = st.multiselect(
            "🗺️ Regiões",
            options=sorted(list(regions)),
            default=sorted(list(regions))[:3] if len(regions) > 3 else sorted(list(regions)),
            help="Selecione as regiões para análise"
        )
    
    with col3:
        # Filtro de culturas
        crop_calendar = calendar_data.get('crop_calendar', {})
        crop_options = list(crop_calendar.keys())
        selected_crops = st.multiselect(
            "🌾 Culturas",
            options=crop_options,
            default=crop_options[:5] if len(crop_options) > 5 else crop_options,
            help="Selecione as culturas para análise"
        )
    
    return selected_states, selected_regions, selected_crops


def _render_basic_calendar_view(calendar_data: dict):
    """Renderizar visão básica do calendário quando o componente avançado não estiver disponível."""
    
    try:
        import pandas as pd
        
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.warning("⚠️ Dados de calendário não encontrados")
            return
        
        st.markdown("### 📅 Calendário de Safras Simplificado")
        
        # Criar tabela resumo
        calendar_summary = []
        for crop, states_data in crop_calendar.items():
            total_states = len(states_data)
            calendar_summary.append({
                'Cultura': crop,
                'Estados com Dados': total_states,
                'Status': '✅ Disponível' if total_states > 0 else '❌ Indisponível'
            })
        
        if calendar_summary:
            df_calendar = pd.DataFrame(calendar_summary)
            st.dataframe(df_calendar, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar calendário básico: {e}")


def _render_data_sources_info(calendar_data: dict, conab_data: dict):
    """Renderizar informações das fontes de dados."""
    
    try:
        import pandas as pd
        
        sources_data = []
        
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            sources_data.append({
                "Fonte": "Calendário Agrícola CONAB",
                "Status": "✅ Ativo",
                "Culturas": len(crop_calendar),
                "Tipo": "Calendário de Safras"
            })
        
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            sources_data.append({
                "Fonte": "Iniciativa CONAB",
                "Status": "✅ Ativo",
                "Culturas": len(detailed_coverage),
                "Tipo": "Monitoramento de Culturas"
            })
        
        if sources_data:
            df_sources = pd.DataFrame(sources_data)
            st.dataframe(df_sources, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Nenhuma fonte de dados disponível")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar fontes de dados: {e}")


def _render_data_quality_metrics(calendar_data: dict, conab_data: dict):
    """Renderizar métricas de qualidade dos dados."""
    
    try:
        import plotly.graph_objects as go
        
        # Calcular métricas de qualidade
        quality_metrics = []
        
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            accuracy = initiative.get('overall_accuracy', 90.0)
            quality_metrics.append(('Precisão CONAB', accuracy))
        
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            states = calendar_data.get('states', {})
            
            # Calcular completude do calendário
            total_possible = len(crop_calendar) * len(states) * 12  # culturas x estados x meses
            total_filled = 0
            
            for states_data in crop_calendar.values():
                for state_data in states_data:
                    calendar_entry = state_data.get('calendar', {})
                    for activity in calendar_entry.values():
                        if activity and activity.strip():
                            total_filled += 1
            
            completude = (total_filled / total_possible) * 100 if total_possible > 0 else 0
            quality_metrics.append(('Completude Calendário', completude))
        
        if quality_metrics:
            labels, values = zip(*quality_metrics)
            
            fig_quality = go.Figure(data=[
                go.Bar(x=list(labels), y=list(values), 
                       marker_color=['#2E8B57', '#4A90E2', '#E2A857'][:len(labels)])
            ])
            
            fig_quality.update_layout(
                title="Métricas de Qualidade (%)",
                yaxis_title="Qualidade (%)",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_quality, use_container_width=True)
        else:
            st.warning("⚠️ Métricas de qualidade não disponíveis")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar métricas de qualidade: {e}")


def _render_temporal_availability(conab_data: dict):
    """Renderizar disponibilidade temporal."""
    
    try:
        import plotly.express as px
        import pandas as pd
        
        if not conab_data:
            st.warning("⚠️ Dados CONAB não disponíveis")
            return
        
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        available_years = initiative.get('available_years', [])
        
        if available_years:
            years_df = pd.DataFrame({
                'Ano': available_years,
                'Disponível': [1] * len(available_years)
            })
            
            fig_timeline = px.bar(
                years_df,
                x='Ano',
                y='Disponível',
                title="Anos com Dados CONAB Disponíveis",
                color_discrete_sequence=['#2E8B57']
            )
            fig_timeline.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.warning("⚠️ Dados de anos disponíveis não encontrados")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar disponibilidade temporal: {e}")


def _render_geographic_coverage(calendar_data: dict, conab_data: dict):
    """Renderizar cobertura geográfica."""
    
    try:
        import pandas as pd
        
        coverage_data = []
        
        if calendar_data:
            states = calendar_data.get('states', {})
            regions = {}
            for state_code, state_info in states.items():
                region = state_info.get('region', 'Não especificada')
                if region not in regions:
                    regions[region] = 0
                regions[region] += 1
            
            for region, count in regions.items():
                coverage_data.append({
                    'Região': region,
                    'Estados': count,
                    'Fonte': 'Calendário Agrícola'
                })
        
        if conab_data:
            initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
            coverage_info = initiative.get('coverage', 'Brasil')
            coverage_data.append({
                'Região': coverage_info,
                'Estados': 'Nacional',
                'Fonte': 'Dados CONAB'
            })
        
        if coverage_data:
            df_coverage = pd.DataFrame(coverage_data)
            st.dataframe(df_coverage, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Dados de cobertura geográfica não disponíveis")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar cobertura geográfica: {e}")


if __name__ == "__main__":
    # Executar diretamente se chamado como script
    run()
