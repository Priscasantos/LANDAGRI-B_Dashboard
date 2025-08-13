"""
Crop Distribution Charts
=======================

"""



import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional

# Import das funções seguras
from ...agricultural_loader import safe_get_data, validate_data_structure

# Modern color palette for consistency
MODERN_COLORS = {
    'primary': '#2E86C1',      # Professional blue
    'secondary': '#28B463',     # Fresh green
    'accent': '#F39C12',        # Warm orange
    'danger': '#E74C3C',        # Alert red
    'north': '#27AE60',         # North region
    'northeast': '#E67E22',     # Northeast region  
    'central_west': '#F39C12',  # Central-West region
    'southeast': '#2E86C1',     # Southeast region
    'south': '#8E44AD'          # South region
}

def get_state_acronym(state_name: str) -> str:
    """Convert full state name to acronym"""
    state_mapping = {
        'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
        'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES',
        'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
        'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
        'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
        'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC',
        'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
    }
    return state_mapping.get(state_name, state_name)

def get_brazilian_region(state_acronym: str) -> str:
    """Map state acronym to Brazilian region (in English)"""
    region_mapping = {
        'AC': 'North', 'AP': 'North', 'AM': 'North', 'PA': 'North', 'RO': 'North', 'RR': 'North', 'TO': 'North',
        'AL': 'Northeast', 'BA': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast', 'PB': 'Northeast', 
        'PE': 'Northeast', 'PI': 'Northeast', 'RN': 'Northeast', 'SE': 'Northeast',
        'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
        'ES': 'Southeast', 'MG': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
        'PR': 'South', 'RS': 'South', 'SC': 'South'
    }
    return region_mapping.get(state_acronym, 'Unknown')


