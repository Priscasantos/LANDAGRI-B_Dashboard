"""
IBGE Agricultural Data Dashboard Component
Integrated with the agricultural_analysis.py orchestration system
Version: 1.0 - Updated
"""

import streamlit as st

def render():
    """Renders IBGE-specific data"""

    st.markdown("### 📈 General Summary")

    # Try to load IBGE data
    data = load_ibge_data()
    
    if not data:
        st.warning("⚠️ IBGE data not available at the moment")
        
        # Information about IBGE
        st.markdown("""
        ### 📊 About IBGE - PAM
        
        The **Municipal Agricultural Production (PAM)** is an IBGE survey that investigates 
        information on planted area, harvested area, quantity produced, average yield 
        and value of municipal agricultural production.
        
        - 📋 **Coverage**: All Brazilian municipalities
        - 🌾 **Crops**: More than 60 agricultural products
        - 📅 **Frequency**: Annual (data since 1974)
        - 📍 **Detail**: Municipal, State and National
        
        ### 🎯 Main Researched Crops
        
        #### Cereals, Legumes and Oilseeds
        - Soybean, Corn, Rice, Beans
        - Wheat, Sorghum, Oats, Rye
        - Cotton, Sunflower, Peanut
        - Castor Bean, Sesame, Canola
        
        #### Fruits
        - Orange, Banana, Grape, Apple
        - Mango, Papaya, Pineapple, Coconut
        - Watermelon, Melon, Guava
        
        #### Other Crops
        - Sugarcane, Coffee, Cocoa
        - Tobacco, Cassava, Potato
        - Tomato, Onion, Garlic
        
        ### 📊 Investigated Variables
        
        - **Planted Area** (hectares)
        - **Harvested Area** (hectares)  
        - **Quantity Produced** (tons)
        - **Average Yield** (kg/ha)
        - **Production Value** (thousand reais)
        
        ### 📈 Available Historical Series
        
        - **Historical Data**: 1974 to present
        - **Last Update**: 2023 data
        - **Frequency**: Annual release (September/October)
        
        **Source:** [IBGE - PAM - Municipal Agricultural Production](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html)
        """)
        
        return
    
    # If we have data, render visualizations
    render_ibge_visualizations(data)


def load_ibge_data():
    """Loads IBGE agricultural data"""
    try:
        import json
        import os
        
        # First tries to load the specific IBGE data file
        data_path = os.path.join('data', 'brazilian_ibge_agricultural_data.json')
        if os.path.exists(data_path):
            with open(data_path, encoding='utf-8') as f:
                return json.load(f)
        
        # Fallback to alternative file
        alt_data_path = os.path.join('data', 'ibge_agricultural_data.json')
        if os.path.exists(alt_data_path):
            with open(alt_data_path, encoding='utf-8') as f:
                return json.load(f)
        
        return None
    except Exception as e:
        st.error(f"❌ Error loading IBGE data: {e}")
        return None


def render_ibge_visualizations(data):
    """Renders IBGE data visualizations"""
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Extract data from actual JSON
        producao_data = data.get('data', {}).get('producao_agricola', {})
        latest_year = "2023"  # Most recent year in the data
        
        with col1:
            total_crops = len(producao_data)
            st.metric("🌾 Crops", total_crops)
        
        with col2:
            st.metric("📅 Reference Year", latest_year)
        
        with col3:
            # Calculate total production for the most recent year
            total_production = 0
            for _crop_name, crop_data in producao_data.items():
                producao_toneladas = crop_data.get('quantidade_produzida_toneladas', {})
                if latest_year in producao_toneladas:
                    total_production += producao_toneladas[latest_year]
            
            st.metric("📈 Total Production", f"{total_production/1000000:.1f}M ton")
        
        with col4:
            # Calculate total harvested area for the most recent year
            total_area = 0
            for _crop_name, crop_data in producao_data.items():
                area_colhida = crop_data.get('area_colhida_hectares', {})
                if latest_year in area_colhida:
                    total_area += area_colhida[latest_year]
            
            st.metric("🌍 Total Area", f"{total_area/1000000:.1f}M ha")
    
    except Exception as e:
        st.error(f"❌ Error processing IBGE metrics: {e}")
    
    st.divider()
    
    # Analysis tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Production by Crop",
        "🗺️ Regional Distribution", 
        "📈 Historical Series"
    ])
    
    with tab1:
        render_ibge_production_tab(data)
    
    with tab2:
        render_ibge_regional_tab(data)
        
    with tab3:
        render_ibge_historical_tab(data)


