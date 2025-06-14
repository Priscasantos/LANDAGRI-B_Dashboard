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
import pandas as pd # Added import for pd.Series

# Global cache for data loading optimization
_DATA_CACHE = {}

def get_cached_data():
    """Get cached data or load it if not cached"""
    if 'data' not in _DATA_CACHE:
        from scripts.data_generation.data_wrapper import load_data, prepare_plot_data
        df, metadata, _ = load_data()
        df_prepared_dict = prepare_plot_data(df)
        df_for_plots = df_prepared_dict.get('data', pd.DataFrame())
        _DATA_CACHE['data'] = {
            'df': df,
            'metadata': metadata,
            'df_for_plots': df_for_plots
        }
        print(f"📊 Dados carregados e cachados: {len(df_for_plots)} iniciativas")
    return _DATA_CACHE['data']

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
            from scripts.data_generation.data_wrapper import load_data  # Use correct import
            # Preview dos dados carregados
            print("📊 Carregando dados das iniciativas LULC...")
            df, metadata, _ = load_data()  # Fixed tuple unpacking
            print(f"✅ Dados carregados: {len(df)} iniciativas")
            print(f"📋 Colunas disponíveis: {list(df.columns)}")
            if 'Type' in df.columns:
                print(f"🏷️ Tipos de iniciativas: {df['Type'].unique().tolist()}")            
            elif 'Tipo' in df.columns:
                print(f"🏷️ Tipos de iniciativas: {df['Tipo'].unique().tolist()}")
                
        elif module_name == "analise_comparativa":
            # Use cached data for better performance
            cached_data = get_cached_data()
            df_for_plots = cached_data['df_for_plots']
            metadata = cached_data['metadata']
            
            # Import direct from modular chart files for better performance
            from scripts.plotting.charts.distribution_charts import (
                plot_resolution_accuracy,
                plot_classes_por_iniciativa,
                plot_distribuicao_classes,
                plot_distribuicao_metodologias
            )
            from scripts.plotting.charts.timeline_chart import plot_timeline
            
            plot_resolution_accuracy(df_for_plots)
            plot_timeline(metadata, df_for_plots) # Added metadata
            plot_classes_por_iniciativa(df_for_plots)
            plot_distribuicao_classes(df_for_plots)
            plot_distribuicao_metodologias(df_for_plots['Methodology'].value_counts() if 'Methodology' in df_for_plots and not df_for_plots.empty else pd.Series())
            
        elif module_name == "analise_temporal":
            from dashboard.temporal.temporal import run_non_streamlit
            from scripts.data_generation.data_wrapper import load_data # Corrected import
            # Load data and pass to temporal analysis
            df, metadata, _ = load_data() # Load processed data
            
            # Execute temporal analysis without Streamlit UI
            success = run_non_streamlit(metadata, df, "graphics/temporal")
            if not success:
                print("❌ Falha na geração das análises temporais")
                return False            
        elif module_name == "analise_detalhada":
            from dashboard.detailed.detailed import run_non_streamlit as detailed_run_non_streamlit
            from scripts.data_generation.data_wrapper import load_data # Corrected import
            # Load data and pass to detailed analysis
            df, metadata, _ = load_data() # Load processed data
            
            # Execute detailed analysis without Streamlit UI
            success = detailed_run_non_streamlit(df, metadata, "graphics/detailed")
            if not success:
                print("❌ Falha na geração das análises detalhadas")
                return False
        
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
    # Import direct from modular chart files for better performance
    from scripts.plotting.charts.distribution_charts import (
        plot_resolution_accuracy,
        plot_classes_por_iniciativa,
        plot_distribuicao_classes,
        plot_distribuicao_metodologias
    )
    from scripts.plotting.charts.timeline_chart import plot_timeline
    from scripts.plotting.charts.coverage_charts import plot_annual_coverage_multiselect
    
    opcoes = [
        ("Resolução vs Acurácia", plot_resolution_accuracy),
        ("Timeline de Iniciativas", plot_timeline),
        ("Cobertura Anual (Seleção Múltipla)", plot_annual_coverage_multiselect),
        ("Classes por iniciativa", plot_classes_por_iniciativa),
        ("Distribuição de classes", plot_distribuicao_classes),
        ("Distribuição de metodologias", plot_distribuicao_metodologias),
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
    from scripts.data_generation.data_wrapper import load_data, prepare_plot_data # Corrected import
    df, metadata, _ = load_data() # Corrected tuple unpacking
    df_prepared_dict = prepare_plot_data(df) # df_prepared is now a dict
    df_for_plots = df_prepared_dict.get('data', pd.DataFrame()) # Get the DataFrame from the dict
    
    for idx in indices:
        desc, func = opcoes[idx-1]
        print(f"\n🔄 Gerando: {desc}")
        try:
            if desc == "Timeline de Iniciativas":
                func(metadata, df_for_plots)
            elif desc == "Cobertura Anual (Seleção Múltipla)":
                # Requires interactive selection, skipping for non-interactive run
                print(f"⚠️ {desc} requer seleção interativa, pulando na execução de script.")
                # func(metadata, df_for_plots, df_for_plots['Name'].unique().tolist()[:3]) # Example if we wanted to force it
            elif desc == "Distribuição de metodologias":
                method_counts = df_for_plots['Methodology'].value_counts() if 'Methodology' in df_for_plots and not df_for_plots.empty else pd.Series()
                func(method_counts)
            else:
                func(df_for_plots)
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
        from scripts.data_generation.lulc_data_engine import UnifiedDataProcessor
        import json

        processor = UnifiedDataProcessor()

        # Gerar dataset principal
        print("\n1️⃣ GERANDO DATASET PRINCIPAL...")
        df, metadata = processor.load_data_from_jsonc()
        # Apply any additional processing if needed, similar to add_derived_metrics
        # For now, we assume load_data_from_jsonc and create_comprehensive_auxiliary_data cover it.
        
        # Adicionar coluna Sigla (Acronym) - This should ideally be part of the main data processing
        # If 'Acronym' is already generated by lulc_data_engine.py, this step might be redundant
        # or needs to be harmonized.
        # For now, let's assume 'Acronym' is handled or can be mapped here if necessary.
        # Example: if 'Acronym' is not in df.columns:
        # df['Acronym'] = df['Name'].map(processor.get_acronym_map()).fillna(df['Name'].str[:8])

        # Salvar dataset
        df.to_csv('data/processed/initiatives_processed.csv', index=False, encoding='utf-8')
        print(f"✅ Dataset salvo: {len(df)} iniciativas")
        
        # Gerar metadados processados
        print("\n2️⃣ GERANDO METADADOS PROCESSADOS...")
        # metadata is already loaded, just need to save it
        output_path_metadata = 'data/processed/metadata_processed.json'
        with open(output_path_metadata, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ Metadados salvos: {len(metadata)} iniciativas")

        # Gerar dados auxiliares
        print("\n3️⃣ GERANDO DADOS AUXILIARES PROCESSADOS...")
        auxiliary_data = processor.create_comprehensive_auxiliary_data(df, metadata)
        # Use the save_data method from the processor instance
        processor.save_data(auxiliary_data, 'data/processed/auxiliary_data.json', data_type="JSON")
        # output_path_auxiliary = 'data/processed/auxiliary_data.json'
        # with open(output_path_auxiliary, 'w', encoding='utf-8') as f:
        #     json.dump(auxiliary_data, f, ensure_ascii=False, indent=2)
        # print(f"✅ Dados auxiliares salvos.") # Corrected f-string
        
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
