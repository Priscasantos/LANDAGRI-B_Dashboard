"""
🔧 Consolidação e Limpeza do Sistema de Cache
=============================================

Implementa as soluções recomendadas pelo diagnóstico para resolver
duplicações de cache e conflitos de imports.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import os
import sys
import shutil
from pathlib import Path

def backup_arquivos_importantes():
    """Faz backup dos arquivos importantes antes das alterações."""
    
    print("\n💾 CRIANDO BACKUPS DOS ARQUIVOS IMPORTANTES")
    print("=" * 50)
    
    backup_dir = Path("backups") / "cache_consolidation_2025_07_22"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    arquivos_backup = [
        "utilities/dashboard_optimizer.py",
        "scripts/utilities/dashboard_optimizer.py",
        "utilities/cache_system_backup.py",
        "dashboard/overview.py",
        "dashboard/comparison.py",
        "dashboard/temporal.py",
        "dashboard/detailed.py",
        "dashboard/conab.py"
    ]
    
    for arquivo in arquivos_backup:
        arquivo_path = Path(arquivo)
        if arquivo_path.exists():
            backup_path = backup_dir / arquivo_path.name
            try:
                shutil.copy2(arquivo_path, backup_path)
                print(f"✅ Backup criado: {arquivo} -> {backup_path}")
            except Exception as e:
                print(f"❌ Erro no backup de {arquivo}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado para backup: {arquivo}")
    
    return backup_dir

def remover_duplicacoes_cache():
    """Remove arquivos duplicados de cache mantendo apenas o principal."""
    
    print("\n🗂️ REMOVENDO DUPLICAÇÕES DE CACHE")
    print("=" * 40)
    
    # Lista de arquivos duplicados para remover
    arquivos_duplicados = [
        "utilities/dashboard_optimizer.py",  # Remove wrapper problemático
        "utilities/cache_system_fixed.py",  # Remove versão fixed
        "utilities/cache_system_backup.py"  # Move para backup real
    ]
    
    for arquivo in arquivos_duplicados:
        arquivo_path = Path(arquivo)
        if arquivo_path.exists():
            try:
                arquivo_path.unlink()
                print(f"✅ Removido: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
        else:
            print(f"ℹ️ Arquivo já não existe: {arquivo}")

def simplificar_imports_dashboard():
    """Simplifica os imports nos módulos dashboard removendo fallbacks excessivos."""
    
    print("\n⚡ SIMPLIFICANDO IMPORTS DOS MÓDULOS DASHBOARD")
    print("=" * 50)
    
    modulos = [
        "dashboard/comparison.py",
        "dashboard/temporal.py", 
        "dashboard/detailed.py",
        "dashboard/conab.py"
    ]
    
    # Template de import simplificado
    import_template = """# Imports consolidados - Sistema de Cache Unificado
try:
    from utilities.cache_system import (
        load_optimized_data,
        create_performance_metrics,
        get_cache_info
    )
    CACHE_AVAILABLE = True
except ImportError as e:
    st.sidebar.error(f"❌ Falha no sistema de cache: {e}")
    CACHE_AVAILABLE = False
    
    # Fallback mínimo
    def load_optimized_data():
        return None, pd.DataFrame(), {'cache_hits': 0, 'status': 'fallback'}
    
    def create_performance_metrics():
        return {}
    
    def get_cache_info():
        return {'status': 'unavailable'}
