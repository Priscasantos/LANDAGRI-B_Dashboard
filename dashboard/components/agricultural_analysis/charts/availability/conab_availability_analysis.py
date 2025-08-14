"""
Análise de Disponibilidade CONAB
================================

Módulo para análise de disponibilidade baseado exclusivamente em dados CONAB.
Implementa visualizações modernas por região e estado usando Plotly.

Autor: LANDAGRI-B Project Team 
Data: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .conab_availability_matrix import create_conab_availability_matrix


def render_conab_availability_analysis(conab_data: dict) -> None:
    """
    Renderiza análise completa de disponibilidade CONAB.

    Parâmetros:
    -----------
    conab_data : dict
        Dados CONAB com estrutura completa do JSON
    """
    if not conab_data or not isinstance(conab_data, dict):
        st.warning("⚠️ Dados CONAB não disponíveis para análise.")
        return

    st.markdown("### 📊 Análise de Disponibilidade CONAB")
    st.markdown("*Análise baseada em dados oficiais CONAB por região e estado*")

    try:
        # Extrair dados principais do JSON CONAB
        crop_calendar = conab_data.get('crop_calendar', {})
        states_info = conab_data.get('states', {})

        if not crop_calendar:
            st.warning("⚠️ Dados de calendário agrícola não encontrados.")
            return

        # Análises principais em tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🗺️ Análise Regional",
            "📅 Sazonalidade",
            "⏰ Timeline",
            "📈 Tendências"
        ])

        with tab1:
            _render_regional_analysis(crop_calendar, states_info)

        with tab2:
            _render_seasonality_analysis(crop_calendar, states_info)

        with tab3:
            _render_timeline_analysis(crop_calendar, states_info)

        with tab4:
            _render_trends_analysis(crop_calendar, states_info)

    except Exception as e:
        st.error(f"❌ Erro na análise de disponibilidade CONAB: {e}")


def _render_regional_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise por região brasileira."""
    st.markdown("#### 🗺️ Disponibilidade por Região")

    # Agregar dados por região
    regional_data = _aggregate_by_region(crop_calendar, states_info)

    if not regional_data:
        st.info("📊 Dados regionais não disponíveis.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📊 Diversidade por Região")
        # Gráfico de barras por região
        regions = list(regional_data.keys())
        counts = list(regional_data.values())

        fig_regions = px.bar(
            x=regions,
            y=counts,
            title="Diversidade de Culturas por Região",
            labels={'x': 'Região', 'y': 'Número de Culturas'},
            color=counts,
            color_continuous_scale='Viridis',
            text=counts
        )
        fig_regions.update_traces(texttemplate='%{text}', textposition='outside')
        fig_regions.update_layout(showlegend=False, xaxis_tickangle=45)
        st.plotly_chart(fig_regions, use_container_width=True, key="regional_diversity_chart")

    with col2:
        st.markdown("##### 🗺️ Matriz de Disponibilidade")
        # Matriz de disponibilidade
        try:
            fig_matrix = create_conab_availability_matrix({
                'crop_calendar': crop_calendar,
                'states': states_info
            })
            if fig_matrix:
                st.plotly_chart(fig_matrix, use_container_width=True, key="conab_matrix_regional")
        except Exception as e:
            st.error(f"❌ Erro ao gerar matriz: {e}")


