#!/usr/bin/env python3
"""
Debug detalhado da função load_optimized_data
"""

print("🔍 DEBUG DETALHADO DA FUNÇÃO")
print("=" * 50)

import sys
from pathlib import Path

# Adiciona paths
current_dir = Path(".")
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Testa importação
print("📦 Importando utilities.dashboard_optimizer...")
from utilities.dashboard_optimizer import load_optimized_data

# Primeiro vamos verificar as variáveis globais
print("🔍 Verificando estado das variáveis...")

# Acessa as variáveis do módulo
import utilities.dashboard_optimizer as opt_module
print(f"CACHE_AVAILABLE: {getattr(opt_module, 'CACHE_AVAILABLE', 'UNDEFINED')}")
print(f"_load_optimized_data: {getattr(opt_module, '_load_optimized_data', 'UNDEFINED')}")

# Agora vamos executar e ver o que acontece
print("\n📊 Executando função com debug...")

# Vamos fazer debug dentro da própria função criando uma versão debug
def debug_load_optimized_data():
    print("   🔍 Dentro da função debug...")
    
    try:
        from utilities.dashboard_optimizer import CACHE_AVAILABLE, _load_optimized_data
        print(f"   📋 CACHE_AVAILABLE: {CACHE_AVAILABLE}")
        print(f"   📋 _load_optimized_data: {_load_optimized_data}")
        
        if CACHE_AVAILABLE and _load_optimized_data is not None:
            print("   ✅ Tentando usar cache otimizado...")
            try:
                result = _load_optimized_data()
                print(f"   📦 Resultado do cache: {result}")
                return result
            except Exception as e:
                print(f"   ❌ Erro no cache: {e}")
        else:
            print("   ⚠️  Cache não disponível, usando fallback...")
            
        # Fallback
        print("   🔄 Executando fallback...")
        import pandas as pd
        import json
        import re
        
        data_path = Path(".") / "data" / "initiatives_metadata.jsonc"
        print(f"   📁 Caminho: {data_path}")
        
        if data_path.exists():
            print("   📄 Arquivo existe, carregando...")
            
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limpa JSONC
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            data = json.loads(content)
            print(f"   🔍 Dados carregados: {type(data)}")
            
            # Converte para DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data])
                print(f"   ✅ DataFrame criado: {df.shape}")
                
                cache_info = {
                    'status': 'basic_load_success',
                    'rows': len(df),
                    'columns': len(df.columns)
                }
                
                return None, df, cache_info
            else:
                print(f"   ⚠️  Tipo inesperado: {type(data)}")
                return None, pd.DataFrame(), {'status': 'type_error'}
        else:
            print("   ❌ Arquivo não existe")
            return None, pd.DataFrame(), {'status': 'file_not_found'}
            
    except Exception as e:
        print(f"   ❌ Erro geral: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")
        return None, {}, {'status': 'error', 'error': str(e)}

# Executa debug
resultado = debug_load_optimized_data()
print(f"\n📦 Resultado final: {resultado}")

print("\n" + "=" * 50)
print("🏁 DEBUG CONCLUÍDO")
