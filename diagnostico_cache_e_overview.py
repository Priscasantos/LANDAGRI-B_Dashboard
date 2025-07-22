"""
🔍 Diagnóstico Completo do Sistema de Cache e Overview Dashboard
===============================================================

Análise detalhada das duplicações de cache e problemas no overview dashboard.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd

def analisar_duplicacoes_cache():
    """Analisa as múltiplas implementações de cache encontradas."""
    
    print("\n🔍 ANÁLISE DAS DUPLICAÇÕES DO SISTEMA DE CACHE")
    print("=" * 70)
    
    cache_files = [
        "utilities/cache_system.py",
        "utilities/dashboard_optimizer.py", 
        "scripts/utilities/dashboard_optimizer.py",
        "utilities/cache_system_fixed.py",
        "utilities/cache_system_backup.py"
    ]
    
    cache_info = {}
    
    for cache_file in cache_files:
        file_path = Path(cache_file)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                cache_info[cache_file] = {
                    'exists': True,
                    'size': len(content),
                    'lines': len(content.split('\n')),
                    'has_load_optimized_data': 'def load_optimized_data' in content,
                    'has_imports': 'import' in content[:500],
                    'has_streamlit': 'streamlit' in content or 'st.' in content,
                    'has_pandas': 'pandas' in content or 'pd.' in content,
                    'has_cache_management': 'cache' in content.lower()
                }
                
                print(f"\n📁 {cache_file}")
                print(f"   ✅ Existe: {cache_info[cache_file]['exists']}")
                print(f"   📏 Tamanho: {cache_info[cache_file]['size']} chars, {cache_info[cache_file]['lines']} linhas")
                print(f"   🔧 Has load_optimized_data: {cache_info[cache_file]['has_load_optimized_data']}")
                print(f"   📦 Has streamlit: {cache_info[cache_file]['has_streamlit']}")
                print(f"   💾 Has cache mgmt: {cache_info[cache_file]['has_cache_management']}")
                
            except Exception as e:
                cache_info[cache_file] = {'exists': False, 'error': str(e)}
                print(f"\n❌ {cache_file}: Erro ao ler - {e}")
        else:
            cache_info[cache_file] = {'exists': False}
            print(f"\n❌ {cache_file}: Não existe")
    
    return cache_info

def analisar_overview_original():
    """Analisa o estado atual do overview dashboard."""
    
    print("\n🖥️ ANÁLISE DO OVERVIEW DASHBOARD")
    print("=" * 50)
    
    overview_path = Path("dashboard/overview.py")
    if not overview_path.exists():
        print("❌ Overview dashboard não encontrado!")
        return {}
    
    try:
        with open(overview_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        overview_info = {
            'size': len(content),
            'lines': len(content.split('\n')),
            'functions': content.count('def '),
            'streamlit_elements': content.count('st.'),
            'plotly_usage': content.count('plotly') + content.count('px.') + content.count('go.'),
            'cache_imports': 'cache_system' in content,
            'has_metrics': 'metric' in content.lower(),
            'has_charts': 'chart' in content.lower() or 'plot' in content.lower(),
            'has_dataframes': 'dataframe' in content.lower() or 'df' in content,
            'complexity_indicators': {
                'tabs': content.count('tab'),
                'columns': content.count('column'),
                'containers': content.count('container'),
                'expanders': content.count('expander'),
                'selectboxes': content.count('selectbox'),
                'multiselects': content.count('multiselect')
            }
        }
        
        print(f"📏 Tamanho atual: {overview_info['size']} chars, {overview_info['lines']} linhas")
        print(f"🔧 Funções: {overview_info['functions']}")
        print(f"🎯 Elementos Streamlit: {overview_info['streamlit_elements']}")
        print(f"📊 Uso Plotly: {overview_info['plotly_usage']}")
        print(f"💾 Import Cache: {overview_info['cache_imports']}")
        print(f"📈 Has metrics: {overview_info['has_metrics']}")
        print(f"📉 Has charts: {overview_info['has_charts']}")
        
        print(f"\n🔍 Indicadores de Complexidade:")
        for indicator, count in overview_info['complexity_indicators'].items():
            print(f"   {indicator}: {count}")
        
        return overview_info
        
    except Exception as e:
        print(f"❌ Erro ao analisar overview: {e}")
        return {}

def analisar_imports_conflitos():
    """Analisa conflitos de imports nos módulos dashboard."""
    
    print("\n📦 ANÁLISE DE CONFLITOS DE IMPORTS")
    print("=" * 45)
    
    dashboard_modules = [
        "dashboard/overview.py",
        "dashboard/comparison.py",
        "dashboard/temporal.py",
        "dashboard/detailed.py",
        "dashboard/conab.py"
    ]
    
    import_conflicts = {}
    
    for module in dashboard_modules:
        module_path = Path(module)
        if module_path.exists():
            try:
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import_info = {
                    'cache_system_import': 'from utilities.cache_system import' in content,
                    'dashboard_optimizer_import': 'from utilities.dashboard_optimizer import' in content,
                    'scripts_optimizer_import': 'from scripts.utilities.dashboard_optimizer import' in content,
                    'local_load_optimized_data': 'def load_optimized_data' in content,
                    'fallback_functions': 'def load_optimized_data()' in content,
                    'try_except_imports': content.count('try:') + content.count('except ImportError'),
                    'total_imports': content.count('import ') + content.count('from ')
                }
                
                import_conflicts[module] = import_info
                
                print(f"\n📁 {module}")
                print(f"   💾 Cache system import: {import_info['cache_system_import']}")
                print(f"   ⚡ Dashboard optimizer import: {import_info['dashboard_optimizer_import']}")
                print(f"   📦 Scripts optimizer import: {import_info['scripts_optimizer_import']}")
                print(f"   🔧 Local load_optimized_data: {import_info['local_load_optimized_data']}")
                print(f"   🔄 Try/except imports: {import_info['try_except_imports']}")
                print(f"   📋 Total imports: {import_info['total_imports']}")
                
            except Exception as e:
                import_conflicts[module] = {'error': str(e)}
                print(f"❌ Erro ao analisar {module}: {e}")
        else:
            print(f"❌ {module}: Não encontrado")
    
    return import_conflicts

def testar_carregamento_dados():
    """Testa o carregamento atual de dados."""
    
    print("\n📊 TESTE DE CARREGAMENTO DE DADOS")
    print("=" * 40)
    
    try:
        # Testa o sistema consolidado
        print("🔍 Testando utilities.cache_system...")
        sys.path.insert(0, str(Path.cwd()))
        
        from utilities.cache_system import load_optimized_data
        
        metadata, df, cache_info = load_optimized_data()
        
        print(f"✅ Cache system carregado com sucesso!")
        print(f"   📊 Metadata: {type(metadata)} - {len(metadata) if metadata is not None else 0} rows")
        print(f"   📋 DataFrame: {type(df)} - {len(df) if df is not None else 0} rows")
        print(f"   ℹ️ Cache info: {cache_info}")
        
        if df is not None and not df.empty:
            print(f"   📏 Shape: {df.shape}")
            print(f"   📝 Columns: {list(df.columns)}")
            print(f"   🔍 Sample data preview:")
            print(f"      {df.head(1).to_dict()}")
        
        return True, {'metadata': metadata, 'df': df, 'cache_info': cache_info}
        
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        return False, {'error': str(e)}

def analisar_data_files():
    """Analisa os arquivos de dados disponíveis."""
    
    print("\n📂 ANÁLISE DOS ARQUIVOS DE DADOS")
    print("=" * 40)
    
    data_files = [
        "data/initiatives_metadata.jsonc",
        "data/sensors_metadata.jsonc",
        "data/initiatives_metadata_backup.jsonc",
        "data/conab_detailed_initiative.jsonc"
    ]
    
    data_info = {}
    
    for data_file in data_files:
        file_path = Path(data_file)
        if file_path.exists():
            try:
                file_size = file_path.stat().st_size
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Análise básica do conteúdo JSONC
                data_info[data_file] = {
                    'exists': True,
                    'size_bytes': file_size,
                    'content_lines': len(content.split('\n')),
                    'has_comments': '//' in content or '/*' in content,
                    'appears_json': content.strip().startswith(('{', '[')),
                    'estimated_entries': content.count('"name"') + content.count('"id"'),
                }
                
                print(f"\n📁 {data_file}")
                print(f"   💾 Tamanho: {file_size} bytes")
                print(f"   📄 Linhas: {data_info[data_file]['content_lines']}")
                print(f"   💬 Has comments: {data_info[data_file]['has_comments']}")
                print(f"   📋 Appears JSON: {data_info[data_file]['appears_json']}")
                print(f"   🔢 Estimated entries: {data_info[data_file]['estimated_entries']}")
                
            except Exception as e:
                data_info[data_file] = {'exists': True, 'error': str(e)}
                print(f"❌ Erro ao analisar {data_file}: {e}")
        else:
            data_info[data_file] = {'exists': False}
            print(f"❌ {data_file}: Não existe")
    
    return data_info

def gerar_relatorio_diagnostico():
    """Gera relatório consolidado do diagnóstico."""
    
    print("\n📋 RELATÓRIO DE DIAGNÓSTICO CONSOLIDADO")
    print("=" * 50)
    
    print("\n🔍 PROBLEMAS IDENTIFICADOS:")
    print("-" * 30)
    
    # Analisa duplicações
    cache_info = analisar_duplicacoes_cache()
    cache_files_count = sum(1 for info in cache_info.values() if info.get('exists', False))
    
    if cache_files_count > 2:
        print(f"❌ DUPLICAÇÃO DE CACHE: {cache_files_count} implementações diferentes")
        print("   Recomendação: Consolidar em uma única implementação")
    
    # Analisa overview
    overview_info = analisar_overview_original()
    if overview_info:
        complexity_score = sum(overview_info.get('complexity_indicators', {}).values())
        if complexity_score < 10:
            print(f"❌ OVERVIEW SIMPLIFICADO: Score de complexidade baixo ({complexity_score})")
            print("   Recomendação: Restaurar funcionalidades originais")
    
    # Analisa conflitos
    import_conflicts = analisar_imports_conflitos()
    conflicted_modules = sum(1 for info in import_conflicts.values() 
                           if info.get('try_except_imports', 0) > 2)
    
    if conflicted_modules > 0:
        print(f"❌ CONFLITOS DE IMPORT: {conflicted_modules} módulos com fallbacks excessivos")
        print("   Recomendação: Unificar sistema de imports")
    
    # Testa carregamento
    load_success, load_result = testar_carregamento_dados()
    if not load_success:
        print(f"❌ FALHA NO CARREGAMENTO: {load_result.get('error', 'Erro desconhecido')}")
        print("   Recomendação: Verificar integridade do sistema de cache")
    else:
        print("✅ CARREGAMENTO OK: Sistema básico funcional")
    
    # Analisa dados
    data_info = analisar_data_files()
    missing_files = sum(1 for info in data_info.values() if not info.get('exists', False))
    
    if missing_files > 0:
        print(f"⚠️ ARQUIVOS FALTANDO: {missing_files} arquivos de dados não encontrados")
    
    print("\n🛠️ SOLUÇÕES RECOMENDADAS:")
    print("-" * 30)
    print("1. 🗂️ Consolidar cache em utilities/cache_system.py")
    print("2. 🔄 Remover utilities/dashboard_optimizer.py (duplicação)")
    print("3. 📁 Manter scripts/utilities/dashboard_optimizer.py como backup")
    print("4. 🖥️ Restaurar complexidade original do overview.py")
    print("5. ⚡ Simplificar imports nos módulos dashboard")
    print("6. 🧪 Implementar testes de regressão")
    
    return {
        'cache_duplications': cache_files_count,
        'overview_simplified': complexity_score < 10 if overview_info else True,
        'import_conflicts': conflicted_modules,
        'loading_works': load_success,
        'missing_data_files': missing_files
    }

def main():
    """Executa diagnóstico completo."""
    
    print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # Muda para o diretório do projeto
    os.chdir(Path(__file__).parent)
    
    try:
        relatorio = gerar_relatorio_diagnostico()
        
        print(f"\n✅ DIAGNÓSTICO CONCLUÍDO")
        print(f"   📊 Duplicações de cache: {relatorio['cache_duplications']}")
        print(f"   🖥️ Overview simplificado: {relatorio['overview_simplified']}")
        print(f"   📦 Conflitos de import: {relatorio['import_conflicts']}")
        print(f"   💾 Carregamento funciona: {relatorio['loading_works']}")
        print(f"   📂 Arquivos faltando: {relatorio['missing_data_files']}")
        
        return relatorio
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return None

if __name__ == "__main__":
    relatorio_final = main()
    
    if relatorio_final:
        print("\n🎯 Diagnóstico salvo. Execute as soluções recomendadas.")
    else:
        print("\n❌ Falha no diagnóstico. Verifique manualmente.")
