"""
🧪 Validação do Sistema de Cache Consolidado
===========================================

Verifica se a consolidação foi bem-sucedida e o sistema está funcional.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import sys
from pathlib import Path

def test_cache_system():
    """Testa o sistema de cache consolidado."""
    print("🔍 TESTANDO SISTEMA DE CACHE CONSOLIDADO")
    print("=" * 50)
    
    try:
        # Testa import principal
        from utilities.cache_system import load_optimized_data, create_performance_metrics
        print("✅ Import do cache system: OK")
        
        # Testa carregamento de dados
        metadata, df, cache_info = load_optimized_data()
        print(f"✅ Carregamento de dados: OK")
        print(f"   📊 DataFrame: {len(df) if df is not None else 0} rows")
        print(f"   ℹ️ Cache info: {cache_info.get('status', 'unknown')}")
        
        # Testa métricas
        metrics = create_performance_metrics()
        print(f"✅ Métricas de performance: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_dashboard_modules():
    """Testa os módulos dashboard com imports simplificados."""
    print("\n🖥️ TESTANDO MÓDULOS DASHBOARD")
    print("=" * 40)
    
    modules = [
        "dashboard.comparison",
        "dashboard.temporal", 
        "dashboard.detailed",
        "dashboard.conab"
    ]
    
    success_count = 0
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}: Import OK")
            success_count += 1
        except Exception as e:
            print(f"❌ {module}: Erro - {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(modules)} módulos OK")
    return success_count == len(modules)

def main():
    """Executa validação completa."""
    print("🧪 INICIANDO VALIDAÇÃO COMPLETA DO SISTEMA")
    print("=" * 60)
    
    # Testa cache
    cache_ok = test_cache_system()
    
    # Testa módulos
    modules_ok = test_dashboard_modules()
    
    # Resultado final
    print("\n🎯 RESULTADO DA VALIDAÇÃO")
    print("=" * 30)
    print(f"💾 Sistema de cache: {'✅ OK' if cache_ok else '❌ FALHOU'}")
    print(f"🖥️ Módulos dashboard: {'✅ OK' if modules_ok else '❌ FALHOU'}")
    
    if cache_ok and modules_ok:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("Consolidação bem-sucedida. Cache unificado e funcional.")
    else:
        print("\n⚠️ SISTEMA COM PROBLEMAS")
        print("Verifique os erros acima e corrija os problemas.")
    
    return cache_ok and modules_ok

if __name__ == "__main__":
    main()
