import os
import sys
import warnings
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# Add paths for imports
current_dir = Path(__file__).parent
root_path = str(current_dir)
scripts_path = str(current_dir / "scripts")

for path in [root_path, scripts_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import modular styles and renderer
from styles import MenuStyles, DashboardStyles, MenuRenderer

# Initialize modern themes system (optional)
try:
    from scripts.utilities.modern_themes import ModernThemes

    ModernThemes.setup_modern_theme()
except Exception:
    pass

def render():
    # Robust local module loader to avoid import cache/key conflicts in some environments (e.g., Streamlit reload)
    def _load_dashboard_module(module_name: str):
        import importlib
        import importlib.util
        from types import ModuleType

        # Ensure project root is first in path
        if root_path not in sys.path:
            sys.path.insert(0, root_path)

        # If a conflicting 'dashboard' exists in sys.modules that's not our package, drop it
        dash_mod = sys.modules.get('dashboard')
        if dash_mod is not None and not hasattr(dash_mod, '__path__'):
            sys.modules.pop('dashboard', None)

        try:
            return importlib.import_module(f"dashboard.{module_name}")
        except Exception:
            # Fallback: load directly from file path
            mod_path = current_dir / 'dashboard' / f'{module_name}.py'
            if not mod_path.exists():
                raise
            spec = importlib.util.spec_from_file_location(f'_local_dashboard_{module_name}', str(mod_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                return mod
            raise
    # Import the JSON interpreter inside render to avoid Streamlit UI at import time
    try:
        from scripts.utilities.json_interpreter import interpret_initiatives_metadata
    except Exception as e:
        st.error(f"❌ Error importing JSON interpreter: {e}")
        st.stop()

    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    warnings.filterwarnings("ignore")

    # Cache main data for better performance
    @st.cache_data(ttl=300)
    def load_cached_data():
        try:
            metadata_file_path = current_dir / "data" / "json" / "initiatives_metadata.jsonc"
            df = interpret_initiatives_metadata(metadata_file_path)
            if df is None or df.empty:
                return pd.DataFrame()
            return df
        except Exception:
            return pd.DataFrame()

    # Page config and styles
    st.set_page_config(page_title="LANDAGRI-B Dashboard", layout="wide", page_icon="🌍", initial_sidebar_state="expanded")

    # Apply modular styles
    st.markdown(DashboardStyles.get_main_container_styles(), unsafe_allow_html=True)
    st.markdown(DashboardStyles.get_header_styles(), unsafe_allow_html=True)
    st.markdown(DashboardStyles.get_card_styles(), unsafe_allow_html=True)
    st.markdown(DashboardStyles.get_responsive_styles(), unsafe_allow_html=True)
    st.markdown(DashboardStyles.get_sidebar_styles(), unsafe_allow_html=True)
    st.markdown(MenuStyles.get_option_menu_styles(), unsafe_allow_html=True)
    st.markdown(MenuStyles.get_breadcrumb_styles(), unsafe_allow_html=True)

    # --- Load and cache data early ---
    if "df_interpreted" not in st.session_state or st.session_state.df_interpreted is None:
        df_loaded = load_cached_data()
        st.session_state.df_interpreted = df_loaded
        # Load raw metadata if available
        try:
            from scripts.utilities.json_interpreter import _load_jsonc_file

            metadata_file_path = current_dir / "data" / "json" / "initiatives_metadata.jsonc"
            st.session_state.metadata = _load_jsonc_file(metadata_file_path)
        except Exception:
            st.session_state.metadata = {}


    # --- Sidebar ---
    with st.sidebar:
        # Simplified menu structure without emoji keys; icons are optional
        MENU_STRUCTURE = {
            "Overview": {"pages": ["Dashboard Overview"], "page_icons": ["binoculars"]},
            "Initiative Analysis": {"pages": ["Temporal Analysis", "Comparative Analysis", "Detailed Analysis"], "page_icons": ["stopwatch-fill", "stack", "zoom-in"]},
            "Agricultural Analysis": {"pages": ["Agriculture Overview", "Crop Calendar", "Agriculture Availability"], "page_icons": ["database-fill-check", "calendar4-week", "columns-gap"]},
            "About": {"pages": ["About the Dashboard"], "page_icons": ["info-circle"]},
        }

        menu_config = {"menu_width": 280, "spacing": 12, "border_radius": 10, "font_size": 15, "font_family": "Inter, Arial, sans-serif"}
        palette = ["#3b82f6", "#1d4ed8", "#60a5fa", "#93c5fd", "#dbeafe"]

        # Use the unified menu renderer; it handles styles and breadcrumb internally
        MenuRenderer.render_menu(palette, menu_config, MENU_STRUCTURE, sync_url=True, show_breadcrumb=True)

        # Ensure session defaults are present
        if 'current_category' not in st.session_state:
            st.session_state.current_category = list(MENU_STRUCTURE.keys())[0]
            st.session_state.current_page = str(MENU_STRUCTURE[st.session_state.current_category]['pages'][0])

    # --- Read-only query params handling: allow URLs to set initial page when app loads ---
    # We only use query params here to set the initial navigation state; the menu renderer
    # itself will write back query params when users interact with the UI.
    query_params = st.query_params
    if query_params:
        q_cat = query_params.get('category', [None])[0] if 'category' in query_params else None
        q_page = query_params.get('page', [None])[0] if 'page' in query_params else None
        if q_cat:
            from urllib.parse import unquote_plus
            decoded_cat = unquote_plus(q_cat)
            if decoded_cat in MENU_STRUCTURE:
                st.session_state.current_category = decoded_cat
                # Validate provided page
                if q_page:
                    decoded_page = unquote_plus(q_page)
                    pages = []
                    data = MENU_STRUCTURE.get(decoded_cat, {})
                    if isinstance(data, dict) and 'pages' in data:
                        pages = data['pages']
                    elif isinstance(data, list):
                        pages = data
                    if decoded_page in pages:
                        st.session_state.current_page = decoded_page
                    else:
                        # Fallback to the first available page without numeric indexing (type-safe)
                        try:
                            first_page = next(iter(pages))
                            if first_page:
                                st.session_state.current_page = str(first_page)
                        except Exception:
                            pass


    # --- Page navigation ---
    current_category = st.session_state.get('current_category')
    current_page = st.session_state.get('current_page')

    if current_category == "Overview":
        if current_page == "Dashboard Overview":
            overview = _load_dashboard_module('overview')
            overview.run()

    elif current_category == "Initiative Analysis":
        if current_page in ["Temporal Analysis", "Comparative Analysis", "Detailed Analysis"]:
            initiative_analysis = _load_dashboard_module('initiative_analysis')
            initiative_analysis.run()

    elif current_category == "Agricultural Analysis":
        if current_page in ["Agriculture Overview", "Crop Calendar", "Agriculture Availability"]:
            agricultural_analysis = _load_dashboard_module('agricultural_analysis')
            agricultural_analysis.run()

    elif current_category == "About":
        if current_page == "About the Dashboard":
            about = _load_dashboard_module('about')
            about.run()


if __name__ == "__main__":
    render()
