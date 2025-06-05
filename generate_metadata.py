# -*- coding: utf-8 -*-
"""
Gerador de Metadados para Iniciativas LULC
==========================================

Este script cria os metadados detalhados para cada iniciativa de mapeamento 
de cobertura e uso da terra (LULC) analisada no sistema.

Autor: Análise Comparativa de Iniciativas LULC
Data: 2024
"""

import json
import os

def create_initiatives_metadata():
    """
    Cria o arquivo JSON com metadados detalhados de cada iniciativa LULC.
    
    Returns:
        dict: Dicionário com metadados de todas as iniciativas
    """
    
    metadata = {
        'Copernicus Global Land Cover Service (CGLS)': {
            'metodologia': 'Combina dados de múltiplos sensores usando algoritmos de machine learning para classificação automática de cobertura terrestre.',
            'validacao': 'Validação independente com dados de campo e comparação com produtos similares. Acurácia global de 75%.',
            'cobertura': 'Cobertura global com atualizações anuais desde 2015. Foco na Europa com extensão mundial.',
            'fonte_dados': 'PROBA-V, Sentinel-1, Sentinel-2, dados auxiliares de topografia e clima.',
            'resolucao_espacial': '100m',
            'acuracia': '75%',
            'frequencia_temporal': 'Anual',
            'classes': '23 classes'
        },
        'Dynamic World (GDW)': {
            'metodologia': 'Deep learning aplicado a dados Sentinel-2 usando Google Earth Engine. Fornece probabilidades para cada classe.',
            'validacao': 'Validação contínua com dados crowdsourced e comparação com mapas de referência. Acurácia de 74%.',
            'cobertura': 'Cobertura global com atualizações em tempo quase real (2-5 dias).',
            'fonte_dados': 'Sentinel-2 Top of Atmosphere, processamento no Google Earth Engine.',
            'resolucao_espacial': '10m',
            'acuracia': '74%',
            'frequencia_temporal': 'Tempo real',
            'classes': '9 classes'
        },
        'ESRI-10m Annual LULC': {
            'metodologia': 'Deep learning treinado com bilhões de pixels rotulados por humanos da National Geographic Society.',
            'validacao': 'Validação com dados curados pela National Geographic. Acurácia superior a 76%.',
            'cobertura': 'Cobertura global anual desde 2017 usando Sentinel-2.',
            'fonte_dados': 'Sentinel-2, pixels rotulados pela National Geographic Society.',
            'resolucao_espacial': '10m',
            'acuracia': '76%',
            'frequencia_temporal': 'Anual',
            'classes': '10 classes'
        },
        'FROM-GLC': {
            'metodologia': 'Classificação automática baseada em pixel usando Random Forest e dados multi-temporais.',
            'validacao': 'Validação visual e comparação com produtos existentes. Acurácia de 71%.',
            'cobertura': 'Cobertura global com produtos para diferentes períodos (2010, 2015, 2017).',
            'fonte_dados': 'Landsat TM/ETM+, dados auxiliares de topografia.',
            'resolucao_espacial': '30m',
            'acuracia': '71%',
            'frequencia_temporal': 'Multi-temporal',
            'classes': '10 classes'
        },
        'WorldCover 10m 2021': {
            'metodologia': 'Machine learning aplicado a dados Sentinel-1 e Sentinel-2 combinados.',
            'validacao': 'Validação independente com fotointerpretação. Acurácia global de 77%.',
            'cobertura': 'Cobertura global para o ano de 2021, com planos de atualizações anuais.',
            'fonte_dados': 'Sentinel-1, Sentinel-2, dados auxiliares de topografia e clima.',
            'resolucao_espacial': '10m',
            'acuracia': '77%',
            'frequencia_temporal': 'Anual',
            'classes': '11 classes'
        },
        'Land Cover CCI': {
            'metodologia': 'Algoritmo de classificação supervisionada usando séries temporais de múltiplos sensores.',
            'validacao': 'Validação independente com base de dados global. Acurácia de 73%.',
            'cobertura': 'Série temporal global de 1992 a 2020 com atualizações anuais.',
            'fonte_dados': 'AVHRR, SPOT-VGT, PROBA-V, MERIS, dados auxiliares.',
            'resolucao_espacial': '300m',
            'acuracia': '73%',
            'frequencia_temporal': 'Anual',
            'classes': '37 classes'
        },
        'MODIS Land Cover': {
            'metodologia': 'Algoritmo de classificação supervisionada baseado em boosted decision trees.',
            'validacao': 'Validação com dados de campo e interpretação visual. Acurácia de 67%.',
            'cobertura': 'Cobertura global anual de 2001 a presente.',
            'fonte_dados': 'MODIS Terra e Aqua, dados de reflectância de superfície.',
            'resolucao_espacial': '500m',
            'acuracia': '67%',
            'frequencia_temporal': 'Anual',
            'classes': '17 classes'
        },
        'GLC_FCS30': {
            'metodologia': 'Random Forest aplicado a métricas espectrais multi-temporais do Landsat.',
            'validacao': 'Validação com amostras independentes. Acurácia global de 68%.',
            'cobertura': 'Cobertura global para 2020 com base em dados Landsat.',
            'fonte_dados': 'Landsat-8 OLI, dados auxiliares de topografia.',
            'resolucao_espacial': '30m',
            'acuracia': '68%',
            'frequencia_temporal': 'Pontual (2020)',
            'classes': '29 classes'
        },
        'MapBiomas Brasil': {
            'metodologia': 'Classificação pixel-based usando Random Forest em Google Earth Engine com dados Landsat.',
            'validacao': 'Validação anual com dados de campo e interpretação visual. Acurácia média de 89%.',
            'cobertura': 'Território brasileiro completo com série temporal de 1985 a presente.',
            'fonte_dados': 'Landsat 5, 7, 8 e 9, dados auxiliares de topografia e clima.',
            'resolucao_espacial': '30m',
            'acuracia': '89%',
            'frequencia_temporal': 'Anual',
            'classes': '27 classes'
        },
        'PRODES Amazônia': {
            'metodologia': 'Interpretação visual assistida por computador usando dados ópticos de alta resolução.',
            'validacao': 'Validação através de verificação de campo e comparação com dados independentes. Acurácia superior a 95%.',
            'cobertura': 'Amazônia Legal brasileira com monitoramento anual desde 1988.',
            'fonte_dados': 'Landsat, CBERS, dados de alta resolução espacial.',
            'resolucao_espacial': '30m',
            'acuracia': '95%',
            'frequencia_temporal': 'Anual',
            'classes': '2 classes'
        },
        'DETER Amazônia': {
            'metodologia': 'Detecção automática de mudanças em tempo quase real usando algoritmos de sensoriamento remoto.',
            'validacao': 'Validação contínua com dados de campo e comparação com PRODES. Acurácia de 85%.',
            'cobertura': 'Amazônia Legal brasileira com alertas em tempo quase real.',
            'fonte_dados': 'MODIS, Landsat, Sentinel-1, CBERS.',
            'resolucao_espacial': '250m',
            'acuracia': '85%',
            'frequencia_temporal': 'Tempo real',
            'classes': '2 classes'
        },
        'PRODES Cerrado': {
            'metodologia': 'Metodologia similar ao PRODES Amazônia adaptada para características do Cerrado.',
            'validacao': 'Validação através de trabalho de campo e comparação com dados independentes. Acurácia de 92%.',
            'cobertura': 'Bioma Cerrado brasileiro com monitoramento desde 2000.',
            'fonte_dados': 'Landsat, CBERS, dados de alta resolução espacial.',
            'resolucao_espacial': '30m',
            'acuracia': '92%',
            'frequencia_temporal': 'Bienal',
            'classes': '2 classes'
        },
        'TerraClass Amazônia': {
            'metodologia': 'Classificação supervisionada de áreas desflorestadas usando dados multi-temporais.',
            'validacao': 'Validação com dados de campo e interpretação visual. Acurácia de 88%.',
            'cobertura': 'Áreas desflorestadas da Amazônia Legal identificadas pelo PRODES.',
            'fonte_dados': 'Landsat, dados auxiliares de uso da terra.',
            'resolucao_espacial': '30m',
            'acuracia': '88%',
            'frequencia_temporal': 'Bienal',
            'classes': '12 classes'
        },
        'IBGE Monitoramento': {
            'metodologia': 'Classificação manual e semiautomática baseada em interpretação visual de imagens.',
            'validacao': 'Validação através de levantamentos de campo e dados estatísticos oficiais. Acurácia de 85%.',
            'cobertura': 'Território brasileiro com foco em mudanças de cobertura e uso da terra.',
            'fonte_dados': 'Landsat, CBERS, dados de alta resolução, levantamentos de campo.',
            'resolucao_espacial': '30m',
            'acuracia': '85%',
            'frequencia_temporal': 'Bienal',
            'classes': '15 classes'
        }
    }
    
    return metadata

def save_metadata_to_file(metadata, filename='initiatives_metadata.json'):
    """
    Salva os metadados em arquivo JSON.
    
    Args:
        metadata (dict): Dicionário com metadados
        filename (str): Nome do arquivo de saída
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo {filename} criado com sucesso!")
        print(f"📊 Total de iniciativas: {len(metadata)}")
        
        # Estatísticas dos metadados
        print("\n📈 Estatísticas dos metadados:")
        print(f"   - Resolução mais alta: 10m")
        print(f"   - Resolução mais baixa: 500m") 
        print(f"   - Maior acurácia: 95% (PRODES Amazônia)")
        print(f"   - Menor acurácia: 67% (MODIS Land Cover)")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

def main():
    """Função principal para executar a geração de metadados."""
    print("🌍 Gerador de Metadados - Iniciativas LULC")
    print("=" * 50)
    
    # Gerar metadados
    metadata = create_initiatives_metadata()
    
    # Salvar em arquivo
    save_metadata_to_file(metadata)
    
    print("\n✨ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
