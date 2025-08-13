"""
Streamlit UI Elements for Chart Customization
=============================================

Provides a reusable function to create Streamlit input widgets
for customizing chart saving parameters.

Author: LANDAGRI-B Project Team 
Date: 2025
"""

import streamlit as st


def setup_download_form(fig, default_filename="chart", key_prefix=""):
    """
    Creates Streamlit input widgets for chart download customization and
    provides a download button.

    Args:
        fig (plotly.graph_objects.Figure): The Plotly figure to download.
        default_filename (str): Default base filename for the chart.
        key_prefix (str): A prefix to ensure unique keys for Streamlit widgets
                          if this function is called multiple times.
    """
    with st.expander("Customize and Download Chart", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            filename = st.text_input(
                "Filename (without extension)",
                value=default_filename,
                key=f"{key_prefix}_filename",
            )
            file_format_display = st.selectbox(
                "Format",
                options=["PNG", "SVG", "PDF", "JPEG", "WebP", "HTML"],
                index=0,  # Default to PNG
                key=f"{key_prefix}_format_display",
            )
            file_format = file_format_display.lower()  # Processed format

        with col2:
            width = st.number_input(
                "Width (pixels or points)",
                min_value=100,
                value=1200,
                step=50,
                key=f"{key_prefix}_width",
                help="For PNG/JPEG/WebP/HTML: pixels. For SVG/PDF: can be points or used to define viewbox.",
            )
            height = st.number_input(
                "Height (pixels or points)",
                min_value=100,
                value=800,
                step=50,
                key=f"{key_prefix}_height",
                help="For PNG/JPEG/WebP/HTML: pixels. For SVG/PDF: can be points or used to define viewbox.",
            )  # DPI/Scale selection
        dpi_options = {
            "Web (72 DPI)": 1.0,
            "Standard Print (150 DPI)": 150 / 72,
            "High Quality Print (300 DPI)": 300 / 72,
            "Ultra High Quality Print (600 DPI)": 600 / 72,
        }
        selected_dpi_label = "Standard Print (150 DPI)"  # Default selection
        scale = dpi_options[selected_dpi_label]  # Default scale

        if file_format in ["png", "jpeg", "webp"]:
            selected_dpi_label = st.selectbox(
                "Resolution (DPI) for PNG/JPEG/WebP",
                options=list(dpi_options.keys()),
                index=1,  # Default to 150 DPI
                key=f"{key_prefix}_dpi_select",
                help="Select a standard DPI. This will adjust the scale factor.",
            )
            scale = dpi_options[selected_dpi_label]

            # Display the calculated scale factor for transparency, but make it read-only or informative
            st.info(f"Selected DPI sets scale factor to: {scale:.2f}")
            # Optionally, allow custom scale if needed, but DPI selection is more user-friendly
            # scale = st.number_input(
            #     "Custom Scale Factor (Overrides DPI selection if changed)",
            #     min_value=0.1,
            #     max_value=10.0,
            #     value=scale,
            #     step=0.1,
            #     key=f"{key_prefix}_scale_custom",
            #     help="Adjust for custom resolution. Default is set by DPI selection."
            # )
        else:
            # For vector formats or HTML, scale is typically 1 or not directly applicable in the same way
            scale = 1.0
            st.info(
                "Scale/DPI is primarily for raster image formats (PNG, JPEG, WebP)."
            )

        file_content = None
        mime_type = None
        error_message = None

        if fig:
            try:
                if file_format == "html":
                    file_content = fig.to_html().encode()
                    mime_type = "text/html"
                elif file_format == "svg":
                    # For SVG, width/height can sometimes be omitted to use figure's layout if preferred
                    file_content = fig.to_image(
                        format=file_format, width=width, height=height
                    )
                    mime_type = "image/svg+xml"
                elif file_format == "pdf":
                    file_content = fig.to_image(
                        format=file_format, width=width, height=height
                    )
                    mime_type = "application/pdf"
                elif file_format in ["png", "jpeg", "webp"]:
                    file_content = fig.to_image(
                        format=file_format, width=width, height=height, scale=scale
                    )
                    mime_type = f"image/{file_format}"
                else:
                    error_message = f"Unsupported file format: {file_format_display}"

            except Exception as e:
                error_message = f"Error preparing chart for download: {str(e)}"
                # Attempt to provide more specific advice for common issues
                if "plotly-orca" in str(e) or "kaleido" in str(e):
                    error_message += " This might be due to a missing or misconfigured image export engine like Kaleido or Orca."
                st.error(error_message)

        if error_message:
            st.warning(
                f"Could not prepare chart for download as {file_format_display}. {error_message}"
            )

        # The download button should be present to allow retrying with different settings
        # or if the figure generation itself is the issue (though 'fig' check handles that).
        # We disable it if file_content could not be generated.
        st.download_button(
            label=f"Download as {file_format_display}",
            data=(
                file_content if file_content else b""
            ),  # Must provide some data, even if empty
            file_name=(
                f"{filename}.{file_format}"
                if filename and file_format
                else "chart.unknown"
            ),
            mime=mime_type,
            key=f"{key_prefix}_download_button",
            disabled=(file_content is None),  # Disable if content generation failed
        )
