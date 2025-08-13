"""
Agricultural Analysis - Dashboard with Real Agricultural Data
============================================================

Comprehensive dashboard for Brazilian agricultural analysis using real agricultural
data, with CONAB as the data source.

Features:
- Integration with the app.py sidebar menu (Agriculture Overview, Crop Calendar, Agriculture Availability)
- Real agricultural data (agricultural_data_complete.jsonc)
- Consolidated overview with Brazilian metrics
- Interactive crop calendar by state and crop
- Data availability and quality analysis

Structure following app.py:
- Agriculture Overview: Consolidated metrics and general visualizations
- Crop Calendar: Interactive calendar by state/crop with consolidated tabs
- Agriculture Availability: Data quality and availability

Author: LANDAGRI-B Project Team 
Date: 2025-08-07
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Adicionar project root ao path

# Modular component imports
from dashboard.components.agricultural_analysis.agricultural_loader import (
    load_agricultural_data,
    load_agricultural_crop_calendar
)
from dashboard.components.agricultural_analysis.helpers import (
    extract_crop_calendar_data,
    create_monthly_activity_chart,
    create_regional_distribution_chart,
    create_crop_calendar_heatmap,
    validate_calendar_data,
    get_crop_summary,
    get_regional_summary
)
from dashboard.components.agricultural_analysis.agriculture_overview.agricultural_overview import render_agricultural_overview
from dashboard.components.agricultural_analysis.charts.availability import (
    render_calendar_availability_analysis,
    render_crop_availability_tab
)
from dashboard.components.agricultural_analysis.charts.calendar import (
    render_complete_calendar_analysis
)


def run():
    """
    Main function that responds to pages selected in the app.py sidebar menu.
    Checks st.session_state.current_page to determine which page to render.
    """
    
    # Load agricultural data
    with st.spinner("🔄 Loading agricultural data..."):
        try:
            agricultural_data = load_agricultural_data()
            calendar_data = load_agricultural_crop_calendar()
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            agricultural_data = {}
            calendar_data = {}
    
    # Check data availability
    has_agricultural = bool(agricultural_data)
    has_calendar = bool(calendar_data)
    
    if not has_agricultural and not has_calendar:
        st.error("❌ No agricultural data available")
        return
    
    # Get current page from session state (set by app.py)
    current_page = getattr(st.session_state, 'current_page', 'Agriculture Overview')
    
    # Render page based on sidebar menu selection
    if current_page == "Agriculture Overview":
        _render_agriculture_overview_page(calendar_data, agricultural_data)
    elif current_page == "Crop Calendar":
        _render_crop_calendar_page(calendar_data, agricultural_data)
    elif current_page == "Agriculture Availability":
        _render_agriculture_availability_page(calendar_data, agricultural_data)
    else:
        # Fallback to default page
        _render_agriculture_overview_page(calendar_data, agricultural_data)

def _render_agriculture_overview_page(calendar_data: dict, agricultural_data: dict):
    """Render Agriculture Overview page - consolidated overview with metrics."""
    # Page header
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
            Consolidated view of Brazilian agriculture with agricultural data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process calendar data using helpers
    df_calendar = extract_crop_calendar_data(agricultural_data)
    
    # Main metrics
    _render_main_metrics_new(df_calendar, agricultural_data)
    
    st.markdown("---")
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ Regional Distribution")
        try:
            fig_regional = create_regional_distribution_chart(df_calendar)
            if fig_regional:
                st.plotly_chart(fig_regional, use_container_width=True)
            else:
                st.warning("⚠️ Could not generate regional distribution chart")
        except Exception as e:
            st.error(f"❌ Error in regional distribution chart: {e}")
    
    with col2:
        st.markdown("### 📊 Monthly Activities")
        try:
            fig_monthly = create_monthly_activity_chart(df_calendar)
            if fig_monthly:
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.warning("⚠️ Could not generate monthly activities chart")
        except Exception as e:
            st.error(f"❌ Error in monthly activities chart: {e}")
    
    # Calendar overview
    st.markdown("### 🗓️ National Agricultural Calendar")
    try:
        fig_calendar = create_crop_calendar_heatmap(df_calendar)
        if fig_calendar:
            st.plotly_chart(fig_calendar, use_container_width=True)
        else:
            st.warning("⚠️ Could not generate calendar heatmap")
    except Exception as e:
        st.error(f"❌ Error in calendar heatmap: {e}")


def _render_main_metrics_new(df_calendar: pd.DataFrame, agricultural_data: dict):
    """Render main metrics using new helpers."""
    validation = validate_calendar_data(agricultural_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌾 Crops",
            value=validation.get('total_crops', 0),
            help="Total crops in agricultural calendar"
        )
    
    with col2:
        st.metric(
            label="🏛️ States",
            value=validation.get('total_states', 0),
            help="States covered by the data"
        )
    
    with col3:
        st.metric(
            label="🗺️ Regions",
            value=validation.get('total_regions', 0),
            help="Brazilian regions covered"
        )
    
    with col4:
        completeness = validation.get('data_completeness', 0)
        st.metric(
            label="✅ Completeness",
            value=f"{completeness:.1f}%",
            help="Percentage of data filled in the calendar"
        )


def _render_crop_calendar_page(calendar_data: dict, agricultural_data: dict):
    """Render Crop Calendar page with consolidated chart tabs using new helpers."""
    
    # Page header
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
            📅 Agricultural Calendar
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Consolidated agricultural calendar - Agricultural data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not agricultural_data or 'crop_calendar' not in agricultural_data:
        st.warning("⚠️ Agricultural calendar data not available")
        return
    
    # Process calendar data using helpers
    df_calendar = extract_crop_calendar_data(agricultural_data)
    
    if df_calendar.empty:
        st.error("❌ Could not process calendar data")
        return
    
    # Create tabs for different types of analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distribution & Diversity",
        "📅 Monthly Activities",
        "🗓️ National Matrix",
        "🌍 Regional Analysis",
        "🔧 Interactive Calendars"
    ])
    
    # Tab 1: Crop Distribution & Diversity
    with tab1:
        st.markdown("### 📊 Crop Distribution & Diversity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                fig_regional = create_regional_distribution_chart(df_calendar)
                if fig_regional:
                    st.plotly_chart(fig_regional, use_container_width=True)
                else:
                    st.warning("⚠️ Insufficient data for regional distribution")
            except Exception as e:
                st.error(f"❌ Error in regional distribution chart: {e}")
        
        with col2:
            # Crop summary
            crop_summary = get_crop_summary(df_calendar)
            if not crop_summary.empty:
                st.dataframe(
                    crop_summary,
                    use_container_width=True,
                    column_config={
                        'crop': 'Crop',
                        'activity_type': 'Activity Type',
                        'states_count': 'States',
                        'regions_count': 'Regions'
                    }
                )
            else:
                st.warning("⚠️ Crop summary not available")
    
    # Tab 2: Monthly Activities
    with tab2:
        st.markdown("### 📅 Monthly Activities Analysis")
        
        try:
            fig_monthly = create_monthly_activity_chart(df_calendar)
            if fig_monthly:
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.warning("⚠️ No monthly activities found in data")
        except Exception as e:
            st.error(f"❌ Error creating monthly activities chart: {e}")
        
        # Regional summary
        st.markdown("#### Regional Summary")
        regional_summary = get_regional_summary(df_calendar)
        if not regional_summary.empty:
            st.dataframe(
                regional_summary,
                use_container_width=True,
                column_config={
                    'region': 'Region',
                    'activity_type': 'Activity Type',
                    'crops_count': 'Crops',
                    'states_count': 'States'
                }
            )
        else:
            st.warning("⚠️ Regional summary not available")
    
    # Tab 3: National Matrix
    with tab3:
        st.markdown("### 🗓️ National Agricultural Calendar Matrix")
        
        # Consolidated matrix
        st.markdown("#### 📋 Consolidated Matrix")
        try:
            fig_heatmap = create_crop_calendar_heatmap(df_calendar)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning("⚠️ Insufficient data for consolidated matrix")
        except Exception as e:
            st.error(f"❌ Error creating national matrix: {e}")
        
        # Detailed heatmap by crop
        st.markdown("#### 🔥 Detailed Heatmap")
        crops = df_calendar['crop'].unique().tolist() if not df_calendar.empty else []
        
        if crops:
            selected_crop = st.selectbox("Select a crop:", crops)
            try:
                fig_crop_heatmap = create_crop_calendar_heatmap(df_calendar, selected_crop)
                if fig_crop_heatmap:
                    st.plotly_chart(fig_crop_heatmap, use_container_width=True)
                else:
                    st.warning(f"⚠️ Insufficient data for {selected_crop}")
            except Exception as e:
                st.error(f"❌ Error creating heatmap for {selected_crop}: {e}")
        else:
            st.warning("⚠️ No crops found")
    
    # Tab 4: Regional Analysis
    with tab4:
        st.markdown("### 🌍 Regional Comparison")
        
        # Filter out BRAZIL and get regions
        regions = df_calendar['region'].unique().tolist() if not df_calendar.empty else []
        regions = [r for r in regions if r != 'BRAZIL']  # Filter out BRAZIL
        
        if regions:
            # Create columns for dropdown selectors
            col1, col2 = st.columns(2)
            
            with col1:
                region1 = st.selectbox(
                    "Select first region:",
                    options=[""] + regions,
                    index=0,
                    key="region_compare_1"
                )
            
            with col2:
                region2 = st.selectbox(
                    "Select second region:",
                    options=[""] + regions,
                    index=0,
                    key="region_compare_2"
                )
            
            # Multi-region comparison option
            st.markdown("**Or select multiple regions:**")
            selected_regions = st.multiselect(
                "Select multiple regions to compare:",
                regions,
                default=[],
                key="multi_region_compare"
            )
            
            # Determine which regions to use
            regions_to_compare = []
            if region1 and region1 != "":
                regions_to_compare.append(region1)
            if region2 and region2 != "" and region2 != region1:
                regions_to_compare.append(region2)
            if selected_regions:
                regions_to_compare.extend([r for r in selected_regions if r not in regions_to_compare])
            
            if regions_to_compare:
                df_filtered = df_calendar[df_calendar['region'].isin(regions_to_compare)]
                
                try:
                    fig_comparison = create_regional_distribution_chart(df_filtered)
                    if fig_comparison:
                        st.plotly_chart(fig_comparison, use_container_width=True)
                        
                        # Add summary table
                        st.markdown("#### 📊 Regional Summary")
                        summary_data = []
                        for region in regions_to_compare:
                            region_data = df_filtered[df_filtered['region'] == region]
                            if not region_data.empty:
                                summary_data.append({
                                    'Region': region,
                                    'Total Crops': len(region_data['crop'].unique()),
                                    'Activities': len(region_data),
                                    'Planting Activities': len(region_data[region_data['activity_type'] == 'planting']),
                                    'Harvest Activities': len(region_data[region_data['activity_type'] == 'harvest'])
                                })
                        
                        if summary_data:
                            import pandas as pd
                            summary_df = pd.DataFrame(summary_data)
                            st.dataframe(summary_df, use_container_width=True)
                    else:
                        st.warning("⚠️ Insufficient data for comparison")
                except Exception as e:
                    st.error(f"❌ Error in regional comparison: {e}")
            else:
                st.info("👆 Select at least one region to compare")
        else:
            st.warning("⚠️ Regional data not available")
    
    # Tab 5: Interactive Calendar  
    with tab5:
        st.markdown("### 🔧 Interactive Calendars")
        
        # Data validation
        validation = validate_calendar_data(agricultural_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Crops", validation.get('total_crops', 0))
        with col2:
            st.metric("States", validation.get('total_states', 0))
        with col3:
            completeness = validation.get('data_completeness', 0)
            st.metric("Completeness", f"{completeness:.1f}%")
        
        # Display issues if any
        issues = validation.get('issues', [])
        if issues:
            with st.expander("⚠️ Problems Found", expanded=False):
                for issue in issues:
                    st.warning(f"• {issue}")
        
        # Original calendar component fallback
        st.markdown("#### Original Calendar Component")
        try:
            render_complete_calendar_analysis({'crop_calendar': agricultural_data.get('crop_calendar', {})})
        except Exception as e:
            st.error(f"❌ Original calendar component not available: {e}")
    
    # Footer with information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <strong>📅 Brazilian Agricultural Calendar</strong><br>
        Data processed and visualized with specialized helper functions<br>
        Source: Agricultural Data
    </div>
    """, unsafe_allow_html=True)