def _render_seasonality_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise de sazonalidade."""
    st.markdown("#### 📅 Análise de Sazonalidade")

    # Extrair dados sazonais
    seasonal_data = _extract_seasonal_data(crop_calendar)

    if not seasonal_data:
        st.info("📊 Dados sazonais não disponíveis.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🔄 Sazonalidade Geral")
        # Criar gráfico polar de sazonalidade
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        fig_polar = go.Figure()

        # Adicionar trace para cada tipo de atividade
        colors = {'P': '#2E8B57', 'H': '#FF6B35', 'PH': '#4682B4'}
        names = {'P': 'Planting', 'H': 'Harvesting', 'PH': 'Planting/Harvesting'}

        for activity_type in ['P', 'H', 'PH']:
            monthly_counts = [seasonal_data.get(month, {}).get(activity_type, 0) for month in months]

            if sum(monthly_counts) > 0:  # Só adicionar se houver dados
                fig_polar.add_trace(go.Scatterpolar(
                    r=monthly_counts,
                    theta=months,
                    fill='toself',
                    name=names[activity_type],
                    line_color=colors[activity_type],
                    opacity=0.7
                ))

        max_value = max(
            max(seasonal_data.get(month, {}).values())
            for month in months
            if seasonal_data.get(month)
        ) if seasonal_data else 1

        fig_polar.update_layout(
            polar={
                'radialaxis': {'visible': True, 'range': [0, max_value]}
            },
            title="Sazonalidade de Atividades Agrícolas",
            showlegend=True
        )

        st.plotly_chart(fig_polar, use_container_width=True, key="seasonality_polar_chart")

    with col2:
        st.markdown("##### 📊 Atividades por Mês")
        # Gráfico de barras empilhadas por mês
        if seasonal_data:
            df_seasonal = pd.DataFrame(seasonal_data).T.fillna(0)
            df_seasonal = df_seasonal.reset_index()
            df_seasonal.rename(columns={'index': 'Mês'}, inplace=True)

            fig_bars = px.bar(
                df_seasonal,
                x='Mês',
                y=['P', 'H', 'PH'],
                title="Distribuição Mensal de Atividades",
                labels={'value': 'Número de Atividades', 'variable': 'Tipo'},
                color_discrete_map={'P': '#2E8B57', 'H': '#FF6B35', 'PH': '#4682B4'}
            )
            fig_bars.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_bars, use_container_width=True, key="monthly_activities_bars")


def _render_timeline_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise de timeline com gráficos temporais."""
    st.markdown("#### ⏰ Análise de Timeline")
    
    # Filtros de seleção organizados
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
            key="timeline_region_filter"
        )
    
    with filter_col2:
        # Filtro por cultura (mais culturas disponíveis)
        crops = ["Todas as Culturas"] + sorted(list(crop_calendar.keys())[:20])
        selected_crop = st.selectbox(
            "🌾 Cultura:",
            crops,
            key="timeline_crop_filter"
        )
    
    with filter_col3:
        # Filtro por tipo de atividade
        activity_types = ["All Activities", "Only Planting", "Only Harvesting", "Planting and Harvesting"]
        selected_activity = st.selectbox(
            "⚡ Tipo de Atividade:",
            activity_types,
            key="timeline_activity_filter"
        )
    
    # Filtrar dados baseado na seleção
    filtered_data = _filter_timeline_data(
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
    
    # Três tipos de timeline
    timeline_tab1, timeline_tab2, timeline_tab3 = st.tabs([
        "📅 Timeline Mensal",
        "🗓️ Gantt de Culturas",
        "📊 Densidade Temporal"
    ])
    
    with timeline_tab1:
        _render_monthly_timeline(filtered_data)
    
    with timeline_tab2:
        _render_crop_gantt_chart(filtered_data, selected_region)
    
    with timeline_tab3:
        _render_temporal_density(filtered_data)
def _filter_timeline_data(crop_calendar: dict, states_info: dict, region: str, crop: str, activity_type: str = "Todas as Atividades") -> dict:
    """Filtra dados de timeline baseado nos filtros selecionados."""
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
                     (activity_type == "Only Harvesting" and activity == 'H') or
                     (activity_type == "Planting and Harvesting" and activity == 'PH'))):
                    has_matching_activity = True
                    break
            
            if has_matching_activity:
                filtered_crop_data.append(state_entry)
        
        if filtered_crop_data:
            filtered_data[crop_name] = filtered_crop_data
    
    return filtered_data
