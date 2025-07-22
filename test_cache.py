#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de cache
"""

import sys
import os

print("🔍 TESTE DO SISTEMA DE CACHE")
print("=" * 50)
print(f"Working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")

# Verifica se o arquivo existe
cache_file = "utilities/dashboard_optimizer.py"
if os.path.exists(cache_file):
    print(f"✅ Arquivo {cache_file} encontrado")
else:
    print(f"❌ Arquivo {cache_file} NÃO encontrado")

# Tenta importar
try:
    from utilities.dashboard_optimizer import load_optimized_data, setup_performance_sidebar
    print("✅ Importação do cache bem-sucedida!")
    
    # Testa funções
    print("   - load_optimized_data:", callable(load_optimized_data))
    print("   - setup_performance_sidebar:", callable(setup_performance_sidebar))
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    
    # Debug adicional
    print("\n🔍 DEBUG DE IMPORTAÇÃO:")
    if "utilities" not in sys.modules:
        print("   - Módulo 'utilities' não carregado")
    
    # Tenta importar passo a passo
    try:
        import utilities
        print("   - ✅ Módulo 'utilities' importado")
        try:
            import utilities.dashboard_optimizer
            print("   - ✅ Submódulo 'dashboard_optimizer' importado")
        except Exception as e2:
            print(f"   - ❌ Erro no submódulo: {e2}")
    except Exception as e3:
        print(f"   - ❌ Erro no módulo utilities: {e3}")

except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\n" + "=" * 50)
print("🏁 TESTE CONCLUÍDO")
