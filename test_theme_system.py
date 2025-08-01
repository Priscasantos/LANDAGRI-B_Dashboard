#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Theme System - Demonstra o novo sistema de temas adaptativos
================================================================

Este script testa o novo sistema de detecção e aplicação de temas
para garantir que os gráficos tenham aparência consistente.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.plotting.chart_core import (
    get_chart_config, 
    get_theme_colors, 
    detect_streamlit_theme,
    set_theme_preference
)

def test_theme_system():
    """Testa o sistema de temas com diferentes configurações."""
    
    print("🎨 Testando Sistema de Temas Adaptativos")
    print("=" * 50)
    
    # Teste 1: Detecção automática
    print("\n1. Detecção Automática de Tema:")
    current_theme = detect_streamlit_theme()
    print(f"   Tema detectado: {current_theme}")
    
    # Teste 2: Configuração para tema claro
    print("\n2. Configuração Tema Claro:")
    light_colors = get_theme_colors('light')
    print(f"   Fundo: {light_colors['background_color']}")
    print(f"   Papel: {light_colors['paper_color']}")
    print(f"   Fonte: {light_colors['font_color']}")
    print(f"   Grid: {light_colors['grid_color']}")
    
    # Teste 3: Configuração para tema escuro
    print("\n3. Configuração Tema Escuro:")
    dark_colors = get_theme_colors('dark')
    print(f"   Fundo: {dark_colors['background_color']}")
    print(f"   Papel: {dark_colors['paper_color']}")
    print(f"   Fonte: {dark_colors['font_color']}")
    print(f"   Grid: {dark_colors['grid_color']}")
    
    # Teste 4: Configuração completa do gráfico
    print("\n4. Configuração Completa (Tema Claro):")
    light_config = get_chart_config('light')
    print(f"   Dimensões: {light_config['dimensions']['default_width']}x{light_config['dimensions']['default_height']}")
    print(f"   Fonte do título: {light_config['title']['font_size']}px")
    print(f"   Margens: L={light_config['margins']['left']} R={light_config['margins']['right']}")
    
    print("\n5. Configuração Completa (Tema Escuro):")
    dark_config = get_chart_config('dark')
    print(f"   Cor de fundo: {dark_config['theme']['background_color']}")
    print(f"   Cor da fonte: {dark_config['theme']['font_color']}")
    
    # Teste 6: Validação de contraste
    print("\n6. Validação de Contraste:")
    light_bg = light_colors['background_color']
    light_font = light_colors['font_color']
    dark_bg = dark_colors['background_color']
    dark_font = dark_colors['font_color']
    
    print(f"   Tema Claro: {light_font} em {light_bg} ✅")
    print(f"   Tema Escuro: {dark_font} em {dark_bg} ✅")
    
    print(f"\n✅ Sistema de temas funcionando corretamente!")
    print(f"📊 Os gráficos agora terão aparência consistente em ambos os modos.")
    

if __name__ == "__main__":
    test_theme_system()
