# -*- coding: utf-8 -*-
"""
Gerador de Dados das Iniciativas LULC
=====================================

Este script cria o dataset principal em formato CSV com todas as características
das iniciativas de mapeamento de cobertura e uso da terra (LULC).

Autor: Análise Comparativa de Iniciativas LULC
Data: 2024
"""

import pandas as pd
import numpy as np

def create_initiatives_dataset():
    """
    Cria o dataset principal com dados de todas as iniciativas LULC.
    
    Returns:
        pd.DataFrame: DataFrame com dados das iniciativas
    """
      # Dados das principais iniciativas LULC baseadas nas tabelas atualizadas
    initiatives_data = {
        'Nome': [
            'Copernicus Global Land Cover Service (CGLS)',
            'Dynamic World (GDW)',
            'ESRI-10m Annual LULC',
            'FROM-GLC',
            'Global LULC change 2000 and 2020',
            'Global Pasture Watch (GPW)',
            'South America Soybean Maps',
            'WorldCover 10m 2021',
            'WorldCereal',
            'Land Cover CCI',
            'MODIS Land Cover',
            'GLC_FCS30',
            'MapBiomas Brasil',
            'PRODES Amazônia',
            'DETER Amazônia', 
            'PRODES Cerrado',
            'TerraClass Amazônia',
            'IBGE Monitoramento',
            'Agricultural Mapping'
        ],
        'Tipo': [
            'Global', 'Global', 'Global', 'Global', 'Global', 'Global', 'Regional',
            'Global', 'Global', 'Global', 'Global', 'Global',
            'Nacional', 'Regional', 'Regional', 'Regional', 'Regional', 'Nacional', 'Nacional'
        ],
        'Resolução (m)': [
            100, 10, 10, 30, 30, 30, 30, 10, 10, 300, 500, 30, 30, 25, 60, 10, 20, 30, 25
        ],
        'Acurácia (%)': [
            80.3, 73.8, 85.0, 71, 85.0, 91.0, 94, 76.7, 97.8, 73, 67, 68, 90.0, 93.0, 93.0, 90.9, 93.9, 0, 0        ],
        'Classes': [
            10, 9, 15, 10, 7, 3, 2, 11, 5, 37, 17, 29, 29, 5, 3, 15, 18, 12, 8
        ],
        'Metodologia': [
            'Supervised Random Forest', 'Deep Learning', 'U-Net Deep Learning', 'Random Forest', 
            'Supervised Machine Learning', 'Supervised Machine Learning', 'Combined Methods', 
            'Gradient Boosting', 'CatBoost Gradient Boosting', 'Classificação Supervisionada', 'Boosted Decision Trees', 
            'Random Forest', 'Supervised Random Forest and U-Net Deep Learning', 'Visual Interpretation and Linear Spectral Mixture Model', 
            'Linear Spectral Mixture Model', 'Visual Interpretation and Deep Learning', 'Visual Interpretation and Deep Learning',
            'Visual Interpretation', 'Machine Learning and Visual Interpretation'
        ],
        'Frequência Temporal': [
            'Anual', 'Near real time', 'Annual or Sub-annual', 'Multi-temporal', 'Cada 4 anos', 'Bi-Annual', 'Anual',
            'Anual', 'Annual and seasonal', 'Anual', 'Anual', 'Pontual', 'Anual', 'Anual', 'Annual since 2012', 'Bienal', 'Bienal', 'Biannual since 2010', 'By Crop Year'
        ],
        'Anos Disponíveis': [
            '2015,2016,2017,2018,2019', '2017,2018,2019,2020,2021,2022,2023,2024', '2017,2018,2019,2020,2021,2022,2023,2024', '2010,2015,2017', 
            '2000,2005,2015,2020', '2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020,2022', 
            '2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023',
            '2020,2021', '2021', '1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020',
            '2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023', '2020', 
            '1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023',
            '2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023', 
            '2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023', '2018,2020,2022', 
            '2008,2010,2012,2014,2016,2018,2020,2022', '2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020', '2018,2019,2020,2021,2022,2023'
        ],
        'Escopo': [
            'Global', 'Global', 'Global', 'Global', 'Global', 'Global', 'Regional (South America)',
            'Global', 'Global', 'Global', 'Global', 'Global',
            'Nacional (Brasil)', 'Regional (Amazônia)', 'Regional (Amazônia)', 'Regional (Cerrado)', 'Regional (Amazônia e Cerrado)', 'Nacional (Brasil)', 'Nacional (Brasil)'
        ],
        'Provedor': [
            'Copernicus European Union\'s Space Program', 'Google and World Resources Institute', 'Environmental Systems Research Institute (ESRI)', 'Tsinghua University',
            'University of Maryland (UMD)', 'Land & Carbon Lab', 'University of Maryland (UMD)', 'European Space Agency (ESA)', 'European Space Agency (ESA)',
            'ESA Climate Change Initiative', 'NASA', 'Chinese Academy of Sciences', 'Non-governmental Organizations', 'National Institute for Space Research (INPE)',
            'National Institute for Space Research (INPE)', 'National Institute for Space Research (INPE)', 'National Institute for Space Research (INPE)', 'Brazilian Institute of Geography and Statistics (IBGE)', 'National Supply Company (Conab)'
        ]
    }
    
    # Criar DataFrame
    df = pd.DataFrame(initiatives_data)
    
    return df

