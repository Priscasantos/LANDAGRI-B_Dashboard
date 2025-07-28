"""
Agricultural Analysis Page
=========================

Complete agricultural analysis dashboard with CONAB data visualization.
"""

import streamlit as st
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import agricultural dashboard
try:
    from dashboard.components.agricultural.agricultural_dashboard import render_agricultural_dashboard
    AGRICULTURAL_MODULE_AVAILABLE = True
except ImportError as e:
    st.error(f"Agricultural dashboard module not available: {e}")
    AGRICULTURAL_MODULE_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Agricultural Analysis - CONAB Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #228B22 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2E8B57;
    }
    
    .insight-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .stTab [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTab [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
    }
    
    .stTab [aria-selected="true"] {
        background-color: #2E8B57;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main page header
st.markdown("""
<div class="main-header">
    <h1>🌾 Brazilian Agricultural Analysis</h1>
    <p>Comprehensive analysis of CONAB (Companhia Nacional de Abastecimento) agricultural monitoring data</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🌾 Agricultural Navigation")
    
    page_option = st.selectbox(
        "Choose Analysis View:",
        [
            "🏠 Main Dashboard",
            "📅 Crop Calendar",
            "🗺️ Regional Analysis", 
            "📈 Temporal Trends",
            "🌿 Crop Diversity",
            "📊 Performance Metrics"
        ]
    )
    
    st.markdown("---")
    
    # Quick info
    st.markdown("""
    **About CONAB Data:**
    - 🇧🇷 Brazil's National Supply Company
    - 🌱 Crop monitoring since 2000
    - 📊 90%+ classification accuracy
    - 🗺️ State-level coverage
    """)
    
    st.markdown("---")
    
    # Navigation buttons
    if st.button("🏠 Return to Main Dashboard", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("📋 View Overview Dashboard", use_container_width=True):
        st.switch_page("pages/📊_Overview.py")

# Main content area
if not AGRICULTURAL_MODULE_AVAILABLE:
    st.error("❌ Agricultural analysis module is not available. Please check the installation.")
    st.stop()

# Render main agricultural dashboard
if page_option == "🏠 Main Dashboard":
    render_agricultural_dashboard()

elif page_option == "📅 Crop Calendar":
    st.markdown("### 📅 Brazilian Crop Calendar Analysis")
    st.markdown("Detailed analysis of planting and harvest periods across Brazilian states.")
    
    # Import specific function
    try:
        from scripts.plotting.charts.agricultural_charts import load_conab_data, plot_crop_calendar_heatmap
        
        with st.spinner("Loading crop calendar data..."):
            detailed_data, calendar_data = load_conab_data()
        
        if calendar_data:
            fig = plot_crop_calendar_heatmap(calendar_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional insights
            st.markdown("""
            <div class="insight-box">
            <h4>📅 Calendar Insights</h4>
            <ul>
            <li><strong>Seasonality:</strong> Clear seasonal patterns across different crops</li>
            <li><strong>Regional Variation:</strong> Planting and harvest times vary significantly by state</li>
            <li><strong>Climate Adaptation:</strong> Calendar reflects Brazil's diverse climate zones</li>
            <li><strong>Optimization:</strong> Farmers can optimize planting schedules using this data</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Crop calendar data not available")
            
    except Exception as e:
        st.error(f"❌ Error loading crop calendar: {e}")

elif page_option == "🗺️ Regional Analysis":
    st.markdown("### 🗺️ Regional Crop Coverage Analysis")
    st.markdown("Distribution and coverage of agricultural monitoring across Brazilian regions.")
    
    try:
        from scripts.plotting.charts.agricultural_charts import load_conab_data, plot_regional_crop_coverage
        
        with st.spinner("Loading regional data..."):
            detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            fig = plot_regional_crop_coverage(detailed_data)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>🗺️ Regional Analysis</h4>
            <ul>
            <li><strong>Coverage Distribution:</strong> Agricultural monitoring varies by state</li>
            <li><strong>Major Regions:</strong> Concentrated in Brazil's agricultural heartland</li>
            <li><strong>State Comparison:</strong> Easy comparison of monitoring intensity</li>
            <li><strong>Strategic Planning:</strong> Identifies areas for expanded monitoring</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Regional data not available")
            
    except Exception as e:
        st.error(f"❌ Error loading regional analysis: {e}")

elif page_option == "📈 Temporal Trends":
    st.markdown("### 📈 Temporal Trends in Agricultural Monitoring")
    st.markdown("Evolution of crop monitoring programs and trends over time (2000-2024).")
    
    try:
        from scripts.plotting.charts.agricultural_charts import load_conab_data, plot_temporal_crop_trends
        
        with st.spinner("Loading temporal data..."):
            detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            fig = plot_temporal_crop_trends(detailed_data)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>📈 Temporal Insights</h4>
            <ul>
            <li><strong>Program Evolution:</strong> Shows expansion of monitoring capabilities</li>
            <li><strong>Technology Adoption:</strong> Reflects improvements in monitoring technology</li>
            <li><strong>Trend Analysis:</strong> Identifies growth patterns and future projections</li>
            <li><strong>Historical Context:</strong> 24+ years of agricultural monitoring evolution</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Temporal data not available")
            
    except Exception as e:
        st.error(f"❌ Error loading temporal trends: {e}")

elif page_option == "🌿 Crop Diversity":
    st.markdown("### 🌿 Crop Diversity Analysis")
    st.markdown("Hierarchical analysis of crop diversity across Brazilian regions and states.")
    
    try:
        from scripts.plotting.charts.agricultural_charts import load_conab_data, plot_crop_diversity_by_region
        
        with st.spinner("Loading diversity data..."):
            detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            fig = plot_crop_diversity_by_region(detailed_data)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>🌿 Diversity Analysis</h4>
            <ul>
            <li><strong>Regional Patterns:</strong> Different regions specialize in different crops</li>
            <li><strong>Biodiversity:</strong> Shows agricultural biodiversity across Brazil</li>
            <li><strong>Economic Impact:</strong> Crop diversity affects regional economic stability</li>
            <li><strong>Risk Management:</strong> Diversification reduces agricultural risk</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Diversity data not available")
            
    except Exception as e:
        st.error(f"❌ Error loading diversity analysis: {e}")

elif page_option == "📊 Performance Metrics":
    st.markdown("### 📊 CONAB Performance Metrics")
    st.markdown("Key performance indicators and system metrics for CONAB agricultural monitoring.")
    
    try:
        from scripts.plotting.charts.agricultural_charts import (
            load_conab_data, 
            plot_agricultural_performance_metrics,
            create_agricultural_summary_stats
        )
        
        with st.spinner("Loading performance data..."):
            detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            # Performance metrics chart
            fig = plot_agricultural_performance_metrics(detailed_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            stats = create_agricultural_summary_stats(detailed_data, calendar_data)
            
            # Performance details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                <h4>📊 System Metrics</h4>
                <p><strong>Total Crops:</strong> {}</p>
                <p><strong>Regions:</strong> {}</p>
                <p><strong>Accuracy:</strong> {}%</p>
                </div>
                """.format(stats['total_crops'], stats['total_regions'], stats['accuracy']), 
                unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                <h4>⏱️ Temporal Coverage</h4>
                <p><strong>Period:</strong> {}</p>
                <p><strong>Years Active:</strong> 24+</p>
                <p><strong>Frequency:</strong> Continuous</p>
                </div>
                """.format(stats['year_span']), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                <h4>🌱 Crop Coverage</h4>
                <p><strong>Main Crops:</strong></p>
                <p>{}</p>
                </div>
                """.format("<br>".join(f"• {crop}" for crop in stats['main_crops'][:5])), 
                unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>📊 Performance Insights</h4>
            <ul>
            <li><strong>High Accuracy:</strong> 90%+ classification accuracy demonstrates system reliability</li>
            <li><strong>Comprehensive Coverage:</strong> Monitoring across all major Brazilian agricultural regions</li>
            <li><strong>Long-term Data:</strong> 24+ years of continuous monitoring provides historical context</li>
            <li><strong>Multi-crop Analysis:</strong> Covers all major Brazilian crops including soybeans, corn, cotton</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Performance data not available")
            
    except Exception as e:
        st.error(f"❌ Error loading performance metrics: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <strong>🌾 CONAB Agricultural Analysis Dashboard</strong><br>
    Data Source: Companhia Nacional de Abastecimento (CONAB) | Brazil's National Supply Company<br>
    Coverage: Brazil | Classification Method: Machine Learning | Accuracy: 90%+
</div>
""", unsafe_allow_html=True)
