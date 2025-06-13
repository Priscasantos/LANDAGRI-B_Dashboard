#!/usr/bin/env python3
"""
Script principal modernizado para análise completa das iniciativas LULC.

Este script executa todos os módulos de análise na ordem correta:
1. Preview dos dados
2. Análise principal com gráficos comparativos 
3. Gráficos temporais 
4. Gráficos detalhados 

Estrutura de saída:
- graphics/comparisons/  - PNGs dos gráficos comparativos entre iniciativas
- graphics/temporal/     - PNGs das análises temporais das iniciativas  
- graphics/detailed/     - PNGs das análises detalhadas específicas

Estrutura do dashboard interativo:
- dashboard/comparisons/ - Módulos Streamlit para análises comparativas
- dashboard/temporal/    - Módulos Streamlit para análises temporais
- dashboard/detailed/    - Módulos Streamlit para análises detalhadas

Baseado na estrutura padrão do dashboard-agricultura
Autor: Sistema de Análise LULC
Data: 2025
"""

import sys
from pathlib import Path

# Adicionar o diretório scripts ao path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.append(str(scripts_dir))

def run_analysis_step(module_name, description):
    """Executa um passo da análise e trata erros"""
    print(f"\n{'='*60}")
    print(f"🔄 EXECUTANDO: {description}")
    print(f"{'='*60}")
    
    try:
        if module_name == "preview_dados":
            from scripts.data_generation.data_processing import load_data, prepare_plot_data
            # Preview dos dados carregados
            print("📊 Carregando dados das iniciativas LULC...")
            df, metadata = load_data()
            print(f"✅ Dados carregados: {len(df)} iniciativas")
            print(f"📋 Colunas disponíveis: {list(df.columns)}")
            print(f"🏷️ Tipos de iniciativas: {df['Tipo'].unique().tolist()}")
        elif module_name == "analise_comparativa":
            from scripts.plotting.generate_graphics import (
                plot_resolucao_acuracia,
                plot_timeline,
                plot_annual_coverage_multiselect,
                plot_classes_por_iniciativa,
                plot_distribuicao_classes,
                plot_distribuicao_metodologias            )
            from scripts.data_generation.data_processing import load_data, prepare_plot_data
            # Executar todas as funções principais de comparação
            df, metadata = load_data()
            df_prepared = prepare_plot_data(df)
            
            plot_resolucao_acuracia(df_prepared)
            plot_timeline(df_prepared)
            plot_annual_coverage_multiselect(df_prepared)
            plot_classes_por_iniciativa(df_prepared)
            plot_distribuicao_classes(df_prepared)
            plot_distribuicao_metodologias(df_prepared)
            
        elif module_name == "analise_temporal":
            from dashboard.temporal.temporal import run as temporal_run
            # Executar análises temporais
            temporal_run()
            
        elif module_name == "analise_detalhada":
            from dashboard.detailed.detailed import run as detailed_run
            from dashboard.detailed.overview import run as overview_run
            from dashboard.detailed.matrix import run as matrix_run
            # Executar todas as análises detalhadas
            overview_run()
            detailed_run()
            matrix_run()
        
        print(f"✅ {description} - CONCLUÍDO COM SUCESSO!")
        return True
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("💡 Verifique se todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ ERRO DURANTE EXECUÇÃO: {e}")
        print(f"💡 Verifique o módulo: {module_name}")
        return False

