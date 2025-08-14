"""
CONAB Agricultural Data Dashboard Component
Displays Brazilian agricultural production data from the National Supply Company (CONAB)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

def load_conab_data():
    """Loads CONAB agricultural data from JSON file"""
    try:
        data_path = os.path.join('data', 'conab_agricultural_data.json')
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("CONAB data file not found!")
        return None
    except Exception as e:
        st.error(f"Error loading CONAB data: {e}")
        return None

def create_conab_production_chart(data):
    """Creates total production chart by harvest season"""
    # Prepare data for chart
    years = []
    productions = []
    
    for _crop_key, crop_data in data['crops'].items():
        for year, values in crop_data['production_data'].items():
            years.append(year)
            productions.append(values['production'])
    
    # Create DataFrame aggregated by year
    df = pd.DataFrame({'Season': years, 'Production': productions})
    df_grouped = df.groupby('Season')['Production'].sum().reset_index()
    df_grouped['Production_MT'] = df_grouped['Production'] / 1000  # Convert to millions of tons
    
    # Create chart
    fig = px.line(df_grouped, x='Season', y='Production_MT',
                  title='Evolution of Total Grain Production - CONAB',
                  labels={'Production_MT': 'Production (Million Tons)', 'Season': 'Season'},
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Season",
        yaxis_title="Production (Million Tons)",
        hovermode='x unified'
    )
    
    return fig

def create_conab_crop_comparison_chart(data):
    """Creates comparison chart between crops"""
    # Prepare data from most recent harvest
    crop_names = []
    productions = []
    areas = []
    
    for _crop_key, crop_data in data['crops'].items():
        # Get data from 2023/24 season (most recent)
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            productions.append(latest_data['production'] / 1000)  # Convert to millions
            areas.append(latest_data['area'] / 1000)  # Convert to millions
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Production (Million t)',
        x=crop_names,
        y=productions,
        yaxis='y',
        offsetgroup=1,
        marker_color='#2E8B57'
    ))
    
    fig.add_trace(go.Bar(
        name='Area (Million ha)',
        x=crop_names,
        y=areas,
        yaxis='y2',
        offsetgroup=2,
        marker_color='#FF6B35'
    ))
    
    fig.update_layout(
        title='Production and Area by Crop - Season 2023/24 (CONAB)',
        xaxis_title="Crops",
        yaxis={
            "title": "Production (Million tons)",
            "side": "left"
        },
        yaxis2={
            "title": "Area (Million hectares)",
            "side": "right",
            "overlaying": "y"
        },
        barmode='group'
    )
    
    return fig

def create_conab_productivity_chart(data):
    """Creates productivity evolution chart"""
    productivity_data = []
    
    # Focus on soybean and corn (main crops)
    main_crops = ['soybean', 'corn']
    crop_names = {'soybean': 'Soybean', 'corn': 'Corn'}

    for crop_key in main_crops:
        if crop_key in data['crops']:
            crop_data = data['crops'][crop_key]
            for year, values in crop_data['production_data'].items():
                productivity_data.append({
                    'Season': year,
                    'Crop': crop_names[crop_key],
                    'Productivity': values['productivity']
                })
    
    df = pd.DataFrame(productivity_data)
    
    fig = px.line(df, x='Season', y='Productivity', color='Crop',
                  title='Productivity Evolution - CONAB',
                  labels={'Productivity': 'Productivity (kg/ha)', 'Season': 'Season'},
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Season",
        yaxis_title="Productivity (kg/ha)",
        hovermode='x unified'
    )
    
    return fig

def create_conab_area_chart(data):
    """Creates pie chart of area distribution"""
    # Data from 2023/24 season
    crop_names = []
    areas = []
    
    for _crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            areas.append(latest_data['area'])
    
    fig = px.pie(
        values=areas,
        names=crop_names,
        title='Planted Area Distribution by Crop - Season 2023/24 (CONAB)'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_conab_all_crops_chart(data):
    """Creates bar chart with all CONAB crops"""
    # Data from 2023/24 season
    crop_names = []
    productions = []
    
    for _crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            crop_names.append(crop_data['name'])
            productions.append(latest_data['production'])
    
    # Create DataFrame and sort by production
    df = pd.DataFrame({'Crop': crop_names, 'Production': productions})
    df = df.sort_values('Production', ascending=True)
    
    fig = px.bar(
        df,
        x='Production',
        y='Crop',
        orientation='h',
        title='Production by Crop for the Current Season',
        labels={'Production': 'Production (thousand tons)', 'Crop': 'Crop'},
        color='Production',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=600)
    
    return fig

def create_conab_regional_chart(data):
    """Creates CONAB regional production chart"""
    if 'regional_production' not in data:
        return None
    
    regional_data = data['regional_production']
    chart_data = []
    
    for _region_key, region_info in regional_data.items():
        region_name = region_info['name']
        production_data = region_info.get('production_2023_24', {})
        
        for crop, production in production_data.items():
            # Convert crop names
            crop_display = crop.replace('_', ' ').replace('total', '').title()
            chart_data.append({
                'Region': region_name,
                'Crop': crop_display,
                'Production': production
            })
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    
    fig = px.bar(
        df,
        x='Region',
        y='Production',
        color='Crop',
        title='Regional Production by Crop for the Current Season',
        labels={'Production': 'Production (thousand tons)', 'Region': 'Region'},
        barmode='group'
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_conab_crops_evolution_chart(data):
    """Creates evolution chart of all CONAB crops"""
    crops_data = []
    
    # Include all crops
    for _crop_key, crop_data in data['crops'].items():
        crop_name = crop_data['name']
        
        for year, values in crop_data['production_data'].items():
            crops_data.append({
                'Season': year,
                'Crop': crop_name,
                'Production': values['production']
            })
    
    df = pd.DataFrame(crops_data)
    
    fig = px.line(
        df,
        x='Season',
        y='Production',
        color='Crop',
        title='Production Evolution by Crop - CONAB (2018/19 - 2023/24)',
        labels={'Production': 'Production (thousand tons)', 'Season': 'Season'},
        markers=True
    )
    
    fig.update_layout(
        height=600,
        hovermode='x unified'
    )
    
    return fig

def render_conab_production_overview(data):
    """Renders CONAB production overview"""
    st.subheader("🔎 Production Overview - CONAB")
    
    # Main metrics from 2023/24 season
    latest_year = '2023/24'
    total_production = 0
    total_area = 0
    main_crops_count = len(data['crops'])
    
    for crop_data in data['crops'].values():
        if latest_year in crop_data['production_data']:
            production_data = crop_data['production_data'][latest_year]
            total_production += production_data['production']
            total_area += production_data['area']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Production 2023/24",
            f"{total_production/1000:.1f} million t",
            delta=f"{main_crops_count} main crops"
        )
    
    with col2:
        st.metric(
            "Total Planted Area",
            f"{total_area/1000:.1f} million ha",
            delta="Season 2023/24"
        )
    
    with col3:
        avg_productivity = (total_production / total_area) if total_area > 0 else 0
        st.metric(
            "Average Productivity",
            f"{avg_productivity:.0f} kg/ha",
            delta="Weighted average"
        )

def render_conab_charts(data):
    """Renders CONAB data charts"""
    st.subheader("📈 Detailed Analysis - CONAB")
    
    # First row: Total production and area distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig_production = create_conab_production_chart(data)
        st.plotly_chart(fig_production, use_container_width=True)
    
    with col2:
        fig_area = create_conab_area_chart(data)
        st.plotly_chart(fig_area, use_container_width=True)
    
    # Second row: Comparison between crops
    fig_comparison = create_conab_crop_comparison_chart(data)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Third row: All crops (horizontal bars)
    fig_all_crops = create_conab_all_crops_chart(data)
    st.plotly_chart(fig_all_crops, use_container_width=True)
    
    # Fourth row: Temporal evolution of all crops
    fig_evolution = create_conab_crops_evolution_chart(data)
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Fifth row: Regional data (if available)
    fig_regional = create_conab_regional_chart(data)
    if fig_regional:
        st.plotly_chart(fig_regional, use_container_width=True)
    
    # Sixth row: Productivity
    fig_productivity = create_conab_productivity_chart(data)
    st.plotly_chart(fig_productivity, use_container_width=True)

def render_conab_data_table(data):
    """Renders table with detailed CONAB data"""
    st.subheader("📋 Detailed Data by Crop - CONAB")
    
    # Information about Portal 360° (if available)
    if 'portal_360_info' in data:
        portal_info = data['portal_360_info']
        st.info(f"ℹ️ **{portal_info['description']}**")
        
        # Display portal features in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Available features:**")
            for feature in portal_info.get('features', []):
                st.markdown(f"• {feature}")
        
        with col2:
            if 'products_covered' in portal_info:
                st.markdown("**Products covered:**")
                products_text = ", ".join(portal_info['products_covered'])
                st.markdown(products_text)
    
    # Prepare data for table
    table_data = []
    
    for _crop_key, crop_data in data['crops'].items():
        if '2023/24' in crop_data['production_data']:
            latest_data = crop_data['production_data']['2023/24']
            table_data.append({
                'Crop': crop_data['name'],
                'Scientific Name': crop_data.get('scientific_name', 'N/A'),
                'Production (thousand t)': f"{latest_data['production']:,}",
                'Area (thousand ha)': f"{latest_data['area']:,}",
                'Productivity (kg/ha)': f"{latest_data['productivity']:,}"
            })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    # Add regional information if available
    if 'regional_production' in data:
        st.subheader("🗺️ Regional Information - CONAB")
        regional_data = data['regional_production']
        
        for _region_key, region_info in regional_data.items():
            with st.expander(f"📍 {region_info['name']}"):
                st.markdown(f"**States:** {', '.join(region_info['states'])}")
                st.markdown(f"**Characteristics:** {region_info['characteristics']}")
                
                if 'production_2023_24' in region_info:
                    st.markdown("**Main productions (season 2023/24):**")
                    prod_data = region_info['production_2023_24']
                    for crop, production in prod_data.items():
                        crop_name = crop.replace('_', ' ').title()
                        st.markdown(f"• {crop_name}: {production:,} thousand tons")

def render():
    """Main function to render the CONAB component"""
    # Load data
    data = load_conab_data()
    
    if data is None:
        return
    
    # Render components
    render_conab_production_overview(data)
    st.divider()
    
    render_conab_charts(data)
    st.divider()
    
    render_conab_data_table(data)
    
    # Footer with data source
    st.markdown("---")
    st.markdown("### 📋 About CONAB Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            "**🏢 CONAB - National Supply Company**  \n"
            "Public company linked to the Ministry of Agriculture,  \n"
            "responsible for managing Brazilian agricultural policies.  \n\n"
            "**🌐 Official Website:** https://www.gov.br/conab/pt-br  \n"
            "**📊 Information Portal:** [Products 360°](https://portaldeinformacoes.conab.gov.br/produtos-360.html)  \n"
            "**📈 Harvest Bulletins:** Monthly grain surveys"
        )
    
    with col2:
        st.markdown(
            f"**📅 Data Period:** Seasons 2018/19 to 2023/24  \n"
            f"**🌾 Total Crops:** {len(data['crops'])} main crops  \n"
            f"**🗺️ Coverage:** Entire Brazilian national territory  \n"
            f"**📊 Regional Data:** {len(data.get('regional_production', {}))} regions  \n\n"
            "**🔗 Portal 360°:** Detailed information by product,  \n"
            "historical series, production costs and regional analysis."
        )

# Function for testing
if __name__ == "__main__":
    st.set_page_config(page_title="CONAB Data", layout="wide")
    st.title("🌾 CONAB Agricultural Data")
    render()
