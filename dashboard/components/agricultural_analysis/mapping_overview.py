"""
Mapping Overview Component - Clean Version
==========================================

Componente para exibir overview básico dos dados CONAB
Apenas métricas gerais, gráficos detalhados em Crop Calendar e Availability

Author: LANDAGRI-B Project Team 
Date: 2025-08-08
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from pathlib import Path


def load_mapping_data():
    """Loads CONAB mapping data"""
    try:
        # First, try the complete file
        data_path = Path("data/json/agricultural_conab_mapping_data_complete.jsonc")
        if data_path.exists():
            with open(data_path, encoding='utf-8') as f:
                content = f.read()
                # Remove comentários JSONC
                content = re.sub(r'//.*', '', content)
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                return json.loads(content)
        
        # Fallback to the legacy file
        data_path = Path("data/conab_mapping_data.json")
        with open(data_path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ CONAB mapping data file not found!")
        return None
    except Exception as e:
        st.error(f"❌ Error loading mapping data: {e}")
        return None


def calculate_conab_metrics(data):
    """Calculates specific metrics from the CONAB calendar data"""
    if not data or 'crop_calendar' not in data:
        return {}
    
    # Count unique crops
    total_crops = len(data['crop_calendar'])
    
    # Count unique states
    all_states = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            all_states.add(state_info['state_code'])
    total_states = len(all_states)
    
    # Count regions
    all_regions = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            all_regions.add(state_info['region'])
    total_regions = len(all_regions)
    
    # Calcular completude dos dados
    total_cells = 0
    filled_cells = 0
    
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            calendar = state_info.get('calendar', {})
            total_cells += len(calendar)
            filled_cells += sum(1 for v in calendar.values() if v and v.strip())
    
    completeness = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Calcular período de cobertura
    coverage_years = "2020-2024"
    
    # Calcular área total estimada
    estimated_area = total_states * total_crops * 0.5
    
    return {
        'total_crops': total_crops,
        'total_states': total_states, 
        'total_regions': total_regions,
        'completeness': completeness,
        'total_calendar_entries': total_cells,
        'filled_entries': filled_cells,
        'coverage_years': coverage_years,
        'estimated_area': estimated_area
    }


def create_overview_summary_chart(data):
    """Creates a simple summary chart of crops"""
    if not data or 'crop_calendar' not in data:
        return None
    
    crop_data = []
    
    for crop_name, crop_states in data['crop_calendar'].items():
        states_count = len(crop_states)
        
        # Contar atividades totais
        total_activities = 0
        for state_info in crop_states:
            calendar = state_info.get('calendar', {})
            total_activities += sum(1 for v in calendar.values() if v and v.strip())
        
        # Use concise string operations and avoid repeated replace calls for performance
        crop_label = crop_name
        crop_label = crop_label.replace(' (1st harvest)', ' 1st')
        crop_label = crop_label.replace(' (2nd harvest)', ' 2nd')
        crop_label = crop_label.replace(' (3th harvest)', ' 3rd')

        crop_data.append({
            'Crop': crop_label,
            'States': states_count,
            'Activities': total_activities
        })
    
    df = pd.DataFrame(crop_data)
    
    # Optimize DataFrame usage and Plotly rendering for performance
    # Use categorical ordering for crops to avoid unnecessary sorting
    df['Crop'] = pd.Categorical(df['Crop'], categories=df['Crop'], ordered=True)

    fig = px.bar(
        df,
        x='Crop',
        y='States',
        title='Coverage: Crop versus Monitored States',
        labels={'States': 'Number of States', 'Crop': 'Crop'},
        color='Activities',
        color_continuous_scale='viridis'
    )
    # Reduce chart rendering overhead
    fig.update_traces(marker_line_width=0.5)
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig


def render_conab_mapping_metrics(data):
    """Renders main metrics of the CONAB calendar"""
    if not data:
        return
    
    metrics = calculate_conab_metrics(data)
    
    st.markdown("### General Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌾 Crops",
            f"{metrics.get('total_crops', 0)}",
            help="Total number of crops in the calendar"
        )
    
    with col2:
        st.metric(
            "🏛️ States", 
            f"{metrics.get('total_states', 0)}",
            help="Covered Brazilian States"
        )
    
    with col3:
        st.metric(
            "🗺️ Regions",
            f"{metrics.get('total_regions', 0)}",
            help="Brazilian Regions"
        )
    
    with col4:
        completeness = metrics.get('completeness', 0)
        st.metric(
            "✅ Completeness",
            f"{completeness:.1f}%",
            help="Percentage of filled data"
        )
    
    st.divider()
    
    # Métricas adicionais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📅 Period",
            metrics.get('coverage_years', 'N/A'),
            help="Data coverage period"
        )
    
    with col2:
        area = metrics.get('estimated_area', 0)
        st.metric(
            "📏 Estimated Area",
            f"{area:.1f} M ha",
            help="Total estimated monitored area"
        )
    
    with col3:
        entries = metrics.get('filled_entries', 0)
        st.metric(
            "📋 Valid Entries",
            f"{entries:,}",
            help="Filled calendar entries"
        )


def render_mapping_overview():
    """Main function to render the basic CONAB mapping overview"""
    # Carregar dados
    data = load_mapping_data()
    
    if not data:
        st.warning("⚠️ CONAB calendar data not available")
        return
    
    # Render main CONAB metrics
    render_conab_mapping_metrics(data)
    
    # Simple overview chart
    st.markdown("### Distribution by Crop")
    fig_overview = create_overview_summary_chart(data)
    if fig_overview:
        st.plotly_chart(fig_overview, use_container_width=True)
    
    # Basic information about data source
    st.markdown("### ℹ️ About the Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📋 Data Source:**
        - CONAB (National Supply Company)
        - National Agricultural Calendar
        - Planting and Harvesting Periods
        """)
    
    with col2:
        st.info("""
        **🎯 Detailed Analyses:**
        - **Crop Calendar**: Temporal charts and heatmaps
        - **Availability**: Availability analyses
        - Filters available by region and crop
        """)
    
    # Rodapé informativo
    st.markdown("---")
    st.markdown("""
    💡 **Tip**: For detailed analyses, go to the **Crop Calendar** and **Availability** tabs,
    where you will find interactive charts, region filters, and comprehensive temporal analyses.
    """)


if __name__ == "__main__":
    st.set_page_config(page_title="Overview CONAB", layout="wide")
    st.title("🔎 Overview - Dados CONAB")
    render_mapping_overview()