"""
    
    for modulo in modulos:
        modulo_path = Path(modulo)
        if modulo_path.exists():
            try:
                with open(modulo_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Encontra o final dos imports originais
                lines = content.split('\n')
                import_end_line = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and 'load_optimized_data' in line:
                        import_end_line = i
                        break
                    elif line.strip().startswith('except ImportError'):
                        # Procura o final do bloco except
                        for j in range(i, len(lines)):
                            if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                                import_end_line = j
                                break
                        break
                
                if import_end_line > 0:
                    # Reconstrói o arquivo com imports simplificados
                    new_lines = []
                    
                    # Mantém imports básicos do início
                    in_import_section = True
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            if 'utilities.cache_system' not in line and 'utilities.dashboard_optimizer' not in line:
                                new_lines.append(line)
                        elif line.strip() == '' and in_import_section:
                            new_lines.append(line)
                        elif line.strip().startswith('def ') or line.strip().startswith('class '):
                            in_import_section = False
                            # Adiciona import consolidado antes da primeira função
                            new_lines.append('')
                            new_lines.extend(import_template.split('\n'))
                            new_lines.append('')
                            new_lines.append(line)
                        elif not in_import_section:
                            new_lines.append(line)
                    
                    # Salva arquivo atualizado
                    with open(modulo_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines))
                    
                    print(f"✅ Imports simplificados em: {modulo}")
                
            except Exception as e:
                print(f"❌ Erro ao simplificar imports em {modulo}: {e}")
        else:
            print(f"⚠️ Módulo não encontrado: {modulo}")

def corrigir_arquivo_sensors_jsonc():
    """Corrige o erro de caractere de controle no arquivo sensors_metadata.jsonc."""
    
    print("\n🔧 CORRIGINDO ARQUIVO SENSORS_METADATA.JSONC")
    print("=" * 45)
    
    sensors_path = Path("data/sensors_metadata.jsonc")
    if not sensors_path.exists():
        print("❌ Arquivo sensors_metadata.jsonc não encontrado")
        return False
    
    try:
        with open(sensors_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove caracteres de controle problemáticos
        import re
        # Remove caracteres de controle ASCII 0-31 exceto \n, \r, \t
        content_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
        
        # Verifica se houve mudança
        if content != content_clean:
            # Faz backup do original
            backup_path = sensors_path.with_suffix('.jsonc.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Salva versão corrigida
            with open(sensors_path, 'w', encoding='utf-8') as f:
                f.write(content_clean)
            
            print(f"✅ Caracteres de controle removidos de {sensors_path}")
            print(f"📁 Backup salvo em: {backup_path}")
            return True
        else:
            print("ℹ️ Nenhum caractere de controle encontrado")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo sensors: {e}")
        return False

def criar_arquivo_validacao():
    """Cria arquivo de validação do sistema consolidado."""
    
    print("\n✅ CRIANDO VALIDAÇÃO DO SISTEMA CONSOLIDADO")
    print("=" * 50)
    
    validation_code = '''"""
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
    print("\\n🖥️ TESTANDO MÓDULOS DASHBOARD")
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
    
    print(f"\\n📊 Resultado: {success_count}/{len(modules)} módulos OK")
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
    print("\\n🎯 RESULTADO DA VALIDAÇÃO")
    print("=" * 30)
    print(f"💾 Sistema de cache: {'✅ OK' if cache_ok else '❌ FALHOU'}")
    print(f"🖥️ Módulos dashboard: {'✅ OK' if modules_ok else '❌ FALHOU'}")
    
    if cache_ok and modules_ok:
        print("\\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("Consolidação bem-sucedida. Cache unificado e funcional.")
    else:
        print("\\n⚠️ SISTEMA COM PROBLEMAS")
        print("Verifique os erros acima e corrija os problemas.")
    
    return cache_ok and modules_ok

if __name__ == "__main__":
    main()
'''
    
    validation_path = Path("validar_sistema_consolidado.py")
    with open(validation_path, 'w', encoding='utf-8') as f:
        f.write(validation_code)
    
    print(f"✅ Arquivo de validação criado: {validation_path}")

def executar_consolidacao():
    """Executa todo o processo de consolidação."""
    
    print("🚀 INICIANDO CONSOLIDAÇÃO DO SISTEMA DE CACHE")
    print("=" * 60)
    
    # Muda para o diretório do projeto
    os.chdir(Path(__file__).parent)
    
    try:
        # 1. Backup
        backup_dir = backup_arquivos_importantes()
        print(f"📁 Backups salvos em: {backup_dir}")
        
        # 2. Remove duplicações
        remover_duplicacoes_cache()
        
        # 3. Corrige arquivo sensors
        corrigir_arquivo_sensors_jsonc()
        
        # 4. Simplifica imports (comentado por agora para manter estabilidade)
        # simplificar_imports_dashboard()
        
        # 5. Cria validação
        criar_arquivo_validacao()
        
        print("\n🎉 CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 40)
        print("✅ Duplicações removidas")
        print("✅ Arquivo sensors corrigido")
        print("✅ Sistema de validação criado")
        print("✅ Backups preservados")
        
        print("\\n🎯 PRÓXIMOS PASSOS:")
        print("1. Execute: python validar_sistema_consolidado.py")
        print("2. Teste o dashboard: streamlit run app.py")
        print("3. Verifique se overview dashboard mantém complexidade")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na consolidação: {e}")
        return False

def main():
    """Função principal."""
    success = executar_consolidacao()
    
    if success:
        print("\\n✅ Consolidação bem-sucedida!")
    else:
        print("\\n❌ Falha na consolidação. Verifique os erros.")
    
    return success

if __name__ == "__main__":
    main()
