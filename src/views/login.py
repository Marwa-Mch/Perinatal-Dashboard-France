import streamlit as st

from src.controllers.auth import auth
from src.controllers.signup import signup
from src.router import redirect


def retourner_apres_connexion():
    """
    Redirige l'utilisateur vers la page depuis laquelle
    il a demandé la connexion.

    Si aucune page n'a été mémorisée, retour à l'accueil.
    """

    page_retour = st.session_state.pop(
        "page_apres_connexion",
        "/home"
    )

    redirect(
        page_retour,
        reload=True
    )


def load_view():
    """
    Affiche le formulaire de connexion et d'inscription.
    """

    st.title("Connexion / Inscription")

    st.markdown(
        """
        La consultation de l'application est libre.
        La connexion est nécessaire uniquement pour télécharger
        les données et les résultats.
        """
    )

    email = st.text_input(
        "E-mail",
        value="",
        key="login_email"
    )

    password = st.text_input(
        "Mot de passe",
        value="",
        type="password",
        key="login_password"
    )

    col1, col2 = st.columns(2, gap="small")

    with col1:
        log_in_button = st.button(
            "Se connecter",
            use_container_width=True
        )

    with col2:
        sign_up_button = st.button(
            "S'inscrire",
            use_container_width=True
        )

    if log_in_button:

        result = auth(email, password)

        if result["success"]:
            st.success(result["message"])
            retourner_apres_connexion()
        else:
            st.error(result["message"])

    elif sign_up_button:

        result = signup(email, password)

        if result["success"]:
            st.success(result["message"])
            retourner_apres_connexion()
        else:
            st.error(result["message"])