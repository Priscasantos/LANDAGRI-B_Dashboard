"""
Brazilian Agricultural Data Component
=====================================

Component for displaying Brazilian agricultural production data from IBGE.

Author: Dashboard Iniciativas LULC
Date: 2025-01-28
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def load_agricultural_data() -> dict:
    """
    Load Brazilian agricultural data from JSON file.

    Returns:
        dict: Agricultural data dictionary or empty dict if error
    """
    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "brazilian_agricultural_data.json"

        if data_path.exists():
            with open(data_path, encoding='utf-8') as f:
                return json.load(f)
        else:
            st.warning(f"Agricultural data file not found at: {data_path}")
            return {}
    except Exception as e:
        st.error(f"Error loading agricultural data: {e}")
        return {}


def render_production_overview(data: dict) -> None:
    """
    Render agricultural production overview with key metrics.
    
    Args:
        data: Agricultural data dictionary
    """
    if not data or 'data' not in data:
        st.warning("No agricultural data available")
        return
    
    st.markdown("### 🌾 Panorama da Produção Agrícola Brasileira")
    
    # Get latest year data (2023)
    latest_year = "2023"
    agri_data = data['data']['producao_agricola']
    
    # Calculate key metrics
    total_production = 0
    total_area = 0
    major_crops = []

    for _, crop_data in agri_data.items():
        if 'quantidade_produzida_toneladas' in crop_data and latest_year in crop_data['quantidade_produzida_toneladas']:
            prod = crop_data['quantidade_produzida_toneladas'][latest_year]
            area = crop_data.get('area_colhida_hectares', {}).get(latest_year, 0)

            total_production += prod
            total_area += area

            major_crops.append({
                'crop': crop_data['nome'],
                'production': prod,
                'area': area
            })
    
    # Sort crops by production
    major_crops.sort(key=lambda x: x['production'], reverse=True)
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Produção Total (2023)",
            f"{total_production/1_000_000:.1f}M ton",
            help="Produção total de culturas temporárias em milhões de toneladas"
        )
    
    with col2:
        st.metric(
            "Área Colhida Total",
            f"{total_area/1_000_000:.1f}M ha",
            help="Área total colhida em milhões de hectares"
        )
    
    with col3:
        if major_crops:
            st.metric(
                "Principal Cultura",
                major_crops[0]['crop'].split('(')[0].strip(),
                f"{major_crops[0]['production']/1_000_000:.1f}M ton"
            )
    
    with col4:
        productivity = (total_production / total_area) if total_area > 0 else 0
        st.metric(
            "Produtividade Média",
            f"{productivity:.2f} ton/ha",
            help="Produtividade média das culturas temporárias"
        )


def render_production_charts(data: dict) -> None:
    """
    Render production charts for major crops.
    
    Args:
        data: Agricultural data dictionary
    """
    if not data or 'data' not in data:
        return
    
    agri_data = data['data']['producao_agricola']
    
    # Prepare data for charts
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    major_crops = ['soja', 'milho', 'cana_de_acucar', 'mandioca', 'arroz']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Evolução da Produção (2018-2023)")
        
        # Create production evolution chart
        fig_prod = go.Figure()
        
        for crop_key in major_crops:
            if crop_key in agri_data:
                crop_data = agri_data[crop_key]
                production_data = crop_data.get('quantidade_produzida_toneladas', {})
                
                y_values = [production_data.get(year, 0)/1_000_000 for year in years]  # Convert to millions
                
                fig_prod.add_trace(go.Scatter(
                    x=years,
                    y=y_values,
                    mode='lines+markers',
                    name=crop_data['nome'].split('(')[0].strip(),
                    line={'width': 3}
                ))
        
        fig_prod.update_layout(
            title="Produção (Milhões de Toneladas)",
            xaxis_title="Ano",
            yaxis_title="Produção (M ton)",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_prod, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribuição da Produção em 2023")
        
        # Create pie chart for 2023 production
        latest_year = "2023"
        production_2023 = []
        labels_2023 = []
        
        for crop_key in major_crops:
            if crop_key in agri_data:
                crop_data = agri_data[crop_key]
                prod = crop_data.get('quantidade_produzida_toneladas', {}).get(latest_year, 0)
                if prod > 0:
                    production_2023.append(prod)
                    labels_2023.append(crop_data['nome'].split('(')[0].strip())
        
        if production_2023:
            fig_pie = px.pie(
                values=production_2023,
                names=labels_2023,
                title="Distribuição da Produção 2023"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            
            st.plotly_chart(fig_pie, use_container_width=True)


def render_area_analysis(data: dict) -> None:
    """
    Render area harvested analysis.
    
    Args:
        data: Agricultural data dictionary
    """
    if not data or 'data' not in data:
        return
    
    st.markdown("#### Análise da Área Colhida")
    
    agri_data = data['data']['producao_agricola']
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    
    # Create area evolution chart
    fig_area = go.Figure()
    
    major_crops = ['soja', 'milho', 'cana_de_acucar', 'mandioca', 'arroz']
    
    for crop_key in major_crops:
        if crop_key in agri_data:
            crop_data = agri_data[crop_key]
            area_data = crop_data.get('area_colhida_hectares', {})
            
            y_values = [area_data.get(year, 0)/1_000_000 for year in years]  # Convert to millions
            
            fig_area.add_trace(go.Scatter(
                x=years,
                y=y_values,
                mode='lines+markers',
                name=crop_data['nome'].split('(')[0].strip(),
                line={'width': 3}
            ))
    
    fig_area.update_layout(
        title="Evolução da Área Colhida (Milhões de Hectares)",
        xaxis_title="Ano",
        yaxis_title="Área Colhida (M ha)",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_area, use_container_width=True)


def render_detailed_table(data: dict) -> None:
    """
    Render detailed data table.
    
    Args:
        data: Agricultural data dictionary
    """
    if not data or 'data' not in data:
        return
    
    st.markdown("#### Dados Detalhados por Cultura")
    
    agri_data = data['data']['producao_agricola']
    latest_year = "2023"
    
    # Prepare table data
    table_data = []

    for _, crop_data in agri_data.items():
        production = crop_data.get('quantidade_produzida_toneladas', {}).get(latest_year, 0)
        area = crop_data.get('area_colhida_hectares', {}).get(latest_year, 0)
        productivity = (production / area) if area > 0 else 0

        table_data.append({
            'Cultura': crop_data['nome'],
            'Produção (ton)': f"{production:,.0f}",
            'Área Colhida (ha)': f"{area:,.0f}",
            'Produtividade (ton/ha)': f"{productivity:.2f}"
        })
    
    # Sort by production
    table_data.sort(key=lambda x: float(x['Produção (ton)'].replace(',', '')), reverse=True)
    
    # Display table
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)


def render() -> None:
    """
    Main render function for Brazilian agricultural data component.
    """
    # Load agricultural data
    data = load_agricultural_data()
    
    if not data:
        st.error("❌ Não foi possível carregar os dados agrícolas brasileiros")
        return
    
    # Add section header
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 600;">
            🇧🇷 Dados Agrícolas do Brasil
        </h2>
        <p style="color: #d1fae5; margin: 0.3rem 0 0 0; font-size: 1rem;">
            Produção agrícola nacional - Dados IBGE 2018-2023
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Display metadata info
    if 'metadata' in data:
        with st.expander("ℹ️ Informações sobre os dados", expanded=False):
            metadata = data['metadata']
            st.markdown(f"**Fonte:** {metadata.get('source', 'N/A')}")
            st.markdown(f"**Pesquisa:** {metadata.get('survey', 'N/A')}")
            st.markdown(f"**Período:** {metadata.get('period_range', 'N/A')}")
            st.markdown(f"**Última atualização:** {metadata.get('last_updated', 'N/A')}")
            st.markdown(f"**Descrição:** {metadata.get('description', 'N/A')}")
    
    # Render components
    render_production_overview(data)
    
    st.markdown("---")
    
    render_production_charts(data)
    
    st.markdown("---")
    
    render_area_analysis(data) 
    
    st.markdown("---")
    
    render_detailed_table(data)
