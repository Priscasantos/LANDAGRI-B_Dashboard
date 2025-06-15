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


def save_chart_robust(fig, file_path, file_name_base, width=1200, height=800, scale: float = 2.0, file_format="png"): # Changed scale type to float
    """
    Robustly save a Plotly figure with multiple fallback mechanisms.
    
    Args:
        fig: Plotly figure object
        file_path: Directory path to save the file
        file_name_base: Base filename without extension (now includes user-defined name)
        width: Image width in pixels
        height: Image height in pixels
        scale: Image scale factor (can be float)
        file_format: Desired output format (e.g., "png", "svg", "pdf", "jpeg", "webp", "html")
    
    Returns:
        tuple: (success, saved_path, format_used)
    """
    # Ensure output directory exists
    Path(file_path).mkdir(parents=True, exist_ok=True)
    
    # Construct the full filename with the chosen extension
    # file_name_base already includes the user-defined name from the UI
    output_filename = f"{file_name_base}.{file_format.lower()}"
    output_path = os.path.join(file_path, output_filename)

    print(f"ℹ️ Attempting to save chart to: {output_path}")
    print(f"ℹ️ Parameters: Width={width}, Height={height}, Scale={scale}, Format={file_format}")

    try:
        if file_format.lower() == "html":
            print(f"🔄 Saving as HTML: {output_path}...")
            fig.write_html(output_path)
            print(f"✅ HTML saved successfully: {output_path}")
            return True, output_path, "HTML"
        elif file_format.lower() == "json": # Though not typically a user choice for "image"
            print(f"🔄 Saving as JSON: {output_path}...")
            fig.write_json(output_path)
            print(f"✅ JSON saved successfully: {output_path}")
            return True, output_path, "JSON"
        else: # For PNG, JPEG, SVG, PDF, WebP - uses kaleido
            print(f"🔄 Saving as {file_format.upper()} using Plotly's write_image: {output_path}...")
            fig.write_image(output_path, width=width, height=height, scale=scale, format=file_format.lower())
            print(f"✅ {file_format.upper()} saved successfully: {output_path}")
            return True, output_path, file_format.upper()
            
    except Exception as e:
        print(f"❌ Failed to save chart as {file_format.upper()}: {e}")
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        
        # Fallback to HTML if the chosen static image format fails
        if file_format.lower() not in ["html", "json"]:
            print("⚠️ Fallback: Attempting to save as HTML instead.")
            try:
                html_fallback_filename = f"{file_name_base}_fallback.html"
                html_fallback_path = os.path.join(file_path, html_fallback_filename)
                fig.write_html(html_fallback_path)
                print(f"✅ HTML fallback saved successfully: {html_fallback_path}")
                return True, html_fallback_path, "HTML (Fallback)"
            except Exception as html_e:
                print(f"❌ Failed to save HTML fallback: {html_e}")
                print(f"🔍 Full traceback for HTML fallback failure: {traceback.format_exc()}")

    return False, None, None


def test_kaleido_compatibility():
    """Test if kaleido is working properly with current setup."""
    try:
        import plotly.graph_objects as go
        
        # Create a simple test figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3], name="test"))
        fig.update_layout(title="Test Chart")
        
        test_dir = "test_output"
        
        # Test various formats
        formats_to_test = ["png", "svg", "jpeg", "pdf", "webp", "html"]
        for fmt in formats_to_test:
            print(f"\n--- Testing {fmt.upper()} ---")
            success, path, format_used = save_chart_robust(
                fig, 
                test_dir, 
                f"kaleido_test_{fmt}", 
                width=600, 
                height=400, 
                scale=1.0,  # Use float for testing
                file_format=fmt
            )
            
            if success:
                print(f"✅ Test save successful for {fmt.upper()}! Path: {path}, Format Used: {format_used}")
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                        print(f"🗑️ Cleaned up test file: {path}")
                except OSError as e:
                    print(f"⚠️ Could not remove test file {path}: {e}")
            else:
                print(f"❌ Test save FAILED for {fmt.upper()}.")
        
        # Clean up test directory if empty
        try:
            if os.path.exists(test_dir) and not os.listdir(test_dir):
                os.rmdir(test_dir)
                print(f"🗑️ Cleaned up test directory: {test_dir}")
        except OSError as e:
            print(f"⚠️ Could not remove test directory {test_dir}: {e}")

    except ImportError:
        print("❌ Plotly not installed, cannot run compatibility test.")
    except Exception as e:
        print(f"❌ An error occurred during Kaleido compatibility test: {e}")
        print(f"🔍 Full traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    print("Running chart_saver.py tests...")
    test_kaleido_compatibility()
