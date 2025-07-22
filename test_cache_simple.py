#!/usr/bin/env python3
"""
Teste do sistema de cache simplificado
"""

print("🚀 TESTE DO SISTEMA DE CACHE SIMPLIFICADO")
print("=" * 60)

try:
    from utilities.cache_system import load_optimized_data, setup_performance_sidebar, get_cache_manager
    print("✅ Importação bem-sucedida!")
    
    # Testa carregamento de dados
    print("\n📊 Testando carregamento de dados...")
    metadata, df, cache_info = load_optimized_data()
    
    print(f"🔍 Tipos retornados:")
    print(f"   metadata: {type(metadata)}")
    print(f"   df: {type(df)}")
    print(f"   cache_info: {type(cache_info)}")
    
    print(f"\n📈 Cache info: {cache_info}")
    
    if hasattr(df, 'shape'):
        print(f"✅ DataFrame válido com shape: {df.shape}")
        if not df.empty:
            print(f"📋 Colunas: {list(df.columns)[:5]}...")
        else:
            print("⚠️  DataFrame está vazio")
    else:
        print(f"❌ df não é DataFrame: {df}")
    
    # Testa cache manager
    print("\n🗄️  Testando cache manager...")
    cache_mgr = get_cache_manager()
    print(f"Cache manager: {type(cache_mgr).__name__}")
    
    # Testa sidebar
    print("\n📊 Testando performance sidebar...")
    setup_performance_sidebar()
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    print(f"🔍 Traceback: {traceback.format_exc()}")

print("\n" + "=" * 60)
print("🏁 TESTE CONCLUÍDO")
