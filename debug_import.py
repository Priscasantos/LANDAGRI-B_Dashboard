#!/usr/bin/env python3
"""
Debug da importação circular
"""

print("🔍 DEBUG DE IMPORTAÇÃO CIRCULAR")
print("=" * 50)

import sys
from pathlib import Path

current_dir = Path(".")
scripts_path = str(current_dir / "scripts")
print(f"📁 Scripts path: {scripts_path}")

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

print(f"📋 Sys.path:")
for i, path in enumerate(sys.path[:10]):
    print(f"   {i+1}. {path}")

print("\n🧪 TESTE DE IMPORTAÇÃO:")

try:
    sys.path.insert(0, str(current_dir / "scripts" / "utilities"))
    print("✅ Path adicionado")
    
    print("📦 Tentando importar dashboard_optimizer...")
    import dashboard_optimizer as original_optimizer
    print(f"✅ Importação bem-sucedida: {original_optimizer}")
    print(f"📋 Funções disponíveis: {[attr for attr in dir(original_optimizer) if not attr.startswith('_')]}")
    
    # Verifica se tem load_optimized_data
    if hasattr(original_optimizer, 'load_optimized_data'):
        print("✅ Função load_optimized_data encontrada")
        func = getattr(original_optimizer, 'load_optimized_data', None)
        print(f"📋 Função: {func}")
    else:
        print("❌ Função load_optimized_data NÃO encontrada")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\n" + "=" * 50)
print("🏁 DEBUG CONCLUÍDO")