def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    required_packages = ["pandas", "matplotlib", "numpy", "plotly", "seaborn", "streamlit"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ DEPENDÊNCIAS FALTANDO:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Execute primeiro: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def create_output_directories():
    """Cria os diretórios de saída para PNGs se não existirem"""
    directories = [
        "graphics/comparisons", 
        "graphics/temporal",
        "graphics/detailed",
        "data/processed",
        "data/raw"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Diretório verificado: {directory}")

def main():
    """Função principal com menu interativo para geração de análises LULC"""
    print("🛰️ ANÁLISE COMPLETA DAS INICIATIVAS LULC")
    print("=" * 60)
    print("📊 Sistema de Análise de Dados de Mapeamento LULC")
    print("🌍 Comparação entre iniciativas de monitoramento")
    print("📅 Análises temporais e comparativas detalhadas")
    print("=" * 60)
    
    if not check_dependencies():
        return False
    
    print("\n📁 CRIANDO DIRETÓRIOS DE SAÍDA...")
    create_output_directories()
    
    while True:
        print("\nMENU PRINCIPAL:")
        print("1. Gerar Análises Comparativas")
        print("2. Gerar Análises Temporais")
        print("3. Gerar Apenas Dados Processados")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            menu_analises_comparativas()
        elif opcao == "2":
            menu_analises_temporais()
        elif opcao == "3":
            menu_gerar_dados_processados()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_analises_comparativas():
    """Menu para análises comparativas"""
    from scripts.plotting import generate_graphics
    opcoes = [
        ("Resolução vs Acurácia", generate_graphics.plot_resolucao_acuracia),
        ("Timeline das iniciativas", generate_graphics.plot_timeline),
        ("Cobertura anual", generate_graphics.plot_annual_coverage_multiselect),
        ("Classes por iniciativa", generate_graphics.plot_classes_por_iniciativa),
        ("Distribuição de classes", generate_graphics.plot_distribuicao_classes),
        ("Distribuição de metodologias", generate_graphics.plot_distribuicao_metodologias),
    ]
    
    print("\nAnálises Comparativas Disponíveis:")
    for idx, (desc, _) in enumerate(opcoes, 1):
        print(f"{idx}. {desc}")
    print("0. Voltar ao menu principal")
    
    escolhas = input("Digite os números das análises desejadas separados por vírgula (ex: 1,3,5): ").strip()
    if escolhas == "0":
        return
        
    indices = [int(i) for i in escolhas.split(",") if i.strip().isdigit() and 1 <= int(i) <= len(opcoes)]
      # Carregar dados uma vez
    from scripts.data_generation.data_processing import load_data, prepare_plot_data
    df, metadata = load_data()
    df_prepared = prepare_plot_data(df)
    
    for idx in indices:
        desc, func = opcoes[idx-1]
        print(f"\n🔄 Gerando: {desc}")
        try:
            func(df_prepared)
            print(f"✅ {desc} gerado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao gerar {desc}: {e}")

def menu_analises_temporais():
    """Menu para análises temporais"""
    print("\n🔄 Executando análises temporais...")
    try:
        run_analysis_step("analise_temporal", "Análises temporais das iniciativas")
    except Exception as e:
        print(f"❌ Erro nas análises temporais: {e}")

def menu_gerar_dados_processados():
    """Menu para gerar apenas dados processados"""
    print("\n🔄 Executando geração de dados processados...")
    print("💡 Esta opção gera apenas os dados necessários para o dashboard")
    print("🚀 Processo otimizado - sem gráficos")
    
    try:
        # Executar o script de processamento diretamente
        import sys
        import os
        current_dir = os.getcwd()
        sys.path.append(os.path.join(current_dir, 'scripts', 'data_generation'))
        
        # Executar geração de dataset
        print("\n1️⃣ GERANDO DATASET PRINCIPAL...")
        from generate_dataset import create_initiatives_dataset, add_derived_metrics
        df = create_initiatives_dataset()
        df = add_derived_metrics(df)
        
        # Adicionar coluna Sigla
        sigla_map = {
            'Copernicus Global Land Cover Service (CGLS)': 'CGLS',
            'Dynamic World (GDW)': 'GDW',
            'ESRI-10m Annual LULC': 'ESRI',
            'FROM-GLC': 'FROM-GLC',
            'Global LULC change 2000 and 2020': 'GLULC',
            'Global Pasture Watch (GPW)': 'GPW',
            'South America Soybean Maps': 'SASM',
            'WorldCover 10m 2021': 'WorldCover',
            'WorldCereal': 'WorldCereal',
            'Land Cover CCI': 'CCI',
            'MODIS Land Cover': 'MODIS',
            'GLC_FCS30': 'GLC_FCS30',
            'MapBiomas Brasil': 'MapBiomas',
            'PRODES Amazônia': 'PRODES-AMZ',
            'DETER Amazônia': 'DETER',
            'PRODES Cerrado': 'PRODES-CER',
            'TerraClass Amazônia': 'TerraClass',
            'IBGE Monitoramento': 'IBGE',
            'Agricultural Mapping': 'AgriMap'
        }
        df['Sigla'] = df['Nome'].map(sigla_map).fillna(df['Nome'].str[:8])
        
        # Salvar dataset
        df.to_csv('data/processed/initiatives_processed.csv', index=False, encoding='utf-8')
        print(f"✅ Dataset salvo: {len(df)} iniciativas")
        
        # Executar geração de metadados
        print("\n2️⃣ GERANDO METADADOS PROCESSADOS...")
        from generate_metadata import create_initiatives_metadata
        import json
        
        metadata = create_initiatives_metadata()
        output_path = 'data/processed/metadata_processed.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ Metadados salvos: {len(metadata)} iniciativas")
        
        print("\n🎉 DADOS PROCESSADOS GERADOS COM SUCESSO!")
        print("💡 Os arquivos estão prontos para uso no dashboard")
        print("📁 Localização: data/processed/")
        
    except Exception as e:
        print(f"❌ Erro na geração de dados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚡ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {e}")
        print("💡 Verifique a instalação e os arquivos de dados")
