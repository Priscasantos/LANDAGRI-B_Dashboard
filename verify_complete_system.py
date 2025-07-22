#!/usr/bin/env python3
"""
Script de verificação completa do sistema de cache
em todos os módulos do dashboard
"""

import sys
import os
from pathlib import Path

print("🚀 VERIFICAÇÃO COMPLETA DO SISTEMA DE CACHE")
print("=" * 60)

# Lista de módulos para verificar
modules_to_check = [
    ("dashboard.overview", "Overview Dashboard"),
    ("dashboard.temporal", "Temporal Analysis"),
    ("dashboard.detailed", "Detailed Analysis"),
    ("dashboard.comparison", "Comparison Analysis"),
    ("dashboard.conab", "CONAB Dashboard")
]

# Configuração base
current_dir = Path(os.getcwd())
print(f"📁 Diretório de trabalho: {current_dir}")

# Verifica cache otimizado
print("\n🔧 VERIFICAÇÃO DO CACHE PRINCIPAL:")
try:
    from utilities.dashboard_optimizer import (
        load_optimized_data, 
        setup_performance_sidebar,
        get_cache_manager
    )
    print("   ✅ Cache principal importado com sucesso")
    
    # Testa cache manager
    cache_mgr = get_cache_manager()
    print(f"   📊 Cache manager: {type(cache_mgr).__name__}")
    
except Exception as e:
    print(f"   ❌ Erro no cache principal: {e}")

# Verifica cada módulo
print("\n📋 VERIFICAÇÃO DOS MÓDULOS DO DASHBOARD:")
for module_name, display_name in modules_to_check:
    print(f"\n📄 Verificando: {display_name}")
    try:
        # Tenta importar o módulo
        exec(f"import {module_name}")
        print(f"   ✅ Módulo {module_name} importado")
        
        # Verifica se tem função run
        module_obj = sys.modules[module_name]
        if hasattr(module_obj, 'run'):
            print(f"   ✅ Função 'run' encontrada")
        else:
            print(f"   ⚠️  Função 'run' não encontrada")
            
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
    except Exception as e:
        print(f"   ❌ Erro geral: {e}")

# Verificação de arquivos de dados
print("\n📊 VERIFICAÇÃO DOS DADOS:")
data_files = [
    "data/initiatives_metadata.jsonc",
    "data/sensors_metadata.jsonc",
    "data/conab_detailed_initiative.jsonc"
]

for data_file in data_files:
    file_path = current_dir / data_file
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ {data_file} ({size_mb:.2f} MB)")
    else:
        print(f"   ❌ {data_file} não encontrado")

# Teste final de integração
print("\n🧪 TESTE DE INTEGRAÇÃO:")
try:
    from utilities.cache_system import load_optimized_data
    metadata, df, cache_info = load_optimized_data()
    
    print(f"   🔍 Tipos retornados: metadata={type(metadata)}, df={type(df)}, cache_info={type(cache_info)}")
    
    if df is not None:
        if hasattr(df, 'empty') and hasattr(df, 'shape'):
            # É um DataFrame
            if not df.empty:
                print(f"   ✅ DataFrame carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
            else:
                print("   ⚠️  DataFrame vazio")
        else:
            # Não é um DataFrame
            print(f"   ⚠️  Objeto retornado não é DataFrame: {type(df)}")
    else:
        print("   ⚠️  DataFrame é None")
        
    print(f"   📈 Cache info: {cache_info}")
        
except Exception as e:
    print(f"   ❌ Erro no teste de integração: {e}")
    import traceback
    print(f"   🔍 Traceback: {traceback.format_exc()}")

print("\n" + "=" * 60)
print("🎯 VERIFICAÇÃO CONCLUÍDA!")
print("🌐 Dashboard disponível em: http://localhost:8501")
print("=" * 60)
