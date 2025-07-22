"""
🔧 Correção Específica do Arquivo Sensors JSONC
===============================================

Identifica e corrige o caractere de controle específico no arquivo sensors_metadata.jsonc.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import json
import re
from pathlib import Path

def encontrar_caractere_problematico():
    """Encontra e identifica o caractere de controle específico."""
    
    print("🔍 ANALISANDO CARACTERE PROBLEMÁTICO")
    print("=" * 40)
    
    sensors_path = Path("data/sensors_metadata.jsonc")
    
    with open(sensors_path, 'rb') as f:
        content_bytes = f.read()
    
    # Analisa bytes ao redor da posição 991
    start = max(0, 980)
    end = min(len(content_bytes), 1010)
    
    print(f"📍 Analisando bytes {start}-{end}:")
    
    for i in range(start, end):
        byte_val = content_bytes[i]
        char = chr(byte_val) if 32 <= byte_val <= 126 else f'\\x{byte_val:02x}'
        print(f"  Pos {i}: {byte_val:3d} ({char})")
        
        if byte_val < 32 and byte_val not in [9, 10, 13]:  # Não tab, \n, \r
            print(f"  ⚠️ CARACTERE DE CONTROLE ENCONTRADO: {byte_val} na posição {i}")
            return i, byte_val
    
    return None, None

def corrigir_arquivo_especifico():
    """Corrige o arquivo removendo caracteres de controle específicos."""
    
    print("\n🔧 CORRIGINDO ARQUIVO SENSORS_METADATA.JSONC")
    print("=" * 50)
    
    sensors_path = Path("data/sensors_metadata.jsonc")
    
    # Lê como bytes para controle total
    with open(sensors_path, 'rb') as f:
        content_bytes = f.read()
    
    print(f"📄 Tamanho original: {len(content_bytes)} bytes")
    
    # Filtra bytes válidos (mantém apenas printáveis + \n, \r, \t)
    valid_bytes = bytearray()
    removed_count = 0
    
    for byte_val in content_bytes:
        if byte_val >= 32 or byte_val in [9, 10, 13]:  # Printável ou tab/\n/\r
            valid_bytes.append(byte_val)
        else:
            removed_count += 1
            print(f"🗑️ Removendo byte de controle: {byte_val} (\\x{byte_val:02x})")
    
    if removed_count > 0:
        # Backup do original
        backup_path = sensors_path.with_suffix('.jsonc.backup_bytes')
        with open(backup_path, 'wb') as f:
            f.write(content_bytes)
        print(f"💾 Backup salvo: {backup_path}")
        
        # Salva versão corrigida
        with open(sensors_path, 'wb') as f:
            f.write(valid_bytes)
        
        print(f"✅ Arquivo corrigido: {len(valid_bytes)} bytes ({removed_count} bytes removidos)")
    else:
        print("ℹ️ Nenhum caractere de controle encontrado")
    
    return removed_count > 0

def testar_arquivo_corrigido():
    """Testa se o arquivo corrigido carrega sem erros."""
    
    print("\n🧪 TESTANDO ARQUIVO CORRIGIDO")
    print("=" * 35)
    
    try:
        from utilities.cache_system import _load_jsonc_file
        
        sensors_path = Path("data/sensors_metadata.jsonc")
        data = _load_jsonc_file(sensors_path)
        
        if data:
            print("✅ Arquivo JSONC carregado com sucesso!")
            if isinstance(data, dict):
                print(f"📋 Tipo: Dicionário com {len(data)} chaves")
                print(f"🔑 Primeiras chaves: {list(data.keys())[:3]}")
            else:
                print(f"📋 Tipo: {type(data)}")
            return True
        else:
            print("⚠️ Arquivo vazio ou não carregou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        return False

def main():
    """Executa correção específica do arquivo sensors."""
    
    print("🎯 CORREÇÃO ESPECÍFICA - SENSORS_METADATA.JSONC")
    print("=" * 55)
    
    # Muda para o diretório do projeto
    import os
    os.chdir(Path(__file__).parent)
    
    # 1. Encontra o caractere problemático
    pos, byte_val = encontrar_caractere_problematico()
    
    if pos is not None:
        print(f"🎯 Caractere de controle encontrado na posição {pos}: {byte_val}")
    
    # 2. Corrige o arquivo
    corrigido = corrigir_arquivo_especifico()
    
    # 3. Testa o arquivo corrigido
    sucesso = testar_arquivo_corrigido()
    
    # 4. Resultado final
    print(f"\n🎉 RESULTADO")
    print("=" * 15)
    print(f"🔧 Arquivo corrigido: {'✅' if corrigido else '⚠️'}")
    print(f"✅ Teste de carregamento: {'✅' if sucesso else '❌'}")
    
    if sucesso:
        print("\n🚀 PROBLEMA RESOLVIDO!")
        print("O erro de caractere de controle foi eliminado.")
    else:
        print("\n🔧 PROBLEMA PERSISTE")
        print("Pode ser necessária investigação adicional.")
    
    return sucesso

if __name__ == "__main__":
    main()
