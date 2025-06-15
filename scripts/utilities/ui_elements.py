"""
Streamlit UI Elements for Chart Customization
=============================================

Provides a reusable function to create Streamlit input widgets
for customizing chart saving parameters.

Author: Dashboard Iniciativas LULC
Date: 2025
"""
import streamlit as st

def get_chart_save_params(default_filename="chart", key_prefix="") -> tuple[str, str, int, int, float, bool]:
    """
    Creates Streamlit input widgets for chart saving customization.

    Args:
        default_filename (str): Default base filename for the chart.
        key_prefix (str): A prefix to ensure unique keys for Streamlit widgets
                          if this function is called multiple times on the same page.
    
    Returns:
        tuple: (filename, file_format, width, height, scale, save_button_pressed)
    """
    with st.expander("Customize Chart Download", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            filename = st.text_input(
                "Filename (without extension)", 
                value=default_filename,
                key=f"{key_prefix}_filename"
            )
            file_format = st.selectbox(
                "Format",
                options=["PNG", "SVG", "PDF", "JPEG", "WebP", "HTML"],
                index=0,  # Default to PNG
                key=f"{key_prefix}_format"
            )
        with col2:
            width = st.number_input(
                "Width (pixels)", 
                min_value=100, 
                value=1200, 
                step=50,
                key=f"{key_prefix}_width"
            )
            height = st.number_input(
                "Height (pixels)", 
                min_value=100, 
                value=800, 
                step=50,
                key=f"{key_prefix}_height"
            )
        
        scale = st.number_input(
            "Scale Factor (affects DPI for PNG/JPEG/WebP)",
            min_value=0.1,
            max_value=10.0,
            value=2.0,
            step=0.1,
            key=f"{key_prefix}_scale",
            help="Increase for higher resolution/DPI in raster formats (PNG, JPEG, WebP). E.g., scale=2 with 1200px width is ~2400px effective resolution."
        )
        
        save_button_pressed = st.button(
            "Download Chart with Custom Settings", 
            key=f"{key_prefix}_save_button"
        )
        
    return filename, file_format.lower(), width, height, scale, save_button_pressed