def render_ibge_production_tab(data):
    """Renders production by crop tab"""
    st.markdown("#### 🌾 Production by Crop from 2023 IBGE's PAM Data")
    
    # Bar chart of main crops
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extract actual data from JSON
        producao_data = data.get('data', {}).get('producao_agricola', {})
        latest_year = "2023"
        
        crops_data = []
        for _crop_key, crop_info in producao_data.items():
            nome = crop_info.get('nome', _crop_key.title())
            producao = crop_info.get('quantidade_produzida_toneladas', {}).get(latest_year, 0)
            area = crop_info.get('area_colhida_hectares', {}).get(latest_year, 0)
            
            # Calculate productivity
            produtividade = (producao * 1000 / area) if area > 0 else 0  # kg/ha
            
            crops_data.append({
                'Crop': nome,
                'Production (thousand t)': producao / 1000,
                'Area (thousand ha)': area / 1000,
                'Productivity (t/ha)': produtividade / 1000
            })
        
        # Create DataFrame and sort by production
        df = pd.DataFrame(crops_data)
        df = df.sort_values('Production (thousand t)', ascending=False)
        
        # Production chart
        fig1 = px.bar(
            df.head(10), 
            x='Crop', 
            y='Production (thousand t)',
            title="📊 Production by Crop from 2023 IBGE's PAM Data",
            color='Production (thousand t)',
            color_continuous_scale='Greens'
        )
        fig1.update_layout(height=400)
        fig1.update_xaxes(tickangle=45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Harvested area chart
        fig2 = px.bar(
            df.head(10), 
            x='Crop', 
            y='Area (thousand ha)',
            title="🌍 Harvested Area by Crop - IBGE PAM 2023",
            color='Area (thousand ha)',
            color_continuous_scale='Blues'
        )
        fig2.update_layout(height=400)
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed table
        st.markdown("##### 📋 Detailed IBGE PAM 2023 Data")
        st.dataframe(df.round(2), use_container_width=True)
        
        # Data source
        st.markdown("**Source:** IBGE - Municipal Agricultural Production (PAM)")
        
    except Exception as e:
        st.error(f"❌ Error rendering production charts: {e}")


def render_ibge_regional_tab(data):
    """Renders regional analysis tab"""
    st.markdown("#### 🗺️ Regional Analysis - IBGE PAM")
    
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extract actual regional data
        producao_data = data.get('data', {}).get('producao_agricola', {})
        resumo_regional = data.get('data', {}).get('resumo_regional', {})
        
        # Mapeamento de regiões para cálculo consolidado
        regional_data = {}
        
        # Processar dados por cultura para extrair informações regionais
        for _crop_key, crop_info in producao_data.items():
            crop_name = crop_info.get('nome', _crop_key.title())
            
            # Get most recent data (2023)
            producao_2023 = crop_info.get('quantidade_produzida_toneladas', {}).get('2023', 0)
            area_2023 = crop_info.get('area_colhida_hectares', {}).get('2023', 0)
            
            # Calculate productivity
            produtividade = (producao_2023 / area_2023) if area_2023 > 0 else 0
            
            regional_data[crop_name] = {
                'Production (t)': producao_2023,
                'Area (ha)': area_2023,
                'Productivity (t/ha)': produtividade
            }
        
        # If we have specific regional data, use them
        if resumo_regional:
            region_summary = {}
            for region, region_data in resumo_regional.items():
                total_prod = sum(region_data.get('culturas', {}).values())
                region_summary[region] = total_prod
            
            # Create bar chart by region
            regions = list(region_summary.keys())
            productions = [region_summary[r] / 1000000 for r in regions]  # Millions of tons
            
            df_regions = pd.DataFrame({
                'Region': regions,
                'Production (M ton)': productions
            })
            
            fig_regions = px.bar(
                df_regions,
                x='Region',
                y='Production (M ton)',
                title="🗺️ Agricultural Production by Region (2023)",
                color='Production (M ton)',
                color_continuous_scale='Greens'
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        
        else:
            # Regional distribution simulation based on actual data
            crops_by_region = {
                'Southeast': ['soybean', 'corn', 'sugarcane', 'coffee', 'orange'],
                'South': ['soybean', 'corn', 'rice', 'tobacco'],
                'Center-West': ['soybean', 'corn', 'cotton'],
                'Northeast': ['sugarcane', 'cassava', 'beans'],
                'North': ['cassava', 'cocoa', 'acai']
            }
            
            region_totals = {}
            for region, main_crops in crops_by_region.items():
                total_production = 0
                for crop in main_crops:
                    for crop_key, crop_data in regional_data.items():
                        if any(crop_word in crop_key.lower() for crop_word in crop.split('_')):
                            # Estimated distribution by region
                            region_factor = {
                                'Southeast': 0.3, 'South': 0.25, 'Center-West': 0.25,
                                'Northeast': 0.15, 'North': 0.05
                            }
                            total_production += crop_data['Production (t)'] * region_factor.get(region, 0.2)
                
                region_totals[region] = total_production / 1000000  # Millions of tons
            
            # Bar chart by region
            df_regions = pd.DataFrame([
                {'Region': region, 'Production (M ton)': production}
                for region, production in region_totals.items()
            ])
            
            fig_regions = px.bar(
                df_regions,
                x='Region',
                y='Production (M ton)',
                title="🗺️ Agricultural Production Distribution by Region (2023)",
                color='Production (M ton)',
                color_continuous_scale='Greens'
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        
        # Crop concentration analysis
        st.markdown("##### 🌾 Main Crops by Region")
        
        # Prepare main crops data
        top_crops = sorted(regional_data.items(), key=lambda x: x[1]['Production (t)'], reverse=True)[:8]
        
        crops_data = []
        for crop_name, crop_data in top_crops:
            crops_data.append({
                'Crop': crop_name,
                'Production (M ton)': crop_data['Production (t)'] / 1000000,
                'Area (M ha)': crop_data['Area (ha)'] / 1000000,
                'Productivity (t/ha)': crop_data['Productivity (t/ha)']
            })
        
        df_crops = pd.DataFrame(crops_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart - Production by crop
            fig_crops = px.bar(
                df_crops.head(6),
                x='Crop',
                y='Production (M ton)',
                title="📊 Main Crops - Production",
                color='Production (M ton)',
                color_continuous_scale='Blues'
            )
            fig_crops.update_xaxes(tickangle=45)
            st.plotly_chart(fig_crops, use_container_width=True)
        
        with col2:
            # Bar chart - Area by crop
            fig_area = px.bar(
                df_crops.head(6),
                x='Crop',
                y='Area (M ha)',
                title="🌍 Main Crops - Area",
                color='Area (M ha)',
                color_continuous_scale='Oranges'
            )
            fig_area.update_xaxes(tickangle=45)
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Regional metrics
        st.markdown("##### 📊 Regional Indicators")
        
        total_production = sum(crop_data['Production (t)'] for crop_data in regional_data.values()) / 1000000
        total_area = sum(crop_data['Area (ha)'] for crop_data in regional_data.values()) / 1000000
        avg_productivity = total_production * 1000 / total_area if total_area > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌾 Total Production", f"{total_production:.1f} M ton")
        
        with col2:
            st.metric("🌍 Total Area", f"{total_area:.1f} M ha")
        
        with col3:
            st.metric("📊 Average Productivity", f"{avg_productivity:.2f} t/ha")
        
        with col4:
            st.metric("🔢 Number of Crops", len(regional_data))
        
        # Detailed table by crop
        st.markdown("##### 📋 Detailed Data by Crop")
        st.dataframe(df_crops.round(2), use_container_width=True)
        
        # Data source
        st.markdown("**Source:** IBGE - Municipal Agricultural Production (PAM)")
        
    except Exception as e:
        st.error(f"❌ Error rendering regional analysis: {e}")


def render_ibge_historical_tab(data):
    """Renders historical series tab"""
    st.markdown("#### 📈 Historical Series - IBGE PAM (2018-2023)")
    
    try:
        import pandas as pd
        import plotly.express as px
        
        # Extract actual historical data
        producao_data = data.get('data', {}).get('producao_agricola', {})
        
        # Prepare historical total production data
        years = ['2018', '2019', '2020', '2021', '2022', '2023']
        total_production_by_year = []
        total_area_by_year = []
        
        for year in years:
            year_production = 0
            year_area = 0
            
            for _crop_key, crop_info in producao_data.items():
                producao = crop_info.get('quantidade_produzida_toneladas', {}).get(year, 0)
                area = crop_info.get('area_colhida_hectares', {}).get(year, 0)
                
                year_production += producao
                year_area += area
            
            total_production_by_year.append(year_production / 1000000)  # Millions of tons
            total_area_by_year.append(year_area / 1000000)  # Millions of hectares
        
        # Calculate average productivity
        productivity_by_year = [
            (prod * 1000 / area) if area > 0 else 0 
            for prod, area in zip(total_production_by_year, total_area_by_year)
        ]
        
        # Create historical DataFrame
        df_hist = pd.DataFrame({
            'Year': [int(y) for y in years],
            'Total Production (M ton)': total_production_by_year,
            'Total Area (M ha)': total_area_by_year,
            'Productivity (t/ha)': productivity_by_year
        })
        
        # Line chart for total production
        fig_line = px.line(
            df_hist, 
            x='Year', 
            y='Total Production (M ton)',
            title="📈 Evolution of Total Agricultural Production IBGE (2018-2023)",
            markers=True
        )
        fig_line.update_traces(line_color='green', line_width=3)
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Area chart
            fig_area = px.line(
                df_hist, 
                x='Year', 
                y='Total Area (M ha)',
                title="🌍 Evolution of Total Harvested Area",
                markers=True
            )
            fig_area.update_traces(line_color='blue')
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            # Productivity chart
            fig_prod = px.line(
                df_hist,
                x='Year',
                y='Productivity (t/ha)',
                title="📊 Evolution of Average Productivity",
                markers=True
            )
            fig_prod.update_traces(line_color='orange')
            st.plotly_chart(fig_prod, use_container_width=True)
        
        # Trend analysis
        st.markdown("##### 📊 Trend Analysis (2018-2023)")
        
        growth_production = ((df_hist['Total Production (M ton)'].iloc[-1] / df_hist['Total Production (M ton)'].iloc[0]) - 1) * 100
        growth_area = ((df_hist['Total Area (M ha)'].iloc[-1] / df_hist['Total Area (M ha)'].iloc[0]) - 1) * 100
        growth_productivity = ((df_hist['Productivity (t/ha)'].iloc[-1] / df_hist['Productivity (t/ha)'].iloc[0]) - 1) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📈 Production Growth", 
                f"{growth_production:.1f}%",
                delta=f"{growth_production:.1f}%"
            )
        
        with col2:
            st.metric(
                "🌍 Area Growth", 
                f"{growth_area:.1f}%",
                delta=f"{growth_area:.1f}%"
            )
        
        with col3:
            st.metric(
                "📊 Productivity Growth", 
                f"{growth_productivity:.1f}%",
                delta=f"{growth_productivity:.1f}%"
            )
        
        # Main crops evolution chart
        st.markdown("##### 🌾 Evolution of Main Crops")
        
        # Select the 5 main crops by production in 2023
        main_crops = {}
        for crop_key, crop_info in producao_data.items():
            producao_2023 = crop_info.get('quantidade_produzida_toneladas', {}).get('2023', 0)
            main_crops[crop_key] = {
                'nome': crop_info.get('nome', crop_key.title()),
                'producao_2023': producao_2023
            }
        
        # Sort and get top 5
        top_crops = sorted(main_crops.items(), key=lambda x: x[1]['producao_2023'], reverse=True)[:5]
        
        # Prepare data for multiple line chart
        evolution_data = []
        for year in years:
            for crop_key, crop_data in top_crops:
                crop_info = producao_data[crop_key]
                producao = crop_info.get('quantidade_produzida_toneladas', {}).get(year, 0) / 1000000
                evolution_data.append({
                    'Year': int(year),
                    'Crop': crop_data['nome'],
                    'Production (M ton)': producao
                })
        
        df_evolution = pd.DataFrame(evolution_data)
        
        fig_evolution = px.line(
            df_evolution,
            x='Year',
            y='Production (M ton)',
            color='Crop',
            title="📈 Evolution of Top 5 Crops (2018-2023)",
            markers=True
        )
        fig_evolution.update_layout(height=400)
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Complete historical table
        st.markdown("##### 📋 Complete Historical Data")
        st.dataframe(df_hist.round(2), use_container_width=True)
        
        # Data source
        st.markdown("**Source:** IBGE - Municipal Agricultural Production (PAM)")
        
    except Exception as e:
        st.error(f"❌ Error rendering historical series: {e}")