def _render_monthly_timeline(filtered_data: dict) -> None:
    """Renderiza timeline mensal com linha temporal."""
    st.markdown("##### 📅 Timeline Mensal de Atividades")

    if not filtered_data:
        st.info("📊 Dados insuficientes para timeline mensal.")
        return

    # Mapeamento correto de meses inglês -> português
    month_mapping = {
        'January': 'Jan', 'February': 'Fev', 'March': 'Mar', 'April': 'Abr',
        'May': 'Mai', 'June': 'Jun', 'July': 'Jul', 'August': 'Ago',
        'September': 'Set', 'October': 'Out', 'November': 'Nov', 'December': 'Dez'
    }

    month_names = list(month_mapping.values())

    # Contar atividades por mês (usando nomes em português)
    monthly_counts = {month_pt: {'P': 0, 'H': 0, 'PH': 0} for month_pt in month_names}

    for _crop_name, crop_data in filtered_data.items():
        for state_entry in crop_data:
            calendar_data = state_entry.get('calendar', {})

            for month_en, activity in calendar_data.items():
                if month_en in month_mapping and activity in ['P', 'H', 'PH']:
                    month_pt = month_mapping[month_en]
                    monthly_counts[month_pt][activity] += 1

    # Verificar se há dados para exibir
    total_activities = sum(
        sum(activities.values()) for activities in monthly_counts.values()
    )

    if total_activities == 0:
        st.info("📊 Nenhuma atividade agrícola encontrada para os filtros selecionados.")
        return

    # Criar gráfico de linha temporal
    planting = [monthly_counts[month]['P'] for month in month_names]
    harvest = [monthly_counts[month]['H'] for month in month_names]
    both = [monthly_counts[month]['PH'] for month in month_names]

    fig_timeline = go.Figure()

    # Adicionar linhas para cada tipo de atividade
    fig_timeline.add_trace(go.Scatter(
        x=month_names,
        y=planting,
        mode='lines+markers',
        name='🌱 Planting',
        line={'color': '#2E8B57', 'width': 3},
        marker={'size': 8},
        hovertemplate='<b>%{fullData.name}</b><br>Mês: %{x}<br>Atividades: %{y}<extra></extra>'
    ))

    fig_timeline.add_trace(go.Scatter(
        x=month_names,
        y=harvest,
        mode='lines+markers',
        name='🌾 Harvest',
        line={'color': '#FF6B35', 'width': 3},
        marker={'size': 8},
        hovertemplate='<b>%{fullData.name}</b><br>Mês: %{x}<br>Atividades: %{y}<extra></extra>'
    ))

    fig_timeline.add_trace(go.Scatter(
        x=month_names,
        y=both,
        mode='lines+markers',
        name='🔄 Planting/Harvesting',
        line={'color': '#4682B4', 'width': 3},
        marker={'size': 8},
        hovertemplate='<b>%{fullData.name}</b><br>Mês: %{x}<br>Atividades: %{y}<extra></extra>'
    ))

    fig_timeline.update_layout(
        title="Agricultural Activities Timeline Throughout the Year",
        xaxis_title="Month",
        yaxis_title="Number of Activities",
        hovermode='x unified',
        showlegend=True,
        height=400,
        xaxis={'categoryorder': 'array', 'categoryarray': month_names}
    )

    st.plotly_chart(fig_timeline, use_container_width=True, key="monthly_timeline_chart")

    # Adicionar métricas resumidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌱 Total Planting", sum(planting))
    with col2:
        st.metric("🌾 Total Harvesting", sum(harvesting))
    with col3:
        st.metric("🔄 Both Activities", sum(both))
    with col4:
        st.metric("📊 Total Activities", total_activities)


def _render_crop_gantt_chart(filtered_data: dict, region: str) -> None:
    """Renderiza gráfico de Gantt para mostrar períodos de culturas."""
    st.markdown("##### 🗓️ Diagrama de Gantt - Períodos de Cultivo")

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
        # Find planting and harvesting periods
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

        # Create bars for harvesting
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

    # Create Gantt chart using Plotly
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
        height=max(400, len(gantt_data) * 40),
        barmode='overlay',
        showlegend=False
    )

    st.plotly_chart(fig_gantt, use_container_width=True, key="crop_gantt_chart")

    # Add summary information
    st.markdown("**Data Summary**")
    col1, col2 = st.columns(2)
    with col1:
        planting_count = len([g for g in gantt_data if 'Planting' in g['Task']])
        st.metric("🌱 Planting Periods", planting_count)
    with col2:
        harvest_count = len([g for g in gantt_data if 'Harvest' in g['Task']])
        st.metric("🌾 Harvest Periods", harvest_count)


def _render_temporal_density(filtered_data: dict) -> None:
    """Renderiza análise de densidade temporal."""
    st.markdown("##### 📊 Densidade Temporal de Atividades")

    if not filtered_data:
        st.info("📊 Dados insuficientes para análise de densidade.")
        return

    # Calcular densidade de atividades
    months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    density_matrix = []
    cultures = list(filtered_data.keys())[:15]  # Primeiras 15 culturas

    for crop_name in cultures:
        crop_data = filtered_data[crop_name]
        monthly_density = [0] * 12

        for state_entry in crop_data:
            calendar_data = state_entry.get('calendar', {})

            for i, month in enumerate(months_order):
                activity = calendar_data.get(month, '')
                if activity:
                    # Atribuir pesos diferentes para diferentes atividades
                    if activity in ['P', 'H']:
                        monthly_density[i] += 1
                    elif activity == 'PH':
                        monthly_density[i] += 2  # Peso maior para atividade dupla

        density_matrix.append(monthly_density)

    # Criar heatmap de densidade
    fig_density = go.Figure(data=go.Heatmap(
        z=density_matrix,
        x=month_names,
        y=cultures,
        colorscale='Viridis',
        colorbar={'title': 'Intensidade de Atividade'},
        hovertemplate='<b>%{y}</b><br>Mês: %{x}<br>Intensidade: %{z}<extra></extra>'
    ))

    fig_density.update_layout(
        title="Mapa de Calor - Densidade Temporal de Atividades",
        xaxis_title="Mês",
        yaxis_title="Culturas",
        height=max(400, len(cultures) * 25)
    )

    st.plotly_chart(fig_density, use_container_width=True, key="temporal_density_heatmap")


