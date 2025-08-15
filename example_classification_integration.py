"""
Exemplo de como integrar o suporte a detailed_products na aplicação principal
===========================================================================

Este arquivo demonstra como modificar o código que chama render_lulc_classes_section
para suportar tanto class_legend simples quanto detailed_products.
"""

import json
from typing import Dict, Any


def extract_classification_data(initiative_data: Dict[str, Any]) -> str:
    """
    Extrai dados de classificação de uma iniciativa, suportando tanto
    class_legend simples quanto detailed_products complexos.
    
    Args:
        initiative_data: Dados da iniciativa do metadata JSON
        
    Returns:
        String JSON contendo as classificações para renderização
    """
    # Verificar se existe detailed_products
    if "detailed_products" in initiative_data:
        detailed_products = initiative_data["detailed_products"]
        if detailed_products and isinstance(detailed_products, list):
            return json.dumps(detailed_products)
    
    # Fallback para class_legend simples
    if "class_legend" in initiative_data:
        class_legend = initiative_data["class_legend"]
        if isinstance(class_legend, str):
            # Converter string separada por vírgulas em lista
            classes = [cls.strip() for cls in class_legend.split(",")]
            return json.dumps(classes)
        elif isinstance(class_legend, list):
            return json.dumps(class_legend)
    
    # Retornar lista vazia se não houver dados de classificação
    return json.dumps([])


def example_usage():
    """
    Exemplo de uso com dados reais do ESRI-10m Annual LULC.
    """
    # Dados de exemplo do ESRI (como no metadata)
    esri_initiative_data = {
        "coverage": "Global",
        "acronym": "ESRI-10m LULC",
        "provider": "Environmental Systems Research Institute (ESRI), Impact Observatory, and Microsoft Maps for Good Initiative",
        "source": "Sentinel-2 MSI",
        "spatial_resolution": 10,
        "detailed_products": [
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
    }
    
    # Extrair dados de classificação
    classification_json = extract_classification_data(esri_initiative_data)
    
    print("🎯 Dados de classificação extraídos para o ESRI:")
    print(classification_json)
    
    # Exemplo com iniciativa simples (Dynamic World)
    dynamic_world_data = {
        "coverage": "Global",
        "acronym": "GDW",
        "provider": "Google and World Resources Institute",
        "class_legend": "Water, Trees, Grass, Flooded Vegetation, Crops, Shrub and Scrub, Built, Bare, Snow and Ice",
        "overall_accuracy": 73.8
    }
    
    classification_simple_json = extract_classification_data(dynamic_world_data)
    
    print("\n🎯 Dados de classificação extraídos para o Dynamic World:")
    print(classification_simple_json)


# Código para integração na aplicação principal
def render_initiative_classification(initiative_name: str, initiative_data: Dict[str, Any]):
    """
    Função que seria usada na aplicação principal para renderizar classificações.
    
    Args:
        initiative_name: Nome da iniciativa
        initiative_data: Dados da iniciativa do metadata
    """
    from dashboard.components.overview.lulc_classes import render_lulc_classes_section
    
    print(f"\n📊 Renderizando classificação para: {initiative_name}")
    
    # Extrair dados de classificação
    classification_json = extract_classification_data(initiative_data)
    
    # Renderizar usando a função atualizada
    render_lulc_classes_section(classification_json)


if __name__ == "__main__":
    example_usage()