def add_derived_metrics(df):
    """
    Adiciona métricas derivadas ao dataset.
    
    Args:
        df (pd.DataFrame): DataFrame original
        
    Returns:
        pd.DataFrame: DataFrame com métricas adicionais
    """
    
    # Calcular score de resolução (menor resolução = melhor score)
    df['Score Resolução'] = 1000 / df['Resolução (m)']
    
    # Calcular score geral (combinação de acurácia e resolução)
    df['Score Geral'] = (df['Acurácia (%)'] * 0.7) + (df['Score Resolução'] * 0.3)
    
    # Categorizar por faixa de acurácia
    def categorize_accuracy(accuracy):
        if accuracy >= 90:
            return 'Muito Alta'
        elif accuracy >= 80:
            return 'Alta'
        elif accuracy >= 70:
            return 'Média'
        else:
            return 'Baixa'
    
    df['Categoria Acurácia'] = df['Acurácia (%)'].apply(categorize_accuracy)
    
    # Categorizar por resolução
    def categorize_resolution(resolution):
        if resolution <= 10:
            return 'Muito Alta'
        elif resolution <= 30:
            return 'Alta'
        elif resolution <= 100:
            return 'Média'
        else:
            return 'Baixa'
    
    df['Categoria Resolução'] = df['Resolução (m)'].apply(categorize_resolution)
    
    return df

def save_dataset_to_csv(df, filename='initiatives_comparison.csv'):
    """
    Salva o dataset em arquivo CSV.
    
    Args:
        df (pd.DataFrame): DataFrame para salvar
        filename (str): Nome do arquivo de saída
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"✅ Arquivo {filename} criado com sucesso!")
        print(f"📊 Dataset com {len(df)} iniciativas e {len(df.columns)} colunas")
        
        # Estatísticas do dataset
        print("\n📈 Estatísticas do dataset:")
        print(f"   - Iniciativas globais: {len(df[df['Tipo'] == 'Global'])}")
        print(f"   - Iniciativas nacionais: {len(df[df['Tipo'] == 'Nacional'])}")
        print(f"   - Acurácia média: {df['Acurácia (%)'].mean():.1f}%")
        print(f"   - Resolução média: {df['Resolução (m)'].mean():.0f}m")
        print(f"   - Total de classes: {df['Classes'].sum()}")
        
        # Top 3 por acurácia
        print(f"\n🏆 Top 3 em acurácia:")
        top_accuracy = df.nlargest(3, 'Acurácia (%)')
        for i, (_, row) in enumerate(top_accuracy.iterrows(), 1):
            print(f"   {i}. {row['Nome']} - {row['Acurácia (%)']}%")
        
        # Top 3 por resolução
        print(f"\n🔍 Top 3 em resolução:")
        top_resolution = df.nsmallest(3, 'Resolução (m)')
        for i, (_, row) in enumerate(top_resolution.iterrows(), 1):
            print(f"   {i}. {row['Nome']} - {row['Resolução (m)']}m")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

def validate_dataset(df):
    """
    Valida a consistência do dataset.
    
    Args:
        df (pd.DataFrame): DataFrame para validar
    """
    print("\n🔍 Validação do dataset:")
    
    # Verificar valores nulos
    null_counts = df.isnull().sum()
    if null_counts.sum() == 0:
        print("   ✅ Nenhum valor nulo encontrado")
    else:
        print(f"   ⚠️ Valores nulos encontrados: {null_counts.sum()}")
    
    # Verificar duplicatas
    if df.duplicated().sum() == 0:
        print("   ✅ Nenhuma duplicata encontrada")
    else:
        print(f"   ⚠️ Duplicatas encontradas: {df.duplicated().sum()}")
    
    # Verificar faixas de valores
    if df['Acurácia (%)'].min() >= 0 and df['Acurácia (%)'].max() <= 100:
        print("   ✅ Acurácia em faixa válida (0-100%)")
    else:
        print("   ⚠️ Acurácia fora da faixa válida")
    
    if df['Resolução (m)'].min() > 0:
        print("   ✅ Resolução com valores positivos")
    else:
        print("   ⚠️ Resolução com valores inválidos")

def main():
    """Função principal para executar a geração do dataset."""
    print("🌍 Gerador de Dataset - Iniciativas LULC")
    print("=" * 50)
    
    # Criar dataset
    print("\n📊 Criando dataset das iniciativas...")
    df = create_initiatives_dataset()
    
    # Adicionar métricas derivadas
    print("📈 Adicionando métricas derivadas...")
    df = add_derived_metrics(df)
    
    # Validar dataset
    validate_dataset(df)
    
    # Salvar em CSV
    print("\n💾 Salvando dataset em CSV...")
    save_dataset_to_csv(df)
    
    print("\n✨ Processo concluído com sucesso!")
    
    return df

if __name__ == "__main__":
    df = main()
