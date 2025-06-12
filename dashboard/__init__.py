"""
Módulo de gráficos para o dashboard LULC.
Configura imports e utilitários comuns para todos os submódulos.
"""

import sys
from pathlib import Path

def setup_scripts_path():
    """Configura o path para importar módulos dos scripts"""
    current_dir = Path(__file__).parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    return scripts_path

def safe_import_module(module_name, function_names=None):
    """
    Importa módulos de forma segura com tratamento de erros
    
    Args:
        module_name: Nome do módulo a importar
        function_names: Lista de funções específicas para importar
    
    Returns:
        Módulo ou dicionário com funções importadas
    """
    setup_scripts_path()
    
    try:
        module = __import__(module_name)
        
        if function_names:
            functions = {}
            for func_name in function_names:
                if hasattr(module, func_name):
                    functions[func_name] = getattr(module, func_name)
                else:
                    functions[func_name] = lambda *args, **kwargs: None  # Função placeholder
            return functions
        
        return module
    
    except ImportError as e:
        print(f"Erro ao importar {module_name}: {e}")
        
        if function_names:
            # Retorna funções placeholder
            return {name: lambda *args, **kwargs: None for name in function_names}
        
        return None

# Funções auxiliares comuns
def safe_download_placeholder(fig, filename, button_text):
    """Placeholder para safe_download_image quando não disponível"""
    import streamlit as st
    st.info(f"Download disponível: {filename}")

# Configurar path automaticamente quando o módulo é importado
setup_scripts_path()
