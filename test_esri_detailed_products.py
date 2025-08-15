"""
Teste para validar a renderização dos produtos detalhados do ESRI-10m Annual LULC
==============================================================================

Este teste demonstra como a função render_lulc_classes_section agora suporta
a estrutura de detailed_products com múltiplas classificações.
"""

import json
import streamlit as st
from dashboard.components.overview.lulc_classes import render_lulc_classes_section


def test_esri_detailed_products():
    """
    Testa a renderização dos produtos detalhados do ESRI-10m Annual LULC.
    """
    st.title("🧪 Teste: ESRI-10m Annual LULC - Produtos Detalhados")
    
    # Dados de exemplo do ESRI-10m Annual LULC
    esri_detailed_products = [
        {
            "product_name": "Open Data Product",
            "product_type": "Open",
            "number_of_classes": 9,
            "class_legend": "Built, Crops, Trees, Water, Rangeland, Flooded Vegetation, Snow/Ice, Bare Ground, Clouds",
            "accuracy": 85.0,
            "description": "Open access version with 9 land cover classes",
            "access_type": "Open"
        },
        {
            "product_name": "Private Data Product", 
            "product_type": "Private",
            "number_of_classes": 15,
            "class_legend": "Water Channel Extent, Variable Water, Persistent Water, Dense Trees, Sparse Trees, Dense Rangeland, Sparse Rangeland, Flooded Vegetation, Inactive Cropland, Active Cropland, High Density Built, Low Density Built, Bare Ground, Snow/Ice, Cloud",
            "accuracy": 85.0,
            "description": "Commercial version with 15 detailed land cover classes",
            "access_type": "Commercial"
        }
    ]
    
    st.info("📋 Este teste demonstra a renderização dos produtos detalhados do ESRI com classificações Open e Private/Commercial.")
    
    # Converter para JSON string como seria passado na aplicação real
    detailed_products_json = json.dumps(esri_detailed_products)
    
    # Renderizar usando a função
    render_lulc_classes_section(detailed_products_json)
    
    st.success("✅ Teste concluído! A função agora suporta produtos detalhados.")
    
    # Mostrar o JSON usado no teste
    with st.expander("🔍 Ver JSON de entrada usado no teste"):
        st.code(detailed_products_json, language="json")


def test_simple_class_legend():
    """
    Testa a compatibilidade com o formato simples de class_legend.
    """
    st.title("🧪 Teste: Compatibilidade com Formato Simples")
    
    simple_classes = [
        "Forest",
        "Cropland", 
        "Urban",
        "Water",
        "Grassland"
    ]
    
    st.info("📋 Este teste verifica se a função ainda funciona com o formato simples de lista de classes.")
    
    simple_json = json.dumps(simple_classes)
    render_lulc_classes_section(simple_json)
    
    st.success("✅ Compatibilidade mantida com formato simples!")
    
    with st.expander("🔍 Ver JSON simples usado no teste"):
        st.code(simple_json, language="json")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Teste LULC Classes",
        page_icon="🧪",
        layout="wide"
    )
    
    st.sidebar.title("🧪 Testes")
    test_option = st.sidebar.radio(
        "Escolha o teste:",
        ["Produtos Detalhados (ESRI)", "Formato Simples", "Ambos"]
    )
    
    if test_option == "Produtos Detalhados (ESRI)":
        test_esri_detailed_products()
    elif test_option == "Formato Simples":
        test_simple_class_legend()
    else:
        test_esri_detailed_products()
        st.divider()
        test_simple_class_legend()