def _render_agriculture_availability_page(calendar_data: dict, agricultural_data: dict):
    """Render Agriculture Availability page with consolidated tab structure using new helpers."""
    
    # Page header
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
            📋 Agricultural Data Availability
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Consolidated analysis of agricultural data availability and quality
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Validate input data
    if not calendar_data and not agricultural_data:
        st.warning("⚠️ Agricultural availability data not available.")
        return
    
    # Process data using helpers
    df_calendar = extract_crop_calendar_data(agricultural_data) if agricultural_data else pd.DataFrame()
    validation = validate_calendar_data(agricultural_data) if agricultural_data else {}
    
    # Main metrics
    st.markdown("### 📊 Main Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_crops = validation.get('total_crops', 0)
        st.metric("🌾 Crops", total_crops, help="Total crops in calendar")
    
    with col2:
        total_states = validation.get('total_states', 0)
        st.metric("🗺️ States", total_states, help="States covered")
    
    with col3:
        total_regions = validation.get('total_regions', 0)
        st.metric("🌍 Regions", total_regions, help="Brazilian regions")
    
    with col4:
        completeness = validation.get('data_completeness', 0)
        st.metric("✅ Completeness", f"{completeness:.1f}%", 
                 help="Percentage of data filled")
    
    st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Calendar Availability",
        "🗺️ Geographic Coverage",
        "📊 Data Quality",
        "🔍 Detailed Analysis"
    ])
    
    # Tab 1: Calendar Availability
    with tab1:
        st.markdown("### 📅 Calendar Availability Analysis")
        
        if not df_calendar.empty:
            # Monthly distribution
            try:
                fig_monthly = create_monthly_activity_chart(df_calendar)
                if fig_monthly:
                    st.plotly_chart(fig_monthly, use_container_width=True)
                else:
                    st.warning("⚠️ Could not generate monthly activities chart")
            except Exception as e:
                st.error(f"❌ Erro no gráfico mensal: {e}")
            
            # Availability by activity type
            if 'activity_type' in df_calendar.columns:
                activity_counts = df_calendar['activity_type'].value_counts()
                st.markdown("#### Distribution by Activity Type")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig_pie = px.pie(
                        values=activity_counts.values,
                        names=activity_counts.index,
                        title="Tipos de Atividades no Calendário"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        pd.DataFrame({
                            'Tipo': activity_counts.index,
                            'Quantidade': activity_counts.values
                        }),
                        use_container_width=True
                    )
        else:
            st.warning("⚠️ Calendar data not available for analysis")
    
    # Tab 2: Geographic Coverage
    with tab2:
        st.markdown("### 🗺️ Geographic Coverage")
        
        if not df_calendar.empty:
            try:
                fig_regional = create_regional_distribution_chart(df_calendar)
                if fig_regional:
                    st.plotly_chart(fig_regional, use_container_width=True)
                else:
                    st.warning("⚠️ Insufficient data for geographic coverage")
            except Exception as e:
                st.error(f"❌ Erro no gráfico de cobertura: {e}")
            
            # Coverage details
            st.markdown("#### Detalhes da Cobertura")
            coverage_data = []
            
            for region in df_calendar['region'].unique():
                region_data = df_calendar[df_calendar['region'] == region]
                crops = region_data['crop'].nunique()
                states = region_data['state_code'].nunique()
                activities = len(region_data)
                
                coverage_data.append({
                    'Region': region,
                    'Crops': crops,
                    'States': states,
                    'Activities': activities
                })
            
            if coverage_data:
                st.dataframe(pd.DataFrame(coverage_data), use_container_width=True)
        else:
            st.warning("⚠️ Geographic data not available")
    
    # Tab 3: Data Quality
    with tab3:
        st.markdown("### 📊 Data Quality")
        
        # Data validation results
        if validation:
            issues = validation.get('issues', [])
            
            if issues:
                st.markdown("#### ⚠️ Problems Found")
                for issue in issues:
                    st.warning(f"• {issue}")
            else:
                st.success("✅ Nenhum problema detectado na estrutura dos dados")
            
            # Quality metrics
            st.markdown("#### 📈 Quality Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                missing_pct = validation.get('missing_data_percentage', 0)
                st.metric(
                    "📉 Dados Faltantes",
                    f"{missing_pct:.1f}%",
                    delta=f"{100-missing_pct:.1f}% completo",
                    delta_color="inverse"
                )
            
            with col2:
                completeness_pct = validation.get('data_completeness', 0)
                st.metric(
                    "✅ Integridade",
                    f"{completeness_pct:.1f}%",
                    help="Percentage of valid data"
                )
        else:
            st.warning("⚠️ Data validation not available")
    
    # Tab 4: Detailed Analysis
    with tab4:
        st.markdown("### 🔍 Detailed Analysis")
        
        if not df_calendar.empty:
            # Summary tables
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Summary by Crop")
                crop_summary = get_crop_summary(df_calendar)
                if not crop_summary.empty:
                    st.dataframe(
                        crop_summary,
                        use_container_width=True,
                        column_config={
                            'crop': 'Crop',
                            'activity_type': 'Activity',
                            'states_count': 'States',
                            'regions_count': 'Regions'
                        }
                    )
                else:
                    st.warning("⚠️ Crop summary not available")
            
            with col2:
                st.markdown("#### Regional Summary")
                regional_summary = get_regional_summary(df_calendar)
                if not regional_summary.empty:
                    st.dataframe(
                        regional_summary,
                        use_container_width=True,
                        column_config={
                            'region': 'Region',
                            'activity_type': 'Activity',
                            'crops_count': 'Crops',
                            'states_count': 'States'
                        }
                    )
                else:
                    st.warning("⚠️ Regional summary not available")
            
            # Raw data sample
            st.markdown("#### 📋 Data Sample")
            if len(df_calendar) > 0:
                sample_size = min(100, len(df_calendar))
                st.dataframe(
                    df_calendar.head(sample_size),
                    use_container_width=True,
                    column_config={
                        'crop': 'Cultura',
                        'state_name': 'Estado',
                        'region': 'Region',
                        'month': 'Month',
                        'activity': 'Atividade',
                        'activity_type': 'Tipo'
                    }
                )
                
                st.caption(f"Mostrando {sample_size} de {len(df_calendar)} registros")
            else:
                st.warning("⚠️ Data not available for visualization")
        else:
            st.warning("⚠️ Detailed analysis not available - insufficient data")
    
    # Footer with data source information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <strong>📊 Agricultural Data Availability Analysis</strong><br>
        Automated processing and validation using specialized helper functions<br>
        Source: Agricultural Data
    </div>
    """, unsafe_allow_html=True)


def _render_main_metrics(calendar_data: dict, agricultural_data: dict):
    """Render main metrics at the top of the page."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Number of crops in the calendar
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            total_calendar_crops = len(crop_calendar)
        else:
            total_calendar_crops = 0
        st.metric("🌾 Crops (Calendar)", total_calendar_crops)
    
    with col2:
        # Number of agricultural crops from main data
        if agricultural_data:
            total_ag_crops = len(agricultural_data.get('crops', {}))
        else:
            total_ag_crops = 0
        st.metric("📊 Crops (Data)", total_ag_crops)
    
    with col3:
        # Number of states/regions
        if calendar_data:
            states = calendar_data.get('states', {})
            total_states = len(states)
        elif agricultural_data:
            # Try to extract states from agricultural data
            df_calendar = extract_crop_calendar_data(agricultural_data)
            total_states = df_calendar['state_code'].nunique() if not df_calendar.empty else 0
        else:
            total_states = 0
        st.metric("🗺️ States", total_states)
    
    with col4:
        # Data completeness or quality indicator
        if agricultural_data:
            validation = validate_calendar_data(agricultural_data)
            completeness = validation.get('data_completeness', 0)
            st.metric("✅ Completude", f"{completeness:.1f}%")
        else:
            st.metric("📅 Disponibilidade", "0%")


def _render_regional_distribution_chart(agricultural_data: dict):
    """Render regional distribution chart using agricultural data."""
    
    try:
        if not agricultural_data:
            st.warning("⚠️ Dados agrícolas não disponíveis")
            return
        
        # Extract calendar data and create regional distribution
        df_calendar = extract_crop_calendar_data(agricultural_data)
        
        if df_calendar.empty:
            st.warning("⚠️ Calendar data not found")
            return
        
        # Use the helper function to create regional distribution chart
        fig_regional = create_regional_distribution_chart(df_calendar)
        
        if fig_regional:
            st.plotly_chart(fig_regional, use_container_width=True)
        else:
            st.info("📊 Insufficient data for regional chart")
        
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico regional: {e}")


def _render_crop_diversity_chart(agricultural_data: dict, calendar_data: dict):
    """Render crop diversity chart using agricultural data."""
    
    try:
        crops_data = []
        
        # Calendar data
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            for crop in crop_calendar.keys():
                crops_data.append({
                    'Crop': crop,
                    'Source': 'Agricultural Calendar',
                    'Available': 1
                })
        
        # Agricultural data
        if agricultural_data:
            df_calendar = extract_crop_calendar_data(agricultural_data)
            unique_crops = df_calendar['crop'].unique() if not df_calendar.empty else []
            for crop in unique_crops:
                crops_data.append({
                    'Crop': crop,
                    'Source': 'Dados Agrícolas',
                    'Available': 1
                })
        
        if crops_data:
            df_crops = pd.DataFrame(crops_data)
            
            fig_crops = px.bar(
                df_crops,
                x='Crop',
                y='Available',
                color='Source',
                title="Crop Diversity by Source",
                color_discrete_map={
                    'Agricultural Calendar': '#2E8B57',
                    'Dados Agrícolas': '#FF8C00'
                }
            )
            fig_crops.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_crops, use_container_width=True)
        else:
            st.info("📊 Insufficient data for diversity chart")
        
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de diversidade: {e}")


