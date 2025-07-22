#!/usr/bin/env python3
"""
Script de debug específico para o carregamento de dados
"""

import sys
import os
from pathlib import Path
import json
import pandas as pd

print("🔍 DEBUG ESPECÍFICO DO CARREGAMENTO DE DADOS")
print("=" * 60)

# Testa carregamento direto do arquivo JSONC
current_dir = Path(os.getcwd())
data_path = current_dir / "data" / "initiatives_metadata.jsonc"

print(f"📁 Caminho do arquivo: {data_path}")
print(f"📄 Arquivo existe: {data_path.exists()}")

if data_path.exists():
    try:
        # Carregamento do arquivo
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📏 Tamanho do conteúdo: {len(content)} caracteres")
        print(f"📋 Primeiras 200 caracteres:")
        print(content[:200])
        print("...")
        
        # Remove comentários JSONC
        import re
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        print(f"📄 Conteúdo após limpeza (primeiras 200 chars):")
        print(content[:200])
        print("...")
        
        # Parse JSON
        data = json.loads(content)
        print(f"🔍 Tipo de dados após parse: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📊 É dicionário com {len(data)} chaves:")
            for i, key in enumerate(list(data.keys())[:5]):
                print(f"   {i+1}. {key}")
            if len(data) > 5:
                print(f"   ... e mais {len(data)-5} chaves")
                
            # Tenta converter para DataFrame
            df = pd.DataFrame([data])
            print(f"✅ Conversão para DataFrame: {df.shape}")
            print(f"📋 Colunas: {list(df.columns)[:5]}...")
            
        elif isinstance(data, list):
            print(f"📊 É lista com {len(data)} itens")
            if data:
                print(f"   Primeiro item: {type(data[0])}")
            df = pd.DataFrame(data)
            print(f"✅ Conversão para DataFrame: {df.shape}")
            
        else:
            print(f"⚠️  Tipo inesperado: {type(data)}")
            
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

# Agora testa a função do dashboard_optimizer
print("\n" + "=" * 40)
print("🧪 TESTE DA FUNÇÃO DO DASHBOARD OPTIMIZER")

try:
    from utilities.dashboard_optimizer import load_optimized_data
    
    print("📊 Executando load_optimized_data()...")
    resultado = load_optimized_data()
    
    print(f"📦 Resultado completo: {resultado}")
    print(f"📏 Tamanho do resultado: {len(resultado)}")
    
    if len(resultado) == 3:
        metadata, df, cache_info = resultado
        print(f"   🔍 metadata: {type(metadata)} - {metadata}")
        print(f"   🔍 df: {type(df)} - {df}")
        print(f"   🔍 cache_info: {type(cache_info)} - {cache_info}")
    else:
        print(f"   ⚠️  Resultado tem tamanho inesperado: {len(resultado)}")
        
except Exception as e:
    print(f"❌ Erro na função: {e}")
    import traceback
    print(f"🔍 Traceback: {traceback.format_exc()}")

print("\n" + "=" * 60)
print("🏁 DEBUG CONCLUÍDO")