def _render_trends_analysis(crop_calendar: dict, states_info: dict) -> None:
    """Renderiza análise de tendências."""
    st.markdown("#### 📈 Análise de Tendências")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🌾 Culturas com Múltiplas Safras")
        # Análise de safras múltiplas
        crops_with_multiple_harvests = _analyze_multiple_harvests(crop_calendar)

        if crops_with_multiple_harvests:
            crops = list(crops_with_multiple_harvests.keys())
            harvests = list(crops_with_multiple_harvests.values())

            fig_harvests = px.bar(
                x=crops,
                y=harvests,
                title="Culturas com Múltiplas Safras",
                labels={'x': 'Cultura', 'y': 'Número de Safras'},
                color=harvests,
                color_continuous_scale='Plasma',
                text=harvests
            )
            fig_harvests.update_traces(texttemplate='%{text}', textposition='outside')
            fig_harvests.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_harvests, use_container_width=True, key="multiple_harvests_chart")
        else:
            st.info("📊 Nenhuma cultura com múltiplas safras identificada.")

    with col2:
        st.markdown("##### 🗺️ Distribuição Geográfica")
        # Análise de distribuição por estado
        state_distribution = _analyze_state_distribution(crop_calendar, states_info)

        if state_distribution:
            df_states = pd.DataFrame(list(state_distribution.items()),
                                   columns=['Estado', 'Culturas'])
            df_states = df_states.sort_values('Culturas', ascending=False).head(10)

            fig_states = px.bar(
                df_states,
                x='Estado',
                y='Culturas',
                title="Top 10 Estados - Diversidade de Culturas",
                labels={'Estado': 'Estado', 'Culturas': 'Número de Culturas'},
                color='Culturas',
                color_continuous_scale='Blues'
            )
            fig_states.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_states, use_container_width=True, key="state_distribution_chart")


def _aggregate_by_region(crop_calendar: dict, states_info: dict) -> dict[str, int]:
    """Agrega dados por região brasileira."""
    regional_data = {}

    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue

        for state_entry in crop_data:
            state_code = state_entry.get('state_code', '')
            region = states_info.get(state_code, {}).get('region', 'Desconhecida')

            if region not in regional_data:
                regional_data[region] = set()

            # Verificar se há atividades no calendário
            calendar_data = state_entry.get('calendar', {})
            if any(activity for activity in calendar_data.values() if activity):
                regional_data[region].add(crop_name)

    # Converter sets para contagem
    return {region: len(crops) for region, crops in regional_data.items() if crops}


def _extract_seasonal_data(crop_calendar: dict) -> dict:
    """Extrai dados sazonais de atividades."""
    seasonal_data = {}

    # Mapeamento de meses em inglês para português abreviado
    month_mapping = {
        'January': 'Jan', 'February': 'Fev', 'March': 'Mar', 'April': 'Abr',
        'May': 'Mai', 'June': 'Jun', 'July': 'Jul', 'August': 'Ago',
        'September': 'Set', 'October': 'Out', 'November': 'Nov', 'December': 'Dez'
    }

    for _crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue

        for state_entry in crop_data:
            calendar_data = state_entry.get('calendar', {})

            for month, activity in calendar_data.items():
                if activity and month in month_mapping:
                    month_short = month_mapping[month]

                    if month_short not in seasonal_data:
                        seasonal_data[month_short] = {'P': 0, 'H': 0, 'PH': 0}

                    if activity in ['P', 'H', 'PH']:
                        seasonal_data[month_short][activity] += 1

    return seasonal_data


def _analyze_multiple_harvests(crop_calendar: dict) -> dict[str, int]:
    """Analisa culturas com múltiplas safras."""
    harvest_counts = {}

    for crop_name in crop_calendar:
        if '(' in crop_name and ('harvest' in crop_name.lower() or 'safra' in crop_name.lower()):
            base_crop = crop_name.split('(')[0].strip()

            if base_crop not in harvest_counts:
                harvest_counts[base_crop] = 0

            harvest_counts[base_crop] += 1

    return {crop: count for crop, count in harvest_counts.items() if count > 1}


def _analyze_state_distribution(crop_calendar: dict, states_info: dict) -> dict[str, int]:
    """Analisa distribuição de culturas por estado."""
    state_distribution = {}

    for crop_name, crop_data in crop_calendar.items():
        if not isinstance(crop_data, list):
            continue

        for state_entry in crop_data:
            state_code = state_entry.get('state_code', '')
            state_name = states_info.get(state_code, {}).get('name', state_code)

            # Verificar se há atividades no calendário
            calendar_data = state_entry.get('calendar', {})
            if any(activity for activity in calendar_data.values() if activity):
                if state_name not in state_distribution:
                    state_distribution[state_name] = set()
                state_distribution[state_name].add(crop_name)

    # Converter sets para contagem
    return {state: len(crops) for state, crops in state_distribution.items() if crops}
