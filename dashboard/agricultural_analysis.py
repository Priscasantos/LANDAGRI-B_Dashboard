"""
Agricultural Analysis Dashboard Orchestrator
===========================================

Dashboard orchestrator for Brazilian agricultural analysis based on the app.py menu.
Responds to pages: Agriculture Overview, Crop Calendar, Agriculture Availability

Author: LANDAGRI-B Project Team 
Date: 2025-08-08
"""

import streamlit as st


def run():
    """
    Main function that responds to pages selected in the app.py sidebar menu.
    Checks st.session_state.current_page to determine which page to render.
    """
    
    # Get current page from session state (defined by app.py)
    current_page = getattr(st.session_state, 'current_page', 'Agriculture Overview')
    
    # Render page based on sidebar menu selection
    if current_page == "Agriculture Overview":
        render_agriculture_overview_page()
    elif current_page == "Crop Calendar":
        render_crop_calendar_page()
    elif current_page == "Agriculture Availability":
        render_agriculture_availability_page()
    elif current_page == "CONAB Availability Analysis":
        render_conab_availability_analysis_page()
    else:
        # Fallback for page not found
        st.error(f"❌ Page '{current_page}' not found")
        st.info("Available pages: Agriculture Overview, Crop Calendar, Agriculture Availability, CONAB Availability Analysis")


def render_agriculture_overview_page():
    """Renders Agriculture Overview page with 3 internal tabs"""
    
    # Page header
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #EC9706 0%, #ffb347 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(236,151,6,0.15);
        border: 1px solid rgba(236,151,6,0.12);
    ">
        <h1 style="color: #8d4004; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🏞 Agricultural Analysis
        </h1>
        <p style="color: #8d4004; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-style: italic;">
            Land Use and Land Cover (LULC) Initiatives Mapping Data Analysis applied to Brazilian Agricultural Context.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, rgba(236,151,6,0.06) 0%, rgba(255,180,71,0.04) 100%);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid rgba(236,151,6,0.08);
    ">
        <h2 style="color: #8d4004; margin: 0; font-size: 1.6rem; font-weight: 600;">
            🔎 Agriculture Overview
        </h2>
        <p style="color: #8d4004; margin: 0.35rem 0 0 0; font-size: 0.95rem; font-style: italic;">
            Overview of Integrated Agricultural Data Information from National Supply Company (CONAB) and Brazilian Institute of Geography and Statistics (IBGE) Web Portals.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Contextual information
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📊 **Mapped Data**\nGeospatial and remote sensing")
        
        with col2:
            st.info("📈 **CONAB Estimates**\nOfficial harvest bulletins")
        
        with col3:
            st.info("📋 **IBGE Statistics**\nCensus and sample data")
    
    st.divider()
    
    # INTERNAL Overview tabs system
    tab1, tab2, tab3 = st.tabs([
        "🗺️ CONAB Mapping",
        "🌿 CONAB Estimates",
        "🌿 IBGE Estimates"
    ])
    
    # Tab 1: General Overview with mapped data
    with tab1:
        st.markdown("## 🗺️ CONAB Mapping ")
        st.markdown("*Remote sensing-based agricultural data from National Supply Company (CONAB).*")
        
        # Import and render mapping component
        try:
            from dashboard.components.agricultural_analysis.mapping_overview import render_mapping_overview
            render_mapping_overview()
        except ImportError as e:
            st.warning(f"⚠️ Mapping component: {e}")
            
            # Temporary information about mapping
            st.markdown("""
            ### 📡 Source: Agricultural Information Portal - CONAB
            
            **Available Mapping:**
            - 🌱 Soybean (Sentinel-2, Landsat-8)
            - 🌽 1st and 2nd Harvest Corn (MODIS, Sentinel-2)
            - 🌿 Cotton (Landsat-8, SPOT)
            - 🎋 Sugarcane (Multi-sensor)
            
            **Technical Features:**
            - Resolution: 10-30m
            - Coverage: National
            - Period: 2020-2024
            - Accuracy: 88-94%
            
            **Downloads:** [CONAB Portal](https://portaldeinformacoes.conab.gov.br/mapeamentos-agricolas-downloads.html)
            """)
    
    # Tab 2: CONAB Estimates
    with tab2:
        st.markdown("## 🌿 CONAB Estimates")
        st.markdown("*Official production, area and productivity estimates.*")
        
        # Import and render CONAB component
        try:
            from dashboard.conab_agricultural_data import render
            render()
        except ImportError as e:
            st.error(f"❌ Error loading CONAB data: {e}")
    
    # Tab 3: IBGE Estimates
    with tab3:
        st.markdown("## 🌿 IBGE Estimates")
        st.markdown("*Official statistics from Municipal Agricultural Production (PAM).*")
        
        # Import and render IBGE component
        try:
            from dashboard.components.agricultural_analysis.ibge_estimates import render
            render()
        except ImportError as e:
            st.error(f"❌ Error loading IBGE data: {e}")


def render_crop_calendar_page():
    """Renders Crop Calendar page with organized charts from #file:calendar"""
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #EC9706 0%, #ffb347 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(236,151,6,0.15);
        border: 1px solid rgba(236,151,6,0.12);
    ">
        <h1 style="color: #8d4004; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🏞 Agricultural Analysis
        </h1>
        <p style="color: #8d4004; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-style: italic;">
            Land Use and Land Cover (LULC) Initiatives Mapping Data Analysis applied to Brazilian Agricultural Context.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, rgba(236,151,6,0.06) 0%, rgba(255,180,71,0.04) 100%);
        padding: 1rem 1.2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(236,151,6,0.08);
    ">
        <h2 style="color: #8d4004; margin: 0; font-size: 1.6rem; font-weight: 600;">
            📅 Crop Calendar
        </h2>
        <p style="color: #8d4004; margin: 0.35rem 0 0 0; font-size: 0.95rem; font-style: italic;">
            Agricultural Calendar Analysis for the Main Brazilian Crops. Mapping Data Acquired from National Supply Company (CONAB).
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Load data
    data = load_calendar_data()
    
    if not data:
        st.warning("⚠️ Agricultural calendar data not available")
        return
    
    # Global filters
    st.markdown("### 🎛️ Filters")
    st.info("💡 **Tip:** Use the multiselect filters below to focus on specific crops and regions. All options are selected by default.")
    col1, col2 = st.columns(2)
    
    with col1:
        cultures = get_available_cultures(data)
        selected_cultures = st.multiselect(
            "🌾 Select Crops:",
            options=cultures,
            default=cultures  # All crops selected by default
        )
    
    with col2:
        regions = get_available_regions(data)
        selected_regions = st.multiselect(
            "🗺️ Select Regions:",
            options=regions,
            default=regions  # All regions selected by default
        )
    
    # Filter data
    filtered_data = filter_data(data, selected_cultures, selected_regions)
    
    st.divider()
    
    # Organizar gráficos em abas baseado nos arquivos em #file:calendar
    cal_tab1, cal_tab2, cal_tab3, cal_tab4, cal_tab5, cal_tab6, cal_tab7 = st.tabs([
        "🗓️ Calendar Heatmaps",
        "⏳ Activities Timeline", 
        "𖦹 Spatio-temporal Distribution",
        "🌞 Seasonal Overview",
        "📊 Crop Distribution", 
        "📈 Monthly Intensity",
        "⚡ Activity Intensity"
    ])
    
    with cal_tab1:
        render_calendar_heatmaps_tab(filtered_data)

    with cal_tab2:
        render_timeline_regional_tab(filtered_data)
    
    with cal_tab3:
        render_spatial_temporal_tab(filtered_data)
    
    with cal_tab4:
        render_seasonal_overview_tab(filtered_data)
    
    with cal_tab5:
        render_crop_distribution_tab(filtered_data)
    
    with cal_tab6:
        render_monthly_intensity_tab(filtered_data)
    
    with cal_tab7:
        render_activity_intensity_tab(filtered_data)



