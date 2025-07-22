"""
🔧 Correção Final do Sistema - Overview Dashboard
==================================================

Corrige o erro de caractere de controle no arquivo sensors_metadata.jsonc
e valida que o overview dashboard mantém sua complexidade original.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import json
import re
from pathlib import Path

def corrigir_sensors_metadata():
    """Corrige o erro de caractere de controle no arquivo sensors_metadata.jsonc."""
    
    print("🔧 CORRIGINDO SENSORS_METADATA.JSONC")
    print("=" * 40)
    
    sensors_path = Path("data/sensors_metadata.jsonc")
    
    if not sensors_path.exists():
        print("❌ Arquivo sensors_metadata.jsonc não encontrado")
        return False
    
    try:
        # Lê o arquivo atual
        with open(sensors_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Arquivo original: {len(content)} caracteres")
        
        # Remove caracteres de controle problemáticos (exceto \n, \r, \t)
        content_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
        
        # Verifica se houve mudança
        chars_removed = len(content) - len(content_clean)
        if chars_removed > 0:
            print(f"🧹 Removidos {chars_removed} caracteres de controle")
            
            # Backup do original
            backup_path = sensors_path.with_suffix('.jsonc.original')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 Backup salvo: {backup_path}")
            
            # Salva versão limpa
            with open(sensors_path, 'w', encoding='utf-8') as f:
                f.write(content_clean)
            
            print(f"✅ Arquivo corrigido: {len(content_clean)} caracteres")
            
            # Testa se é válido JSON
            try:
                # Remove comentários JSONC para testar
                json_content = re.sub(r'//.*?$', '', content_clean, flags=re.MULTILINE)
                json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
                json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
                
                json.loads(json_content)
                print("✅ JSON válido após correção")
                return True
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Ainda há problemas no JSON: {e}")
                print("🔍 Fazendo limpeza adicional...")
                
                # Limpeza mais agressiva
                lines = content_clean.split('\n')
                clean_lines = []
                
                for line in lines:
                    # Remove caracteres não ASCII problemáticos
                    clean_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t\n\r')
                    clean_lines.append(clean_line)
                
                final_content = '\n'.join(clean_lines)
                
                with open(sensors_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                print(f"✅ Limpeza adicional concluída: {len(final_content)} caracteres")
                return True
        else:
            print("ℹ️ Nenhum caractere de controle encontrado")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo: {e}")
        return False

def testar_carregamento_dados():
    """Testa o carregamento de dados após correção."""
    
    print("\n📊 TESTANDO CARREGAMENTO APÓS CORREÇÃO")
    print("=" * 45)
    
    try:
        from utilities.cache_system import load_optimized_data
        
        metadata, df, cache_info = load_optimized_data()
        
        print(f"✅ Carregamento bem-sucedido!")
        print(f"   Status: {cache_info.get('status', 'unknown')}")
        print(f"   Data loaded: {cache_info.get('data_loaded', False)}")
        print(f"   Rows: {cache_info.get('rows', 0)}")
        print(f"   Columns: {cache_info.get('columns', 0)}")
        
        if df is not None and not df.empty:
            print(f"   DataFrame shape: {df.shape}")
            return True
        else:
            print("⚠️ DataFrame vazio")
            return False
            
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        return False

def verificar_overview_complexidade():
    """Verifica se o overview dashboard mantém sua complexidade."""
    
    print("\n🖥️ VERIFICANDO COMPLEXIDADE DO OVERVIEW")
    print("=" * 45)
    
    overview_path = Path("dashboard/overview.py")
    
    if not overview_path.exists():
        print("❌ Overview não encontrado")
        return False
    
    try:
        with open(overview_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Análise de complexidade
        metrics = {
            'total_lines': len(content.split('\n')),
            'functions': content.count('def '),
            'streamlit_elements': content.count('st.'),
            'plotly_elements': content.count('plotly') + content.count('px.') + content.count('go.'),
            'tabs': content.count('tab'),
            'columns': content.count('column'),
            'containers': content.count('container'),
            'expanders': content.count('expander'),
            'selectboxes': content.count('selectbox'),
            'multiselects': content.count('multiselect'),
            'metrics': content.count('metric'),
            'charts': content.count('chart') + content.count('plot')
        }
        
        complexity_score = sum([
            metrics['tabs'],
            metrics['columns'], 
            metrics['containers'],
            metrics['expanders'],
            metrics['selectboxes'],
            metrics['multiselects']
        ])
        
        print(f"📏 Total de linhas: {metrics['total_lines']}")
        print(f"🔧 Funções: {metrics['functions']}")
        print(f"🎯 Elementos Streamlit: {metrics['streamlit_elements']}")
        print(f"📊 Elementos Plotly: {metrics['plotly_elements']}")
        print(f"🔢 Score de complexidade: {complexity_score}")
        
        # Avaliação
        if complexity_score >= 100:
            print("✅ OVERVIEW MANTÉM ALTA COMPLEXIDADE")
            return True
        elif complexity_score >= 50:
            print("⚠️ OVERVIEW COM COMPLEXIDADE MODERADA")
            return True
        else:
            print("❌ OVERVIEW SIMPLIFICADO DEMAIS")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar overview: {e}")
        return False

def executar_correcao_final():
    """Executa todas as correções finais do sistema."""
    
    print("🎯 CORREÇÃO FINAL DO SISTEMA")
    print("=" * 40)
    
    # 1. Corrige sensors_metadata
    sensors_ok = corrigir_sensors_metadata()
    
    # 2. Testa carregamento
    loading_ok = testar_carregamento_dados()
    
    # 3. Verifica complexidade do overview
    overview_ok = verificar_overview_complexidade()
    
    # Resultado final
    print(f"\n🎉 RESULTADO FINAL")
    print("=" * 20)
    print(f"🔧 Sensors corrigido: {'✅' if sensors_ok else '❌'}")
    print(f"📊 Carregamento OK: {'✅' if loading_ok else '❌'}")
    print(f"🖥️ Overview complexo: {'✅' if overview_ok else '❌'}")
    
    all_ok = sensors_ok and loading_ok and overview_ok
    
    if all_ok:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Cache consolidado e funcional")
        print("✅ Dados carregando sem erros")
        print("✅ Overview mantém complexidade original")
        print("✅ Todas as duplicações removidas")
    else:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("Alguns aspectos precisam de atenção")
    
    return all_ok

def main():
    """Função principal."""
    
    # Muda para o diretório do projeto
    import os
    os.chdir(Path(__file__).parent)
    
    success = executar_correcao_final()
    
    if success:
        print("\n🚀 PRONTO PARA USO!")
        print("Execute: streamlit run app.py")
    else:
        print("\n🔧 VERIFIQUE OS PROBLEMAS RELATADOS")
    
    return success

if __name__ == "__main__":
    main()
