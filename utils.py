import streamlit as st
import io

def safe_download_image(fig, filename, button_text="⬇️ Baixar Gráfico (PNG)"):
    """Safely export a Plotly figure as PNG with fallback instructions"""
    try:
        buf = io.BytesIO()
        fig.write_image(buf, format="png")
        st.download_button(button_text, data=buf.getvalue(), file_name=filename, mime="image/png")
        return True
    except Exception as e:
        st.warning("⚠️ **Erro ao gerar PNG automaticamente**")
        st.info("💡 **Alternativas para salvar o gráfico:**\n"
               "1. Clique no ícone 📷 (câmera) no canto superior direito do gráfico\n"
               "2. Ou clique com botão direito no gráfico → 'Salvar imagem como'\n"
               "3. Ou use o menu de opções do gráfico (⋯) → 'Download plot as PNG'")
        return False