def render_agriculture_availability_page():
    """Renders Agriculture Availability page with new charts organized in tabs"""
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #EC9706 0%, #ffb347 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(236,151,6,0.15);
        border: 1px solid rgba(236,151,6,0.12);
    ">
        <h1 style="color: #8d4004; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🏞 Agricultural Analysis
        </h1>
        <p style="color: #8d4004; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-style: italic;">
            Land Use and Land Cover (LULC) Initiatives Mapping Data Analysis applied to Brazilian Agricultural Context.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, rgba(236,151,6,0.06) 0%, rgba(255,180,71,0.04) 100%);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid rgba(236,151,6,0.08);
    ">
        <h2 style="color: #8d4004; margin: 0; font-size: 1.6rem; font-weight: 600;">
            ⏳ Agriculture Availability
        </h2>
        <p style="color: #8d4004; margin: 0.35rem 0 0 0; font-size: 0.95rem; font-style: italic;">
            Agricultural Data Availability Analysis from National Supply Company (CONAB).
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Load data
    data = load_calendar_data()
    
    if not data:
        st.warning("⚠️ Data for availability analysis not available")
        return

    # Global filters
    st.markdown("### 🎛️ Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        cultures = get_available_cultures(data)
        selected_cultures = st.multiselect(
            "🌾 Select Crops:",
            options=cultures,
            default=cultures  # All crops selected by default
        )
    
    with col2:
        regions = get_available_regions(data)
        selected_regions = st.multiselect(
            "🗺️ Select Regions:",
            options=regions,
            default=regions  # All regions selected by default
        )
    
    # Filter data
    filtered_data = filter_data(data, selected_cultures, selected_regions)
    
    st.divider()
    
    # Organizar gráficos em abas
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Spatial Coverage",
        "🌱 Crop Diversity",
        "🗺 Regional Activity"
    ])
    
    with tab1:
        render_spatial_coverage_tab(filtered_data)
    
    with tab2:
        render_crop_diversity_tab(filtered_data)

    with tab3:
        render_regional_activity_tab(filtered_data)

# Helper functions
def load_calendar_data():
    """Loads agricultural calendar data"""
    try:
        from dashboard.components.agricultural_analysis.agricultural_loader import load_agricultural_data
        return load_agricultural_data()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None


def get_available_cultures(data):
    """Extracts available crops from data"""
    if not data or 'crop_calendar' not in data:
        return []
    return list(data['crop_calendar'].keys())


def get_available_regions(data):
    """Extracts available regions from data"""
    if not data or 'crop_calendar' not in data:
        return []
    
    regions = set()
    for crop_data in data['crop_calendar'].values():
        for state_info in crop_data:
            regions.add(state_info.get('region', 'Unknown'))
    return sorted(list(regions))


def filter_data(data, selected_cultures, selected_regions):
    """Filters data based on multiple selections"""
    if not data or 'crop_calendar' not in data:
        return data
    
    filtered_data = {'crop_calendar': {}}
    
    for crop_name, crop_data in data['crop_calendar'].items():
        # Filter by crops - if no crops selected, show all
        if selected_cultures and crop_name not in selected_cultures:
            continue
        
        # Filter by regions - if no regions selected, show all
        filtered_states = []
        for state_info in crop_data:
            state_region = state_info.get('region')
            if not selected_regions or state_region in selected_regions:
                filtered_states.append(state_info)
        
        if filtered_states:
            filtered_data['crop_calendar'][crop_name] = filtered_states
    
    return filtered_data


