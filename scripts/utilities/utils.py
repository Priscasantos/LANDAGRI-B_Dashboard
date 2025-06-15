import streamlit as st
import io

def safe_download_image(fig, filename, button_text="⬇️ Download Chart (PNG)", width=None, height=None):
    """Safely export a Plotly figure as PNG with fallback instructions and custom dimensions."""
    try:
        buf = io.BytesIO()
        fig.write_image(buf, format="png", width=width, height=height)
        st.download_button(button_text, data=buf.getvalue(), file_name=filename, mime="image/png")
        return True
    except Exception:
        st.warning("⚠️ **Error generating PNG automatically**")
        st.info("💡 **Alternatives to save the chart:**\n"
               "1. Click the 📷 (camera) icon in the top right corner of the chart\n"
               "2. Or right-click on the chart → 'Save image as'\n"
               "3. Or use the chart options menu (⋯) → 'Download plot as PNG'")
        return False
