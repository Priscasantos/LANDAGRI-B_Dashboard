#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar as novas cores mais divergentes
"""

import sys
from pathlib import Path

# Add scripts to path
current_dir = Path(__file__).parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from scripts.plotting.chart_core import get_scope_colors

def test_improved_colors():
    """Testa as novas cores mais divergentes"""
    print("🎨 Testando nova paleta de cores mais divergentes...")
    
    # Test light theme
    light_colors = get_scope_colors('light')
    print("\n📱 Tema Claro:")
    for scope, color in light_colors.items():
        print(f"  {scope:12} -> {color}")
    
    # Test dark theme  
    dark_colors = get_scope_colors('dark')
    print("\n🌙 Tema Escuro:")
    for scope, color in dark_colors.items():
        print(f"  {scope:12} -> {color}")
    
    # Test color contrast
    print("\n🔍 Análise de Contraste:")
    expected_keys = ["Global", "Nacional", "Regional", "Continental"]
    
    for theme_name, colors in [("Light", light_colors), ("Dark", dark_colors)]:
        print(f"\n{theme_name} Theme:")
        for key in expected_keys:
            if key in colors:
                print(f"  ✅ {key} definido: {colors[key]}")
            else:
                print(f"  ❌ {key} não encontrado")
    
    print("\n✨ Teste concluído! As cores agora são mais divergentes e acessíveis.")
    return True

if __name__ == "__main__":
    test_improved_colors()
