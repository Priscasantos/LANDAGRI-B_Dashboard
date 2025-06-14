#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust Chart Saver Utility
==========================

Utility for saving Plotly charts with fallback mechanisms.
Handles different kaleido versions and provides HTML fallback.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import os
from pathlib import Path
import traceback


def save_chart_robust(fig, file_path, file_name_base, width=1200, height=800, scale=2):
    """
    Robustly save a Plotly figure with multiple fallback mechanisms.
    
    Args:
        fig: Plotly figure object
        file_path: Directory path to save the file
        file_name_base: Base filename without extension
        width: Image width in pixels
        height: Image height in pixels
        scale: Image scale factor
    
    Returns:
        tuple: (success, saved_path, format_used)
    """
    # Ensure output directory exists
    Path(file_path).mkdir(parents=True, exist_ok=True)
    
    # Try PNG first with different engines
    png_engines = ["kaleido", "auto", None]
    
    for engine in png_engines:
        try:
            png_path = os.path.join(file_path, f"{file_name_base}.png")
            print(f"🔄 Tentando salvar PNG com engine: {engine}...")
            
            if engine:
                fig.write_image(png_path, width=width, height=height, scale=scale, engine=engine)
            else:
                fig.write_image(png_path, width=width, height=height, scale=scale)
            
            print(f"✅ PNG salvo com sucesso: {png_path}")
            return True, png_path, "PNG"
            
        except Exception as e:
            print(f"⚠️ Falha com engine {engine}: {e}")
            continue
      # If PNG fails, try HTML
    try:
        html_path = os.path.join(file_path, f"{file_name_base}.html")
        print("🔄 Tentando salvar como HTML...")
        fig.write_html(html_path)
        print(f"✅ HTML salvo com sucesso: {html_path}")
        return True, html_path, "HTML"
        
    except Exception as e:
        print(f"❌ Falha ao salvar HTML: {e}")
    
    # If both fail, try JSON
    try:
        json_path = os.path.join(file_path, f"{file_name_base}.json")
        print("🔄 Tentando salvar como JSON...")
        fig.write_json(json_path)
        print(f"✅ JSON salvo com sucesso: {json_path}")
        return True, json_path, "JSON"
        
    except Exception as e:
        print(f"❌ Falha ao salvar JSON: {e}")
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
    
    return False, None, None


def test_kaleido_compatibility():
    """Test if kaleido is working properly with current setup."""
    try:
        import plotly.graph_objects as go
        
        # Create a simple test figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3], name="test"))
        fig.update_layout(title="Test Chart")
          # Try to save it
        test_dir = "test_output"
        success, path, format_used = save_chart_robust(fig, test_dir, "kaleido_test")
        
        if success:
            print(f"✅ Kaleido funcionando! Formato usado: {format_used}")
            # Clean up test file
            try:
                if path:  # Check if path is not None
                    os.remove(path)
                    os.rmdir(test_dir)
            except Exception:
                pass
            return True, format_used
        else:
            print("❌ Kaleido não está funcionando corretamente")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro no teste do kaleido: {e}")
        return False, None


if __name__ == "__main__":
    # Test the functionality
    test_kaleido_compatibility()
