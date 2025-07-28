"""
Agricultural Dashboard Component
===============================

Comprehensive agricultural analysis dashboard using CONAB data.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional

try:
    from scripts.plotting.charts.agricultural_charts import (
        load_conab_data,
        plot_crop_calendar_heatmap,
        plot_regional_crop_coverage,
        plot_temporal_crop_trends,
        plot_crop_diversity_by_region,
        plot_agricultural_performance_metrics,
        create_agricultural_summary_stats
    )
    AGRICULTURAL_CHARTS_AVAILABLE = True
except ImportError as e:
    st.error(f"Agricultural charts module not available: {e}")
    AGRICULTURAL_CHARTS_AVAILABLE = False


def render_agricultural_dashboard():
    """Render the comprehensive agricultural dashboard."""
    st.header("🌾 Agricultural Analysis - CONAB Data")
    
    if not AGRICULTURAL_CHARTS_AVAILABLE:
        st.error("❌ Agricultural charts module not available")
        return
    
    # Load CONAB data
    with st.spinner("Loading CONAB agricultural data..."):
        detailed_data, calendar_data = load_conab_data()
    
    if not detailed_data and not calendar_data:
        st.error("❌ Could not load CONAB data. Please check if data files exist.")
        return
    
    # Create summary statistics
    stats = create_agricultural_summary_stats(detailed_data, calendar_data)
    
    # Display overview metrics
    st.markdown("### 📊 Agricultural Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Crops Monitored",
            value=stats['total_crops']
        )
    
    with col2:
        st.metric(
            label="Regions Covered",
            value=stats['total_regions']
        )
    
    with col3:
        st.metric(
            label="Time Period",
            value=stats['year_span']
        )
    
    with col4:
        st.metric(
            label="Overall Accuracy",
            value=f"{stats['accuracy']}%"
        )
    
    # Main crops information
    if stats['main_crops']:
        st.markdown("### 🌱 Main Crops Monitored")
        crop_cols = st.columns(len(stats['main_crops']))
        for i, crop in enumerate(stats['main_crops']):
            with crop_cols[i]:
                st.info(f"**{crop}**")
    
    st.markdown("---")
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Crop Calendar", 
        "🗺️ Regional Coverage", 
        "📈 Temporal Trends", 
        "🌿 Crop Diversity",
        "📊 Performance Metrics"
    ])
    
    with tab1:
        st.markdown("#### 📅 Brazilian Crop Calendar")
        st.markdown("Interactive calendar showing planting and harvest periods for major crops across Brazilian states.")
        
        try:
            if calendar_data:
                fig_calendar = plot_crop_calendar_heatmap(calendar_data)
                st.plotly_chart(fig_calendar, use_container_width=True)
                
                # Legend explanation
                st.markdown("""
                **Legend:**
                - 🟢 **Green**: Planting period
                - 🟠 **Orange**: Harvest period  
                - 🔴 **Red**: Both planting and harvest
                - ⚪ **White**: No activity
                """)
            else:
                st.warning("⚠️ Crop calendar data not available")
        except Exception as e:
            st.error(f"❌ Error creating crop calendar: {e}")
    
    with tab2:
        st.markdown("#### 🗺️ Regional Crop Coverage Analysis")
        st.markdown("Distribution of monitored crops across Brazilian states and regions.")
        
        try:
            if detailed_data:
                fig_regional = plot_regional_crop_coverage(detailed_data)
                st.plotly_chart(fig_regional, use_container_width=True)
                
                # Additional regional insights
                st.markdown("""
                **Key Insights:**
                - Coverage varies significantly across Brazilian states
                - Agricultural regions show higher crop diversity
                - Data reflects Brazil's main agricultural zones
                """)
            else:
                st.warning("⚠️ Regional coverage data not available")
        except Exception as e:
            st.error(f"❌ Error creating regional coverage chart: {e}")
    
    with tab3:
        st.markdown("#### 📈 Temporal Trends in Crop Monitoring")
        st.markdown("Evolution of crop monitoring programs from 2000 to 2024.")
        
        try:
            if detailed_data:
                fig_temporal = plot_temporal_crop_trends(detailed_data)
                st.plotly_chart(fig_temporal, use_container_width=True)
                
                # Temporal insights
                st.markdown("""
                **Temporal Analysis:**
                - Shows expansion of monitoring programs over time
                - Identifies peak monitoring periods
                - Trend line indicates overall direction
                """)
            else:
                st.warning("⚠️ Temporal data not available")
        except Exception as e:
            st.error(f"❌ Error creating temporal trends chart: {e}")
    
    with tab4:
        st.markdown("#### 🌿 Crop Diversity by Region")
        st.markdown("Hierarchical view of crop diversity across Brazilian regions and states.")
        
        try:
            if detailed_data:
                fig_diversity = plot_crop_diversity_by_region(detailed_data)
                st.plotly_chart(fig_diversity, use_container_width=True)
                
                # Diversity insights
                st.markdown("""
                **Diversity Analysis:**
                - Interactive sunburst shows regional hierarchy
                - Size indicates relative crop diversity
                - Colors represent different regions
                """)
            else:
                st.warning("⚠️ Diversity data not available")
        except Exception as e:
            st.error(f"❌ Error creating diversity chart: {e}")
    
    with tab5:
        st.markdown("#### 📊 CONAB Performance Metrics")
        st.markdown("Key performance indicators for the CONAB agricultural monitoring system.")
        
        try:
            if detailed_data:
                fig_metrics = plot_agricultural_performance_metrics(detailed_data)
                st.plotly_chart(fig_metrics, use_container_width=True)
                
                # Performance insights
                initiative_data = detailed_data.get("CONAB Crop Monitoring Initiative", {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Classification Details:**")
                    st.write(f"• Method: {initiative_data.get('classification_method', 'N/A')}")
                    st.write(f"• Methodology: {initiative_data.get('methodology', 'N/A')}")
                    st.write(f"• Reference System: {initiative_data.get('reference_system', 'N/A')}")
                
                with col2:
                    st.markdown("**Data Products:**")
                    products = initiative_data.get('data_products', [])
                    for product in products[:3]:  # Show first 3 products
                        if isinstance(product, dict):
                            st.write(f"• {product.get('product_name', 'N/A')}")
            else:
                st.warning("⚠️ Performance metrics data not available")
        except Exception as e:
            st.error(f"❌ Error creating performance metrics: {e}")
    
    # Footer with data source information
    st.markdown("---")
    st.markdown("""
    **Data Source:** CONAB (Companhia Nacional de Abastecimento) - Brazilian National Supply Company  
    **Coverage:** Brazil | **Update Frequency:** Seasonal | **Classification Accuracy:** 90%+
    """)


def render_agricultural_summary_widget():
    """Render a summary widget for the main dashboard."""
    try:
        detailed_data, calendar_data = load_conab_data()
        stats = create_agricultural_summary_stats(detailed_data, calendar_data)
        
        st.markdown("### 🌾 Agricultural Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Monitored Crops", stats['total_crops'])
            st.metric("Coverage Period", stats['year_span'])
        
        with col2:
            st.metric("States Covered", stats['total_regions'])
            st.metric("System Accuracy", f"{stats['accuracy']}%")
        
        if stats['main_crops']:
            st.markdown("**Main Crops:** " + ", ".join(stats['main_crops'][:3]))
        
        if st.button("🔍 View Full Agricultural Analysis", key="agri_analysis_btn"):
            st.switch_page("pages/🌾_Agricultural_Analysis.py")
            
    except Exception as e:
        st.error(f"Agricultural summary not available: {e}")


if __name__ == "__main__":
    render_agricultural_dashboard()
