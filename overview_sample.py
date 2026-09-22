"""
overview_sample.py - Interface Designer para LANDAGRI Dashboard

Ferramenta completa para prototipagem de interfaces de dashboard agrícola.
Permite testar diferentes tipos de menu, paletas de cores, layouts responsivos,
tipografia e exportar/importar configurações.

Recursos:
- 12 paletas de cores profissionais (Material, Tailwind, Corporate, Agricultural, etc.)
- 7 tipos de menu (Expanded, Compact, Top, Overlay, Nested, Tabs, Floating)
- Simulação responsiva (Mobile, Tablet, Desktop)
- Controles avançados de layout (espaçamento, border radius, dimensões)
- Configuração de tipografia
- Export/Import de configurações em JSON
- Modo de comparação de layouts

Como usar:
  1. Ative o venv do projeto
  2. Rode: streamlit run overview_sample.py
  3. Use as abas na sidebar para ajustar cores, layout, tipografia e responsividade
  4. Visualize o preview em tempo real
  5. Export/import configurações conforme necessário

Desenvolvido para o projeto LANDAGRI-B Dashboard
"""
import streamlit as st
import plotly.express as px
import pandas as pd

# Import our new modular styles system
from styles import MenuStyles, DashboardStyles, MenuRenderer




def sample_data():
    df = pd.DataFrame({
        "category": ["A", "B", "C", "D"],
        "value": [10, 23, 17, 9]
    })
    return df


