"""
Test Overview Component
======================

Teste para verificar o novo componente de overview agrícola.
Página única sem abas conforme solicitado.
"""

import streamlit as st
import sys
import os

# Adicionar o caminho do dashboard
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.components.agricultural_analysis.agriculture_overview.agricultural_overview import render_agricultural_overview

def main():
    """Função principal para testar o overview."""
    
    st.set_page_config(
        page_title="Teste Overview Agrícola",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 Teste - Overview Agrícola")
    st.markdown("*Teste do novo componente de overview - página única sem abas*")
    
    st.markdown("---")
    
    # Renderizar o overview
    try:
        render_agricultural_overview()
        
        st.markdown("---")
        st.success("✅ Overview renderizado com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro ao renderizar overview: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