def _render_basic_calendar_view(calendar_data: dict):
    """Render basic calendar view when the advanced component is not available."""
    
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        
        if not crop_calendar:
            st.warning("⚠️ Calendar data not found")
            return
        
        st.markdown("### 📅 Simplified Crop Calendar")
        
        # Create summary table
        calendar_summary = []
        for crop, states_data in crop_calendar.items():
            total_states = len(states_data)
            calendar_summary.append({
                'Crop': crop,
                'States with Data': total_states,
                'Status': '✅ Available' if total_states > 0 else '❌ Unavailable'
            })
        
        if calendar_summary:
            df_calendar = pd.DataFrame(calendar_summary)
            st.dataframe(df_calendar, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"❌ Error rendering basic calendar: {e}")


def _render_data_sources_info(calendar_data: dict, agricultural_data: dict):
    """Render data source information."""
    
    try:
        sources_data = []
        
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            sources_data.append({
                "Source": "Agricultural Calendar",
                "Status": "✅ Ativo",
                "Crops": len(crop_calendar),
                "Tipo": "Calendário de Cultivo"
            })
        
        if agricultural_data:
            df_calendar = extract_crop_calendar_data(agricultural_data)
            unique_crops = df_calendar['crop'].nunique() if not df_calendar.empty else 0
            sources_data.append({
                "Source": "Agricultural Data",
                "Status": "✅ Ativo",
                "Crops": unique_crops,
                "Tipo": "Monitoramento Agrícola"
            })
        
        if sources_data:
            df_sources = pd.DataFrame(sources_data)
            st.dataframe(df_sources, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Nenhuma fonte de dados disponível")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar fontes de dados: {e}")


