#!/usr/bin/env python3
"""
Teste de imports para verificar se a reorganização funcionou.
"""

import sys
from pathlib import Path

# Adicionar scripts ao path
current_dir = Path(__file__).parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

print("🔧 Testando imports do dashboard LULC...")

# Teste 1: Módulos básicos
try:
    from data_processing import load_data, prepare_plot_data
    print("✅ data_processing: OK")
except ImportError as e:
    print(f"❌ data_processing: {e}")

try:
    from utils import safe_download_image
    print("✅ utils: OK")
except ImportError as e:
    print(f"❌ utils: {e}")

try:
    from generate_graphics import plot_resolucao_acuracia, plot_timeline
    print("✅ generate_graphics: OK")
except ImportError as e:
    print(f"❌ generate_graphics: {e}")

try:
    from charts import create_comparison_matrix
    print("✅ charts: OK")
except ImportError as e:
    print(f"❌ charts: {e}")

try:
    from tables import gap_analysis
    print("✅ tables: OK")
except ImportError as e:
    print(f"❌ tables: {e}")

try:
    from config import get_initiative_color_map
    print("✅ config: OK")
except ImportError as e:
    print(f"❌ config: {e}")

print("\n🧪 Teste de carregamento de dados...")
try:
    df, metadata = load_data()
    print(f"✅ Dados carregados: {len(df)} iniciativas")
    print(f"✅ Metadados: {len(metadata)} entradas")
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")

print("\n🎯 Teste concluído!")