PALETTES = {
    "Classic": ["#0b5a8a", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
    "Soft": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#f7f7f7"],
    "HighContrast": ["#0d0d0d", "#ffffff", "#ff6b6b", "#4d96ff", "#ffd93d"],
    "Pastel": ["#a8dadc", "#f1f1f1", "#ffe5d9", "#ffd6e0", "#cdb4db"],
    "Material": ["#1976d2", "#388e3c", "#f57c00", "#d32f2f", "#7b1fa2"],
    "Tailwind": ["#0f172a", "#1e40af", "#059669", "#dc2626", "#7c3aed"],
    "Corporate": ["#1e3a8a", "#374151", "#6b7280", "#d1d5db", "#f3f4f6"],
    "Agricultural": ["#365314", "#84cc16", "#a3a3a3", "#d97706", "#92400e"],
    "Ocean": ["#0c4a6e", "#0284c7", "#06b6d4", "#67e8f9", "#a7f3d0"],
    "Sunset": ["#7c2d12", "#ea580c", "#f97316", "#fbbf24", "#fde047"],
    "Monochrome": ["#000000", "#404040", "#808080", "#c0c0c0", "#ffffff"],
    "Accessibility": ["#000000", "#ffffff", "#0066cc", "#cc0000", "#009900"],
}

ICON_SETS = {
    "Basic": ["home", "bar_chart", "layers", "settings"],
    "Semantic": ["house", "chart-bar", "grid", "cog"],
}

# Estrutura hierárquica de menu para dashboard agrícola
MENU_STRUCTURE = {
    "📊 Dashboard": {
        "icon": "📊",
        "items": ["Overview", "About", "Métricas", "KPIs"]
    },
    "� Initiative Analysis": {
        "icon": "�", 
        "items": ["Temporal Analysis", "Comparative Analysis", "Detailed Analysis", "Reports"]
    },
    "🌾 Agricultural Analysis": {
        "icon": "🌾",
        "items": ["Agriculture Overview", "Crop Calendar", "Agriculture Availability", "Monitoring"]
    },
    "📋 Relatórios": {
        "icon": "📋",
        "items": ["Mensal", "Anual", "Personalizado", "Automático"]
    }
}

# Configurações padrão
DEFAULT_CONFIG = {
    "menu_width": 250,
    "header_height": 60,
    "spacing": 12,
    "border_radius": 8,
    "font_size": 14,
    "font_family": "Arial, sans-serif",
    "screen_size": "Desktop"
}

def generate_css_vars(config):
    """Gera variáveis CSS baseadas na configuração atual."""
    return f"""
    :root {{
        --menu-width: {config['menu_width']}px;
        --header-height: {config['header_height']}px;
        --spacing: {config['spacing']}px;
        --border-radius: {config['border_radius']}px;
        --font-size: {config['font_size']}px;
        --font-family: {config['font_family']};
    }}
    """


def render_menu(menu_type: str, palette, icon_set, config):
    """Renderiza diferentes estilos de menu baseado em menu_type com configurações personalizadas."""
    bg = palette[0]
    fg = "#ffffff" if _is_dark(bg) else "#111111"
    
    # Aplicar CSS personalizado
    css_vars = generate_css_vars(config)
    st.markdown(f"<style>{css_vars}</style>", unsafe_allow_html=True)

    if menu_type == "Expanded":
        # Vertical expanded - usando estrutura hierárquica
        html = f"<div style='padding:{config['spacing']}px; background:{bg}; color:{fg}; width:{config['menu_width']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>"
        html += f"<h3 style='margin:0 0 {config['spacing']}px 0; font-size:{config['font_size'] + 4}px'>🛰️ LANDAGRI-B</h3>"
        
        for category, data in MENU_STRUCTURE.items():
            html += f"<div style='margin:{config['spacing']//2}px 0; padding:{config['spacing']//2}px {config['spacing']}px; border-radius:{config['border_radius']}px; background: rgba(255,255,255,0.03)'><strong style='color:{fg}'>{category}</strong></div>"
            for item in data["items"][:2]:  # Mostra apenas 2 subitens por categoria no modo expandido
                html += f"<div style='margin-left:{config['spacing']*2}px; margin:{config['spacing']//4}px 0; color:rgba(255,255,255,0.7); font-size:{config['font_size']-2}px'>• {item}</div>"
        
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    elif menu_type == "Compact":
        # Icon-only compact menu usando primeiras letras das categorias
        html = f"<div style='padding:{config['spacing']}px; background:{bg}; color:{fg}; display:flex; flex-direction:column; gap:{config['spacing']}px; align-items:center; width:80px'>"
        
        for category in MENU_STRUCTURE.keys():
            # Extrai o emoji ou primeira letra para o ícone
            icon = category.split()[0] if "🔎" in category or "📊" in category or "🌾" in category or "📋" in category or "⚙️" in category else category[0].upper()
            html += f"<div title='{category}' style='width:40px; height:40px; background: rgba(255,255,255,0.04); border-radius:{config['border_radius']}px; display:flex; align-items:center; justify-content:center; font-size:{config['font_size']}px'>{icon}</div>"
        
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    elif menu_type == "Top":
        # Top navigation usando categorias principais
        html = f"<div style='width:100%; padding:{config['spacing']}px; background:{palette[1]}; color:#fff; display:flex; gap:{config['spacing'] * 2}px; align-items:center; height:{config['header_height']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>"
        
        for category in MENU_STRUCTURE.keys():
            html += f"<div style='padding:{config['spacing']//2}px {config['spacing']}px; border-radius:{config['border_radius']}px'>{category}</div>"
        
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    elif menu_type == "Overlay":
        # Simulate drawer / overlay usando estrutura hierárquica
        html = f"<div style='padding:{config['spacing']}px; background:transparent'>"
        html += f"<div style='width:{config['menu_width']}px; box-shadow:0 6px 18px rgba(0,0,0,0.12); padding:{config['spacing']}px; background:{bg}; color:{fg}; border-radius:{config['border_radius']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>"
        html += f"<h4 style='margin:0 0 {config['spacing']}px 0'>🛰️ LANDAGRI Drawer</h4>"
        
        for category, data in MENU_STRUCTURE.items():
            html += f"<div style='margin:{config['spacing']//2}px 0; padding:{config['spacing']//2}px {config['spacing']}px; border-radius:{config['border_radius']}px; background: rgba(255,255,255,0.03)'>{category}</div>"
            # Mostra primeiro subitem como exemplo
            if data["items"]:
                html += f"<div style='margin-left:{config['spacing']*2}px; color:rgba(255,255,255,0.6); font-size:{config['font_size']-2}px'>• {data['items'][0]}</div>"
        
        html += "</div></div>"
        st.markdown(html, unsafe_allow_html=True)

    elif menu_type == "Nested":
        # Grouped/nested menu usando estrutura hierárquica completa
        html = f"<div style='padding:{config['spacing']}px; background:{bg}; color:{fg}; width:{config['menu_width']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>"
        html += f"<h4 style='margin:0 0 {config['spacing']}px 0'>🛰️ LANDAGRI</h4>"
        
        for category, data in MENU_STRUCTURE.items():
            html += f"<div style='margin-bottom:{config['spacing']//2}px'><strong>{category}</strong></div>"
            items_str = "<br>".join([f"- {item}" for item in data["items"]])
            html += f"<div style='margin-left:{config['spacing']}px; margin-bottom:{config['spacing']}px'>{items_str}</div>"
        
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    elif menu_type == "Tabs":
        # Use Streamlit tabs com categorias hierárquicas
        tab_names = [category.split()[-1] if len(category.split()) > 1 else category for category in MENU_STRUCTURE.keys()]
        tabs = st.tabs(tab_names[:3])  # Limita a 3 tabs para não sobrecarregar
        
        for i, (tab, (category, data)) in enumerate(zip(tabs, list(MENU_STRUCTURE.items())[:3])):
            with tab:
                st.write(f"**{category}**")
                for item in data["items"]:
                    st.write(f"• {item}")

    elif menu_type == "Floating":
        # Floating action button simulation
        st.markdown(f"<div style='position:fixed; right:24px; bottom:24px'>\n"
                    f"<div style='width:56px; height:56px; border-radius:50%; background:{palette[2]}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:{config['font_size'] + 6}px'>🛰️</div>\n"
                    f"</div>", unsafe_allow_html=True)

    elif menu_type == "Hierarchical":
        # Menu hierárquico baseado no dashboard principal (visual/funcional)
        render_hierarchical_menu_fancy(palette, config)

    else:
        st.markdown("<div>Menu não suportado</div>", unsafe_allow_html=True)


def render_hierarchical_menu(palette, config):
    """Renderiza um menu hierárquico interativo usando widgets do Streamlit.

    Substitui a versão estática por uma versão que usa `st.expander` e `st.button`.
    Ao clicar em uma sub-página, atualiza `st.session_state['active_page']` com
    o nome da página selecionada para possibilitar navegação/preview.
    """

    # Garantir chave de estado para a página ativa
    if 'active_page' not in st.session_state:
        st.session_state['active_page'] = None

    st.markdown(f"<div style='width:{config['menu_width']}px'>", unsafe_allow_html=True)

    st.markdown(f"### 🛰️ LANDAGRI-B Dashboard", unsafe_allow_html=True)

    # Construir menu interativo com expanders e botões
    for category, data in MENU_STRUCTURE.items():
        with st.expander(f"{category}", expanded=False):
            # Exibir ícone/descrição se disponível
            if data.get('icon'):
                st.write(data['icon'])

            for item in data.get('items', []):
                key = f"menu_select::{category}::{item}"
                # Usar botão pequeno com callback implícito via session_state
                if st.button(item, key=key):
                    st.session_state['active_page'] = item

    st.markdown("</div>", unsafe_allow_html=True)

    # Mostrar a página ativa
    if st.session_state.get('active_page'):
        st.markdown("---")
        st.write(f"**Ativo:** {st.session_state['active_page']}")


def render_hierarchical_menu_fancy(palette, config):
    """Renderiza um menu hierárquico estilizado e funcional usando Streamlit widgets.

    O visual tenta reproduzir o estilo da imagem: cabeçalhos coloridos e botões brancos para
    subitens. Usa CSS injetado e `st.button` dentro de contêineres para capturar cliques.
    """

    # garantir estado
    if 'active_page' not in st.session_state:
        st.session_state['active_page'] = None
    if 'active_category' not in st.session_state:
        st.session_state['active_category'] = list(MENU_STRUCTURE.keys())[0]

    # CSS para estilo similar ao mockup
    css = f"""
    <style>
    .menu-card {{ padding: {config['spacing']}px; width: {config['menu_width']}px; background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,247,250,0.95)); border-radius: {config['border_radius']*1.5}px; box-shadow: 0 8px 30px rgba(15,23,42,0.06); border:1px solid rgba(0,0,0,0.03); }}
    .menu-title-fancy {{ text-align:center; padding:{config['spacing']//1}px; margin-bottom:{config['spacing']}px; font-weight:700; font-size:{config['font_size']+4}px; color:#0f172a }}
    .categories-col {{ display:inline-block; vertical-align:top; width:35%; padding-right:8px; }}
    .subcol {{ display:inline-block; vertical-align:top; width:62%; }}
    .category-btn {{ display:block; text-align:left; padding:{config['spacing']//2}px {config['spacing']}px; margin-bottom:{config['spacing']//2}px; background:{palette[1]}; color:#fff; border-radius:{config['border_radius']//1}px; box-shadow: 0 6px 18px rgba(15,23,42,0.08); border:none; font-weight:600; }}
    .category-btn.inactive {{ background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(250,250,250,0.9)); color:#334155; box-shadow:none; border:1px solid rgba(15,23,42,0.03); }}
    .category-btn.small {{ padding:{config['spacing']//3}px {config['spacing']//1}px; font-size:{config['font_size']}px }}
    .sub-item {{ display:block; margin:6px 0; }}
    .sub-item button {{ background:#fff !important; color:#334155 !important; border-radius:{config['border_radius']//1}px !important; padding:{config['spacing']//2}px {config['spacing']}px !important; width:100% !important; text-align:left !important; box-shadow: 0 2px 8px rgba(15,23,42,0.04) !important; border: none !important; }}
    .sub-item button.active {{ background: {palette[0]} !important; color: #fff !important; box-shadow: 0 8px 24px rgba(15,23,42,0.12) !important; }}
    .divider {{ height:1px; background: linear-gradient(90deg, transparent, rgba(15,23,42,0.04), transparent); margin: {config['spacing']}px 0; border:none; }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    st.markdown(f"<div class='menu-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='menu-title-fancy'>🛰️ LANDAGRI-B<br><small style='color:#475569'>Dashboard</small></div>", unsafe_allow_html=True)

    # construir layout em duas colunas: categorias | subitens
    # usamos st.columns para melhor compatibilidade
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("<div class='categories-col'>", unsafe_allow_html=True)
        for category, data in MENU_STRUCTURE.items():
            cat_key = f"cat::{category}"
            is_active = (st.session_state.get('active_category') == category)
            btn_label = f"{data.get('icon','')} {category}"
            # botões de categoria: estilo diferente se ativo
            if st.button(btn_label, key=cat_key):
                st.session_state['active_category'] = category
            # aplicar estilo in-line via markdown (classe não aplicada por st.button), então re-render abaixo
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='subcol'>", unsafe_allow_html=True)
        active = st.session_state.get('active_category') or (list(MENU_STRUCTURE.keys())[0] if MENU_STRUCTURE else None)
        items = []
        if active and active in MENU_STRUCTURE:
            items = MENU_STRUCTURE[active].get('items', [])

        if not items:
            st.info("Selecione uma categoria à esquerda")
        for item in items:
            key = f"fancy::{active}::{item}"
            is_active_item = (st.session_state.get('active_page') == item)
            # botão do subitem com estilo ativo
            if st.button(item, key=key):
                st.session_state['active_page'] = item
        st.markdown("</div>", unsafe_allow_html=True)

    # divider
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # fim do card
    st.markdown("</div>", unsafe_allow_html=True)

    # mostrar ativo
    if st.session_state.get('active_page'):
        st.markdown("---")
        st.write(f"**Ativo:** {st.session_state['active_page']}")


def _is_dark(hex_color: str) -> bool:
    """Verifica se uma cor hexadecimal é escura baseada na luminância."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return luminance < 128


def render_preview(palette, icon_set, menu_style, config, compact=False):
    # Layout com colunas: sidebar (simulada) e conteúdo
    # se o menu_style for Top, renderiza o menu no topo e usa um container para o conteúdo
    if menu_style == "Top":
        render_menu(menu_style, palette, icon_set, config)
        right_col = st.container()
    else:
        left_col, right_col = st.columns([1, 4], gap="small")
        with left_col:
            render_menu(menu_style, palette, icon_set, config)

    with right_col:
        # header
        st.markdown(f"<div style='display:flex; align-items:center; gap:{config['spacing']}px; font-family:{config['font_family']}; font-size:{config['font_size']}px'>\n"
                    f"<div style='width:56px; height:56px; background:{palette[1]}; border-radius:{config['border_radius']}px'></div>\n"
                    f"<div><h2 style='margin:0'>Dashboard preview</h2><div style='color: #666'>Paleta: {palette_name_from_list(palette)}</div></div>\n"
                    f"</div>", unsafe_allow_html=True)

        if not compact:
            st.write("\n")

            # metric cards
            c1, c2, c3 = st.columns(3)
            colors = palette
            c1.metric("Yield", "12 t/ha", delta="+4%")
            c2.metric("Área", "1,234 ha", delta="-2%")
            c3.metric("Produtividade", "8.7", delta="+1%")

            # chart
            df = sample_data()
            fig = px.bar(df, x="category", y="value", color="category", color_discrete_sequence=palette)
            st.plotly_chart(fig, use_container_width=True)

            # sample buttons
            st.button("Ação primária")
            colors = palette
            st.markdown(f"<div style='display:flex; gap:{config['spacing']}px; margin-top:{config['spacing']}px'>\n"
                        f"<button style='background:{colors[2]}; border:none; color:#fff; padding:{config['spacing']//2}px {config['spacing']}px; border-radius:{config['border_radius']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>Primary</button>\n"
                        f"<button style='background:transparent; border:1px solid {colors[0]}; color:{colors[0]}; padding:{config['spacing']//2}px {config['spacing']}px; border-radius:{config['border_radius']}px; font-size:{config['font_size']}px; font-family:{config['font_family']}'>Secondary</button>\n"
                        f"</div>", unsafe_allow_html=True)
        else:
            # Versão compacta para comparação
            st.markdown(f"<div style='font-size:{config['font_size'] - 2}px; color:#666'>Preview compacto</div>", unsafe_allow_html=True)


def palette_name_from_list(palette_list):
    for k, v in PALETTES.items():
        if v == palette_list:
            return k
    return "Custom"


def main():
    st.set_page_config(page_title="Interface Designer - LANDAGRI Dashboard", layout="wide")
    st.title("🎨 Interface Designer - LANDAGRI Dashboard")
    st.markdown("Ferramenta completa para prototipagem de interfaces de dashboard")
    
    # Inicializar configuração no session_state
    if 'config' not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG.copy()
    
    # Sidebar com abas organizadas
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Abas para organizar controles
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎨 Cores", "📐 Layout", "📱 Responsivo", "🔤 Tipografia", "💾 Config"])
        
        # Aba 1: Cores & Temas
        with tab1:
            st.subheader("Paletas & Cores")
            palette_name = st.selectbox("Tema", options=list(PALETTES.keys()))
            palette = PALETTES[palette_name]
            
            # Visualizar paleta atual
            cols = st.columns(5)
            for i, color in enumerate(palette):
                with cols[i]:
                    st.color_picker(f"Cor {i+1}", value=color, key=f"color_{i}")
                    palette[i] = st.session_state[f"color_{i}"]
            
            # Modo escuro/claro
            dark_mode = st.checkbox("Modo escuro")
            if dark_mode:
                palette = [c if _is_dark(c) else "#1a1a1a" for c in palette]
        
        # Aba 2: Layout & Menu
        with tab2:
            st.subheader("Layout & Menu")
            menu_style = st.selectbox("Tipo de menu",
                options=["Expanded", "Compact", "Top", "Overlay", "Nested", "Tabs", "Floating", "Hierarchical"])
            
            icon_set_name = st.selectbox("Ícones", options=list(ICON_SETS.keys()))
            icon_set = ICON_SETS[icon_set_name]
            
            st.subheader("Dimensões")
            st.session_state.config['menu_width'] = st.slider("Largura do menu (px)", 150, 400, st.session_state.config['menu_width'])
            st.session_state.config['header_height'] = st.slider("Altura do header (px)", 40, 100, st.session_state.config['header_height'])
            st.session_state.config['spacing'] = st.slider("Espaçamento (px)", 4, 32, st.session_state.config['spacing'])
            st.session_state.config['border_radius'] = st.slider("Border radius (px)", 0, 20, st.session_state.config['border_radius'])
        
        # Aba 3: Responsivo
        with tab3:
            st.subheader("Simulação de Tela")
            screen_size = st.radio("Tamanho da tela:", ["Mobile", "Tablet", "Desktop"])
            st.session_state.config['screen_size'] = screen_size
            
            # Mostrar dimensões simuladas
            sizes = {"Mobile": "375px", "Tablet": "768px", "Desktop": "1200px"}
            st.info(f"Simulando: {sizes[screen_size]}")
            
            # Preview de múltiplos layouts
            show_comparison = st.checkbox("Mostrar comparação de layouts")
        
        # Aba 4: Tipografia
        with tab4:
            st.subheader("Tipografia")
            st.session_state.config['font_size'] = st.slider("Tamanho da fonte (px)", 10, 24, st.session_state.config['font_size'])
            st.session_state.config['font_family'] = st.selectbox("Família da fonte", 
                ["Arial, sans-serif", "Georgia, serif", "Courier, monospace", "'Segoe UI', sans-serif"])
        
        # Aba 5: Configurações
        with tab5:
            st.subheader("Export/Import")
            
            # Export
            if st.button("📥 Exportar configuração"):
                config_json = {**st.session_state.config, "palette": palette, "palette_name": palette_name}
                st.json(config_json)
                st.download_button(
                    "💾 Download JSON",
                    data=str(config_json),
                    file_name="dashboard_config.json",
                    mime="application/json"
                )
            
            # Import
            uploaded_file = st.file_uploader("📤 Importar configuração", type=['json'])
            if uploaded_file:
                try:
                    import json
                    config_data = json.load(uploaded_file)
                    st.session_state.config.update(config_data)
                    st.success("Configuração importada!")
                except Exception:
                    st.error("Erro ao importar arquivo")

        # --- Novo: Menu hierárquico interativo (expander + radio) ---
        st.sidebar.title("Menu Hierárquico")

        # Nível 1: Dashboard
        with st.sidebar.expander("📊 DashBoard", expanded=True):
            dash_option = st.radio(
                "Selecione uma opção do Dashboard",
                ("Overview", "About", "Métricas", "KPIs"),
                key="menu_dashboard"
            )

        # Nível 1: Initiative Analysis
        with st.sidebar.expander("📈 Initiative Analysis"):
            initiative_option = st.radio(
                "Selecione uma opção de Initiative Analysis",
                ("Temporal Analysis", "Comparative Analysis", "Detailed Analysis", "Reports"),
                key="menu_initiative"
            )

        # Nível 1: Agricultural Analysis
        with st.sidebar.expander("🌾 Agricultural Analysis"):
            agri_option = st.radio(
                "Selecione uma opção de Agricultural Analysis",
                ("Agriculture Overview", "Crop Calendar", "Agriculture Availability", "Monitoring"),
                key="menu_agriculture"
            )

        # Mostrar escolha ao usuário (pequeno resumo no sidebar)
        st.sidebar.markdown("---")
        st.sidebar.subheader("Escolhas do Menu")
        st.sidebar.write(f"**Dashboard:** {st.session_state.get('menu_dashboard', '—')}")
        st.sidebar.write(f"**Initiative:** {st.session_state.get('menu_initiative', '—')}")
        st.sidebar.write(f"**Agriculture:** {st.session_state.get('menu_agriculture', '—')}")
    
    # Área principal - Preview
    if show_comparison if 'show_comparison' in locals() else False:
        st.subheader("📊 Comparação de Layouts")
        col1, col2, col3 = st.columns(3)
        
        layouts_to_compare = ["Expanded", "Compact", "Top"]
        for i, layout in enumerate(layouts_to_compare):
            with [col1, col2, col3][i]:
                st.markdown(f"**{layout}**")
                with st.container():
                    render_preview(palette, icon_set, layout, st.session_state.config, compact=True)
    else:
        st.subheader(f"📱 Preview - {screen_size if 'screen_size' in locals() else 'Desktop'}")
        
        # Aplicar CSS responsivo baseado no tamanho da tela
        responsive_css = f"""
        <style>
        .main-preview {{
            max-width: {sizes.get(st.session_state.config['screen_size'], '100%')};
            margin: 0 auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        </style>
        """
        st.markdown(responsive_css, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="main-preview">', unsafe_allow_html=True)
            render_preview(palette, icon_set, menu_style, st.session_state.config)
            st.markdown('</div>', unsafe_allow_html=True)


    if __name__ == "__main__":
        main()
if __name__ == "__main__":
    main()
