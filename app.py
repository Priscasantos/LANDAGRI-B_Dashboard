import streamlit as st
from streamlit_option_menu import option_menu
import os
import warnings
import sys
from pathlib import Path

# Adicionar diretório scripts ao path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "scripts"))

# Import atualizado usando o wrapper
try:
    from scripts.data_generation.data_wrapper import load_data
except ImportError:
    try:
        from scripts.data_generation.lulc_data_engine import load_data
    except ImportError:
        st.error("❌ Error importing data loading functions. Please check module structure.")
        st.stop()

# Set environment variable to disable PyArrow optimization
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# Suppress warnings to clean up output
warnings.filterwarnings("ignore")

# Cache dos dados principais para melhor performance

def load_cached_data():
    """Carrega e cache os dados principais do dashboard"""
    return load_data()

# Configuração da página com otimizações de performance
st.set_page_config(
    page_title="LULC Dashboard", 
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="expanded",
    # Otimizações de performance
    menu_items={
        'Report a bug': None,
        'Get Help': None,
        'About': None
    }
)

# CSS customizado para fontes e layout moderno
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, .main .block-container {
        font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif !important;
        font-size: 16px;
        line-height: 1.7;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    .css-1d391kg, .css-1rs6os, .css-17eq0hr {
        display: none !important;
    }
    .main > div:first-child {
        padding-top: 1rem;
    }
    .stSidebar {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        border-right: 3px solid #60a5fa;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    .stSidebar .element-container:first-child {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
    }
    .stSidebar * {
        color: #e2e8f0 !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #60a5fa !important;
        font-weight: 600;
    }
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    .nav-link {
        background: rgba(148, 163, 184, 0.1) !important;
        margin-bottom: 0.3rem !important;
        border-radius: 0.7rem !important;
        transition: all 0.3s ease !important;
        border-left: 3px solid transparent !important;
    }
    .nav-link:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        border-left: 3px solid #60a5fa !important;
        transform: translateX(2px) !important;
    }
    .nav-link-selected {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-left: 3px solid #60a5fa !important;
        box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3) !important;
    }
    .nav-link i {
        margin-right: 0.5rem;
        width: 20px;
        text-align: center;
    }
    @media (max-width: 900px) {
        html, body, .main .block-container {
            font-size: 15px;
        }
        .stSidebar {
            font-size: 14px;
        }
    }
    @media (max-width: 600px) {
        html, body, .main .block-container {
            font-size: 14px;
        }
        .stSidebar {
            font-size: 13px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# Hide Streamlit's default sidebar navigation (multipage menu)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar customizado com nova estrutura ---
with st.sidebar:
    selected = option_menu(
        menu_title="🛰️ LULC Dashboard",        options=[
            "Overview",
            "Comparative Analysis", 
            "Detailed Analysis"
        ],
        icons=["globe-americas", "bar-chart-steps", "layers"],
        menu_icon="satellite",
        default_index=0,
        styles={
            "container": {"padding": "0.5rem", "background-color": "transparent"},
            "icon": {"color": "#60a5fa", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0.2rem 0",
                "padding": "0.8rem 1rem",
                "border-radius": "0.7rem",
                "font-family": "Inter, Roboto, Segoe UI, Arial, sans-serif",
                "background": "rgba(148, 163, 184, 0.1)",
                "border-left": "3px solid transparent",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                "color": "#ffffff",
                "font-weight": "600",
                "border-left": "3px solid #60a5fa",
                "box-shadow": "0 3px 10px rgba(59, 130, 246, 0.3)"
            },
            "menu-title": {
                "color": "#60a5fa",
                "font-weight": "700", 
                "font-size": "20px",
                "text-align": "center",
                "margin-bottom": "1rem",
                "padding": "0.5rem",
                "background": "rgba(59, 130, 246, 0.1)",
                "border-radius": "0.5rem"
            }
        }
    )
    
    # Removido: filtro de subcomparação, agora é feito apenas na página principal

# --- Page navigation with new structure ---
if selected == "Overview":
    import dashboard.detailed.overview as overview
    overview.run()
    
elif selected == "Comparative Analysis":
    st.markdown("---")
    st.markdown("### 📊 Comparative Analysis")
    # Removed: sub_selected = st.radio(...)
    # The comparison type is defined only by the sidebar menu, no need for extra filter on the page
    
    import dashboard.comparisons.comparison as comparison
    comparison.run()  # For now use the same page, later can create specific one
    
elif selected == "Detailed Analysis":
    import dashboard.detailed.detailed as detailed
    detailed.run()
