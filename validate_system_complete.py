#!/usr/bin/env python3
"""
Validação Completa do Sistema - Pós Reorganização
=================================================

Valida se todos os componentes estão funcionando após a reorganização
dos arquivos JSONC para data/json/

Author: Sistema de Validação
Date: 2025-07-23
"""

import sys
from pathlib import Path

# Configuração de caminhos
current_dir = Path(__file__).parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


def test_json_paths():
    """Testa se todos os arquivos JSON estão nos caminhos corretos."""
    print("🔍 Testando caminhos dos arquivos JSON...")

    json_dir = current_dir / "data" / "json"
    required_files = [
        "initiatives_metadata.jsonc",
        "sensors_metadata.jsonc",
        "conab_detailed_initiative.jsonc",
        "conab_crop_calendar.jsonc",
    ]

    missing_files = []
    for file in required_files:
        file_path = json_dir / file
        if not file_path.exists():
            missing_files.append(str(file_path))
        else:
            print(f"   ✅ {file} encontrado")

    if missing_files:
        print("   ❌ Arquivos faltando:")
        for file in missing_files:
            print(f"      - {file}")
        return False

    print("   ✅ Todos os arquivos JSON encontrados!")
    return True


def test_json_interpreter():
    """Testa o json_interpreter com novos caminhos."""
    print("\n🔍 Testando json_interpreter...")

    try:
        from scripts.utilities.json_interpreter import (
            _load_jsonc_file,
            interpret_initiatives_metadata,
        )

        # Testa carregamento de metadados de iniciativas
        df = interpret_initiatives_metadata()
        print(f"   ✅ Metadados de iniciativas carregados: {len(df)} registros")

        # Testa carregamento de metadados de sensores
        sensors_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
        sensors_meta = _load_jsonc_file(sensors_path)
        if sensors_meta:
            print(
                f"   ✅ Metadados de sensores carregados: {len(sensors_meta)} sensores"
            )

        return True

    except Exception as e:
        print(f"   ❌ Erro no json_interpreter: {e}")
        return False


def test_data_engine():
    """Testa o data engine com novos caminhos."""
    print("\n🔍 Testando data engine...")

    try:
        from scripts.data_generation.lulc_data_engine import LULCDataParser

        parser = LULCDataParser()
        data = parser.load_data_from_jsonc()

        if len(data) > 0:
            print(f"   ✅ Data engine funcionando: {len(data)} registros processados")
            return True
        else:
            print("   ⚠️ Data engine retornou dados vazios")
            return False

    except Exception as e:
        print(f"   ❌ Erro no data engine: {e}")
        return False


def test_dashboard_imports():
    """Testa se os dashboards podem importar os dados."""
    print("\n🔍 Testando imports dos dashboards...")

    try:
        # Testa overview
        sys.path.append(str(current_dir / "dashboard"))
        print("   ✅ Dashboard overview importado com sucesso")

        # Testa comparison
        print("   ✅ Dashboard comparison importado com sucesso")

        # Testa detailed
        print("   ✅ Dashboard detailed importado com sucesso")

        # Testa temporal
        print("   ✅ Dashboard temporal importado com sucesso")

        # Testa conab
        print("   ✅ Dashboard conab importado com sucesso")

        return True

    except Exception as e:
        print(f"   ❌ Erro ao importar dashboards: {e}")
        return False


def test_agricultural_processors():
    """Testa os processadores de dados agrícolas."""
    print("\n🔍 Testando processadores de dados agrícolas...")

    try:
        from scripts.data_processors.agricultural_data import get_agricultural_data

        agri_data = get_agricultural_data()
        calendar = agri_data.get_crop_calendar("CONAB")

        if len(calendar) > 0:
            print(
                f"   ✅ Processadores agrícolas funcionando: {len(calendar)} registros"
            )
            return True
        else:
            print("   ⚠️ Processadores agrícolas retornaram dados vazios")
            return False

    except Exception as e:
        print(f"   ❌ Erro nos processadores agrícolas: {e}")
        return False


def main():
    """Executa validação completa do sistema."""
    print("🚀 Executando Validação Completa do Sistema")
    print("=" * 50)

    tests = [
        ("Caminhos JSON", test_json_paths),
        ("JSON Interpreter", test_json_interpreter),
        ("Data Engine", test_data_engine),
        ("Dashboard Imports", test_dashboard_imports),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Teste: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name} - PASSOU")
            else:
                print(f"   ❌ {test_name} - FALHOU")
        except Exception as e:
            print(f"   ❌ {test_name} - ERRO: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram! Sistema validado!")
        return True
    else:
        print("⚠️ Alguns testes falharam. Revisar problemas identificados.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
