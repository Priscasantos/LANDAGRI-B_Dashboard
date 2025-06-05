# -*- coding: utf-8 -*-
"""
Verificador e Validador do Sistema
=================================

Este script verifica a integridade de todos os arquivos do sistema e 
valida se o software está pronto para execução.

Autor: Análise Comparativa de Iniciativas LULC
Data: 2024
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

def check_file_exists(filename, description=""):
    """
    Verifica se um arquivo existe e retorna informações sobre ele.
    
    Args:
        filename (str): Nome do arquivo
        description (str): Descrição do arquivo
    
    Returns:
        dict: Informações sobre o arquivo
    """
    info = {
        'filename': filename,
        'description': description,
        'exists': False,
        'size': 0,
        'readable': False
    }
    
    if os.path.exists(filename):
        info['exists'] = True
        info['size'] = os.path.getsize(filename)
        info['readable'] = os.access(filename, os.R_OK)
    
    return info

def validate_csv_file(filename):
    """
    Valida o arquivo CSV de dados das iniciativas.
    
    Args:
        filename (str): Nome do arquivo CSV
    
    Returns:
        dict: Resultado da validação
    """
    result = {
        'valid': False,
        'rows': 0,
        'columns': 0,
        'required_columns': [],
        'missing_columns': [],
        'errors': []
    }
    
    required_columns = [
        'Nome', 'Tipo', 'Resolução (m)', 'Acurácia (%)', 'Classes',
        'Metodologia', 'Frequência Temporal', 'Anos Disponíveis', 'Escopo'
    ]
    
    try:
        df = pd.read_csv(filename, encoding='utf-8')
        result['rows'] = len(df)
        result['columns'] = len(df.columns)
        result['required_columns'] = required_columns
        
        # Verificar colunas obrigatórias
        missing = [col for col in required_columns if col not in df.columns]
        result['missing_columns'] = missing
        
        if not missing:
            # Verificar dados
            if df.isnull().sum().sum() > 0:
                result['errors'].append("Valores nulos encontrados no dataset")
            
            if len(df) < 10:
                result['errors'].append("Dataset com poucas iniciativas (< 10)")
            
            # Verificar faixas de valores
            if 'Acurácia (%)' in df.columns:
                acc_min, acc_max = df['Acurácia (%)'].min(), df['Acurácia (%)'].max()
                if acc_min < 0 or acc_max > 100:
                    result['errors'].append("Acurácia fora da faixa 0-100%")
            
            if 'Resolução (m)' in df.columns:
                if df['Resolução (m)'].min() <= 0:
                    result['errors'].append("Resolução com valores inválidos")
            
            result['valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Erro ao ler CSV: {str(e)}")
    
    return result

def validate_json_file(filename):
    """
    Valida o arquivo JSON de metadados.
    
    Args:
        filename (str): Nome do arquivo JSON
    
    Returns:
        dict: Resultado da validação
    """
    result = {
        'valid': False,
        'initiatives': 0,
        'required_fields': [],
        'errors': []
    }
    
    required_fields = [
        'metodologia', 'validacao', 'cobertura', 'fonte_dados'
    ]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result['initiatives'] = len(data)
        result['required_fields'] = required_fields
        
        # Verificar estrutura
        for initiative, metadata in data.items():
            if not isinstance(metadata, dict):
                result['errors'].append(f"Metadados inválidos para {initiative}")
                continue
            
            missing_fields = [field for field in required_fields if field not in metadata]
            if missing_fields:
                result['errors'].append(f"Campos ausentes em {initiative}: {missing_fields}")
        
        result['valid'] = len(result['errors']) == 0
        
    except json.JSONDecodeError as e:
        result['errors'].append(f"JSON inválido: {str(e)}")
    except Exception as e:
        result['errors'].append(f"Erro ao ler JSON: {str(e)}")
    
    return result

def check_python_environment():
    """
    Verifica o ambiente Python e dependências.
    
    Returns:
        dict: Status do ambiente
    """
    result = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'python_compatible': False,
        'packages': {},
        'missing_packages': [],
        'errors': []
    }
    
    # Verificar versão do Python
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        result['python_compatible'] = True
    else:
        result['errors'].append("Python 3.8+ necessário")
    
    # Verificar pacotes necessários
    required_packages = [
        'streamlit', 'plotly', 'pandas', 'numpy', 'scikit-learn'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            result['packages'][package] = '✅ Instalado'
        except ImportError:
            result['packages'][package] = '❌ Ausente'
            result['missing_packages'].append(package)
    
    return result

def generate_system_report():
    """
    Gera um relatório completo do sistema.
    
    Returns:
        dict: Relatório completo
    """
    print("🔍 Verificando Sistema - Iniciativas LULC")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'files': {},
        'csv_validation': {},
        'json_validation': {},
        'environment': {},
        'overall_status': 'unknown'
    }
    
    # Verificar arquivos essenciais
    essential_files = {
        'app.py': 'Aplicativo principal Streamlit',
        'initiatives_comparison.csv': 'Dataset das iniciativas',
        'initiatives_metadata.json': 'Metadados detalhados',
        'requirements.txt': 'Dependências Python'
    }
    
    print("\\n📁 Verificando arquivos essenciais...")
    all_files_ok = True
    
    for filename, description in essential_files.items():
        info = check_file_exists(filename, description)
        report['files'][filename] = info
        
        if info['exists'] and info['readable']:
            print(f"   ✅ {filename} - {info['size']:,} bytes")
        else:
            print(f"   ❌ {filename} - {description}")
            all_files_ok = False
    
    # Validar CSV
    if report['files'].get('initiatives_comparison.csv', {}).get('exists'):
        print("\\n📊 Validando dataset CSV...")
        csv_result = validate_csv_file('initiatives_comparison.csv')
        report['csv_validation'] = csv_result
        
        if csv_result['valid']:
            print(f"   ✅ CSV válido - {csv_result['rows']} iniciativas, {csv_result['columns']} colunas")
        else:
            print(f"   ❌ CSV inválido:")
            for error in csv_result['errors']:
                print(f"      • {error}")
            all_files_ok = False
    
    # Validar JSON
    if report['files'].get('initiatives_metadata.json', {}).get('exists'):
        print("\\n📋 Validando metadados JSON...")
        json_result = validate_json_file('initiatives_metadata.json')
        report['json_validation'] = json_result
        
        if json_result['valid']:
            print(f"   ✅ JSON válido - {json_result['initiatives']} iniciativas")
        else:
            print(f"   ❌ JSON inválido:")
            for error in json_result['errors']:
                print(f"      • {error}")
            all_files_ok = False
    
    # Verificar ambiente Python
    print("\\n🐍 Verificando ambiente Python...")
    env_result = check_python_environment()
    report['environment'] = env_result
    
    print(f"   Python: {env_result['python_version']}")
    if env_result['python_compatible']:
        print("   ✅ Versão compatível")
    else:
        print("   ❌ Versão incompatível")
        all_files_ok = False
    
    print("\\n   📦 Pacotes:")
    for package, status in env_result['packages'].items():
        print(f"      {package}: {status}")
    
    # Status geral
    if all_files_ok and env_result['python_compatible'] and not env_result['missing_packages']:
        report['overall_status'] = 'ready'
        print("\\n🎉 Sistema pronto para execução!")
    elif env_result['missing_packages']:
        report['overall_status'] = 'missing_dependencies'
        print("\\n⚠️ Sistema quase pronto - instale as dependências:")
        print("   pip install -r requirements.txt")
    else:
        report['overall_status'] = 'error'
        print("\\n❌ Sistema com problemas - verifique os erros acima")
    
    return report

def save_report(report, filename='system_report.json'):
    """
    Salva o relatório em arquivo JSON.
    
    Args:
        report (dict): Relatório do sistema
        filename (str): Nome do arquivo de saída
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\\n📋 Relatório salvo em: {filename}")
    except Exception as e:
        print(f"\\n❌ Erro ao salvar relatório: {e}")

def main():
    """Função principal para verificação do sistema."""
    report = generate_system_report()
    
    # Salvar relatório
    save_report(report)
    
    # Instruções finais
    print("\\n" + "=" * 50)
    
    if report['overall_status'] == 'ready':
        print("🚀 Para executar o aplicativo:")
        print("   streamlit run app.py")
        print("\\n💡 Ou use os scripts de execução:")
        print("   • Windows: run_app.bat")
        print("   • Linux/Mac: ./run_app.sh")
    
    elif report['overall_status'] == 'missing_dependencies':
        print("🔧 Para instalar dependências:")
        print("   pip install -r requirements.txt")
        print("\\n💡 Ou use os instaladores:")
        print("   • Windows: install.bat")
        print("   • Linux/Mac: ./install.sh")
    
    else:
        print("🛠️ Para corrigir problemas:")
        print("   1. Execute os scripts de geração:")
        print("      python generate_dataset.py")
        print("      python generate_metadata.py")
        print("   2. Instale dependências:")
        print("      pip install -r requirements.txt")
    
    return report['overall_status'] == 'ready'

if __name__ == "__main__":
    main()
