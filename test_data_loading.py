"""
Teste de Carregamento de Dados
==============================

Script para testar se o sistema de carregamento de dados está funcionando.
"""

import sys
from pathlib import Path

# Add scripts directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "scripts"))


def test_data_loading():
    """Testa o carregamento dos dados."""
    print("🔍 Testando carregamento de dados...")

    try:
        from scripts.utilities.json_interpreter import interpret_initiatives_metadata

        # Testar com o caminho correto
        metadata_file_path = (
            current_dir / "data" / "json" / "initiatives_metadata.jsonc"
        )

        print(f"📁 Verificando arquivo: {metadata_file_path}")
        print(f"   Existe: {metadata_file_path.exists()}")

        if not metadata_file_path.exists():
            print("❌ Arquivo não encontrado!")
            return False

        # Tentar carregar
        df = interpret_initiatives_metadata(metadata_file_path)

        if df is None or df.empty:
            print("❌ Dados vazios ou nulos!")
            return False

        print("✅ Dados carregados com sucesso!")
        print(f"   Linhas: {len(df)}")
        print(f"   Colunas: {len(df.columns)}")
        print(f"   Primeiras colunas: {list(df.columns[:5])}")

        return True

    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_data_loading()
    if success:
        print("\n🎉 Teste passou! Os dados estão sendo carregados corretamente.")
    else:
        print("\n💥 Teste falhou! Verifique os erros acima.")
