"""
Agricultural Calendar Dashboard - Enhanced Version
=================================================

Dashboard especializado em calendário agrícola interativo com análises avançadas.
Inspirado em sistemas internacionais como USDA iPAD, FAO GIEWS e Crop Monitor.

Funcionalidades aprimoradas:
- Filtros interativos regionais e por grupos de culturas
- Análise de padrões sazonais avançada
- Gráficos polares para visualização circular
- Análise de concentração e sobreposição de atividades
- Índices de diversidade temporal
- Visualizações de ondas sazonais
- Matriz de atividades mensais

Inspiração: USDA iPAD, FAO GIEWS, Crop Monitor, GEOGLAM
Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Adicionar project root ao path
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

_dashboard_root = Path(__file__).resolve().parent.parent.parent
if str(_dashboard_root) not in sys.path:
    sys.path.insert(0, str(_dashboard_root))

from .agricultural_loader import load_conab_crop_calendar
from .charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
    plot_monthly_activity_calendar
)


def run():
    """
    Executar dashboard do Calendário Agrícola com análises avançadas.
    """
    
    # Header aprimorado
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(5, 150, 105, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📅 Agricultural Calendar Analysis
        </h1>
        <p style="color: #dcfce7; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Enhanced interactive exploration of crop planting and harvesting periods across Brazil
        </p>
        <p style="color: #a7f3d0; margin: 0.2rem 0 0 0; font-size: 0.9rem;">
            Inspired by USDA iPAD, FAO GIEWS, Crop Monitor and GEOGLAM platforms
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Carregar dados
    with st.spinner("🔄 Loading enhanced calendar data..."):
        calendar_data = load_conab_crop_calendar()

    if not calendar_data:
        st.error("❌ No agricultural calendar data available.")
        st.info("🔧 Please check if the data files are available in the data/json/ folder")
        return

    # Extrair filtros disponíveis
    states_data, crops_data, years_data = _extract_calendar_filters(calendar_data)

    if not states_data or not crops_data:
        st.warning("⚠️ No valid calendar data found for analysis")
        return

    # Sidebar com controles avançados
    st.sidebar.markdown("## 🎛️ Enhanced Controls")
    
    # Seleção regional inteligente
    st.sidebar.markdown("### 🗺️ Geographic Selection")
    
    region_groups = {
        "North": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
        "Northeast": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "Central-West": ["DF", "GO", "MT", "MS"],
        "Southeast": ["ES", "MG", "RJ", "SP"],
        "South": ["PR", "RS", "SC"]
    }
    
    region_preset = st.sidebar.selectbox(
        "Quick region selection:",
        ["Custom"] + list(region_groups.keys()),
        help="Select a region or choose Custom for manual selection"
    )
    
    if region_preset != "Custom":
        default_states = [s for s in states_data if any(s.startswith(code) for code in region_groups[region_preset])]
    else:
        default_states = states_data[:8] if len(states_data) > 8 else states_data
    
    selected_states = st.sidebar.multiselect(
        "🗺️ States/Regions",
        options=states_data,
        default=default_states,
        help="Select states or regions to include in the analysis"
    )

    # Seleção de culturas com agrupamento por tipo
    st.sidebar.markdown("### 🌱 Crop Selection")
    
    crop_groups = {
        "Grains": ["Soja", "Milho", "Arroz", "Trigo", "Feijão"],
        "Cash Crops": ["Algodão", "Cana-de-açúcar", "Café"],
        "Fruits": ["Citrus", "Banana", "Uva"],
        "Others": []
    }
    
    # Organizar culturas por grupo
    organized_crops = {}
    for crop in crops_data:
        found = False
        for group, group_crops in crop_groups.items():
            if any(crop_name.lower() in crop.lower() for crop_name in group_crops):
                if group not in organized_crops:
                    organized_crops[group] = []
                organized_crops[group].append(crop)
                found = True
                break
        if not found:
            if "Others" not in organized_crops:
                organized_crops["Others"] = []
            organized_crops["Others"].append(crop)
    
    crop_preset = st.sidebar.selectbox(
        "Quick crop group selection:",
        ["Custom"] + list(organized_crops.keys()),
        help="Select a crop group or choose Custom for manual selection"
    )
    
    if crop_preset != "Custom" and crop_preset in organized_crops:
        default_crops = organized_crops[crop_preset][:6]
    else:
        default_crops = crops_data[:6] if len(crops_data) > 6 else crops_data
        
    selected_crops = st.sidebar.multiselect(
        "🌱 Crops",
        options=crops_data,
        default=default_crops,
        help="Select crops to include in the calendar analysis"
    )

    # Controles temporais
    selected_years = st.sidebar.multiselect(
        "📅 Years",
        options=years_data,
        default=years_data[-3:] if len(years_data) >= 3 else years_data,
        help="Select years for temporal analysis"
    )

    # Tipo de análise
    analysis_type = st.sidebar.selectbox(
        "📊 Analysis Type",
        ["Enhanced Overview", "Seasonal Patterns", "Activity Intensity", "Regional Distribution", "Temporal Waves"],
        help="Choose the type of enhanced analysis to perform"
    )

    if not selected_states or not selected_crops or not selected_years:
        st.info("👆 Please select states, crops, and years in the sidebar to display the enhanced calendar analysis")
        return

    # Filtrar dados
    filtered_data = _filter_calendar_data(calendar_data, selected_states, selected_crops, selected_years)

    st.markdown("---")

    # Renderizar análise baseada no tipo selecionado
    if analysis_type == "Enhanced Overview":
        _render_enhanced_overview(filtered_data, selected_crops, selected_states)
    elif analysis_type == "Seasonal Patterns":
        _render_enhanced_seasonal_patterns(filtered_data)
    elif analysis_type == "Activity Intensity":
        _render_activity_intensity_analysis(filtered_data)
    elif analysis_type == "Regional Distribution":
        _render_enhanced_regional_distribution(filtered_data, selected_states)
    elif analysis_type == "Temporal Waves":
        _render_temporal_waves_analysis(filtered_data, selected_years)


def _render_enhanced_overview(filtered_data: dict, selected_crops: list[str], selected_states: list[str]):
    """Renderizar visão geral aprimorada do calendário."""
    
    st.markdown("## 🔥 Enhanced Calendar Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Advanced Activity Heatmap")
        _create_enhanced_calendar_heatmap(filtered_data)
    
    with col2:
        st.markdown("### 🌙 Polar Activity Distribution")
        _create_polar_activity_chart(filtered_data)

    st.markdown("### 📈 Interactive Activity Timeline")
    _create_interactive_timeline(filtered_data)

    # Estatísticas de resumo aprimoradas
    st.markdown("### 📋 Enhanced Statistics")
    _create_enhanced_statistics(filtered_data, selected_crops, selected_states)


def _render_enhanced_seasonal_patterns(filtered_data: dict):
    """Renderizar análise de padrões sazonais aprimorada."""
    
    st.markdown("## 🌀 Enhanced Seasonal Patterns Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Seasonality Index")
        _create_seasonality_index_chart(filtered_data)
    
    with col2:
        st.markdown("### 📊 Concentration Matrix")
        _create_concentration_matrix(filtered_data)

    st.markdown("### 🌊 Seasonal Waves Visualization")
    _create_seasonal_waves_3d(filtered_data)


def _render_activity_intensity_analysis(filtered_data: dict):
    """Renderizar análise de intensidade de atividades."""
    
    st.markdown("## 🔥 Activity Intensity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Intensity Heatmap")
        _create_intensity_heatmap(filtered_data)
    
    with col2:
        st.markdown("### 📈 Peak Activity Analysis")
        _create_peak_activity_analysis(filtered_data)

    st.markdown("### 🎲 Activity Overlap Matrix")
    _create_activity_overlap_matrix(filtered_data)


def _render_enhanced_regional_distribution(filtered_data: dict, selected_states: list[str]):
    """Renderizar análise de distribuição regional aprimorada."""
    
    st.markdown("## 🗺️ Enhanced Regional Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Regional Coverage Score")
        _create_regional_coverage_score(filtered_data, selected_states)
    
    with col2:
        st.markdown("### 🎯 Diversity Index by Region")
        _create_regional_diversity_index(filtered_data)

    st.markdown("### 📊 Cross-Regional Comparison")
    _create_cross_regional_comparison(filtered_data, selected_states)


def _render_temporal_waves_analysis(filtered_data: dict, selected_years: list[int]):
    """Renderizar análise de ondas temporais."""
    
    st.markdown("## 🌊 Temporal Waves Analysis")
    
    if len(selected_years) < 2:
        st.warning("⚠️ Please select at least 2 years for temporal waves analysis")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Temporal Consistency")
        _create_temporal_consistency_chart(filtered_data, selected_years)
    
    with col2:
        st.markdown("### 🔄 Year-over-Year Stability")
        _create_stability_analysis(filtered_data, selected_years)

    st.markdown("### 🌊 Wave Pattern Analysis")
    _create_wave_pattern_analysis(filtered_data)


def _create_enhanced_calendar_heatmap(filtered_data: dict):
    """Criar heatmap aprimorado do calendário com mais detalhes."""
    
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("No calendar data for enhanced heatmap")
            return

        # Mapeamento de meses completos para abreviados
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }

        # Preparar dados para heatmap com atividades diferenciadas
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        heatmap_data = []
        
        for crop, crop_states in crop_calendar.items():
            crop_activities = {month: {'planting': 0, 'harvesting': 0, 'both': 0} for month in months}
            
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                
                for month_full, activity in calendar_entry.items():
                    # Mapear mês completo para abreviado
                    month = month_mapping.get(month_full, month_full)
                    
                    if month in months and activity and activity.strip():
                        # Categorizar atividades
                        if 'P' in activity and 'H' in activity:
                            crop_activities[month]['both'] += 1
                        elif 'P' in activity:
                            crop_activities[month]['planting'] += 1
                        elif 'H' in activity:
                            crop_activities[month]['harvesting'] += 1
            
            # Calcular score de atividade total
            for month in months:
                total_score = (crop_activities[month]['planting'] +
                             crop_activities[month]['harvesting'] +
                             crop_activities[month]['both'] * 2)
                
                heatmap_data.append({
                    'Crop': crop,
                    'Month': month,
                    'Activity_Score': total_score,
                    'Planting': crop_activities[month]['planting'],
                    'Harvesting': crop_activities[month]['harvesting'],
                    'Both': crop_activities[month]['both']
                })

        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data)
            pivot_heatmap = df_heatmap.pivot(index='Crop', columns='Month', values='Activity_Score')
            pivot_heatmap = pivot_heatmap.fillna(0)
            
            # Reordenar colunas na ordem correta dos meses
            pivot_heatmap = pivot_heatmap.reindex(columns=months, fill_value=0)

            fig = px.imshow(
                pivot_heatmap.values,
                x=pivot_heatmap.columns,
                y=pivot_heatmap.index,
                color_continuous_scale='Viridis',
                title="Enhanced Crop Calendar Activity Heatmap",
                labels={'x': 'Month', 'y': 'Crop', 'color': 'Activity Score'},
                aspect='auto'
            )
            
            # Adicionar anotações com detalhes
            for i, _crop in enumerate(pivot_heatmap.index):
                for j, _month in enumerate(pivot_heatmap.columns):
                    value = pivot_heatmap.iloc[i, j]
                    if value > 0:
                        fig.add_annotation(
                            x=j, y=i,
                            text=str(int(value)),
                            showarrow=False,
                            font={"color": "white" if value > pivot_heatmap.values.max()/2 else "black"}
                        )
            
            fig.update_layout(height=max(500, len(pivot_heatmap.index) * 35))
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating enhanced heatmap: {e}")


def _create_polar_activity_chart(filtered_data: dict):
    """Criar gráfico polar de atividades com mais detalhes."""
    
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_counts = {month: {'Planting': 0, 'Harvesting': 0} for month in months}
        
        for _crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                
                for month, activity in calendar_entry.items():
                    if activity and activity.strip():
                        if 'P' in activity:
                            monthly_counts[month]['Planting'] += 1
                        if 'H' in activity:
                            monthly_counts[month]['Harvesting'] += 1

        # Preparar dados para gráfico polar
        months_extended = months + [months[0]]
        planting_values = [monthly_counts[month]['Planting'] for month in months] + [monthly_counts[months[0]]['Planting']]
        harvesting_values = [monthly_counts[month]['Harvesting'] for month in months] + [monthly_counts[months[0]]['Harvesting']]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=planting_values,
            theta=months_extended,
            fill='toself',
            name='Planting Activities',
            line_color='#10b981',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))

        fig.add_trace(go.Scatterpolar(
            r=harvesting_values,
            theta=months_extended,
            fill='toself',
            name='Harvesting Activities',
            line_color='#f59e0b',
            fillcolor='rgba(245, 158, 11, 0.2)'
        ))

        fig.update_layout(
            polar={
                "radialaxis": {"visible": True, "range": [0, max(max(planting_values), max(harvesting_values))]},
                "angularaxis": {"direction": "clockwise", "period": 12}
            },
            title="Polar Distribution of Agricultural Activities",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating polar chart: {e}")


def _create_interactive_timeline(filtered_data: dict):
    """Criar timeline interativa de atividades."""
    
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        timeline_data = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_name = state_entry.get('state_name', '')
                calendar_entry = state_entry.get('calendar', {})
                
                for month, activity in calendar_entry.items():
                    if activity and activity.strip():
                        activity_types = []
                        if 'P' in activity:
                            activity_types.append('Planting')
                        if 'H' in activity:
                            activity_types.append('Harvesting')
                        
                        for act_type in activity_types:
                            timeline_data.append({
                                'Crop': crop,
                                'State': state_name,
                                'Month': month,
                                'Activity': act_type,
                                'Month_Num': months.index(month) + 1,
                                'Activity_ID': f"{crop}_{state_name}_{month}_{act_type}"
                            })

        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            # Criar gráfico de gantt-style
            fig = px.scatter(
                df_timeline,
                x='Month_Num',
                y='Crop',
                color='Activity',
                hover_data=['State', 'Month'],
                title="Interactive Agricultural Activity Timeline",
                labels={'Month_Num': 'Month'},
                color_discrete_map={
                    'Planting': '#10b981',
                    'Harvesting': '#f59e0b'
                }
            )
            
            # Personalizar eixo x
            fig.update_xaxes(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=months
            )
            
            fig.update_layout(height=max(500, len(df_timeline['Crop'].unique()) * 40))
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error creating timeline: {e}")


def _create_enhanced_statistics(filtered_data: dict, selected_crops: list[str], selected_states: list[str]):
    """Criar estatísticas aprimoradas do calendário."""
    
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        # Calcular estatísticas avançadas
        total_combinations = len(selected_crops) * len(selected_states)
        available_combinations = sum(len(crop_states) for crop_states in crop_calendar.values())
        coverage_rate = (available_combinations / total_combinations) * 100 if total_combinations > 0 else 0
        
        # Calcular diversidade temporal
        all_activities = []
        seasonal_spread = []
        
        for crop_states in crop_calendar.values():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                active_months = sum(1 for activity in calendar_entry.values() if activity and activity.strip())
                all_activities.append(active_months)
                
                # Calcular spread sazonal (número de meses consecutivos)
                month_indices = []
                for month, activity in calendar_entry.items():
                    if activity and activity.strip():
                        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        if month in months:
                            month_indices.append(months.index(month))
                
                if month_indices:
                    spread = max(month_indices) - min(month_indices) + 1
                    seasonal_spread.append(spread)
        
        avg_active_months = sum(all_activities) / len(all_activities) if all_activities else 0
        avg_seasonal_spread = sum(seasonal_spread) / len(seasonal_spread) if seasonal_spread else 0
        
        # Calcular índice de concentração
        concentration_index = (12 - avg_active_months) / 11 * 100 if avg_active_months > 0 else 0
        
        # Exibir métricas avançadas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Coverage Rate",
                f"{coverage_rate:.1f}%",
                help="Percentage of crop-state combinations with available data"
            )
        
        with col2:
            st.metric(
                "Avg Active Months",
                f"{avg_active_months:.1f}",
                help="Average number of months with agricultural activity"
            )
        
        with col3:
            st.metric(
                "Seasonal Spread",
                f"{avg_seasonal_spread:.1f}",
                help="Average seasonal span in months"
            )
        
        with col4:
            st.metric(
                "Concentration Index",
                f"{concentration_index:.1f}%",
                help="Degree of seasonal activity concentration"
            )
        
        with col5:
            st.metric(
                "Data Points",
                available_combinations,
                help="Total number of crop-state combinations available"
            )
            
    except Exception as e:
        st.error(f"Error creating enhanced statistics: {e}")


# Função placeholder para outras análises avançadas
def _create_seasonality_index_chart(filtered_data: dict):
    """Criar gráfico de índice de sazonalidade."""
    st.info("🔧 Advanced seasonality index analysis - Feature under development")


def _create_concentration_matrix(filtered_data: dict):
    """Criar matriz de concentração."""
    st.info("🔧 Concentration matrix analysis - Feature under development")


def _create_seasonal_waves_3d(filtered_data: dict):
    """Criar visualização 3D de ondas sazonais."""
    st.info("🔧 3D seasonal waves visualization - Feature under development")


def _create_intensity_heatmap(filtered_data: dict):
    """Criar heatmap de intensidade."""
    st.info("🔧 Intensity heatmap analysis - Feature under development")


def _create_peak_activity_analysis(filtered_data: dict):
    """Criar análise de picos de atividade."""
    st.info("🔧 Peak activity analysis - Feature under development")


def _create_activity_overlap_matrix(filtered_data: dict):
    """Criar matriz de sobreposição de atividades."""
    st.info("🔧 Activity overlap matrix - Feature under development")


def _create_regional_coverage_score(filtered_data: dict, selected_states: list[str]):
    """Criar score de cobertura regional."""
    st.info("🔧 Regional coverage scoring - Feature under development")


def _create_regional_diversity_index(filtered_data: dict):
    """Criar índice de diversidade regional."""
    st.info("🔧 Regional diversity index - Feature under development")


def _create_cross_regional_comparison(filtered_data: dict, selected_states: list[str]):
    """Criar comparação cross-regional."""
    st.info("🔧 Cross-regional comparison - Feature under development")


def _create_temporal_consistency_chart(filtered_data: dict, selected_years: list[int]):
    """Criar gráfico de consistência temporal."""
    st.info("🔧 Temporal consistency analysis - Feature under development")


def _create_stability_analysis(filtered_data: dict, selected_years: list[int]):
    """Criar análise de estabilidade."""
    st.info("🔧 Year-over-year stability analysis - Feature under development")


def _create_wave_pattern_analysis(filtered_data: dict):
    """Criar análise de padrões de ondas."""
    st.info("🔧 Wave pattern analysis - Feature under development")

    # Header visual
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(14, 165, 233, 0.2);
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                📅 Calendário Agrícola Brasileiro
            </h1>
            <p style="color: #e0f2fe; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Análise temporal e sazonalidade das culturas brasileiras
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Carregar dados
    calendar_data = _load_calendar_data()
    
    if not calendar_data:
        st.error("❌ Dados de calendário agrícola não disponíveis.")
        return

    # Filtros interativos na sidebar
    _render_sidebar_filters(calendar_data)
    
    # Seção principal do calendário
    _render_main_calendar_section(calendar_data)
    
    # Análises adicionais
    _render_additional_analyses(calendar_data)


def _load_calendar_data():
    """Carregar dados do calendário agrícola."""
    with st.spinner("🔄 Carregando dados do calendário..."):
        try:
            return load_conab_crop_calendar()
        except Exception as e:
            st.error(f"❌ Erro ao carregar calendário: {e}")
            return {}


def _extract_calendar_filters(calendar_data: dict) -> tuple[list[str], list[str], list[int]]:
    """Extrair filtros disponíveis dos dados do calendário."""
    states_set = set()
    crops_set = set()
    years_set = set()
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    
    for crop, crop_states in crop_calendar.items():
        crops_set.add(crop)
        
        for state_entry in crop_states:
            state_name = state_entry.get('state_name', '')
            if state_name:
                states_set.add(state_name)
            
            years = state_entry.get('years', [])
            if years:
                years_set.update(years)
    
    if not years_set:
        years_set = {2020, 2021, 2022, 2023, 2024}
    
    return sorted(states_set), sorted(crops_set), sorted(years_set)


def _render_sidebar_filters(calendar_data: dict):
    """Renderizar filtros na sidebar."""
    st.sidebar.markdown("## 🎛️ Filtros do Calendário")
    
    states_data, crops_data, years_data = _extract_calendar_filters(calendar_data)
    
    # Filtros
    st.sidebar.markdown("### 🗺️ Estados")
    selected_states = st.sidebar.multiselect(
        "Selecionar Estados",
        options=states_data,
        default=states_data[:8] if len(states_data) > 8 else states_data,
        help="Selecione os estados para incluir na análise"
    )
    
    st.sidebar.markdown("### 🌱 Culturas")
    selected_crops = st.sidebar.multiselect(
        "Selecionar Culturas",
        options=crops_data,
        default=crops_data[:6] if len(crops_data) > 6 else crops_data,
        help="Selecione as culturas para o calendário"
    )
    
    st.sidebar.markdown("### 📅 Anos")
    selected_years = st.sidebar.multiselect(
        "Selecionar Anos",
        options=years_data,
        default=years_data[-3:] if len(years_data) >= 3 else years_data,
        help="Selecione os anos para análise temporal"
    )
    
    # Salvar seleções no session state
    st.session_state.selected_states = selected_states
    st.session_state.selected_crops = selected_crops
    st.session_state.selected_years = selected_years
    
    # Informações dos filtros
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Resumo dos Filtros")
    st.sidebar.info(f"""
    **Estados:** {len(selected_states)}
    **Culturas:** {len(selected_crops)}
    **Anos:** {len(selected_years)}
    """)


def _render_main_calendar_section(calendar_data: dict):
    """Renderizar seção principal do calendário."""
    
    # Verificar se filtros foram aplicados
    if not hasattr(st.session_state, 'selected_states'):
        st.info("👈 Use os filtros na barra lateral para configurar o calendário")
        return
    
    selected_states = st.session_state.selected_states
    selected_crops = st.session_state.selected_crops
    selected_years = st.session_state.selected_years
    
    if not selected_states or not selected_crops:
        st.warning("⚠️ Selecione pelo menos um estado e uma cultura nos filtros")
        return
    
    # Filtrar dados
    filtered_data = _filter_calendar_data(calendar_data, selected_states, selected_crops, selected_years)
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🗓️ Calendário de Plantio e Colheita")
        fig_heatmap = plot_crop_calendar_heatmap(filtered_data)
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.caption("Mapa de calor mostrando períodos de plantio (P) e colheita (H) filtrados.")
        else:
            st.info("📊 Não foi possível gerar o heatmap com os filtros selecionados")
    
    with col2:
        st.markdown("### 📊 Atividade Mensal")
        fig_monthly = plot_monthly_activity_calendar(calendar_data, selected_crops)
        if fig_monthly:
            st.plotly_chart(fig_monthly, use_container_width=True)
            st.caption("Resumo mensal das atividades para as culturas selecionadas.")
        else:
            st.info("📊 Dados mensais não disponíveis")


def _filter_calendar_data(calendar_data: dict, selected_states: list[str],
                         selected_crops: list[str], selected_years: list[int]) -> dict:
    """Filtrar dados do calendário com base nas seleções."""
    filtered_data = {'crop_calendar': {}}
    
    crop_calendar = calendar_data.get('crop_calendar', {})
    
    for crop in selected_crops:
        if crop in crop_calendar:
            filtered_states = []
            
            for state_entry in crop_calendar[crop]:
                state_name = state_entry.get('state_name', '')
                
                if state_name in selected_states:
                    entry_years = state_entry.get('years', selected_years)
                    if any(year in selected_years for year in entry_years):
                        filtered_states.append(state_entry)
            
            if filtered_states:
                filtered_data['crop_calendar'][crop] = filtered_states
    
    return filtered_data


def _render_additional_analyses(calendar_data: dict):
    """Renderizar análises adicionais do calendário."""
    
    st.markdown("---")
    st.markdown("## 📈 Análises Avançadas")
    
    # Análise de sazonalidade
    tab1, tab2, tab3 = st.tabs(["🔄 Sazonalidade", "📊 Comparação Temporal", "🗺️ Distribuição Regional"])
    
    with tab1:
        _render_seasonality_analysis(calendar_data)
    
    with tab2:
        _render_temporal_comparison(calendar_data)
    
    with tab3:
        _render_regional_distribution(calendar_data)


def _render_seasonality_analysis(calendar_data: dict):
    """Renderizar análise de sazonalidade."""
    st.markdown("### 🔄 Análise de Sazonalidade")
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        # Dados de sazonalidade
        monthly_activity = {f"Mês {i}": 0 for i in range(1, 13)}
        
        for _crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                for month, activity in calendar_entry.items():
                    if activity:
                        month_num = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"].index(month) + 1
                        monthly_activity[f"Mês {month_num}"] += 1
        
        # Gráfico de sazonalidade
        months = list(monthly_activity.keys())
        activities = list(monthly_activity.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=activities,
            theta=months,
            fill='toself',
            name='Atividade Agrícola'
        ))
        
        fig.update_layout(
            polar={
                "radialaxis": {
                    "visible": True,
                    "range": [0, max(activities)]
                }},
            title="Distribuição Sazonal da Atividade Agrícola",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Gráfico polar mostrando a intensidade das atividades agrícolas ao longo do ano.")
        
    except Exception as e:
        st.error(f"Erro na análise de sazonalidade: {e}")


def _render_temporal_comparison(calendar_data: dict):
    """Renderizar comparação temporal."""
    st.markdown("### 📊 Comparação Temporal")
    
    try:
        # Análise básica de comparação temporal
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        temporal_data = []
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                years = state_entry.get('years', [2024])
                state_name = state_entry.get('state_name', '')
                
                for year in years:
                    temporal_data.append({
                        'Ano': year,
                        'Estado': state_name,
                        'Cultura': crop,
                        'Atividade': 1
                    })
        
        if temporal_data:
            df_temporal = pd.DataFrame(temporal_data)
            
            # Gráfico de linha temporal
            yearly_summary = df_temporal.groupby(['Ano', 'Cultura'])['Atividade'].sum().reset_index()
            
            fig = px.line(
                yearly_summary,
                x='Ano',
                y='Atividade',
                color='Cultura',
                title="Evolução Temporal das Culturas"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Evolução da atividade por cultura ao longo dos anos.")
            
        else:
            st.info("📊 Dados temporais não disponíveis")
        
    except Exception as e:
        st.error(f"Erro na comparação temporal: {e}")


def _render_regional_distribution(calendar_data: dict):
    """Renderizar distribuição regional."""
    st.markdown("### 🗺️ Distribuição Regional")
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        regional_data = []
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_name = state_entry.get('state_name', '')
                calendar_entry = state_entry.get('calendar', {})
                
                # Contar atividades por estado
                activity_count = sum(1 for activity in calendar_entry.values() if activity)
                
                regional_data.append({
                    'Estado': state_name,
                    'Cultura': crop,
                    'Atividades': activity_count
                })
        
        if regional_data:
            df_regional = pd.DataFrame(regional_data)
            
            # Heatmap por estado e cultura
            pivot_regional = df_regional.pivot_table(
                index='Estado',
                columns='Cultura',
                values='Atividades',
                fill_value=0
            )
            
            fig = px.imshow(
                pivot_regional.values,
                x=pivot_regional.columns,
                y=pivot_regional.index,
                aspect="auto",
                title="Intensidade de Atividade por Estado e Cultura"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Mapa de calor da intensidade de atividades agrícolas por estado e cultura.")
            
        else:
            st.info("📊 Dados regionais não disponíveis")
        
    except Exception as e:
        st.error(f"Erro na distribuição regional: {e}")


if __name__ == "__main__":
    run()