# Crop Calendar tab rendering functions
def render_calendar_heatmaps_tab(data):
    """Renders heatmaps and matrices tab"""
    st.markdown("#### 🗓️ Calendar Heatmaps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.enhanced_calendar_heatmap import create_enhanced_calendar_heatmap
            create_enhanced_calendar_heatmap(data)
        except Exception as e:
            st.warning(f"⚠️ Enhanced Calendar Heatmap: {e}")
    
    with col2:
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.national_calendar_matrix import create_calendar_heatmap_chart
            fig = create_calendar_heatmap_chart(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ National Calendar Matrix: {e}")


def render_monthly_seasonal_tab(data):
    """Renders monthly and seasonal analysis tab with sub-tabs for each chart"""
    st.markdown("#### 📊 Monthly & Seasonal Analysis")
    
    # Create sub-tabs to better organize charts
    monthly_tab1, monthly_tab2 = st.tabs([
        "🔄 Seasonality & Monthly",
        "🎯 Polar Activity"
    ])
    
    with monthly_tab1:
        # Monthly Activity Charts and Seasonality Analysis together
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔄 Seasonality Analysis")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                create_seasonality_index_chart(data, "seasonality_monthly_seasonal_tab")
            except Exception as e:
                st.warning(f"⚠️ Seasonality Analysis: {e}")
        
        with col2:
            st.markdown("##### 🔎 Monthly Overview")
            # Placeholder for additional monthly analysis if needed
            st.info("📊 Additional monthly analysis can be added here")
    
    with monthly_tab2:
        # Polar Activity Chart in its own tab
        st.markdown("##### 🎯 Polar Activity Distribution")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.polar_activity_chart import create_polar_activity_chart
            fig = create_polar_activity_chart(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Polar Activity Chart: {e}")
    
    # with monthly_tab3:
    #     # Crop Distribution in its own tab
    #     st.markdown("##### 🌾 Crop Distribution")
    #     try:
    #         from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import render_crop_distribution_charts
    #         render_crop_distribution_charts(data)
    #     except Exception as e:
    #         st.warning(f"⚠️ Crop Distribution: {e}")


def render_timeline_regional_tab(data):
    """Renders timeline and regional analysis tab with sub-tabs for each chart"""
    st.markdown("#### ⏳ Activities Timeline")
    
    # Create sub-tabs to better organize charts
    timeline_tab1, timeline_tab2, timeline_tab3 = st.tabs([
        "🗒 Monthly & Seasonality",
        "☰ Gantt Chart",
        "○⃝° Polar Seasonality"
    ])
    
    with timeline_tab1:
        # Monthly Activity Charts and Seasonality side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Monthly Activity and Seasonality Analysis")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.monthly_activity_charts import create_total_activities_per_month_chart
                fig = create_total_activities_per_month_chart(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Monthly Activity Charts: {e}")
        
        with col2:
            st.markdown("#####")
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                create_seasonality_index_chart(data, "seasonality_timeline_regional_tab")
            except Exception as e:
                st.warning(f"⚠️ Seasonality Analysis: {e}")
        
        # # Interactive Timeline below the two charts above
        # st.markdown("##### Interactive Agricultural Activity Timeline")
        # try:
        #     from dashboard.components.agricultural_analysis.charts.calendar.interactive_timeline import create_interactive_timeline
        #     fig = create_interactive_timeline(data)
        #     if fig:
        #         st.plotly_chart(fig, use_container_width=True)
        # except Exception as e:
        #     st.warning(f"⚠️ Interactive Timeline: {e}")
    
    
    with timeline_tab2:
        # Gantt Chart in its own tab
        st.markdown("##### Crop Cultivation Periods in Brazil")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.crop_gantt_chart import render_crop_gantt_chart
            
            # Use data already filtered from tab for Gantt
            crop_calendar = data.get('crop_calendar', {})
            
            if crop_calendar:
                # Render Gantt diagram without additional filters (uses tab filters)
                render_crop_gantt_chart(crop_calendar, "Brazil")
            else:
                st.info("📊 No calendar data available for Gantt chart")
                
        except Exception as e:
            st.warning(f"⚠️ Gantt Chart: {e}")
    
    with timeline_tab3:
        # Polar Seasonality Analysis in its own sub-tab
        st.markdown("##### Polar analysis of agricultural activities throughout the year")
        
        try:
            # Import and use the polar analysis function created earlier
            from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_polar_seasonality_analysis
            
            # Create polar seasonality chart
            create_polar_seasonality_analysis(data, "timeline_polar_seasonality_chart")
            
            
        except Exception as e:
            st.error(f"❌ Error in polar seasonality analysis: {str(e)}")
            st.info("📊 Check if calendar data is available")
    


def render_statistics_analysis_tab(data):
    """Renders statistics and advanced analysis tab"""
    st.markdown("#### 🎯 Statistics & Advanced Analysis")
    
    # Basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Crops", len(data.get('crop_calendar', {})))
    
    with col2:
        total_states = sum(len(crops) for crops in data.get('crop_calendar', {}).values())
        st.metric("Total States", total_states)
    
    with col3:
        # Calculate average calendar span
        calendar_spans = []
        for crop_data in data.get('crop_calendar', {}).values():
            for state_info in crop_data:
                if 'planting_months' in state_info and 'harvesting_months' in state_info:
                    planting = len(state_info.get('planting_months', []))
                    harvesting = len(state_info.get('harvesting_months', []))
                    calendar_spans.append(planting + harvesting)
        
        avg_span = sum(calendar_spans) / len(calendar_spans) if calendar_spans else 0
        st.metric("Average Calendar Span", f"{avg_span:.1f} months")
    
    # Enhanced Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Enhanced Statistics")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.enhanced_statistics import create_enhanced_statistics
            selected_crops = list(data.get('crop_calendar', {}).keys())[:5]  # Top 5 crops
            selected_states = ['SP', 'MG', 'MT', 'GO', 'RS']  # Main agricultural states
            create_enhanced_statistics(data, selected_crops, selected_states)
        except Exception as e:
            st.info("📊 Enhanced statistics chart will be implemented")
    
    with col2:
        st.markdown("##### 📈 Additional Analysis")
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.additional_analysis import render_seasonality_analysis
            render_seasonality_analysis(data)
        except Exception as e:
            st.info("📈 Additional analysis chart will be implemented")


# Availability tab rendering functions
def render_availability_analysis_tab(data):
    """Renders general availability analysis tab"""
    st.markdown("#### 📈 General Availability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Calendar Availability Analysis")
        try:
            from dashboard.components.agricultural_analysis.charts.availability.calendar_availability_analysis import render_calendar_availability_analysis
            render_calendar_availability_analysis(data)
        except Exception as e:
            st.warning(f"⚠️ Calendar Availability Analysis: {e}")
    
    with col2:
        st.markdown("##### 📋 Data Quality Metrics")
        try:
            # Add data quality metrics here
            st.info("📊 Data quality metrics will be displayed here")
        except Exception as e:
            st.warning(f"⚠️ Data Quality Metrics: {e}")
    


def render_conab_specific_tab(data):
    """Renders CONAB specific tab with charts migrated from overview"""
    st.markdown("#### 🎯 CONAB Specific Analysis")
    
    # Load CONAB detailed data for charts
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        st.warning("⚠️ CONAB detailed data not available")
        return
    
    # CONAB Spatial and Temporal Distribution
    st.markdown("##### 🗺️ Spatial and Temporal Distribution")
    try:
        fig = plot_conab_spatial_temporal_distribution(conab_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ CONAB Spatial Temporal Distribution: {e}")
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📈 Temporal Coverage")
        try:
            fig = plot_conab_temporal_coverage(conab_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ CONAB Temporal Coverage: {e}")
    
    with col2:
        st.markdown("##### 🗺️ Spatial Coverage")
        try:
            fig = plot_conab_spatial_coverage(conab_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ CONAB Spatial Coverage: {e}")
    
    # Crop Diversity Chart
    st.markdown("##### 🌾 Crop Diversity")
    try:
        fig = plot_conab_crop_diversity(conab_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ CONAB Crop Diversity: {e}")
    
    # CONAB Availability Matrix
    st.markdown("##### 📊 CONAB Availability Matrix")
    try:
        from dashboard.components.agricultural_analysis.charts.availability.conab_availability_matrix import create_conab_availability_matrix
        create_conab_availability_matrix(data)
    except Exception as e:
        st.warning(f"⚠️ CONAB Availability Matrix: {e}")


def render_crop_availability_detailed_tab(data):
    """Renders detailed crop availability tab"""
    st.markdown("#### 📊 Detailed Crop Availability")
    
    # Tab selector for detailed analysis
    cultures = get_available_cultures(data)
    
    if not cultures:
        st.info("No crops available for detailed analysis")
        return
    
    # Create subtabs for each culture
    if len(cultures) <= 5:
        # If few cultures, create tabs for each
        culture_tabs = st.tabs([f"🌾 {culture}" for culture in cultures])
        
        for i, culture in enumerate(cultures):
            with culture_tabs[i]:
                render_individual_crop_analysis(data, culture)
    else:
        # If many cultures, use selectbox
        selected_culture = st.selectbox("Select Crop for Detailed Analysis:", cultures)
        render_individual_crop_analysis(data, selected_culture)


def render_individual_crop_analysis(data, culture):
    """Renders individual crop analysis"""
    st.markdown(f"##### 📊 Availability Analysis: {culture}")
    
    # Extract culture-specific data
    culture_data = data.get('crop_calendar', {}).get(culture, [])
    
    if not culture_data:
        st.info(f"Data not available for {culture}")
        return
    
    # Basic metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("States with Data", len(culture_data))
    
    with col2:
        regions = set()
        for state_info in culture_data:
            regions.add(state_info.get('region', 'Unknown'))
        st.metric("Regions Covered", len(regions))
    
    with col3:
        total_months = set()
        for state_info in culture_data:
            total_months.update(state_info.get('planting_months', []))
            total_months.update(state_info.get('harvesting_months', []))
        st.metric("Activity Months", len(total_months))
    
    # Individual crop availability analysis
    # TODO: Implement detailed crop analysis
    st.info(f"Detailed analysis for {culture} will be implemented")


# === MIGRATED CONAB FUNCTIONS FROM OVERVIEW ===

def load_conab_detailed_data():
    """Load CONAB detailed data from JSON file."""
    try:
        from pathlib import Path
        import json
        
        current_dir = Path(__file__).parent.parent.parent
        file_path = current_dir / "data" / "conab_detailed_initiative.jsonc"
        
        if not file_path.exists():
            # Try alternative path
            file_path = current_dir / "data" / "json" / "conab_detailed_initiative.jsonc"
        
        if not file_path.exists():
            st.warning("CONAB detailed data file not found")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Clean the JSONC content
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove control characters and clean the line
                cleaned_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t\n\r')
                
                # Remove comments but keep the line if it has valid JSON
                if '//' in cleaned_line:
                    json_part = cleaned_line.split('//')[0].strip()
                    if json_part:
                        cleaned_lines.append(json_part)
                else:
                    if cleaned_line.strip():
                        cleaned_lines.append(cleaned_line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # Additional cleanup for common JSON issues
            cleaned_content = cleaned_content.replace('\r', '').replace('\x00', '')
            
            return json.loads(cleaned_content)
            
    except Exception as e:
        st.warning(f"Error loading CONAB detailed data: {e}")
        return {}


def plot_conab_spatial_temporal_distribution(conab_data):
    """Create a spatial and temporal distribution chart for CONAB mapping initiatives."""
    import plotly.graph_objects as go
    import plotly.express as px
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No data available)")
    
    # Extract data from CONAB detailed initiative
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    # Prepare data for timeline chart
    timeline_data = []
    all_states = set()
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        second_crop_years = crop_info.get("second_crop_years", {})
        
        # Process first and second semester data
        for state, years in first_crop_years.items():
            if state in regions:
                all_states.add(state)
                for year_range in years:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    
                    for year in range(start_year, end_year + 1):
                        timeline_data.append({
                            'State': state,
                            'Year': year,
                            'Crop': crop,
                            'Semester': 'First',
                            'Coverage': 1                        
                        })
    
    if not timeline_data:
        return go.Figure().update_layout(title="CONAB Spatial and Temporal Distribution (No timeline data)")
    
    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(timeline_data)
    
    # Create figure
    fig = go.Figure()
    
    # Get unique crop types and assign colors
    crop_types = sorted(df['Crop'].unique())
    colors = px.colors.qualitative.Set3
    crop_colors = {crop: colors[i % len(colors)] for i, crop in enumerate(crop_types)}
    
    states_list = sorted(list(all_states), reverse=True)
    states_list.append("Brazil")
    
    legend_added = set()
    
    # Add traces for each state
    for state in states_list:
        if state == "Brazil":
            continue
        
        state_data = df[df['State'] == state]
        if not state_data.empty:
            for crop in crop_types:
                crop_state_data = state_data[state_data['Crop'] == crop]
                if not crop_state_data.empty:
                    years = sorted(crop_state_data['Year'].unique())
                    
                    if years:
                        start_year = years[0]
                        end_year = years[-1]
                        
                        show_in_legend = crop not in legend_added
                        if show_in_legend:
                            legend_added.add(crop)
                        
                        fig.add_trace(go.Scatter(
                            x=[start_year, end_year],
                            y=[state, state],
                            mode='lines',
                            line=dict(width=15, color=crop_colors[crop]),
                            name=crop,
                            legendgroup=crop,
                            showlegend=show_in_legend,
                            hovertemplate=f"<b>{state}</b><br>Crop: {crop}<br>Period: {start_year}-{end_year}<br><extra></extra>"
                        ))
    
    # Add Brazil trace
    if timeline_data:
        all_years = sorted(df['Year'].unique())
        if all_years:
            brazil_start = min(all_years)
            brazil_end = max(all_years)
            
            fig.add_trace(go.Scatter(
                x=[brazil_start, brazil_end],
                y=["Brazil", "Brazil"],
                mode='lines',
                line=dict(width=15, color='#808080'),
                name='Overall Coverage',
                showlegend=True,
                hovertemplate=f"<b>Brazil</b><br>Overall Period: {brazil_start}-{brazil_end}<br><extra></extra>"
            ))
    
    # Update layout
    fig.update_layout(
        title="CONAB Spatial and Temporal Distribution",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Region</b>",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title=dict(text="<b>Crop Type</b>")
        ),   
        yaxis=dict(
            categoryorder='array',
            categoryarray=states_list,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            tickfont=dict(size=14),
            showline=True,
            linewidth=0,
            zeroline=False
        ),
        xaxis=dict(
            dtick=1,
            showgrid=False,
            ticks='outside',
            ticklen=8,
            tickcolor='black',
            showline=True,
            linewidth=0,
            zeroline=False
        )
    )
    
    return fig


def plot_conab_temporal_coverage(conab_data):
    """Create a temporal coverage chart showing percentage of states covered over time."""
    import plotly.graph_objects as go
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No data available)")
    
    # Extract data and calculate coverage percentages
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    year_coverage = {}
    TOTAL_STATES_PLUS_DF = 27
    
    for crop, crop_info in crop_coverage.items():
        first_crop_years = crop_info.get("first_crop_years", {})
        
        for state, years in first_crop_years.items():
            for year_range in years:
                start_year = int(year_range.split('-')[0])
                end_year = int(year_range.split('-')[1])
                
                for year in range(start_year, end_year + 1):
                    if year not in year_coverage:
                        year_coverage[year] = set()
                    year_coverage[year].add(state)
    
    if not year_coverage:
        return go.Figure().update_layout(title="CONAB Temporal Coverage (No coverage data)")
    
    years = sorted(year_coverage.keys())
    coverage_percentages = []
    
    for year in years:
        num_states = len(year_coverage[year])
        percentage = (num_states / TOTAL_STATES_PLUS_DF) * 100
        coverage_percentages.append(percentage)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=coverage_percentages,
        mode='lines+markers',
        line=dict(width=3, color='#17a2b8'),
        marker=dict(size=8, color='#17a2b8'),
        name='Coverage %',
        hovertemplate="<b>Year:</b> %{x}<br><b>Coverage:</b> %{y:.1f}%<br><extra></extra>"
    ))
    
    fig.update_layout(
        title="CONAB Temporal Coverage",
        xaxis_title="Year",
        yaxis_title="Percentage of States",
        height=400,
        yaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    return fig


def plot_conab_spatial_coverage(conab_data):
    """Create a spatial coverage chart showing percentage coverage by state."""
    import plotly.graph_objects as go
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No data available)")
    
    # Extract and process data
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    state_coverage = {}
    total_years = 24  # 2000-2023
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        first_crop_years = crop_info.get("first_crop_years", {})
        
        for state in regions:
            if state not in state_coverage:
                state_coverage[state] = set()
            
            if state in first_crop_years:
                for year_range in first_crop_years[state]:
                    start_year = int(year_range.split('-')[0])
                    end_year = int(year_range.split('-')[1])
                    for year in range(start_year, end_year + 1):
                        state_coverage[state].add(year)
    
    if not state_coverage:
        return go.Figure().update_layout(title="CONAB Spatial Coverage (No coverage data)")
    
    states = []
    coverages = []
    
    for state, years in state_coverage.items():
        coverage_percent = (len(years) / total_years) * 100
        states.append(state)
        coverages.append(coverage_percent)
    
    # Sort by coverage percentage
    sorted_data = sorted(zip(states, coverages), key=lambda x: x[1])
    states, coverages = zip(*sorted_data)
    
    # Color gradient based on coverage
    colors = ['#ffcccc' if c < 25 else '#ffeb99' if c < 50 else '#ccffcc' if c < 75 else '#99ccff' for c in coverages]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=coverages,
        y=states,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c:.1f}%" for c in coverages],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<br><extra></extra>"
    ))
    
    fig.update_layout(
        title="CONAB Spatial Coverage (2000-2023)",
        xaxis_title="Coverage (%)",
        yaxis_title="State/Area",
        height=500,
        showlegend=False
    )
    
    return fig


def plot_conab_crop_diversity(conab_data):
    """Create a crop type diversity chart showing crop types by state."""
    import plotly.graph_objects as go
    # Use central crop color palette
    from dashboard.components.agricultural_analysis.charts.availability.color_palettes import get_crop_color
    
    if not conab_data:
        return go.Figure().update_layout(title="CONAB Crop Diversity (No data available)")
    
    # Extract and process data
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
    crop_coverage = initiative_data.get("detailed_crop_coverage", {})
    
    state_crops = {}
    
    for crop, crop_info in crop_coverage.items():
        regions = crop_info.get("regions", [])
        
        for state in regions:
            if state not in state_crops:
                state_crops[state] = []
            state_crops[state].append(crop)
    
    if not state_crops:
        return go.Figure().update_layout(title="CONAB Crop Diversity (No crop data)")
    
    states = sorted(state_crops.keys())
    crop_types = list(set([crop for crops in state_crops.values() for crop in crops]))
    
    
    fig = go.Figure()
    
    # Count crops per state
    for crop in crop_types:
        crop_counts = []
        for state in states:
            count = state_crops[state].count(crop) if state in state_crops else 0
            crop_counts.append(count)
        
        fig.add_trace(go.Bar(
            x=crop_counts,
            y=states,
            orientation='h',
            name=crop,
            marker=dict(color=get_crop_color(crop)),
            hovertemplate=f"<b>{crop}</b><br>State: %{{y}}<br>Count: %{{x}}<br><extra></extra>"
        ))
    
    fig.update_layout(
        title="CONAB Crop Type Diversity by State (2000-2023)",
        xaxis_title="Crop Type Count",
        yaxis_title="State/Area",
        height=500,
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig


# Funções de renderização das abas da Agriculture Availability
def render_spatial_coverage_tab(data):
    """Renders spatial coverage tab with state-level analysis"""
    st.markdown("### 🗺️ Spatial Coverage Analysis")
    st.markdown("*Analysis of agricultural data spatial coverage across Brazilian states.*")
    
    try:
        from dashboard.components.agricultural_analysis.charts.availability import plot_conab_spatial_coverage_by_state
        fig = plot_conab_spatial_coverage_by_state(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Analysis:** Coverage percentage by state, showing data availability across Brazilian states using acronyms.")
        else:
            st.warning("⚠️ Unable to generate spatial coverage chart")
    except Exception as e:
        st.error(f"❌ Error loading spatial coverage chart: {e}")


def render_crop_diversity_tab(data):
    """Renders crop diversity tab with state-level analysis"""
    st.markdown("### 🌱 Crop Diversity Analysis")
    st.markdown("*Analysis of crop type diversity across Brazilian states.*")
    
    try:
        from dashboard.components.agricultural_analysis.charts.availability import plot_conab_crop_diversity_by_state
        fig = plot_conab_crop_diversity_by_state(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Analysis:** Number and types of crops cultivated in each state, showing agricultural diversity by state acronym.")
        else:
            st.warning("⚠️ Unable to generate crop diversity chart")
    except Exception as e:
        st.error(f"❌ Error loading crop diversity chart: {e}")


def render_seasonal_patterns_tab(data):
    """Renders seasonal patterns tab with subtabs by state and region"""
    st.markdown("### 🌀 Seasonal Patterns Analysis")
    st.markdown("*Analysis of seasonal agricultural activity patterns throughout the year.*")
    
    # First level: State vs Region
    main_tab1, main_tab2 = st.tabs(["📍 By State", "🌍 By Region"])
    
    with main_tab1:
        st.markdown("**Seasonal patterns at state level**")
        st.info("ℹ️ **Seasonal analysis has been moved to the Crop Calendar page**")
        st.markdown("""
        The following sections are now available in the **Crop Calendar** page:
        - 🌞 **Seasonal Overview** - Overview of seasonal planting and harvest patterns
        - 📊 **Crop Distribution** - Seasonal distribution heatmaps by state
        - 📈 **Monthly Intensity** - Monthly activity intensity analysis
        
        Navigate to the **Crop Calendar** page using the sidebar menu to access these charts.
        """)
    
    with main_tab2:
        st.markdown("**Seasonal patterns at regional level**")
        st.info("🔄 Regional-level seasonal analysis - aggregating state data by Brazilian regions.")
        # For region, we can reuse the same charts but with data aggregated by region
        # For now, let's show a message indicating it will be implemented
        st.markdown("*Regional seasonal analysis will aggregate data from states within each Brazilian region (North, Northeast, Central-West, Southeast, South).*")


def render_regional_activity_tab(data):
    """Renders regional activity tab with state-level analysis (region filtering handled by global filters)"""
    st.markdown("### 🗺 Regional Activity Analysis")
    st.markdown("*Analysis of agricultural activities across Brazilian states. Use region filter above to focus on specific regions.*")
    
    # Direct state-level analyses (no more By State/By Region tabs)
    state_tab1, state_tab2, state_tab3= st.tabs([
        "📊 Activity Comparison",
        "🗺️ Activity Heatmap", 
        "🌾 Crop Distribution"
    ])
    
    with state_tab1:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_comparison
                fig = plot_state_activity_comparison(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Comparison of planting and harvesting activities between Brazilian states.")
                else:
                    st.warning("⚠️ Unable to generate activity comparison chart")
            except Exception as e:
                st.error(f"❌ Error loading state activity comparison chart: {e}")
    
    with state_tab2:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_heatmap
                fig = plot_state_activity_heatmap(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Heatmap showing planting and harvesting activity intensity across Brazilian states.")
                else:
                    st.warning("⚠️ Unable to generate activity heatmap")
            except Exception as e:
                st.error(f"❌ Error loading state activity heatmap: {e}")
    
    with state_tab3:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_state_crop_distribution
                fig = plot_state_crop_distribution(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Distribution of crop types and their planting/harvesting activities across Brazilian states.")
                else:
                    st.warning("⚠️ Unable to generate crop distribution chart")
            except Exception as e:
                st.error(f"❌ Error loading crop distribution chart: {e}")
    



def render_overview_tab(data):
        st.markdown("**Activity analysis at Brazilian region level**")
        # Sub-tabs for different regional analyses
        region_tab1, region_tab2, region_tab3 = st.tabs([
            "� Regional Comparison",
            "🗺️ Regional Heatmap",
            "🌾 Regional Specialization", 
            "⏰ Regional Timeline"
        ])
        
        with region_tab1:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_regional_activity_comparison
                fig = plot_regional_activity_comparison(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Comparison of agricultural activity levels between Brazilian regions (North, Northeast, Central-West, Southeast, South).")
                else:
                    st.warning("⚠️ Unable to generate regional comparison chart")
            except Exception as e:
                st.error(f"❌ Error loading regional comparison chart: {e}")
        
        with region_tab2:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_regional_activity_heatmap
                fig = plot_regional_activity_heatmap(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Heatmap showing activity intensity across Brazilian regions and months.")
                else:
                    st.warning("⚠️ Unable to generate regional activity heatmap")
            except Exception as e:
                st.error(f"❌ Error loading regional activity heatmap: {e}")
        
        with region_tab3:
            try:
                from dashboard.components.agricultural_analysis.charts.availability import plot_regional_crop_specialization
                fig = plot_regional_crop_specialization(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Analysis:** Crop specialization patterns showing which crops dominate in each Brazilian region.")
                else:
                    st.warning("⚠️ Unable to generate regional crop specialization chart")
            except Exception as e:
                st.error(f"❌ Error loading regional crop specialization chart: {e}")


def render_overview_tab(data):
    """Renders general overview tab"""
    st.markdown("### 📊 General Overview")
    st.markdown("General view of data and main statistics.")
    
    if not data or 'crop_calendar' not in data:
        st.warning("⚠️ Data not available for analysis")
        return
    
    # General statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_crops = len(data['crop_calendar'])
    total_states = len(set(
        state_info.get('state_code', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('state_code')
    ))
    total_regions = len(set(
        state_info.get('region', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('region')
    ))
    total_activities = sum(
        sum(1 for activity in state_info.get('calendar', {}).values() if activity and activity.strip())
        for crop_data in data['crop_calendar'].values()
        for state_info in crop_data
    )
    
    with col1:
        st.metric("🌾 Total Crops", total_crops)
    
    with col2:
        st.metric("🗺️ States Covered", total_states)
    
    with col3:
        st.metric("🌍 Regions", total_regions)
    
    with col4:
        st.metric("📊 Total Activities", total_activities)
    
    st.markdown("---")
    
    # Data information
    st.markdown("#### 📋 Data Summary")
    
    # Crops list
    st.markdown("**Available crops:**")
    crops_list = ", ".join(sorted(data['crop_calendar'].keys()))
    st.markdown(f"- {crops_list}")
    
    # Regions list
    regions_list = sorted(set(
        state_info.get('region', '') 
        for crop_data in data['crop_calendar'].values() 
        for state_info in crop_data 
        if state_info.get('region')
    ))
    st.markdown("**Covered regions:**")
    st.markdown(f"- {', '.join(regions_list)}")
    
    # Data source info
    st.markdown("---")
    st.markdown("#### 📊 Data Source")
    st.info("""
    **Source:** CONAB (National Supply Company)
    
    **Description:** Agricultural calendar showing planting and harvest periods by state and crop type
    
    **Legend:**
    - P = Planting
    - H = Harvest
    - PH = Planting and Harvest
    """)


def render_conab_availability_analysis_page():
    """Renders dedicated and independent page for CONAB Availability Analysis"""
    
    # Page header
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
            🎯 CONAB Availability Analysis
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            📊 CONAB Availability Analysis - Analysis based on official CONAB data by region and state
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load CONAB data
    data = load_calendar_data()
    
    if not data:
        st.error("❌ CONAB data not available for analysis")
        st.info("This page requires CONAB agricultural calendar data to function.")
        return
    
    # Contextual information about CONAB data
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📈 **Harvest Estimates**\nOfficial monthly bulletins")
        
        with col2:
            st.info("🗺️ **Mapping**\nGeospatial satellite data")
        
        with col3:
            st.info("📅 **Agricultural Calendar**\nPlanting and harvest periods")
    
    st.divider()
    
    # Tab system for organized CONAB analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Regional Analysis",
        "🔄 Seasonality", 
        "⏰ Timeline",
        "📈 Trends"
    ])
    
    # Tab 1: Regional Analysis
    with tab1:
        st.markdown("## 🗺️ Regional Analysis")
        st.markdown("*Analysis of CONAB data availability by region and state*")
        
        # Subtabs for different types of regional analysis
        subtab1, subtab2, subtab3 = st.tabs([
            "📊 Regional Distribution",
            "🗾 National Matrix", 
            "🎚️ Activity Intensity"
        ])
        
        with subtab1:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import create_crop_type_distribution_chart, create_crop_diversity_by_region_chart
                
                st.markdown("### 📊 Crop Distribution by Region")
                
                # Specific filters
                col1, col2 = st.columns(2)
                with col1:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "🗺️ Region:",
                        options=['All'] + regions,
                        key="regional_distribution_region"
                    )
                
                with col2:
                    chart_type = st.selectbox(
                        "📊 Analysis Type:",
                        options=['Distribution by Crop', 'Regional Diversity'],
                        key="regional_distribution_type"
                    )
                
                # Prepare filtered data
                filtered_data = data.copy()
                
                # Generate chart based on selection
                if chart_type == 'Distribution by Crop':
                    fig = create_crop_type_distribution_chart(filtered_data)
                else:
                    fig = create_crop_diversity_by_region_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Could not generate distribution analysis")
                    
            except ImportError as e:
                st.error(f"❌ Error loading component: {e}")
            except Exception as e:
                st.warning(f"⚠️ Error generating distribution: {e}")
        
        with subtab2:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.national_calendar_matrix import create_calendar_heatmap_chart, create_consolidated_calendar_matrix_chart
                
                st.markdown("### 🗾 National Calendar Matrix")
                
                # Specific filters
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Crop:",
                        options=['All'] + cultures,
                        key="regional_matrix_culture"
                    )
                
                with col2:
                    chart_type = st.selectbox(
                        "📊 Visualization Type:",
                        options=['Heatmap', 'Consolidated Matrix'],
                        key="regional_matrix_type"
                    )
                
                # Prepare filtered data
                filtered_data = data.copy()
                
                # Generate chart based on selection
                if chart_type == 'Heatmap':
                    fig = create_calendar_heatmap_chart(filtered_data)
                else:
                    fig = create_consolidated_calendar_matrix_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Could not generate calendar matrix")
                    
            except ImportError as e:
                st.error(f"❌ Error loading component: {e}")
            except Exception as e:
                st.warning(f"⚠️ Error generating matrix: {e}")
        
        with subtab3:
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.activity_intensity import create_intensity_heatmap
                
                st.markdown("### 🎚️ Activity Intensity by Region")
                
                # Specific filters
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Crop:",
                        options=['All'] + cultures,
                        key="regional_intensity_culture"
                    )
                
                with col2:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "🗺️ Region:",
                        options=['All'] + regions,
                        key="regional_intensity_region"
                    )
                
                # Prepare filtered data
                filtered_data = data.copy()
                
                # Render chart
                create_intensity_heatmap(filtered_data)
                    
            except ImportError as e:
                st.error(f"❌ Error loading component: {e}")
            except Exception as e:
                st.warning(f"⚠️ Error generating intensity chart: {e}")
    
    # Tab 2: Seasonality
    with tab2:
        st.markdown("## 🔄 Seasonality")
        st.markdown("*Analysis of seasonal patterns in Brazilian agriculture*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
            
            # Specific filters
            st.markdown("### 🎛️ Filters")
            col1, col2 = st.columns(2)
            
            with col1:
                cultures = get_available_cultures(data)
                selected_culture = st.selectbox(
                    "🌾 Crop:",
                    options=['All'] + cultures,
                    key="seasonal_culture"
                )
            
            with col2:
                activity_types = ['All', 'Planting', 'Harvest', 'Planting/Harvest']
                selected_activity = st.selectbox(
                    "🔄 Activity:",
                    options=activity_types,
                    key="seasonal_activity"
                )
            
            # Prepare filtered data
            filtered_data = data.copy()
            
            # Render analysis
            create_seasonality_index_chart(filtered_data, "seasonality_monthly_seasonal_subsection")
            
            # Additional information about seasonality
            st.markdown("""
            ### 📋 Seasonality Interpretation
            - **High seasonality**: Activities concentrated in specific periods
            - **Low seasonality**: Activities distributed throughout the year
            - **Regional patterns**: Climate variations influence seasonality
            """)
                
        except ImportError as e:
            st.error(f"❌ Error loading component: {e}")
        except Exception as e:
            st.warning(f"⚠️ Error generating seasonal analysis: {e}")
    
    # Tab 3: Timeline
    with tab3:
        st.markdown("## ⏰ Timeline")
        st.markdown("*Interactive timeline of agricultural activities throughout the year*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.calendar.timeline_charts import create_timeline_activities_chart
            
            # Specific filters
            st.markdown("### 🎛️ Filters")
            col1, col2 = st.columns(2)
            
            with col1:
                cultures = get_available_cultures(data)
                selected_culture = st.selectbox(
                    "🌾 Crop:",
                    options=['All'] + cultures,
                    key="timeline_culture"
                )
            
            with col2:
                regions = get_available_regions(data)
                selected_region = st.selectbox(
                    "🗺️ Region:",
                    options=['All'] + regions,
                    key="timeline_region"
                )
            
            # Generate timeline
            fig = create_timeline_activities_chart(data)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanatory information
                st.markdown("""
                ### 📋 How to interpret the timeline
                - 🟢 **Green points**: Planting activities
                - 🟡 **Yellow points**: Harvest activities
                - 🔵 **Blue points**: Combined activities (planting/harvest)
                - **Line**: Temporal trend of activities
                - **Interactivity**: Click on points for details
                """)
            else:
                st.warning("⚠️ Could not generate activity timeline")
                
        except ImportError as e:
            st.error(f"❌ Error loading component: {e}")
        except Exception as e:
            st.warning(f"⚠️ Error generating timeline: {e}")
    
    # Tab 4: Trends
    with tab4:
        st.markdown("## 📈 Trends")
        st.markdown("*Analysis of trends and temporal evolution of CONAB data*")
        
        # Subtabs for different types of trends
        trend_tab1, trend_tab2, trend_tab3 = st.tabs([
            "📊 Annual Trends",
            "🔄 Temporal Comparison",
            "📈 Projections"
        ])
        
        with trend_tab1:
            st.markdown("### 📊 Annual Activity Trends")
            
            try:
                # Use existing components for trend analysis
                from dashboard.components.agricultural_analysis.charts.calendar.seasonality_analysis import create_seasonality_index_chart
                
                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    cultures = get_available_cultures(data)
                    selected_culture = st.selectbox(
                        "🌾 Crop:",
                        options=['All'] + cultures,
                        key="trends_annual_culture"
                    )
                
                with col2:
                    regions = get_available_regions(data)
                    selected_region = st.selectbox(
                        "🗺️ Region:",
                        options=['All'] + regions,
                        key="trends_annual_region"
                    )
                
                filtered_data = data.copy()
                create_seasonality_index_chart(filtered_data, "seasonality_monthly_seasonal_trends")
                
                st.info("📊 **Analysis**: Trends based on seasonal patterns identified in CONAB data")
                
            except Exception as e:
                st.warning(f"⚠️ Error generating annual trends: {e}")
        
        with trend_tab2:
            st.markdown("### 🔄 Temporal Comparison between Regions")
            
            try:
                from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import create_crop_diversity_by_region_chart
                
                filtered_data = data.copy()
                fig = create_crop_diversity_by_region_chart(filtered_data)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                st.info("🔄 **Analysis**: Comparison of crop diversity between different regions over time")
                
            except Exception as e:
                st.warning(f"⚠️ Error generating temporal comparison: {e}")
        
        with trend_tab3:
            st.markdown("### 📈 Projections and Insights")
            
            # Insights based on data
            st.markdown("""
            #### 🎯 CONAB Data Insights
            
            **📊 Regional Availability:**
            - Regions with greater data coverage
            - States with more complete calendars
            - Crops with better temporal mapping
            
            **🌀 Seasonal Patterns:**
            - Identification of planting and harvest peaks
            - Regional variations in calendars
            - Agricultural activity overlaps
            
            **⏰ Temporal Evolution:**
            - Crop expansion trends
            - Changes in regional patterns
            - Climate adaptations reflected in calendar
            """)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if data and 'crop_calendar' in data:
                    total_cultures = len(data['crop_calendar'])
                    st.metric("🌾 Total Crops", total_cultures)
            
            with col2:
                if data and 'crop_calendar' in data:
                    total_regions = len(get_available_regions(data))
                    st.metric("🗺️ Regions Covered", total_regions)
            
            with col3:
                if data and 'crop_calendar' in data:
                    # Calculate total states with data
                    total_states = 0
                    for crop_data in data['crop_calendar'].values():
                        total_states += len(crop_data)
                    st.metric("🏛️ States with Data", total_states)


def render_spatial_temporal_tab(data):
    """Renders CONAB spatial and temporal distribution tab"""
    st.markdown("#### 𖦹 Spatio-temporal Distribution")
    st.markdown("*Analysis of CONAB Spatial and Temporal Data Distribution.*")
    
    # Load CONAB data
    conab_data = load_conab_data()
    
    if not conab_data:
        st.warning("⚠️ CONAB data not available for spatial and temporal analysis")
        return
    
    # Import and use the plotting function
    try:
        from dashboard.components.agricultural_analysis.charts.calendar.spatial_temporal import (
            plot_conab_spatial_temporal_distribution
        )
        
        # Create the chart
        fig = plot_conab_spatial_temporal_distribution(conab_data)
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Add additional information
        st.markdown("---")
        st.markdown("### Data Summary")
        
        # Information about the data
        initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})
        crop_coverage = initiative_data.get("detailed_crop_coverage", {})
        
        if crop_coverage:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_crops = len(crop_coverage)
                st.metric("🌾 Mapped Crops", total_crops)
            
            with col2:
                # Count unique states
                all_states = set()
                for crop_info in crop_coverage.values():
                    regions = crop_info.get("regions", [])
                    all_states.update(regions)
                st.metric("🗺️ States/Regions", len(all_states))
            
            with col3:
                # Calculate temporal period
                all_years = set()
                for crop_info in crop_coverage.values():
                    first_years = crop_info.get("first_crop_years", {})
                    second_years = crop_info.get("second_crop_years", {})
                    
                    for years_list in first_years.values():
                        for year_range in years_list:
                            start_year = int(year_range.split('-')[0])
                            end_year = int(year_range.split('-')[1])
                            all_years.update(range(start_year, end_year + 1))
                    
                    for years_list in second_years.values():
                        for year_range in years_list:
                            start_year = int(year_range.split('-')[0])
                            end_year = int(year_range.split('-')[1])
                            all_years.update(range(start_year, end_year + 1))
                
                if all_years:
                    period = f"{min(all_years)}-{max(all_years)}"
                    st.metric("📅 Temporal Period", period)
                else:
                    st.metric("📅 Temporal Period", "N/A")
        
        # Chart description
        st.markdown("""
        **About this chart:**
        - Shows spatial (states/regions) and temporal (years) CONAB coverage distribution
        - Each line represents a state/region
        - Colors represent different crop types
        - Line length indicates coverage period
        - Brazil (bottom line) shows overall coverage period
        """)
        
    except Exception as e:
        st.error(f"❌ Error loading spatial and temporal chart: {str(e)}")
        st.markdown("```python")
        st.markdown(f"Error: {e}")
        st.markdown("```")


def load_conab_data():
    """Loads CONAB data for spatial and temporal analysis"""
    try:
        import json
        from pathlib import Path
        
        # Try to load from different sources
        data_paths = [
            Path("data/json/conab_detailed_initiative.jsonc"),
            Path("data/conab_mapping_data.json"),
            Path("data/conab_agricultural_data.json")
        ]
        
        for path in data_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    # For .jsonc files, remove simple comments
                    content = f.read()
                    if path.suffix == '.jsonc':
                        lines = content.split('\n')
                        lines = [line for line in lines if not line.strip().startswith('//')]
                        content = '\n'.join(lines)
                    
                    data = json.loads(content)
                    return data
        
        # If no files found, return mocked data for demonstration
        return create_mock_conab_data()
        
    except Exception as e:
        st.warning(f"⚠️ Error loading CONAB data: {e}")
        return create_mock_conab_data()


def create_mock_conab_data():
    """Creates mocked data for demonstration of spatial and temporal chart"""
    return {
        "CONAB Crop Monitoring Initiative": {
            "detailed_crop_coverage": {
                "Soybean": {
                    "regions": ["MT", "GO", "PR", "RS", "MS", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "PR": ["2018-2019", "2019-2020", "2020-2021", "2021-2022"],
                        "RS": ["2020-2021", "2021-2022", "2022-2023"],
                        "MS": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2019-2020", "2020-2021", "2021-2022"],
                        "GO": ["2020-2021", "2021-2022", "2022-2023"],
                        "MS": ["2020-2021", "2021-2022"]
                    }
                },
                "Corn": {
                    "regions": ["MT", "GO", "PR", "MG", "SP", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2019-2020", "2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2020-2021", "2021-2022", "2022-2023"],
                        "PR": ["2018-2019", "2019-2020", "2020-2021"],
                        "MG": ["2019-2020", "2020-2021", "2021-2022"],
                        "SP": ["2020-2021", "2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2020-2021", "2021-2022", "2022-2023"],
                        "GO": ["2021-2022", "2022-2023"],
                        "PR": ["2019-2020", "2020-2021"]
                    }
                },
                "Cotton": {
                    "regions": ["MT", "BA", "GO", "Brazil"],
                    "first_crop_years": {
                        "MT": ["2020-2021", "2021-2022", "2022-2023"],
                        "BA": ["2019-2020", "2020-2021", "2021-2022"],
                        "GO": ["2021-2022", "2022-2023"]
                    },
                    "second_crop_years": {
                        "MT": ["2021-2022", "2022-2023"],
                        "BA": ["2020-2021", "2021-2022"]
                    }
                }
            }
        }
    }


def render_seasonal_overview_tab(data):
    """Renders seasonal overview tab for crop calendar"""
    st.markdown("### 🌞 Seasonal Overview")
    st.markdown("*Overview of seasonal planting and harvest patterns by state.*")
    
    try:
        from dashboard.components.agricultural_analysis.charts.availability import plot_seasonal_patterns
        fig = plot_seasonal_patterns(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Analysis:** Overview of seasonal planting and harvest patterns across Brazilian states (horizontal display).")
        else:
            st.warning("⚠️ Unable to generate seasonal patterns chart")
    except Exception as e:
        st.error(f"❌ Error loading seasonal patterns chart: {e}")


def render_crop_distribution_tab(data):
    """Renders crop distribution tab for crop calendar"""
    st.markdown("### 📊 Crop Distribution")
    st.markdown("*Distribution of crop types and their planting/harvesting activities by state.*")
    
    try:
        from dashboard.components.agricultural_analysis.charts.availability import plot_crop_seasonal_distribution
        fig = plot_crop_seasonal_distribution(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Analysis:** Distribution of crop types and their planting/harvesting activities across Brazilian states.")
        else:
            st.warning("⚠️ Unable to generate crop distribution chart by state")
    except Exception as e:
        st.error(f"❌ Error loading crop distribution chart: {e}")


def render_monthly_intensity_tab(data):
    """Renders monthly intensity tab for crop calendar"""
    st.markdown("### 📈 Monthly Intensity")
    st.markdown("*Monthly activity intensity showing peak agricultural periods by state.*")
    
    try:
        from dashboard.components.agricultural_analysis.charts.availability import plot_monthly_activity_intensity
        fig = plot_monthly_activity_intensity(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Analysis:** Monthly activity intensity showing peak agricultural periods by state.")
        else:
            st.warning("⚠️ Unable to generate monthly intensity chart")
    except Exception as e:
        st.error(f"❌ Error loading monthly intensity chart: {e}")


def render_activity_intensity_tab(data):
    """Renders activity intensity analysis tab for crop calendar"""
    st.markdown("### ⚡ Activity Intensity Analysis")
    st.markdown("*Advanced analysis of agricultural activity intensity at state level with specialized visualizations.*")
    
    # Sub-tabs for different intensity analysis views
    intensity_tab1, intensity_tab2, intensity_tab3, intensity_tab4 = st.tabs([
        "🗓️ Intensity Matrix",
        "⚡ Peak Activity",
        "🎯 Density Map", 
        "📊 Concentration Index"
    ])
    
    with intensity_tab1:
        st.markdown("#### 🗓️ Intensity Matrix")
        st.markdown("*Matrix visualization of agricultural activity intensity by state and month.*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_heatmap
            fig = plot_state_activity_heatmap(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Comprehensive matrix showing activity intensity patterns across all Brazilian states and months.")
            else:
                st.warning("⚠️ Unable to generate intensity matrix")
        except Exception as e:
            st.error(f"❌ Error loading intensity matrix: {e}")
    
    with intensity_tab2:
        st.markdown("#### ⚡ Peak Activity")
        st.markdown("*Identification and analysis of peak agricultural activity periods by state.*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_timeline
            fig = plot_state_activity_timeline(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Timeline showing peak activity periods and seasonal patterns for agricultural activities by state.")
            else:
                st.warning("⚠️ Unable to generate peak activity chart")
        except Exception as e:
            st.error(f"❌ Error loading peak activity chart: {e}")
    
    with intensity_tab3:
        st.markdown("#### 🎯 Density Map")
        st.markdown("*Spatial density analysis of agricultural activities across Brazilian territory.*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_regional_activity_heatmap
            fig = plot_regional_activity_heatmap(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Regional density map showing geographical concentration of agricultural activities.")
            else:
                st.warning("⚠️ Unable to generate density map")
        except Exception as e:
            st.error(f"❌ Error loading density map: {e}")
    
    with intensity_tab4:
        st.markdown("#### 📊 Concentration Index")
        st.markdown("*Statistical analysis of activity concentration and distribution patterns.*")
        
        try:
            from dashboard.components.agricultural_analysis.charts.availability import plot_state_activity_comparison
            fig = plot_state_activity_comparison(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Analysis:** Concentration index showing relative activity levels and distribution patterns across states.")
                
                # Additional metrics display
                st.markdown("##### 📈 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total States", "27", help="All Brazilian states included in analysis")
                
                with col2:
                    st.metric("Peak Season", "Mar-May", help="Months with highest activity concentration")
                
                with col3:
                    st.metric("Activity Range", "High Variation", help="Significant differences between states")
                
                with col4:
                    st.metric("Coverage", "National", help="Complete national territory coverage")
                    
            else:
                st.warning("⚠️ Unable to generate concentration index")
        except Exception as e:
            st.error(f"❌ Error loading concentration index: {e}")


# Ensure functions are available when imported
__all__ = ['run', 'render_agriculture_overview_page', 'render_crop_calendar_page', 'render_agriculture_availability_page', 'render_conab_availability_analysis_page']


if __name__ == "__main__":
    # Para testes diretos
    st.set_page_config(page_title="Agricultural Analysis Test")
    run()
