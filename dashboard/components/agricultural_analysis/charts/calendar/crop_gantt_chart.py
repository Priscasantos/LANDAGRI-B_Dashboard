"""
Crop Gantt Chart Module
======================

Módulo para renderização de diagramas de Gantt para visualização de períodos de cultivo.
Extraído do módulo de análise de disponibilidade CONAB para uso independente.

Autor: LANDAGRI-B Project Team 
Data: 2025-08-11
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


def render_crop_gantt_chart(filtered_data: Dict[str, Any], region: str = "Brasil") -> None:
    """
    Renderiza gráfico de Gantt para mostrar períodos de culturas.
    
    Args:
        filtered_data: Dados filtrados de culturas com calendários
        region: Nome da região para exibição no título
    """

    if not filtered_data:
        st.info("📊 Dados insuficientes para gráfico de Gantt.")
        return

    # Mapeamento de meses para índices
    month_mapping = {
        'January': 0, 'February': 1, 'March': 2, 'April': 3,
        'May': 4, 'June': 5, 'July': 6, 'August': 7,
        'September': 8, 'October': 9, 'November': 10, 'December': 11
    }

    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    # Preparar dados para Gantt
    gantt_data = []
    colors = ['#2E8B57', '#FF6B35', '#4682B4', '#9370DB', '#20B2AA', '#FF69B4', '#FFA500']

    for crop_index, (crop_name, crop_data) in enumerate(list(filtered_data.items())[:10]):
        # Find planting and harvest periods
        planting_months = set()
        harvest_months = set()

        for state_entry in crop_data:
            calendar_data = state_entry.get('calendar', {})

            for month, activity in calendar_data.items():
                if month in month_mapping:
                    if activity in ['P', 'PH']:
                        planting_months.add(month)
                    if activity in ['H', 'PH']:
                        harvest_months.add(month)

        # Create bars for planting
        if planting_months:
            month_indices = [month_mapping[m] for m in planting_months]
            start_month = min(month_indices)
            end_month = max(month_indices)

            gantt_data.append({
                'Task': f"{crop_name[:30]} - 🌱 Planting",
                'Start': start_month,
                'Finish': end_month + 1,
                'Resource': 'Planting',
                'Color': colors[crop_index % len(colors)],
                'Opacity': 0.8
            })

        # Create bars for harvest
        if harvest_months:
            month_indices = [month_mapping[m] for m in harvest_months]
            start_month = min(month_indices)
            end_month = max(month_indices)

            gantt_data.append({
                'Task': f"{crop_name[:30]} - 🌾 Harvest",
                'Start': start_month,
                'Finish': end_month + 1,
                'Resource': 'Harvest',
                'Color': colors[crop_index % len(colors)],
                'Opacity': 0.5
            })

    if not gantt_data:
        st.info("📊 Nenhum período de cultivo encontrado.")
        return

    # Criar gráfico de Gantt usando Plotly
    fig_gantt = go.Figure()

    for row in gantt_data:
        # Verificar se os índices estão válidos
        start_idx = max(0, min(11, row['Start']))
        end_idx = max(0, min(11, row['Finish'] - 1))

        fig_gantt.add_trace(go.Bar(
            name=row['Task'],
            x=[row['Finish'] - row['Start']],
            y=[row['Task']],
            base=[row['Start']],
            orientation='h',
            marker={
                'color': row['Color'],
                'opacity': row['Opacity'],
                'line': {'width': 1, 'color': 'white'}
            },
            showlegend=False,
            hovertemplate=f"<b>{row['Task']}</b><br>" +
                         f"Período: {month_names[start_idx]} - {month_names[end_idx]}<br>" +
                         f"Tipo: {row['Resource']}<extra></extra>"
        ))

    # Optimize layout for clarity and performance
    fig_gantt.update_layout(
        title=f"",
        xaxis_title="Months of the Year",
        yaxis_title="Crops and Activities",
        xaxis={
            'tickmode': 'array',
            'tickvals': list(range(12)),
            'ticktext': month_names,
            'range': [-0.5, 11.5]
        },
        height=max(400, len(gantt_data) * 36),
        barmode='overlay',
        showlegend=False,
        margin=dict(l=80, r=30, t=60, b=40),
        plot_bgcolor='white'
    )
    fig_gantt.update_yaxes(automargin=True)
    fig_gantt.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')

    st.plotly_chart(fig_gantt, use_container_width=True, key="crop_gantt_chart")

    # Adicionar informações resumidas
    st.markdown("**Data Summary**")
    col1, col2 = st.columns(2)
    with col1:
        plantio_count = len([g for g in gantt_data if 'Planting' in g['Task']])
        st.metric("🌱 Planting Periods", plantio_count)
    with col2:
        harvest_count = len([g for g in gantt_data if 'Harvest' in g['Task']])
        st.metric("🌾 Harvest Periods", harvest_count)


def create_gantt_chart_with_filters(crop_calendar: Dict[str, Any], states_info: Dict[str, Any]) -> None:
    """
    Cria um diagrama de Gantt com filtros interativos.
    
    Args:
        crop_calendar: Dados de calendário das culturas
        states_info: Informações dos estados
    """
    st.markdown("#### 📊 Diagrama de Gantt - Períodos de Cultivo")
    
    # Filtros organizados
    st.markdown("##### 🔧 Filtros de Análise")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Filtro por região
        regions = ["Todas as Regiões"] + sorted(list({
            state_info.get('region', 'Desconhecida')
            for state_info in states_info.values()
            if state_info.get('region', 'Desconhecida') != 'Desconhecida'
        }))
        selected_region = st.selectbox(
            "🌍 Região:",
            regions,
            key="gantt_region_filter"
        )
    
    with filter_col2:
        # Filtro por cultura
        crops = ["Todas as Culturas"] + sorted(list(crop_calendar.keys())[:20])
        selected_crop = st.selectbox(
            "🌾 Cultura:",
            crops,
            key="gantt_crop_filter"
        )
    
    with filter_col3:
        # Filtro por tipo de atividade
        activity_types = ["All Activities", "Only Planting", "Only Harvest", "Planting and Harvest"]
        selected_activity = st.selectbox(
            "⚡ Tipo de Atividade:",
            activity_types,
            key="gantt_activity_filter"
        )
    
    # Filtrar dados baseado na seleção
    filtered_data = _filter_gantt_data(
        crop_calendar, states_info, selected_region, selected_crop, selected_activity
    )
    
    if not filtered_data:
        st.warning("📊 Nenhum dado disponível para os filtros selecionados. Tente ajustar os filtros.")
        
        # Sugestões para o usuário
        st.markdown("**💡 Sugestões:**")
        st.markdown("- Selecione 'Todas as Regiões' para ver dados de todo o país")
        st.markdown("- Escolha 'Todas as Culturas' para análise geral")
        st.markdown("- Verifique se existem dados para a combinação selecionada")
        return
    
    # Exibir informações resumidas dos filtros
    total_crops = len(filtered_data)
    total_states = len({
        state_entry.get('state_code', '')
        for crop_data in filtered_data.values()
        for state_entry in crop_data
    })
    
    st.info(f"📊 **Dados filtrados:** {total_crops} culturas em {total_states} estados")
    
    # Renderizar o diagrama de Gantt
    render_crop_gantt_chart(filtered_data, selected_region)


def _filter_gantt_data(crop_calendar: Dict[str, Any], states_info: Dict[str, Any], 
                      region: str, crop: str, activity_type: str = "Todas as Atividades") -> Dict[str, Any]:
    """
    Filtra dados para o diagrama de Gantt baseado nos filtros selecionados.
    
    Args:
        crop_calendar: Dados de calendário das culturas
        states_info: Informações dos estados
        region: Região selecionada
        crop: Cultura selecionada
        activity_type: Tipo de atividade selecionada
        
    Returns:
        Dados filtrados para o Gantt
    """
    filtered_data = {}
    
    for crop_name, crop_data in crop_calendar.items():
        # Filtro por cultura
        if crop != "Todas as Culturas" and crop_name != crop:
            continue
            
        if not isinstance(crop_data, list):
            continue
        
        filtered_crop_data = []
        
        for state_entry in crop_data:
            state_code = state_entry.get('state_code', '')
            state_region = states_info.get(state_code, {}).get('region', 'Desconhecida')
            
            # Filtro por região
            if region != "Todas as Regiões" and state_region != region:
                continue
            
            # Verificar se há atividades no calendário que coincidem com o filtro
            calendar_data = state_entry.get('calendar', {})
            has_matching_activity = False
            
            for _month, activity in calendar_data.items():
                if (activity and 
                    (activity_type == "All Activities" or
                     (activity_type == "Only Planting" and activity == 'P') or
                     (activity_type == "Only Harvest" and activity == 'H') or
                     (activity_type == "Planting and Harvest" and activity == 'PH'))):
                    has_matching_activity = True
                    break
            
            if has_matching_activity:
                filtered_crop_data.append(state_entry)
        
        if filtered_crop_data:
            filtered_data[crop_name] = filtered_crop_data
    
    return filtered_data
