# =====================================================
# OUTILS DE L'APPLICATION
# =====================================================

from pathlib import Path

import streamlit as st

from src.models.session import get_current_user
from src.router import redirect


# Racine du projet
BASE_DIR = Path(__file__).resolve().parent

# Chemin du fichier CSS
CSS_PATH = BASE_DIR / "src" / "assets" / "styles.css"


# =====================================================
# CHARGEMENT DU CSS
# =====================================================

def inject_custom_css():
    """
    Charge le fichier CSS personnalisé de l'application.
    """

    if CSS_PATH.exists():

        with open(
            CSS_PATH,
            "r",
            encoding="utf-8"
        ) as fichier_css:

            st.markdown(
                f"<style>{fichier_css.read()}</style>",
                unsafe_allow_html=True
            )

    else:

        st.warning(
            "Le fichier de style CSS est introuvable."
        )


# =====================================================
# BOUTON DE NAVIGATION
# =====================================================

def navigation_button(
    label: str,
    route: str,
    key: str
):
    """
    Crée un bouton qui redirige vers une page
    sans quitter la session Streamlit.
    """

    if st.button(
        label,
        key=key,
        use_container_width=True
    ):
        redirect(
            route,
            reload=True
        )


# =====================================================
# BARRE DE NAVIGATION
# =====================================================

def navbar_component():
    """
    Affiche une barre de navigation native Streamlit.

    Cette navigation conserve st.session_state,
    contrairement aux anciens liens HTML qui pouvaient
    recréer une nouvelle session.
    """

    utilisateur_connecte = get_current_user()

    # Style spécifique des boutons de navigation
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }

        div.stButton > button {
            min-height: 42px;
            white-space: nowrap;
        }

        .navbar-brand {
            font-size: 1.15rem;
            font-weight: 700;
            padding-top: 8px;
            white-space: nowrap;
        }

        .navbar-user {
            text-align: right;
            font-size: 0.78rem;
            margin-top: -4px;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    colonnes = st.columns(
        [1.8, 1, 1.35, 1.05, 1.35, 1, 1.1, 1.15],
        gap="small"
    )

    # Nom de l'application
    with colonnes[0]:

        st.markdown(
            """
            <div class="navbar-brand">
                👶 Perinatal Dashboard
            </div>
            """,
            unsafe_allow_html=True
        )

    # Accueil
    with colonnes[1]:

        navigation_button(
            label="Accueil",
            route="/home",
            key="nav_home"
        )

    # Jeu de données
    with colonnes[2]:

        navigation_button(
            label="Données",
            route="/dataset",
            key="nav_dataset"
        )

    # Naissances
    with colonnes[3]:

        navigation_button(
            label="Naissances",
            route="/naissances",
            key="nav_naissances"
        )

    # Mortinatalité
    with colonnes[4]:

        navigation_button(
            label="Mortinatalité",
            route="/mortinatalite",
            key="nav_mortinatalite"
        )

    # Analyse
    with colonnes[5]:

        navigation_button(
            label="Analyse",
            route="/analysis",
            key="nav_analysis"
        )

    # Conclusion
    with colonnes[6]:

        navigation_button(
            label="Conclusion",
            route="/conclusion",
            key="nav_conclusion"
        )

    # Connexion ou déconnexion
    with colonnes[7]:

        if utilisateur_connecte:

            navigation_button(
                label="Déconnexion",
                route="/logout",
                key="nav_logout"
            )

        else:

            navigation_button(
                label="Connexion",
                route="/login",
                key="nav_login"
            )

    # Affichage facultatif de l'utilisateur connecté
    if utilisateur_connecte:

        st.markdown(
            (
                '<div class="navbar-user">'
                f'Connecté : {utilisateur_connecte}'
                "</div>"
            ),
            unsafe_allow_html=True
        )

    st.divider()