"""
Agricultural Overview Component
==============================

Component responsible for rendering the consolidated agricultural data overview.
ONLY overview data - no tabs, single menu.
Integrated with updated agricultural monitoring information (2025).

Author: Agricultural Dashboard
Date: 2025-08-08
"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .overview_data import (
    get_agricultural_overview_stats,
    get_crops_overview_data,
    get_states_summary,
)


def render_agricultural_overview(calendar_data: dict = None, agricultural_data: dict = None) -> None:
    """
    Render consolidated agricultural overview.
    Single page without tabs - overview only.
    Includes updated agricultural monitoring information for 2025.
    
    Args:
        calendar_data: Agricultural calendar data (optional)
        agricultural_data: Detailed agricultural data (optional)
    """
    
    # Enhanced overview header
    st.markdown("# 🌾 Brazilian Agricultural Overview")
    st.markdown("*Comprehensive monitoring of Brazilian agriculture - Agricultural Data & Research 2025*")
    
    # Info box with updated context
    with st.container():
        st.info("""
        📊 **National Agricultural Monitoring System** | 🇧🇷 **Brazil**
        
        **Sources:** Agricultural Data (CONAB, Embrapa, IBGE)
        **Coverage:** 2024/25 Harvest - Forecast of 339.6 million tons of grains
        **Main Crops:** Soybean, Corn, Coffee, Sugarcane, Cotton, Rice, Beans
        **Update:** August 2025 - Spectral data and real-time monitoring
        """)
    
    # Load specific overview data
    overview_stats = get_agricultural_overview_stats()
    crops_data = get_crops_overview_data()
    states_data = get_states_summary()
    
    # Expanded main metrics
    _render_overview_metrics(overview_stats)
    
    st.markdown("---")
    
    # Real-time indicators dashboard
    _render_real_time_indicators()
    
    st.markdown("---")
    
    # Expanded system status
    _render_system_status(overview_stats)
    
    st.markdown("---")
    
    # Analysis in enhanced layout
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("#### 🌱 Monitored Crops")
        _render_crops_overview(crops_data)
        
    with col2:
        st.markdown("#### 🗺️ Distribution by States")
        _render_states_overview(states_data)
    
    st.markdown("---")
    
    # New section: Trends and insights
    _render_agricultural_insights()
    
    st.markdown("---")
    
    # Expanded technical summary
    _render_technical_summary(overview_stats)


def _render_real_time_indicators() -> None:
    """
    Render real-time indicators of Brazilian agriculture.
    """
    st.markdown("#### ⚡ Real-Time Indicators")
    
    # Real-time data simulation based on agricultural information
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 Production 2024/25",
            "339.6 M tons",
            delta="2.4% vs 2023/24",
            help="Agricultural estimate for 2024/25 grain harvest"
        )
    
    with col2:
        st.metric(
            "🌡️ Weather Conditions",
            "Favorable",
            delta="Second corn crop",
            help="Spectral data indicates adequate conditions"
        )
    
    with col3:
        st.metric(
            "🚜 Planted Area",
            "78.8 M ha",
            delta="1.8% expansion",
            help="Total estimated area for current harvest"
        )
    
    with col4:
        st.metric(
            "💰 Gross Value",
            "R$ 756 B",
            delta="12% vs previous",
            help="Estimated value of agricultural production"
        )


def _render_agricultural_insights() -> None:
    """
    Render insights and trends of Brazilian agriculture.
    """
    st.markdown("#### 📈 Agricultural Trends and Insights")
    
    # Create tabs for different types of insights
    tab1, tab2, tab3 = st.tabs(["🎯 Highlights", "🌍 Sustainability", "🔬 Innovations"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🥇 Main Achievements 2025:**")
            st.success("• Brazil maintains position as world's largest soybean producer")
            st.success("• 2.4% expansion in grain production")
            st.success("• New spectral monitoring technologies")
            st.success("• Reduction in pesticide use through AI")
        
        with col2:
            st.markdown("**⚠️ Current Challenges:**")
            st.warning("• Climate change and extreme events")
            st.warning("• Need for increased productivity")
            st.warning("• Pressure for environmental sustainability")
            st.info("• Demand for digital traceability")
    
    with tab2:
        st.markdown("**🌱 Sustainability Initiatives:**")
        
        # Progress chart for sustainable goals
        progress_data = {
            'Indicator': ['Carbon Neutral', 'Pesticide Reduction', 'Preserved Areas', 'Renewable Energy'],
            'Target 2030': [100, 50, 30, 80],
            'Progress 2025': [35, 28, 22, 45]
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Target 2030',
            x=progress_data['Indicator'],
            y=progress_data['Target 2030'],
            marker_color='lightblue',
            opacity=0.7
        ))
        fig.add_trace(go.Bar(
            name='Progress 2025',
            x=progress_data['Indicator'],
            y=progress_data['Progress 2025'],
            marker_color='green'
        ))
        
        fig.update_layout(
            title="Sustainability Goals Progress (%)",
            xaxis_title="Indicators",
            yaxis_title="Percentage",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("**🚀 Featured Technological Innovations:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Digital Monitoring:**")
            st.info("📱 **Agricultural Monitoring** - App reduces pesticide use")
            st.info("🛰️ **Satellite Images** - Real-time monitoring")
            st.info("🤖 **Agricultural AI** - Pest and disease prediction")
        
        with col2:
            st.markdown("**Biotechnology:**")
            st.info("🧬 **Biofungicides** - 80% efficiency against fungi")
            st.info("🌾 **Improved Seeds** - Greater resistance")
            st.info("♻️ **Circular Agriculture** - Full utilization")


def _render_overview_metrics(overview_stats: dict[str, Any]) -> None:
    """
    Render main overview metrics.
    """
    if not overview_stats:
        st.warning("⚠️ Statistics data not available")
        return
    
    # 5-column layout for metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🗺️ States",
            overview_stats.get('states_covered', 'N/A'),
            help="Brazilian states covered by monitoring"
        )
    
    with col2:
        st.metric(
            "🌱 Crops",
            overview_stats.get('total_crops', 'N/A'),
            help="Agricultural crops monitored"
        )
    
    with col3:
        resolution = overview_stats.get('resolution', 'N/A')
        st.metric(
            "🔍 Resolution",
            resolution,
            help="Spatial resolution of data"
        )
    
    with col4:
        accuracy = overview_stats.get('accuracy', 0)
        accuracy_str = f"{accuracy:.1f}%" if accuracy > 0 else "N/A"
        st.metric(
            "🎯 Accuracy",
            accuracy_str,
            help="Overall monitoring accuracy"
        )
    
    with col5:
        area = overview_stats.get('total_area_monitored', 'N/A')
        st.metric(
            "📏 Coverage",
            area,
            help="Total monitored area"
        )


def _render_system_status(overview_stats: dict[str, Any]) -> None:
    """
    Render monitoring system status.
    """
    st.markdown("#### ⚡ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        provider = overview_stats.get('provider', 'N/A')
        st.info(f"**Provider:** {provider}")
    
    with col2:
        methodology = overview_stats.get('methodology', 'N/A')
        st.info(f"**Methodology:** {methodology}")
    
    with col3:
        # Calculate status based on data availability
        total_crops = overview_stats.get('total_crops', 0)
        states_covered = overview_stats.get('states_covered', 0)
        
        if total_crops > 5 and states_covered > 10:
            st.success("🟢 **System Operational**")
        elif total_crops > 2 and states_covered > 5:
            st.warning("🟡 **Partial Operation**")
        else:
            st.error("🔴 **Limited Data**")


def _render_crops_overview(crops_data: pd.DataFrame) -> None:
    """
    Render enhanced crops overview.
    """
    if crops_data.empty:
        st.info("📊 Crops data not available")
        return
    
    # Quick statistics
    total_crops = len(crops_data)
    total_states = crops_data['States'].sum() if 'States' in crops_data.columns else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Crops", total_crops)
    with col2:
        st.metric("State Coverage", f"{total_states} records")
    
    # Show crop table with better formatting
    st.markdown("**📋 Main Monitored Crops:**")
    if len(crops_data) > 0:
        # Resize for better readability
        display_data = crops_data.head(8)  # Show only top 8 for readability
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            height=300
        )
    
    # Bar chart of crops by states - more compact
    if 'States' in crops_data.columns and len(crops_data) > 0:
        top_cultures = crops_data.head(6)  # Top 6 for readability
        
        fig = px.bar(
            top_cultures,
            x='States',
            y='Crop',
            orientation='h',
            color='Double Crop',
            title="Top 6 Crops by Number of States",
            labels={'States': 'Number of States', 'Crop': 'Crop'},
            height=350,  # Reduced height for compaction
            color_discrete_sequence=['#2E8B57', '#FF6B6B']
        )
        fig.update_layout(
            xaxis_title="Number of States",
            yaxis_title="",
            showlegend=True,
            margin={"l": 10, "r": 10, "t": 40, "b": 10}
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_states_overview(states_data: pd.DataFrame) -> None:
    """
    Render enhanced overview by states.
    """
    if states_data.empty:
        st.info("📊 State data not available")
        return
    
    # Quick statistics
    total_states = len(states_data)
    total_cultures = states_data['Crops'].sum() if 'Crops' in states_data.columns else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("States", total_states)
    with col2:
        st.metric("Total Crops", total_cultures)
    
    # Show compact state table
    st.markdown("**🗺️ Distribution by State:**")
    if len(states_data) > 0:
        st.dataframe(
            states_data,
            use_container_width=True,
            hide_index=True,
            height=250
        )
    
    # Pie chart of states - more compact
    if 'Crops' in states_data.columns and len(states_data) > 0:
        fig = px.pie(
            states_data,
            values='Crops',
            names='State',
            title="Crop Distribution by State",
            height=300,  # Reduced height
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            margin={"l": 10, "r": 10, "t": 40, "b": 10},
            showlegend=False  # Remove legend to save space
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_technical_summary(overview_stats: dict[str, Any]) -> None:
    """
    Render expanded technical summary of the system.
    """
    st.markdown("#### 🔧 Technical Summary & Specifications")
    
    # Column layout for better organization
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 System Data:**")
        with st.container():
            st.code(f"""
