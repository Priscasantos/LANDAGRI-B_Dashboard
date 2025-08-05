"""
Crop Availability Analysis Component
===================================

Análise detalhada de disponibilidade de culturas por região e período.
Baseado em dados do calendário agrícola e monitoramento CONAB.

Funcionalidades:
- Matriz de disponibilidade por cultura/região
- Análise de dupla safra vs safra única  
- Score de disponibilidade temporal
- Gráficos de cobertura espacial
- Comparação entre fontes de dados
- Análise de padrões sazonais

Inspiração: USDA iUSD, FAO GIEWS, Crop Monitor
Autor: Dashboard Agricultural Analysis
Data: 2025-08-05
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# Importar componentes do projeto
from .agricultural_loader import (
    load_conab_detailed_data,
    load_conab_crop_calendar
)


def render_crop_availability():
    """
    Renderizar análise completa de disponibilidade de culturas.
    """
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
            Detailed analysis of crop temporal and spatial availability patterns
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Carregar dados
    with st.spinner("🔄 Loading availability data..."):
        calendar_data = load_conab_crop_calendar()
        conab_data = load_conab_detailed_data()

    if not calendar_data and not conab_data:
        st.error("❌ No crop availability data available for analysis.")
        st.info("🔧 Please check if the data files are available in the data/json/ folder")
        return

    # Seleção de fonte de dados
    st.markdown("### 📊 Data Source Selection")
    data_source = st.radio(
        "Select data source for availability analysis:",
        ["📅 Agricultural Calendar", "🌾 CONAB Data", "🔄 Both Sources"],
        index=2,
        horizontal=True,
        help="Choose which data source to use for the availability analysis"
    )

    st.markdown("---")

    # Análise por fonte de dados
    if data_source in ["📅 Agricultural Calendar", "🔄 Both Sources"] and calendar_data:
        st.markdown("## 📅 Calendar-Based Availability")
        _render_calendar_availability_section(calendar_data)
        
        if data_source == "🔄 Both Sources":
            st.markdown("---")

    if data_source in ["🌾 CONAB Data", "🔄 Both Sources"] and conab_data:
        st.markdown("## 🌾 CONAB-Based Availability") 
        _render_conab_availability_section(conab_data)

    # Análise comparativa se ambas as fontes estão disponíveis
    if data_source == "🔄 Both Sources" and calendar_data and conab_data:
        st.markdown("---")
        st.markdown("## 🔄 Comparative Analysis")
        _render_comparative_availability_analysis(calendar_data, conab_data)


def _render_calendar_availability_section(calendar_data: dict) -> None:
    """Renderizar seção de análise de disponibilidade do calendário."""
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.info("📊 No calendar data available for availability analysis")
            return

        # Preparar dados de disponibilidade
        availability_data = []
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_code = state_entry.get('state_code', '')
                state_name = state_entry.get('state_name', state_code)
                calendar_entry = state_entry.get('calendar', {})
                
                # Analisar atividades mensais
                monthly_activities = {}
                for month, activity in calendar_entry.items():
                    if activity and activity.strip():
                        monthly_activities[month] = activity
                
                # Calcular métricas
                active_months = len(monthly_activities)
                planting_months = sum(1 for activity in monthly_activities.values() if 'P' in activity)
                harvest_months = sum(1 for activity in monthly_activities.values() if 'H' in activity)
                
                availability_data.append({
                    'crop': crop,
                    'state': state_name,
                    'state_code': state_code,
                    'active_months': active_months,
                    'planting_months': planting_months,
                    'harvest_months': harvest_months,
                    'availability_score': active_months / 12.0,
                    'activity_intensity': len([a for a in monthly_activities.values() if len(a) > 1])
                })

        if not availability_data:
            st.warning("⚠️ No availability data could be processed from calendar")
            return

        df_availability = pd.DataFrame(availability_data)
        
        # Layout em colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗺️ Availability Score by State")
            _create_state_availability_chart(df_availability)
        
        with col2:
            st.markdown("#### 🌱 Availability Score by Crop")
            _create_crop_availability_chart(df_availability)

        # Heatmap de disponibilidade
        st.markdown("#### 🔥 Crop-State Availability Heatmap")
        _create_availability_heatmap(df_availability)

        # Análise temporal
        st.markdown("#### 📊 Temporal Distribution Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            _create_monthly_distribution_chart(crop_calendar)
        
        with col2:
            _create_seasonal_intensity_chart(df_availability)

        # Tabela de resumo
        st.markdown("#### 📋 Availability Summary")
        _create_availability_summary_table(df_availability)

    except Exception as e:
        st.error(f"Error in calendar availability analysis: {e}")


def _render_conab_availability_section(conab_data: dict) -> None:
    """Renderizar seção de análise de disponibilidade CONAB."""
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            st.info("📊 No CONAB data available for availability analysis")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗺️ CONAB Availability Matrix")
            _create_conab_availability_matrix(conab_data)
        
        with col2:
            st.markdown("#### 🔄 Single vs Double Cropping Analysis")
            _create_double_crop_analysis(detailed_coverage)

        # Análise de cobertura temporal
        st.markdown("#### ⏳ Temporal Coverage Analysis")
        _create_temporal_coverage_analysis(detailed_coverage)

        # Análise de qualidade dos dados
        st.markdown("#### 📊 Data Quality Metrics")
        _create_data_quality_metrics(detailed_coverage)

    except Exception as e:
        st.error(f"Error in CONAB availability analysis: {e}")


def _render_comparative_availability_analysis(calendar_data: dict, conab_data: dict) -> None:
    """Renderizar análise comparativa entre fontes de dados."""
    
    st.markdown("#### 🔄 Data Source Comparison")
    
    try:
        # Comparar coberturas de culturas
        calendar_crops = set(calendar_data.get('crop_calendar', {}).keys())
        conab_crops = set(conab_data.get('CONAB Crop Monitoring Initiative', {})
                         .get('detailed_crop_coverage', {}).keys())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📅 Calendar Crops", len(calendar_crops))
            
        with col2:
            st.metric("🌾 CONAB Crops", len(conab_crops))
            
        with col3:
            common_crops = calendar_crops & conab_crops
            st.metric("🔄 Common Crops", len(common_crops))

        # Diagrama de Venn
        if calendar_crops and conab_crops:
            _create_crop_coverage_venn(calendar_crops, conab_crops)

        # Análise de cobertura temporal
        if common_crops:
            st.markdown("#### 📊 Coverage Comparison for Common Crops")
            _create_coverage_comparison_chart(calendar_data, conab_data, common_crops)

    except Exception as e:
        st.error(f"Error in comparative analysis: {e}")


def _create_state_availability_chart(df_availability: pd.DataFrame) -> None:
    """Criar gráfico de disponibilidade por estado."""
    
    state_avg = df_availability.groupby('state')['availability_score'].agg(['mean', 'count']).reset_index()
    state_avg.columns = ['state', 'avg_score', 'crop_count']
    state_avg = state_avg.sort_values('avg_score', ascending=False).head(15)
    
    fig = px.bar(
        state_avg,
        x='avg_score',
        y='state',
        orientation='h',
        title="Average Availability Score by State",
        labels={'avg_score': 'Availability Score', 'state': 'State'},
        color='avg_score',
        color_continuous_scale='Viridis',
        hover_data={'crop_count': True}
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _create_crop_availability_chart(df_availability: pd.DataFrame) -> None:
    """Criar gráfico de disponibilidade por cultura."""
    
    crop_avg = df_availability.groupby('crop')['availability_score'].agg(['mean', 'count']).reset_index()
    crop_avg.columns = ['crop', 'avg_score', 'state_count']
    crop_avg = crop_avg.sort_values('avg_score', ascending=False)
    
    fig = px.bar(
        crop_avg,
        x='crop',
        y='avg_score',
        title="Average Availability Score by Crop",
        labels={'avg_score': 'Availability Score', 'crop': 'Crop'},
        color='avg_score',
        color_continuous_scale='Plasma',
        hover_data={'state_count': True}
    )
    
    fig.update_layout(height=400, xaxis_tickangle=45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _create_availability_heatmap(df_availability: pd.DataFrame) -> None:
    """Criar heatmap de disponibilidade cultura x estado."""
    
    # Criar pivot para heatmap
    pivot_data = df_availability.pivot_table(
        index='crop', 
        columns='state', 
        values='availability_score', 
        aggfunc='mean'
    ).fillna(0)
    
    # Limitar para evitar gráfico muito grande
    if len(pivot_data.index) > 20:
        # Pegar as 20 culturas com maior variação
        crop_variance = pivot_data.var(axis=1).sort_values(ascending=False)
        pivot_data = pivot_data.loc[crop_variance.head(20).index]
    
    if len(pivot_data.columns) > 15:
        # Pegar os 15 estados com maior cobertura
        state_coverage = pivot_data.sum(axis=0).sort_values(ascending=False)
        pivot_data = pivot_data[state_coverage.head(15).index]
    
    fig = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='RdYlGn',
        title="Crop-State Availability Matrix",
        labels={'x': 'State', 'y': 'Crop', 'color': 'Availability Score'},
        aspect='auto'
    )
    
    fig.update_layout(
        height=max(400, len(pivot_data.index) * 25),
        xaxis_tickangle=45
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _create_monthly_distribution_chart(crop_calendar: dict) -> None:
    """Criar gráfico de distribuição mensal de atividades."""
    
    monthly_count = {}
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month in months:
        monthly_count[month] = {'Planting': 0, 'Harvesting': 0, 'Other': 0}
    
    for crop, crop_states in crop_calendar.items():
        for state_entry in crop_states:
            calendar_entry = state_entry.get('calendar', {})
            
            for month, activity in calendar_entry.items():
                if activity and activity.strip():
                    if 'P' in activity:
                        monthly_count[month]['Planting'] += 1
                    if 'H' in activity:
                        monthly_count[month]['Harvesting'] += 1
                    if activity not in ['P', 'H', 'PH', 'HP']:
                        monthly_count[month]['Other'] += 1
    
    df_monthly = pd.DataFrame(monthly_count).T
    df_monthly = df_monthly.reset_index()
    df_monthly.columns = ['Month', 'Planting', 'Harvesting', 'Other']
    
    fig = px.bar(
        df_monthly,
        x='Month',
        y=['Planting', 'Harvesting', 'Other'],
        title="Monthly Activity Distribution",
        labels={'value': 'Number of Activities', 'variable': 'Activity Type'},
        color_discrete_map={
            'Planting': '#10b981',
            'Harvesting': '#f59e0b', 
            'Other': '#6b7280'
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def _create_seasonal_intensity_chart(df_availability: pd.DataFrame) -> None:
    """Criar gráfico de intensidade sazonal."""
    
    # Calcular intensidade por cultura
    intensity_data = df_availability.groupby('crop').agg({
        'active_months': 'mean',
        'planting_months': 'mean',
        'harvest_months': 'mean',
        'activity_intensity': 'mean'
    }).reset_index()
    
    fig = px.scatter(
        intensity_data,
        x='active_months',
        y='activity_intensity',
        size='planting_months',
        color='harvest_months',
        hover_name='crop',
        title="Crop Seasonal Intensity",
        labels={
            'active_months': 'Average Active Months',
            'activity_intensity': 'Activity Intensity',
            'planting_months': 'Planting Months',
            'harvest_months': 'Harvest Months'
        },
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def _create_availability_summary_table(df_availability: pd.DataFrame) -> None:
    """Criar tabela de resumo da disponibilidade."""
    
    summary_stats = df_availability.groupby('crop').agg({
        'state': 'count',
        'active_months': 'mean',
        'planting_months': 'mean',
        'harvest_months': 'mean',
        'availability_score': 'mean'
    }).round(2)
    
    summary_stats.columns = [
        'States Covered', 
        'Avg Active Months', 
        'Avg Planting Months',
        'Avg Harvest Months',
        'Availability Score'
    ]
    
    summary_stats = summary_stats.sort_values('Availability Score', ascending=False)
    st.dataframe(summary_stats, use_container_width=True)


def _create_conab_availability_matrix(conab_data: dict) -> None:
    """Criar matriz de disponibilidade CONAB."""
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            st.info("No CONAB data available for matrix")
            return
        
        matrix_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            all_regions = set(first_crop_years.keys()) | set(second_crop_years.keys())
            
            for region in all_regions:
                first_years = first_crop_years.get(region, [])
                second_years = second_crop_years.get(region, [])
                
                # Calcular score de disponibilidade
                has_first = len(first_years) > 0
                has_second = len(second_years) > 0
                
                availability_score = 0
                if has_first and has_second:
                    availability_score = 2  # Dupla safra
                elif has_first:
                    availability_score = 1  # Safra única
                
                matrix_data.append({
                    'crop': crop,
                    'region': region,
                    'availability': availability_score,
                    'years_coverage': len(set(first_years + second_years))
                })
        
        if not matrix_data:
            st.info("No matrix data available")
            return
        
        df_matrix = pd.DataFrame(matrix_data)
        pivot_matrix = df_matrix.pivot(index='crop', columns='region', values='availability')
        pivot_matrix = pivot_matrix.fillna(0)
        
        fig = px.imshow(
            pivot_matrix.values,
            x=pivot_matrix.columns,
            y=pivot_matrix.index,
            color_continuous_scale=['white', 'lightblue', 'darkblue'],
            title="CONAB Availability Matrix",
            labels={'x': 'Region', 'y': 'Crop', 'color': 'Availability'},
            zmin=0, zmax=2
        )
        
        fig.update_layout(
            height=max(400, len(pivot_matrix.index) * 30),
            xaxis_tickangle=45
        )
        
        # Adicionar anotações personalizadas
        annotations = []
        for i, _crop in enumerate(pivot_matrix.index):
            for j, _region in enumerate(pivot_matrix.columns):
                value = pivot_matrix.iloc[i, j]
                if float(value) == 0:
                    text = "No data"
                elif float(value) == 1:
                    text = "Single crop"
                else:
                    text = "Double crop"

                annotations.append(
                    {
                        "x": j, "y": i, "text": text,
                        "showarrow": False,
                        "font": {"color": "white" if float(value) > 1 else "black", "size": 10}
                    }
                )
        
        fig.update_layout(annotations=annotations)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating CONAB matrix: {e}")


def _create_double_crop_analysis(detailed_coverage: dict) -> None:
    """Criar análise de dupla safra."""
    
    double_crop_data = []
    
    for crop, crop_data in detailed_coverage.items():
        first_crop_years = crop_data.get('first_crop_years', {})
        second_crop_years = crop_data.get('second_crop_years', {})
        
        first_regions = len([r for r, years in first_crop_years.items() if years])
        second_regions = len([r for r, years in second_crop_years.items() if years])
        
        double_crop_data.append({
            'crop': crop,
            'single_crop': max(0, first_regions - second_regions),
            'double_crop': second_regions
        })
    
    if double_crop_data:
        df_double = pd.DataFrame(double_crop_data)
        
        fig = px.bar(
            df_double,
            x='crop',
            y=['single_crop', 'double_crop'],
            title="Single vs Double Cropping Regions",
            labels={'value': 'Number of Regions', 'variable': 'Cropping Type'},
            color_discrete_map={
                'single_crop': '#3b82f6',
                'double_crop': '#10b981'
            },
            barmode='stack'
        )
        
        fig.update_layout(height=400, xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)


def _create_temporal_coverage_analysis(detailed_coverage: dict) -> None:
    """Criar análise de cobertura temporal."""
    
    temporal_data = []
    
    for crop, crop_data in detailed_coverage.items():
        first_crop_years = crop_data.get('first_crop_years', {})
        second_crop_years = crop_data.get('second_crop_years', {})
        
        all_years = set()
        for years_list in first_crop_years.values():
            all_years.update(years_list)
        for years_list in second_crop_years.values():
            all_years.update(years_list)
        
        if all_years:
            temporal_data.append({
                'crop': crop,
                'start_year': min(all_years),
                'end_year': max(all_years),
                'span_years': max(all_years) - min(all_years) + 1,
                'total_regions': len(set(first_crop_years.keys()) | set(second_crop_years.keys()))
            })
    
    if temporal_data:
        df_temporal = pd.DataFrame(temporal_data)
        
        fig = px.scatter(
            df_temporal,
            x='span_years',
            y='total_regions',
            size='end_year',
            color='start_year',
            hover_name='crop',
            title="Temporal Coverage vs Regional Coverage",
            labels={
                'span_years': 'Years Span',
                'total_regions': 'Total Regions',
                'end_year': 'End Year',
                'start_year': 'Start Year'
            },
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def _create_data_quality_metrics(detailed_coverage: dict) -> None:
    """Criar métricas de qualidade dos dados."""
    
    quality_data = []
    
    for crop, crop_data in detailed_coverage.items():
        first_crop_years = crop_data.get('first_crop_years', {})
        second_crop_years = crop_data.get('second_crop_years', {})
        
        # Calcular métricas de qualidade
        total_entries = len(first_crop_years) + len(second_crop_years)
        non_empty_entries = len([r for r, years in first_crop_years.items() if years]) + \
                          len([r for r, years in second_crop_years.items() if years])
        
        completeness = non_empty_entries / total_entries if total_entries > 0 else 0
        
        all_years = []
        for years_list in first_crop_years.values():
            all_years.extend(years_list)
        for years_list in second_crop_years.values():
            all_years.extend(years_list)
        
        temporal_density = len(set(all_years)) / max(1, len(all_years)) if all_years else 0
        
        quality_data.append({
            'crop': crop,
            'completeness': completeness,
            'temporal_density': temporal_density,
            'total_entries': total_entries,
            'coverage_score': completeness * temporal_density
        })
    
    if quality_data:
        df_quality = pd.DataFrame(quality_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_comp = px.bar(
                df_quality.sort_values('completeness', ascending=False),
                x='crop',
                y='completeness',
                title="Data Completeness by Crop",
                labels={'completeness': 'Completeness Score'},
                color='completeness',
                color_continuous_scale='RdYlGn'
            )
            fig_comp.update_layout(height=350, xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col2:
            fig_dens = px.bar(
                df_quality.sort_values('temporal_density', ascending=False),
                x='crop',
                y='temporal_density', 
                title="Temporal Density by Crop",
                labels={'temporal_density': 'Temporal Density'},
                color='temporal_density',
                color_continuous_scale='Plasma'
            )
            fig_dens.update_layout(height=350, xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_dens, use_container_width=True)


def _create_crop_coverage_venn(calendar_crops: set, conab_crops: set) -> None:
    """Criar diagrama de Venn para cobertura de culturas."""
    
    # Como Plotly não tem Venn nativo, criar gráfico de barras comparativo
    only_calendar = calendar_crops - conab_crops
    only_conab = conab_crops - calendar_crops
    common = calendar_crops & conab_crops
    
    data = {
        'Category': ['Only Calendar', 'Only CONAB', 'Both Sources'],
        'Count': [len(only_calendar), len(only_conab), len(common)],
        'Color': ['#3b82f6', '#10b981', '#f59e0b']
    }
    
    fig = px.bar(
        data,
        x='Category',
        y='Count',
        color='Category',
        title="Crop Coverage by Data Source",
        color_discrete_map={
            'Only Calendar': '#3b82f6',
            'Only CONAB': '#10b981', 
            'Both Sources': '#f59e0b'
        }
    )
    
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _create_coverage_comparison_chart(calendar_data: dict, conab_data: dict, common_crops: set) -> None:
    """Criar gráfico de comparação de cobertura para culturas comuns."""
    
    comparison_data = []
    
    calendar_coverage = calendar_data.get('crop_calendar', {})
    conab_coverage = conab_data.get('CONAB Crop Monitoring Initiative', {}).get('detailed_crop_coverage', {})
    
    for crop in common_crops:
        calendar_states = len(calendar_coverage.get(crop, []))
        
        conab_regions = 0
        if crop in conab_coverage:
            first_crop = conab_coverage[crop].get('first_crop_years', {})
            second_crop = conab_coverage[crop].get('second_crop_years', {})
            conab_regions = len(set(first_crop.keys()) | set(second_crop.keys()))
        
        comparison_data.append({
            'crop': crop,
            'calendar_coverage': calendar_states,
            'conab_coverage': conab_regions
        })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        fig = px.scatter(
            df_comparison,
            x='calendar_coverage',
            y='conab_coverage',
            hover_name='crop',
            title="Coverage Comparison: Calendar vs CONAB",
            labels={
                'calendar_coverage': 'Calendar Coverage (States)',
                'conab_coverage': 'CONAB Coverage (Regions)'
            }
        )
        
        # Adicionar linha diagonal de referência
        max_coverage = max(df_comparison['calendar_coverage'].max(), 
                          df_comparison['conab_coverage'].max())
        fig.add_shape(
            type="line",
            x0=0, y0=0, x1=max_coverage, y1=max_coverage,
            line={"color": "red", "width": 2, "dash": "dash"},
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    render_crop_availability()
