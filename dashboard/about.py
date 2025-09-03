"""
About Module
============

Página institucional que descreve o objetivo do LANDAGRI-B Dashboard, seus módulos e como navegar.
"""

from pathlib import Path

import streamlit as st

# Largura padrão fixa para os logos (px). Altere aqui para ajustar globalmente.
DEFAULT_LOGO_WIDTH_PX = 300


def run(logo_width: int = DEFAULT_LOGO_WIDTH_PX) -> None:
    """Renderiza a página "About" com uma visão clara e amigável em pt-BR.

    Args:
        logo_width: Largura fixa (em pixels) para exibir os logos.
    """
    st.set_option("client.showErrorDetails", True)

    # Header visual
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #918C00 0%, #626C01 100%);
            padding: 1.2rem 1rem;
            border-radius: 14px;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 12px rgba(30, 41, 59, 0.18);
            color: #fff;
        ">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: 0.2px; font-family: Arial, sans-serif;">ℹ️ About the LANDAGRI-B Dashboard</h1>
            <p style="margin: .4rem 0 0 0; color: #fdebd6; font-family: Arial, sans-serif;">Learn about the LANDAGRI-B Dashboard objectives and how to navigate through its specialized modules.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **LANDAGRI-B Dashboard** is an integrated platform for exploring and comparing Land Use and Land Cover (LULC) mapping initiatives,
        as well as agricultural information from Brazil. It was designed with the objective of assisting students, researchers, public managers and decision makers who need
        to access detailed information about LULC and Agriculture mapping products in Brazil in a centralized way. The Dashboard offers a user-friendly interface and advanced data visualization
        features across three main modules: *Overview*, *Initiative Analysis* and *Agricultural Analysis*; plus the *About* module. Each module is designed to provide specific insights and tools, as shown below:
        """
    )

    # Cards com os módulos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div style="background: rgba(168, 218, 220, 0.5); border: 1px solid #4CAF50; border-radius: 12px; padding: 1rem; margin-bottom: .8rem;">
            <h3 style="margin:0 0 .4rem 0; color:#2E7D32; font-family: Arial, sans-serif;">🔎 Overview</h3>
            <p style="margin:0; color:#000000; font-family: Arial, sans-serif;">
            Consolidated overview of LULC initiatives with key metrics, classifications and sensor information.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="background: #D2B48C; border: 1px solid #A0522D; border-radius: 12px; padding: 1rem; margin-bottom: .8rem;">
            <h3 style="margin:0 0 .4rem 0; color:#8B4513; font-family: Arial, sans-serif;">🏞 Initiative Analysis</h3>
            <p style="margin:0; color:#000000; font-family: Arial, sans-serif;">
            Temporal, comparative and detailed analysis of the thirteen LULC initiatives, with interactive charts and tables.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background: rgba(255, 165, 0, 0.5); border: 1px solid #FF8C00; border-radius: 12px; padding: 1rem;">
            <h3 style="margin:0 0 .4rem 0; color:#8B4513; font-family: Arial, sans-serif;">🌾 Agricultural Analysis</h3>
            <p style="margin:0; color:#000000; font-family: Arial, sans-serif;">
            Agricultural indicators, crop calendar and aggregated availability by region and time period.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="background: rgba(234, 134, 120, 0.5); border: 1px solid #fed7aa; border-radius: 12px; padding: 1rem;">
            <h3 style="margin:0 0 .4rem 0; color:#EF5C67; font-family: Arial, sans-serif;">🧭 How to Navigate</h3>
            <ul style="margin:.2rem 0 0 1.1rem; color:#000000; font-family: Arial, sans-serif;">
                <li>Use the sidebar menu to choose the module and page.</li>
                <li>Filters and tabs appear within each module, according to context.</li>
                <li>Selected parameters are maintained during navigation.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    # Fontes e créditos
    st.markdown("### 🌐 Data Sources and References")
    st.markdown(
        """
        - LULC mapping initiatives: [Santos et al. (2025)](https://doi.org/10.3390/rs17132324).
        - Agricultural data from [CONAB](https://www.conab.gov.br/) and [IBGE](https://www.ibge.gov.br/).
        """
    )
    st.markdown("---")
    st.markdown("### ©️ Citation")
    st.markdown(
        """
        This work is part of the LANDAGRI project, licensed under the Creative Commons Attribution 4.0 International License.

        The reproduction of this work is permitted as long as appropriate credit is given.

        If you use this dashboard in academic or technical work, please cite the products and the LANDAGRI-B project using the following articles:
        - Initiatives and products informations article: [Santos et al. (2025)](https://doi.org/10.3390/rs17132324).
        - Project's main article: [Santos and Adami (2025)](http://mtc-m16c.sid.inpe.br/ibi/sid.inpe.br/mtc-m18/2010/10.19.13.42?ibiurl.clientinformation.citingitem=sid.inpe.br/mtc-m18/2010/12.15.11.49&linktype=relative);
        - LANDAGRI-B repository in Zenodo: [Santos, Silva and Adami (2025)](https://github.com/landagri-b).
        """
    )
    st.markdown("---")
    st.markdown("### ᯓ➤ Contact")
    st.markdown(
        """
        Questions or suggestions can be directed to the project team.

        📧 E-mail: priscilla.santos@inpe.br

        🔗 GitHub: https://github.com/landagri-b
        """
    )

    # Seção de logos institucionais (usando caminhos absolutos)
    st.markdown("---")

    try:
        # Base absoluto a partir da localização deste arquivo
        base_dir = Path(__file__).resolve().parent.parent
    except NameError:
        # Em alguns contextos (por exemplo, REPL) __file__ pode não existir — usar cwd absoluto
        base_dir = Path.cwd().resolve()

    logos_dir = (base_dir / "data" / "Logos_partners").resolve()

    logo_col1, logo_col2, logo_col3 = st.columns(3, gap="small")

    with logo_col1:
        logo1_path = logos_dir / "INPE.png"
        if logo1_path.exists():
            st.image(str(logo1_path), width=logo_width, caption="")
        else:
            st.warning(f"📁 Logo não encontrada: {logo1_path}")

    with logo_col2:
        logo2_path = logos_dir / "AGRIRSLAB.png"
        if logo2_path.exists():
            st.image(str(logo2_path), width=logo_width, caption="")
        else:
            st.warning(f"📁 Logo não encontrada: {logo2_path}")

    with logo_col3:
        logo3_path = logos_dir / "LANDAGRIB.png"
        if logo3_path.exists():
            st.image(str(logo3_path), width=logo_width, caption="")
        else:
            st.warning(f"📁 Logo não encontrada: {logo3_path}")


if __name__ == "__main__":
    run()
