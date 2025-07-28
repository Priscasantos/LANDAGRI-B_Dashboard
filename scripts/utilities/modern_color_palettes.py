"""
Modern Dashboard Color Palettes
===============================

Paletas de cores modernas para dashboards baseadas nas melhores práticas de 2025.
Inclui suporte para modo escuro e light, com acessibilidade WCAG 2.1.

Author: Dashboard Iniciativas LULC
Date: 2025-07-28
"""

# Paleta Principal - Modo Escuro (Recomendado)
DARK_THEME = {
    # Cores de fundo
    "bg_primary": "#0f172a",      # Slate 900 - Fundo principal
    "bg_secondary": "#1e293b",    # Slate 800 - Cards e componentes
    "bg_tertiary": "#334155",     # Slate 700 - Hover states
    "bg_accent": "#475569",       # Slate 600 - Borders sutis
    
    # Cores de texto
    "text_primary": "#f8fafc",    # Slate 50 - Texto principal
    "text_secondary": "#e2e8f0",  # Slate 200 - Texto secundário
    "text_muted": "#94a3b8",      # Slate 400 - Texto desabilitado
    "text_accent": "#64748b",     # Slate 500 - Legendas
    
    # Cores de destaque
    "accent_primary": "#3b82f6",  # Blue 500 - Principal
    "accent_secondary": "#06b6d4", # Cyan 500 - Secundário
    "accent_tertiary": "#8b5cf6", # Violet 500 - Terciário
    
    # Cores semânticas
    "success": "#10b981",         # Emerald 500
    "warning": "#f59e0b",         # Amber 500
    "error": "#ef4444",           # Red 500
    "info": "#3b82f6",            # Blue 500
    
    # Gradientes
    "gradient_primary": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
    "gradient_secondary": "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
    "gradient_accent": "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)",
}

# Paleta Alternativa - Modo Light (Opcional)
LIGHT_THEME = {
    # Cores de fundo
    "bg_primary": "#ffffff",      # Branco puro
    "bg_secondary": "#f8fafc",    # Slate 50 - Cards
    "bg_tertiary": "#f1f5f9",     # Slate 100 - Hover
    "bg_accent": "#e2e8f0",       # Slate 200 - Borders
    
    # Cores de texto
    "text_primary": "#0f172a",    # Slate 900 - Texto principal
    "text_secondary": "#334155",  # Slate 700 - Texto secundário
    "text_muted": "#64748b",      # Slate 500 - Texto desabilitado
    "text_accent": "#94a3b8",     # Slate 400 - Legendas
    
    # Cores de destaque (mais suaves para fundo claro)
    "accent_primary": "#2563eb",  # Blue 600
    "accent_secondary": "#0891b2", # Cyan 600
    "accent_tertiary": "#7c3aed", # Violet 600
    
    # Cores semânticas
    "success": "#059669",         # Emerald 600
    "warning": "#d97706",         # Amber 600
    "error": "#dc2626",           # Red 600
    "info": "#2563eb",            # Blue 600
    
    # Gradientes
    "gradient_primary": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
    "gradient_secondary": "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)",
    "gradient_accent": "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
}

# Paletas para Visualizações de Dados
DATA_VIZ_COLORS = {
    # Paleta categórica (até 10 categorias)
    "categorical": [
        "#3b82f6",  # Blue 500
        "#10b981",  # Emerald 500
        "#f59e0b",  # Amber 500
        "#ef4444",  # Red 500
        "#8b5cf6",  # Violet 500
        "#06b6d4",  # Cyan 500
        "#84cc16",  # Lime 500
        "#f97316",  # Orange 500
        "#ec4899",  # Pink 500
        "#6366f1",  # Indigo 500
    ],
    
    # Paleta sequencial (dados contínuos)
    "sequential_blue": [
        "#eff6ff",  # Blue 50
        "#dbeafe",  # Blue 100
        "#bfdbfe",  # Blue 200
        "#93c5fd",  # Blue 300
        "#60a5fa",  # Blue 400
        "#3b82f6",  # Blue 500
        "#2563eb",  # Blue 600
        "#1d4ed8",  # Blue 700
        "#1e40af",  # Blue 800
        "#1e3a8a",  # Blue 900
    ],
    
    # Paleta divergente (dados com ponto neutro)
    "divergent": [
        "#dc2626",  # Red 600
        "#ef4444",  # Red 500
        "#f87171",  # Red 400
        "#fca5a5",  # Red 300
        "#fed7d7",  # Red 200
        "#f3f4f6",  # Gray 100 - Neutro
        "#ddd6fe",  # Violet 200
        "#c4b5fd",  # Violet 300
        "#a78bfa",  # Violet 400
        "#8b5cf6",  # Violet 500
        "#7c3aed",  # Violet 600
    ],
}

# Configurações de Acessibilidade
ACCESSIBILITY = {
    "min_contrast_ratio": 4.5,     # WCAG AA para texto normal
    "min_contrast_large": 3.0,     # WCAG AA para texto grande
    "colorblind_safe": True,       # Cores distinguíveis para daltônicos
    "focus_ring": "#3b82f6",       # Cor do foco para navegação por teclado
    "selection": "#3b82f640",      # Cor de seleção (com transparência)
}

def get_theme_colors(theme="dark"):
    """
    Retorna a paleta de cores para o tema especificado.
    
    Args:
        theme: "dark" ou "light"
        
    Returns:
        dict: Paleta de cores
    """
    return DARK_THEME if theme == "dark" else LIGHT_THEME

def get_data_viz_palette(type="categorical", count=None):
    """
    Retorna uma paleta para visualização de dados.
    
    Args:
        type: "categorical", "sequential_blue", ou "divergent"
        count: Número de cores necessárias (para categórica)
        
    Returns:
        list: Lista de cores hexadecimais
    """
    palette = DATA_VIZ_COLORS.get(type, DATA_VIZ_COLORS["categorical"])
    
    if count and type == "categorical":
        # Repetir cores se necessário
        while len(palette) < count:
            palette.extend(palette)
        return palette[:count]
    
    return palette

# CSS para Streamlit
STREAMLIT_CSS = f"""
<style>
/* Tema escuro global */
.stApp {{
    background: {DARK_THEME['bg_primary']};
    color: {DARK_THEME['text_primary']};
}}

/* Sidebar */
.css-1d391kg {{
    background: {DARK_THEME['bg_secondary']};
}}

/* Métricas */
.metric-container {{
    background: {DARK_THEME['bg_secondary']};
    border: 1px solid {DARK_THEME['bg_accent']};
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}}

/* Cards */
.card {{
    background: {DARK_THEME['bg_secondary']};
    border: 1px solid {DARK_THEME['bg_accent']};
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}}

/* Botões */
.stButton > button {{
    background: {DARK_THEME['accent_primary']};
    color: {DARK_THEME['text_primary']};
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}}

.stButton > button:hover {{
    background: {DARK_THEME['accent_secondary']};
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}}

/* Navegação breadcrumb melhorada */
.breadcrumb {{
    background: {DARK_THEME['bg_secondary']};
    border: 1px solid {DARK_THEME['bg_accent']};
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: {DARK_THEME['text_secondary']};
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.breadcrumb .current {{
    color: {DARK_THEME['accent_primary']};
    font-weight: 600;
}}

/* Melhorar posição do menu */
.menu-indicator {{
    position: fixed;
    top: 20px;
    left: 20px;
    background: {DARK_THEME['accent_primary']};
    color: {DARK_THEME['text_primary']};
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}}
</style>
"""