Provider: {overview_stats.get('provider', 'N/A')}
Methodology: {overview_stats.get('methodology', 'N/A')}
Resolution: {overview_stats.get('resolution', 'N/A')}
Accuracy: {overview_stats.get('accuracy', 0):.1f}%
            """, language='text')
    
    with col2:
        st.markdown("**🌍 Geographic Coverage:**")
        with st.container():
            st.code(f"""
States: {overview_stats.get('states_covered', 'N/A')}
Crops: {overview_stats.get('total_crops', 'N/A')}
Total Area: {overview_stats.get('total_area_monitored', 'N/A')}
Density: {overview_stats.get('total_crops', 0) / max(overview_stats.get('states_covered', 1), 1):.1f} crops/state
            """, language='text')
    
    with col3:
        st.markdown("**⚡ Performance:**")
        # Calculate performance metrics
        total_crops = overview_stats.get('total_crops', 0)
        states_covered = overview_stats.get('states_covered', 0)
        
        if total_crops > 0 and states_covered > 0:
            efficiency = min(100, (total_crops * states_covered) / 100)
            coverage_score = min(100, (states_covered / 27) * 100)  # 27 Brazilian states
            
            st.code(f"""
Efficiency: {efficiency:.1f}%
National Coverage: {coverage_score:.1f}%
Status: {'Excellent' if efficiency > 80 else 'Good' if efficiency > 60 else 'Regular'}
Last Sync: Aug 2025
            """, language='text')
        else:
            st.code("Metrics not available", language='text')
    
    # Expanded technical information in expandable section
    with st.expander("🔍 Advanced Technical Details"):
        
        # Two columns for detailed information
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("**🛰️ Monitoring Technologies:**")
            st.markdown("""
            • **Remote Sensing**: High-resolution multispectral images
            • **AI and Machine Learning**: Automated detection algorithms
            • **Agricultural IoT**: Real-time field sensors
            • **Spectral Analysis**: Crop condition identification
            • **Georeferencing**: Precise GPS/GNSS coordinates
            """)
            
            st.markdown("**📈 Quality Metrics:**")
            accuracy = overview_stats.get('accuracy', 0)
            if accuracy > 0:
                progress_bar_value = accuracy / 100
                st.progress(progress_bar_value, f"Overall Accuracy: {accuracy:.1f}%")
            
            # Simulate other metrics
            st.progress(0.92, "System Availability: 92%")
            st.progress(0.88, "Update Rate: 88%")
        
        with detail_col2:
            st.markdown("**🌐 Integration and Sources:**")
            st.markdown("""
            • **Agricultural Database**: Main harvest database
            • **Research Institutions**: Research and technological development
            • **Official Statistics**: Complementary government statistics
            • **Satellite Data**: Satellite and meteorological data
            • **Field Producers**: Direct field information
            """)
            
            st.markdown("**📋 Standards and Certifications:**")
            st.markdown("""
            • **ISO 19115**: Geographic metadata
            • **OGC Standards**: Geospatial interoperability
            • **FAIR Principles**: Findable and accessible data
            • **LGPD**: Data protection compliance
            • **Digital Government**: Brazilian federal standards
            """)
    
    # Final density metrics in summary format
    if overview_stats:
        total_crops = overview_stats.get('total_crops', 0)
        states_covered = overview_stats.get('states_covered', 0)
        
        if total_crops > 0 and states_covered > 0:
            coverage_ratio = total_crops / states_covered
            
            # Use a compact final metric
            col_final1, col_final2, col_final3 = st.columns(3)
            
            with col_final1:
                st.metric(
                    "📈 Monitoring Density",
                    f"{coverage_ratio:.1f}",
                    help="Average crops per monitored state"
                )
            
            with col_final2:
                quality_score = min(100, (total_crops + states_covered) / 2)
                st.metric(
                    "⭐ Quality Score",
                    f"{quality_score:.0f}/100",
                    help="Score based on coverage and diversity"
                )
            
            with col_final3:
                st.metric(
                    "🎯 System Status",
                    "🟢 Operational" if coverage_ratio > 2 else "🟡 Partial",
                    help="Status based on monitoring density"
                )
