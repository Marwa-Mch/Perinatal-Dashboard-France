
import html
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
        width="stretch"
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
    Affiche le titre et les boutons de navigation
    sur des lignes distinctes.

    La navigation utilise les boutons natifs Streamlit
    afin de conserver la session utilisateur.
    """

    utilisateur_connecte = get_current_user()

    # Style limité aux éléments de l'en-tête
    st.markdown(
        """
        <style>
        .perinatal-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .perinatal-title {
            font-size: 1.7rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 0.3rem;
        }

        .perinatal-subtitle {
            font-size: 0.95rem;
            opacity: 0.75;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =================================================
    # 1. TITRE DE L'APPLICATION
    # =================================================

    st.markdown(
        """
        <div class="perinatal-header">
            <div class="perinatal-title">
                📊 Tableau de bord périnatal
            </div>
            <div class="perinatal-subtitle">
                Indicateurs de santé périnatale en France
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =================================================
    # 2. PREMIÈRE LIGNE DE NAVIGATION
    # =================================================

    colonnes_1 = st.columns(
        4,
        gap="small"
    )

    with colonnes_1[0]:
        navigation_button(
            label="Accueil",
            route="/home",
            key="nav_home"
        )

    with colonnes_1[1]:
        navigation_button(
            label="Données",
            route="/dataset",
            key="nav_dataset"
        )

    with colonnes_1[2]:
        navigation_button(
            label="Naissances",
            route="/naissances",
            key="nav_naissances"
        )

    with colonnes_1[3]:
        navigation_button(
            label="Mortinatalité",
            route="/mortinatalite",
            key="nav_mortinatalite"
        )

    # =================================================
    # 3. DEUXIÈME LIGNE DE NAVIGATION
    # =================================================

    colonnes_2 = st.columns(
        4,
        gap="small"
    )

    with colonnes_2[0]:
        navigation_button(
            label="Analyse",
            route="/analysis",
            key="nav_analysis"
        )

    with colonnes_2[1]:
        navigation_button(
            label="Conclusion",
            route="/conclusion",
            key="nav_conclusion"
        )

    with colonnes_2[2]:

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

    # =================================================
    # 4. UTILISATEUR CONNECTÉ
    # =================================================

    if utilisateur_connecte:

        st.markdown(
            (
                '<div style="text-align:right;'
                'font-size:0.85rem;margin-top:0.5rem;">'
                f'Connecté : {html.escape(str(utilisateur_connecte))}'
                "</div>"
            ),
            unsafe_allow_html=True
        )

    # =================================================
    # 5. SÉPARATION AVEC LE CONTENU
    # =================================================

    st.divider()