def _render_data_quality_metrics(calendar_data: dict, agricultural_data: dict):
    """Render data quality metrics."""
    
    try:
        import plotly.graph_objects as go
        
        # Calculate quality metrics
        quality_metrics = []
        
        if agricultural_data:
            validation = validate_calendar_data(agricultural_data)
            accuracy = validation.get('data_completeness', 0)
            quality_metrics.append(('Precisão dos Dados', accuracy))
        
        if calendar_data:
            crop_calendar = calendar_data.get('crop_calendar', {})
            states = calendar_data.get('states', {})
            
            # Calculate calendar completeness
            total_possible = len(crop_calendar) * len(states) * 12  # crops x states x months
            total_filled = 0
            
            for states_data in crop_calendar.values():
                for state_data in states_data:
                    calendar_entry = state_data.get('calendar', {})
                    for activity in calendar_entry.values():
                        if activity and activity.strip():
                            total_filled += 1
            
            completeness = (total_filled / total_possible) * 100 if total_possible > 0 else 0
            quality_metrics.append(('Completude do Calendário', completeness))
        
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


def _render_temporal_availability(agricultural_data: dict):
    """Render temporal availability using agricultural data."""
    
    try:
        if not agricultural_data:
            st.warning("⚠️ Dados agrícolas não disponíveis")
            return
        
        # Extract temporal patterns from agricultural data
        df_calendar = extract_crop_calendar_data(agricultural_data)
        
        if df_calendar.empty:
            st.warning("⚠️ Dados temporais não disponíveis")
            return
        
        # Create monthly availability chart
        if 'month' in df_calendar.columns:
            monthly_counts = df_calendar['month'].value_counts().sort_index()
            
            fig_timeline = px.bar(
                x=monthly_counts.index,
                y=monthly_counts.values,
                title="Disponibilidade Temporal por Mês",
                labels={'x': 'Mês', 'y': 'Atividades'}
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.warning("⚠️ Informações de mês não encontradas nos dados")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar disponibilidade temporal: {e}")


def _render_geographic_coverage(calendar_data: dict, agricultural_data: dict):
    """Render geographic coverage."""
    
    try:
        coverage_data = []
        
        if calendar_data:
            states = calendar_data.get('states', {})
            regions = {}
            for state_code, state_info in states.items():
                region = state_info.get('region', 'Não especificado')
                if region not in regions:
                    regions[region] = 0
                regions[region] += 1
            
            for region, count in regions.items():
                coverage_data.append({
                    'Region': region,
                    'States': count,
                    'Source': 'Agricultural Calendar'
                })
        
        if agricultural_data:
            df_calendar = extract_crop_calendar_data(agricultural_data)
            if not df_calendar.empty and 'region' in df_calendar.columns:
                regional_coverage = df_calendar['region'].value_counts()
                for region, count in regional_coverage.items():
                    coverage_data.append({
                        'Region': region,
                        'States': f"{count} activities",
                        'Source': 'Agricultural Data'
                    })
        
        if coverage_data:
            df_coverage = pd.DataFrame(coverage_data)
            st.dataframe(df_coverage, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Geographic coverage data not available")
        
    except Exception as e:
        st.error(f"❌ Error rendering geographic coverage: {e}")


def render():
    """Função de entrada para o componente IBGE"""
    run()

if __name__ == "__main__":
    # Executar diretamente se chamado como script
    run()
