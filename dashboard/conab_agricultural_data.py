"""
CONAB Agricultural Data Dashboard Component
Integrated with the agricultural_analysis.py orchestration system
"""

import streamlit as st

def render():
    """Renders CONAB-specific data"""
    
    st.markdown("### General Summary")
    
    # Try to load CONAB data
    data = load_conab_data()
    
    if not data:
        st.warning("⚠️ CONAB data not available at the moment")
        
        # Information about CONAB
        st.markdown("""
        ### 📈 About CONAB
        
        The **National Supply Company (CONAB)** is a public company linked to the 
        Ministry of Agriculture, Livestock and Supply (MAPA) responsible for:
        
        - 🌾 **Crop Surveys**: Monthly estimates of production, area and productivity
        - 📊 **Market Monitoring**: Prices, stocks and marketing
        - 🗺️ **Agricultural Mapping**: Use of remote sensing for monitoring
        - 📋 **Agricultural Policy**: Support for public sector policies
        
        ### 🎯 Main Monitored Crops
        
        - Soybean, Corn (1st and 2nd crop)
        - Cotton, Rice, Beans
        - Wheat, Sorghum, Sunflower
        - Peanut, Castor Bean, Canola
        
        ### 📅 Monitored Harvests
        
        - **Summer Harvest**: October to March
        - **Winter Harvest**: April to September
        - **Historical Data**: 2003 to present
        
        **Source:** [CONAB - Historical Series](https://www.conab.gov.br/info-agro/safras/serie-historica-das-safras)
        """)
        
        return
    
    # If we have data, render visualizations
    render_conab_visualizations(data)


def load_conab_data():
    """Loads CONAB agricultural data"""
    try:
        import json
        import os
        
        data_path = os.path.join('data', 'conab_agricultural_data.json')
        if os.path.exists(data_path):
            with open(data_path, encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        st.error(f"❌ Error loading CONAB data: {e}")
        return None


def render_conab_visualizations(data):
    """Renders CONAB data visualizations"""
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        total_crops = len(data.get('crops', {}))
        latest_year = "2023/24"  # Most recent crop season
        
        with col1:
            st.metric("🌾 Crops", total_crops)
        
        with col2:
            st.metric("📅 Current Season", latest_year)
        
        with col3:
            # Calculate total production (simplified)
            total_production = 0
            for crop_data in data.get('crops', {}).values():
                if latest_year in crop_data.get('production_data', {}):
                    total_production += crop_data['production_data'][latest_year].get('production', 0)
            
            st.metric("📈 Total Production", f"{total_production/1000:.1f}M ton")
        
        with col4:
            # Calculate total area (simplified)
            total_area = 0
            for crop_data in data.get('crops', {}).values():
                if latest_year in crop_data.get('production_data', {}):
                    total_area += crop_data['production_data'][latest_year].get('area', 0)
            
            st.metric("🗺️ Total Area", f"{total_area/1000:.1f}M ha")
    
    except Exception as e:
        st.warning(f"⚠️ Error calculating metrics: {e}")
    
    st.divider()
    
    # Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            fig_production = create_production_chart(data)
            if fig_production:
                st.plotly_chart(fig_production, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Production chart: {e}")
    
    with col2:
        try:
            fig_area = create_area_chart(data)
            if fig_area:
                st.plotly_chart(fig_area, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Area chart: {e}")


def create_production_chart(data):
    """Creates production chart by crop"""
    try:
        import pandas as pd
        import plotly.express as px
        
        # Latest crop season data
        chart_data = []
        latest_year = "2023/24"
        
        for crop_key, crop_data in data.get('crops', {}).items():
            if latest_year in crop_data.get('production_data', {}):
                production_data = crop_data['production_data'][latest_year]
                chart_data.append({
                    'Crop': crop_data.get('name', crop_key),
                    'Production': production_data.get('production', 0) / 1000  # Convert to millions
                })
        
        if not chart_data:
            return None
        
        df = pd.DataFrame(chart_data)
        df = df.sort_values('Production', ascending=True)
        
        fig = px.bar(
            df,
            x='Production',
            y='Crop',
            orientation='h',
            title=f'Production by Crop for the Current Season ({latest_year})',
            labels={'Production': 'Production (Million t)', 'Crop': 'Crop'},
            color='Production',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        st.error(f"Error in production chart: {e}")
        return None


def create_area_chart(data):
    """Creates planted area chart"""
    try:
        import pandas as pd
        import plotly.express as px
        
        # Latest crop season data
        chart_data = []
        latest_year = "2023/24"
        
        for crop_key, crop_data in data.get('crops', {}).items():
            if latest_year in crop_data.get('production_data', {}):
                production_data = crop_data['production_data'][latest_year]
                chart_data.append({
                    'Crop': crop_data.get('name', crop_key),
                    'Area': production_data.get('area', 0) / 1000  # Convert to millions
                })
        
        if not chart_data:
            return None
        
        df = pd.DataFrame(chart_data)
        
        fig = px.pie(
            df,
            values='Area',
            names='Crop',
            title=f'Planted Area Distribution for the Current Season ({latest_year})'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
        
    except Exception as e:
        st.error(f"Error in area chart: {e}")
        return None


if __name__ == "__main__":
    render()