def create_crop_type_distribution_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates a modern, comprehensive crop type distribution chart with enhanced metrics.
    
    Shows not just state count but also total agricultural activities, coverage intensity,
    and provides interactive insights about crop distribution patterns.
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Modern interactive Plotly figure or None if no data
    """
    try:
        # Safe access to calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for crop type distribution")
            return None

        # Enhanced data collection - count multiple metrics per crop
        crop_metrics = {}
        
        for crop, states_data in crop_calendar.items():
            metrics = {
                'states_count': 0,
                'total_activities': 0,
                'planting_activities': 0,
                'harvesting_activities': 0,
                'coverage_intensity': 0,
                'states_list': []
            }
            
            if isinstance(states_data, dict):
                # Structure: crop -> {state: activities}
                metrics['states_count'] = len(states_data)
                
                for state, activities in states_data.items():
                    # Convert state name to acronym
                    state_acronym = get_state_acronym(state)
                    metrics['states_list'].append(state_acronym)
                    
                    if isinstance(activities, dict):
                        # Count planting and harvesting months
                        planting = safe_get_data(activities, 'planting_months') or []
                        harvesting = safe_get_data(activities, 'harvesting_months') or []
                        
                        if isinstance(planting, list):
                            metrics['planting_activities'] += len(planting)
                        if isinstance(harvesting, list):
                            metrics['harvesting_activities'] += len(harvesting)
                            
                        metrics['total_activities'] += len(planting) + len(harvesting)
                        
                        # Calculate intensity (activities per state)
                        if metrics['states_count'] > 0:
                            metrics['coverage_intensity'] = metrics['total_activities'] / metrics['states_count']
                            
            elif isinstance(states_data, list):
                # CONAB structure: crop -> [state_entries]
                metrics['states_count'] = len(states_data)
                
                for state_entry in states_data:
                    if isinstance(state_entry, dict):
                        state_name = state_entry.get('state_name', '')
                        calendar = state_entry.get('calendar', {})
                        
                        if state_name:
                            # Convert state name to acronym
                            state_acronym = get_state_acronym(state_name)
                            metrics['states_list'].append(state_acronym)
                        
                        # Count calendar activities
                        active_months = sum(1 for activity in calendar.values() if activity and activity.strip())
                        metrics['total_activities'] += active_months
                        
                        # Estimate coverage intensity
                        if metrics['states_count'] > 0:
                            metrics['coverage_intensity'] = metrics['total_activities'] / metrics['states_count']
            else:
                # Fallback for simple structures
                metrics['states_count'] = 1 if states_data else 0
                metrics['total_activities'] = 1 if states_data else 0
                metrics['coverage_intensity'] = 1 if states_data else 0
            
            crop_metrics[crop] = metrics

        if not crop_metrics:
            st.info("📊 No crop types found in data")
            return None

        # Create enhanced DataFrame
        chart_data = []
        for crop, metrics in crop_metrics.items():
            chart_data.append({
                'Crop': crop,
                'States_Count': metrics['states_count'],
                'Total_Activities': metrics['total_activities'],
                'Coverage_Intensity': round(metrics['coverage_intensity'], 2),
                'Planting_Activities': metrics['planting_activities'],
                'Harvesting_Activities': metrics['harvesting_activities'],
                'States_List': ', '.join(metrics['states_list'][:5]) + ('...' if len(metrics['states_list']) > 5 else '')
            })
        
        df = pd.DataFrame(chart_data)
        df = df.sort_values('Total_Activities', ascending=True)

        # Create modern subplot with multiple metrics
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("📍 Geographic Coverage", "🎚️ Activity Intensity"),
            specs=[[{"secondary_y": False}, {"secondary_y": True}]],
            column_widths=[0.6, 0.4]
        )

        # Primary chart: States count with activity overlay
        bar1 = go.Bar(
            y=df['Crop'],
            x=df['States_Count'],
            orientation='h',
            name='States Coverage',
            marker=dict(
                color=df['Total_Activities'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Total Activities",
                    x=0.45,
                    len=0.8
                )
            ),
            text=[f"{states} states<br>{activities} activities" 
                  for states, activities in zip(df['States_Count'], df['Total_Activities'])],
            textposition='outside',
            customdata=df[['States_List', 'Total_Activities', 'Coverage_Intensity']],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "States: %{x}<br>"
                "Total Activities: %{customdata[1]}<br>"
                "Intensity: %{customdata[2]} act/state<br>"
                "States: %{customdata[0]}<br>"
                "<extra></extra>"
            )
        )
        
        fig.add_trace(bar1, row=1, col=1)

        # Secondary chart: Coverage intensity
        bar2 = go.Bar(
            y=df['Crop'],
            x=df['Coverage_Intensity'],
            orientation='h',
            name='Activity Intensity',
            marker=dict(
                color=df['Coverage_Intensity'],
                colorscale='RdYlBu_r',
                showscale=False
            ),
            text=[f"{intensity:.1f}" for intensity in df['Coverage_Intensity']],
            textposition='outside',
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Intensity: %{x:.2f} activities/state<br>"
                "<extra></extra>"
            )
        )
        
        fig.add_trace(bar2, row=1, col=2)

        # Enhanced layout with modern design
        fig.update_layout(
            title={
                'text': "🌾 Modern Crop Distribution Analysis",
                'font': {'size': 20, 'family': 'Arial Black'},
                'x': 0.5,
                'xanchor': 'center'
            },
            height=max(500, 400 + (len(df) * 20)),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            margin=dict(t=80, b=60, l=150, r=150)
        )

        # Customize axes
        fig.update_xaxes(
            title_text="Number of States",
            gridcolor='lightgray',
            gridwidth=1,
            row=1, col=1
        )
        
        fig.update_xaxes(
            title_text="Activities per State",
            gridcolor='lightgray',
            gridwidth=1,
            row=1, col=2
        )
        
        fig.update_yaxes(
            title_text="Crop Types",
            gridcolor='lightgray',
            gridwidth=1,
            row=1, col=1
        )

        # Add annotations for insights
        max_coverage_crop = df.loc[df['States_Count'].idxmax(), 'Crop']
        max_intensity_crop = df.loc[df['Coverage_Intensity'].idxmax(), 'Crop']
        
        fig.add_annotation(
            text=f"📈 Highest Coverage: {max_coverage_crop}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=11, color="darkgreen"),
            bgcolor="rgba(144, 238, 144, 0.3)",
            bordercolor="darkgreen",
            borderwidth=1
        )
        
        fig.add_annotation(
            text=f"🎯 Highest Intensity: {max_intensity_crop}",
            xref="paper", yref="paper",
            x=0.02, y=0.92,
            showarrow=False,
            font=dict(size=11, color="darkblue"),
            bgcolor="rgba(173, 216, 230, 0.3)",
            bordercolor="darkblue",
            borderwidth=1
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating modern crop distribution chart: {e}")
        return None


def create_crop_diversity_by_region_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Creates a modern, comprehensive crop diversity chart by region with enhanced analytics.
    
    Shows regional diversity patterns with detailed insights about crop distribution,
    concentration analysis, and regional agricultural profiles.
    
    Args:
        filtered_data: Filtered agricultural calendar data
        
    Returns:
        go.Figure: Modern interactive Plotly figure or None if no data
    """
    try:
        # Safe access to calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for regional diversity")
            return None

        # Enhanced regional analysis with detailed metrics
        region_metrics = {}
        
        for crop, states_data in crop_calendar.items():
            # Verificar se é estrutura CONAB (lista de estados) ou IBGE (dict)
            if isinstance(states_data, list):
                # Estrutura CONAB: lista de estados com calendários
                for state_entry in states_data:
                    if isinstance(state_entry, dict):
                        state_name = state_entry.get('state_name', '')
                        # Convert state name to acronym and then to region
                        state_acronym = get_state_acronym(state_name)
                        region = get_brazilian_region(state_acronym)
                        calendar = state_entry.get('calendar', {})
                        
                        # Verificar se há atividade neste estado
                        active_months = sum(1 for activity in calendar.values() if activity and activity.strip())
                        
                        if active_months > 0:
                            if region not in region_metrics:
                                region_metrics[region] = {
                                    'crop_diversity': set(),
                                    'total_activities': 0,
                                    'states_count': set(),
                                    'crop_details': []
                                }
                            
                            region_metrics[region]['crop_diversity'].add(crop)
                            region_metrics[region]['total_activities'] += active_months
                            region_metrics[region]['states_count'].add(state_acronym)
                            region_metrics[region]['crop_details'].append(f"{crop} ({state_acronym})")
                            
            elif isinstance(states_data, dict):
                # Estrutura IBGE: dict de estados
                for state, activities in states_data.items():
                    # Convert state name to acronym and then to region
                    state_acronym = get_state_acronym(state)
                    region = get_brazilian_region(state_acronym)
                    
                    if region not in region_metrics:
                        region_metrics[region] = {
                            'crop_diversity': set(),
                            'total_activities': 0,
                            'states_count': set(),
                            'crop_details': []
                        }
                    
                    region_metrics[region]['crop_diversity'].add(crop)
                    region_metrics[region]['states_count'].add(state_acronym)
                    region_metrics[region]['crop_details'].append(f"{crop} ({state_acronym})")
                    
                    # Count activities if detailed structure available
                    if isinstance(activities, dict):
                        planting = safe_get_data(activities, 'planting_months') or []
                        harvesting = safe_get_data(activities, 'harvesting_months') or []
                        region_metrics[region]['total_activities'] += len(planting) + len(harvesting)
                    else:
                        region_metrics[region]['total_activities'] += 1

        if not region_metrics:
            st.info("📊 No regional diversity found in data")
            return None

        # Create enhanced DataFrame with comprehensive metrics
        chart_data = []
        for region, metrics in region_metrics.items():
            diversity_count = len(metrics['crop_diversity'])
            states_count = len(metrics['states_count'])
            total_activities = metrics['total_activities']
            
            # Calculate diversity index (diversity per state)
            diversity_index = diversity_count / states_count if states_count > 0 else 0
            
            # Calculate activity intensity
            activity_intensity = total_activities / states_count if states_count > 0 else 0
            
            # Get top crops for this region
            crop_list = list(metrics['crop_diversity'])[:5]
            crop_summary = ', '.join(crop_list) + ('...' if len(metrics['crop_diversity']) > 5 else '')
            
            chart_data.append({
                'Region': region,
                'Crop_Diversity': diversity_count,
                'States_Count': states_count,
                'Total_Activities': total_activities,
                'Diversity_Index': round(diversity_index, 2),
                'Activity_Intensity': round(activity_intensity, 2),
                'Crop_Summary': crop_summary,
                'Detail_Info': f"{diversity_count} crops in {states_count} states"
            })

        df = pd.DataFrame(chart_data)
        df = df.sort_values('Crop_Diversity', ascending=True)

        # Create single panel chart (removed scatter plot)
        fig = go.Figure()

        # Horizontal bar chart with diversity ranking
        bar = go.Bar(
            y=df['Region'],
            x=df['Crop_Diversity'],
            orientation='h',
            name='Crop Diversity',
            marker=dict(
                color=df['Activity_Intensity'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(
                    title="Activity<br>Intensity",
                    len=0.8
                )
            ),
            text=[f"{div} crops<br>{states} states" 
                  for div, states in zip(df['Crop_Diversity'], df['States_Count'])],
            textposition='outside',
            customdata=df[['Crop_Summary', 'Total_Activities', 'Diversity_Index', 'Detail_Info']],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Crop Diversity: %{x}<br>"
                "Total Activities: %{customdata[1]}<br>"
                "Diversity Index: %{customdata[2]} crops/state<br>"
                "Main Crops: %{customdata[0]}<br>"
                "<extra></extra>"
            )
        )
        
        fig.add_trace(bar)

        # Enhanced layout with modern design
        fig.update_layout(
            title={
                'text': "🌱 Regional Crop Diversity Analysis",
                'font': {'size': 20, 'family': 'Arial Black'},
                'x': 0.5,
                'xanchor': 'center'
            },
            height=max(500, 400 + (len(df) * 15)),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            margin=dict(t=80, b=60, l=120, r=120),
            xaxis_title="Number of Different Crops",
            yaxis_title="Brazilian Regions"
        )

        # Customize axes
        fig.update_xaxes(
            gridcolor='lightgray',
            gridwidth=1
        )
        
        fig.update_yaxes(
            gridcolor='lightgray',
            gridwidth=1
        )

        # Add insights annotations
        max_diversity_region = df.loc[df['Crop_Diversity'].idxmax(), 'Region']
        max_intensity_region = df.loc[df['Activity_Intensity'].idxmax(), 'Region']
        
        fig.add_annotation(
            text=f"🏆 Most Diverse: {max_diversity_region}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=11, color="darkgreen"),
            bgcolor="rgba(144, 238, 144, 0.3)",
            bordercolor="darkgreen",
            borderwidth=1
        )
        
        fig.add_annotation(
            text=f"⚡ Most Active: {max_intensity_region}",
            xref="paper", yref="paper",
            x=0.02, y=0.92,
            showarrow=False,
            font=dict(size=11, color="darkorange"),
            bgcolor="rgba(255, 165, 0, 0.3)",
            bordercolor="darkorange",
            borderwidth=1
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating modern regional diversity chart: {e}")
        return None


def create_number_of_crops_per_region_chart(filtered_data: dict) -> Optional[go.Figure]:
    """
    Cria gráfico do número de culturas por região com detalhamento.
    
    Equivalente ao: number_of_crops_per_region.png do old_calendar/national/
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
        
    Returns:
        go.Figure: Plotly figure ou None if no data
    """
    try:
        # Acesso seguro aos calendar data
        crop_calendar = safe_get_data(filtered_data, 'crop_calendar') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for regional count")
            return None

        # Conta total de atividades por região usando acesso seguro
        region_activities = {}
        for crop, states_data in crop_calendar.items():
            if isinstance(states_data, dict):
                for state, activities in states_data.items():
                    # Convert state name to acronym and then to region
                    state_acronym = get_state_acronym(state)
                    region = get_brazilian_region(state_acronym)
                    
                    if region not in region_activities:
                        region_activities[region] = 0
                    
                    # Acesso seguro às atividades
                    if isinstance(activities, dict):
                        planting_months = safe_get_data(activities, 'planting_months') or []
                        harvesting_months = safe_get_data(activities, 'harvesting_months') or []
                        
                        if planting_months:
                            region_activities[region] += len(planting_months)
                        if harvesting_months:
                            region_activities[region] += len(harvesting_months)
                    else:
                        # Fallback para estruturas simples
                        region_activities[region] += 1
            elif isinstance(states_data, list):
                # Handle CONAB format
                for state_entry in states_data:
                    if isinstance(state_entry, dict):
                        state_name = state_entry.get('state_name', '')
                        if state_name:
                            state_acronym = get_state_acronym(state_name)
                            region = get_brazilian_region(state_acronym)
                            
                            if region not in region_activities:
                                region_activities[region] = 0
                            
                            calendar = state_entry.get('calendar', {})
                            active_months = sum(1 for activity in calendar.values() if activity and activity.strip())
                            region_activities[region] += active_months

        if not region_activities:
            st.info("🗺 No regional activity found in data")
            return None

        # Cria DataFrame
        df = pd.DataFrame(list(region_activities.items()), columns=['Região', 'Total_Atividades'])
        df = df.sort_values('Total_Atividades', ascending=True)

        # Cria gráfico de barras horizontais
        fig = px.bar(
            df,
            x='Total_Atividades',
            y='Região',
            orientation='h',
            title="📈 Total Agricultural Activities by Region",
            labels={
                'Total_Atividades': 'Total de Atividades (Plantio + Colheita)',
                'Região': 'Região Brasileira'
            },
            color='Total_Atividades',
            color_continuous_scale='Blues'
        )

        # Personaliza layout
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Total Activities (Planting + Harvesting)",
            yaxis_title="Brazilian Region",
            coloraxis_showscale=False
        )

        # Adiciona valores nas barras
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside'
        )

        return fig

    except Exception as e:
        st.error(f"❌ Error creating gráfico de número de culturas por região: {e}")
        return None


def render_crop_distribution_charts(filtered_data: dict) -> None:
    """
    Renderiza todos os gráficos de distribuição de culturas.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.markdown("### 📊 Crop Distribution and Diversity")
    
    # Gráfico modernizado de distribuição de tipos de cultura (tela inteira)
    fig1 = create_crop_type_distribution_chart(filtered_data)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True, key="crop_type_distribution_chart")
    
    # Gráfico modernizado de diversidade regional (tela inteira)
    fig2 = create_crop_diversity_by_region_chart(filtered_data)
    if fig2:
        st.plotly_chart(fig2, use_container_width=True, key="crop_diversity_by_region_chart")
    
    # Gráfico de atividades regionais (tela inteira para consistência)
    fig3 = create_number_of_crops_per_region_chart(filtered_data)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True, key="number_of_crops_per_region_chart")
