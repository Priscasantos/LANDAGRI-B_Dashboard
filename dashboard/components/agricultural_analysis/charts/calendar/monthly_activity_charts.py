"""
Monthly Activity Charts
======================

Module for consolidated monthly activity charts from old_calendar.
Implements visualizations for temporal analysis of agricultural activities.

Author: LULC Initiatives Dashboard
Date: 2025-08-07
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Optional

# Import das funções seguras
from ...agricultural_loader import safe_get_data, validate_data_structure


def _get_month_abbreviation(month_name: str) -> str:
    """Convert month name to abbreviation."""
    month_mapping = {
        'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
        'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
        'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
    }
    return month_mapping.get(month_name, month_name[:3])


def _get_full_month_name(month_abbr: str) -> str:
    """Convert month abbreviation to full name."""
    abbr_mapping = {
        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
    }
    return abbr_mapping.get(month_abbr, month_abbr)


def create_total_activities_per_month_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates total activities per month chart.
    
    Equivalent to: total_activities_per_month.png from old_calendar/national/
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for monthly activities")
            return None

        # Inicializa contadores mensais (mapeando nomes completos para abreviações)
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_activities = {month: 0 for month in months}

        # Conta atividades por mês usando a estrutura real do JSON
        for crop_name, states_list in crop_calendar.items():
            if isinstance(states_list, list):
                for state_data in states_list:
                    if isinstance(state_data, dict):
                        calendar = safe_get_data(state_data, 'calendar') or {}
                        
                        # Conta atividades (P=Planting, H=Harvest, PH=Both)
                        for month_full_name, activity in calendar.items():
                            if activity and activity.strip():  # Se tem alguma atividade
                                month_abbr = month_mapping.get(month_full_name)
                                if month_abbr and month_abbr in monthly_activities:
                                    # Conta cada atividade: P=1, H=1, PH=2
                                    if 'PH' in activity:
                                        monthly_activities[month_abbr] += 2  # Plantio + Colheita
                                    elif 'P' in activity or 'H' in activity:
                                        monthly_activities[month_abbr] += 1

        if not any(monthly_activities.values()):
            st.info("📊 No monthly activity found in the data")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(monthly_activities.items()), columns=['Month', 'Total_Activities'])

        # Creates line chart
        fig = px.line(
            df,
            x='Month',
            y='Total_Activities',
            title="📅 Total Agricultural Activities per Month",
            labels={
                'Total_Activities': 'Total Number of Activities',
                'Month': 'Month of Year'
            },
            markers=True
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            xaxis_title="Month of Year",
            yaxis_title="Total Number of Activities",
            showlegend=False
        )

        # Adiciona valores nos pontos
        fig.update_traces(
            mode='lines+markers+text',
            text=df['Total_Activities'],
            textposition='top center'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico de atividades mensais: {e}")
        return None


def create_planting_vs_harvesting_per_month_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates comparative planting vs harvesting chart per month.
    
    Equivalent to: planting_vs_harvesting_per_month.png from old_calendar/national/
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for planting vs harvesting comparison")
            return None

        # Inicializa contadores mensais (mapeando nomes completos para abreviações)
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        planting_counts = dict.fromkeys(months, 0)
        harvesting_counts = dict.fromkeys(months, 0)

        # Conta atividades por mês usando a estrutura real do JSON
        for _crop_name, states_list in crop_calendar.items():
            if isinstance(states_list, list):
                for state_data in states_list:
                    if isinstance(state_data, dict):
                        calendar = safe_get_data(state_data, 'calendar') or {}
                        
                        # Conta atividades (P=Planting, H=Harvest, PH=Both)
                        for month_full_name, activity in calendar.items():
                            if activity and activity.strip():  # Se tem alguma atividade
                                month_abbr = month_mapping.get(month_full_name)
                                if month_abbr and month_abbr in planting_counts:
                                    # Conta plantio
                                    if 'P' in activity:
                                        planting_counts[month_abbr] += 1
                                    # Conta colheita
                                    if 'H' in activity:
                                        harvesting_counts[month_abbr] += 1

        # Cria DataFrame
        df = pd.DataFrame({
            'Month': months,
            'Planting': [planting_counts[month] for month in months],
            'Harvesting': [harvesting_counts[month] for month in months]
        })

        # Creates grouped bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='🌱 Planting',
            x=df['Month'],
            y=df['Planting'],
            marker_color='lightgreen',
            text=df['Planting'],
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='🌾 Harvesting',
            x=df['Month'],
            y=df['Harvesting'],
            marker_color='orange',
            text=df['Harvesting'],
            textposition='outside'
        ))

        # Personaliza layout
        fig.update_layout(
            title="🌱📅 Planting vs Harvesting Comparison by Month",
            xaxis_title="Month of Year",
            yaxis_title="Number of Activities",
            barmode='group',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico plantio vs colheita: {e}")
        return None


def create_simultaneous_planting_harvesting_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico de atividades simultâneas de plantio e colheita.
    
    Equivalente ao: simultaneous_planting_harvesting.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 No calendar data available for simultaneous activities")
            return None

        # Inicializa contadores mensais
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        simultaneous_activities = {month: 0 for month in months}

        # Identifica atividades simultâneas por mês
        for crop, states_data in crop_calendar.items():
            # Handle case where states_data is a list, not a dict
            if isinstance(states_data, list):
                for state_info in states_data:
                    if not isinstance(state_info, dict):
                        continue
                    calendar = state_info.get('calendar', {})
                    for month, activity in calendar.items():
                        if activity and ('P' in str(activity) and 'H' in str(activity)):
                            month_abbr = _get_month_abbreviation(month)
                            if month_abbr in simultaneous_activities:
                                simultaneous_activities[month_abbr] += 1
            else:
                # Original logic for dict format
                for state, activities in states_data.items():
                    planting_months = set(activities.get('planting_months', []))
                    harvesting_months = set(activities.get('harvesting_months', []))
                    
                    # Encontra meses com atividades simultâneas
                    simultaneous_months = planting_months.intersection(harvesting_months)
                    
                    for month in simultaneous_months:
                        if month in simultaneous_activities:
                            simultaneous_activities[month] += 1

        if not any(simultaneous_activities.values()):
            st.info("📊 No simultaneous activity found in the data")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(simultaneous_activities.items()), columns=['Month', 'Simultaneous_Activities'])

        # Creates bar chart
        fig = px.bar(
            df,
            x='Month',
            y='Simultaneous_Activities',
            title="🔄 Simultaneous Planting and Harvesting Activities by Month",
            labels={
                'Simultaneous_Activities': 'Number of Simultaneous Activities',
                'Month': 'Month of Year'
            },
            color='Simultaneous_Activities',
            color_continuous_scale='Reds'
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            xaxis_title="Month of Year",
            yaxis_title="Number of Simultaneous Activities",
            showlegend=False,
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating simultaneous activities chart: {e}")
        return None


def create_monthly_activities_stacked_bar_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates a stacked bar chart showing monthly activities distribution (P, H, PH).
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for monthly activities")
            return None

        # Inicializa contadores mensais
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Inicializa contadores para cada tipo de atividade
        seasonal_data = {}
        for month in months:
            seasonal_data[month] = {'P': 0, 'H': 0, 'PH': 0}

        # Conta atividades por mês usando a estrutura real do JSON
        for crop_name, states_list in crop_calendar.items():
            if isinstance(states_list, list):
                for state_data in states_list:
                    if isinstance(state_data, dict):
                        calendar = safe_get_data(state_data, 'calendar') or {}
                        
                        # Conta atividades por tipo
                        for month_full_name, activity in calendar.items():
                            if activity and activity.strip():  # Se tem alguma atividade
                                month_abbr = month_mapping.get(month_full_name)
                                if month_abbr and month_abbr in seasonal_data:
                                    # Classifica a atividade
                                    if 'PH' in activity:
                                        seasonal_data[month_abbr]['PH'] += 1
                                    elif 'P' in activity:
                                        seasonal_data[month_abbr]['P'] += 1
                                    elif 'H' in activity:
                                        seasonal_data[month_abbr]['H'] += 1

        # Verifica se há dados
        has_data = any(
            seasonal_data[month]['P'] > 0 or 
            seasonal_data[month]['H'] > 0 or 
            seasonal_data[month]['PH'] > 0 
            for month in months
        )
        
        if not has_data:
            st.info("📊 No monthly activity found in the data")
            return None

        # Cria DataFrame no formato adequado para o gráfico empilhado
        df_seasonal = pd.DataFrame(seasonal_data).T.fillna(0)
        df_seasonal = df_seasonal.reset_index()
        df_seasonal.rename(columns={'index': 'Mês'}, inplace=True)
        
        # Cria gráfico de barras empilhadas
        fig = px.bar(
            df_seasonal,
            x='Mês',
            y=['P', 'H', 'PH'],
            title="📊 Distribuição Mensal de Atividades",
            labels={
                'value': 'Número de Atividades', 
                'variable': 'Tipo',
                'Mês': 'Mês'
            },
            color_discrete_map={
                'P': '#2E8B57',   # Verde para Plantio
                'H': '#FF6B35',   # Laranja para Colheita  
                'PH': '#4682B4'   # Azul para Plantio e Colheita
            }
        )
        
        # Personaliza layout
        fig.update_layout(
            height=400,
            xaxis_title="Mês",
            yaxis_title="Número de Atividades",
            xaxis_tickangle=45,
            legend=dict(
                title="Tipo de Atividade",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Adiciona hover personalizado
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>" +
                         "Mês: %{x}<br>" +
                         "Atividades: %{y}<br>" +
                         "<extra></extra>"
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating monthly activities stacked bar chart: {e}")
        return None


def create_planting_harvesting_periods_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates planting and harvesting periods chart.
    
    Equivalent to: planting_harvesting_periods.png from old_calendar/national/
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Plotly figure or None if no data
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 No calendar data available for planting and harvesting periods")
            return None

        # Prepares data for periods heatmap
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        heatmap_data = []
        
        for crop, states_data in crop_calendar.items():
            crop_row_planting = []
            crop_row_harvesting = []
            
            for month in months:
                # Count states with planting this month
                planting_count = 0
                harvesting_count = 0
                
                # Handle case where states_data is a list, not a dict
                if isinstance(states_data, list):
                    for state_info in states_data:
                        if not isinstance(state_info, dict):
                            continue
                        calendar = state_info.get('calendar', {})
                        month_full_name = _get_full_month_name(month)
                        activity = calendar.get(month_full_name, '')
                        if activity:
                            if 'P' in str(activity):
                                planting_count += 1
                            if 'H' in str(activity):
                                harvesting_count += 1
                else:
                    # Original logic for dict format
                    for state, activities in states_data.items():
                        if month in activities.get('planting_months', []):
                            planting_count += 1
                        if month in activities.get('harvesting_months', []):
                            harvesting_count += 1
                
                crop_row_planting.append(planting_count)
                crop_row_harvesting.append(harvesting_count)
            
            # Adds data to heatmap
            heatmap_data.append({
                'Crop': f"{crop} (Planting)",
                'Type': 'Planting',
                **{months[i]: crop_row_planting[i] for i in range(len(months))}
            })
            
            heatmap_data.append({
                'Crop': f"{crop} (Harvesting)",
                'Type': 'Harvesting',
                **{months[i]: crop_row_harvesting[i] for i in range(len(months))}
            })

        if not heatmap_data:
            st.info("📊 No periods found in the data")
            return None

        # Cria DataFrame
        df = pd.DataFrame(heatmap_data)
        
        # Prepares matrix for heatmap
        z_data = df[months].values
        y_labels = df['Crop'].tolist()

        # Creates heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=months,
            y=y_labels,
            colorscale='RdYlGn',
            text=z_data,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))

        # Personaliza layout
        fig.update_layout(
            title="🗓️ Planting and Harvesting Periods by Crop",
            xaxis_title="Month of Year",
            yaxis_title="Crop (Activity Type)",
            height=400 + (len(y_labels) * 15)
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating planting and harvesting periods chart: {e}")
        return None


def render_monthly_activity_charts(filtered_data: dict) -> None:
    """
    Renders all monthly activity charts.
    
    Args:
        filtered_data: Filtered agricultural calendar data
    """
    st.markdown("### 📅 Monthly Activities Analysis")
    
    # First row: total activities and planting vs harvesting comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = create_total_activities_per_month_chart(filtered_data)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = create_planting_vs_harvesting_per_month_chart(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    # Second row: simultaneous activities
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = create_simultaneous_planting_harvesting_chart(filtered_data)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.info("📊 Space reserved for additional metrics")
    
    # Third row: complete periods (full width)
    st.markdown("#### 🗓️ Detailed Planting and Harvesting Periods")
    fig4 = create_planting_harvesting_periods_chart(filtered_data)
    if fig4:
        st.plotly_chart(fig4, use_container_width=True)
