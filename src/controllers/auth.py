
from src.models.session import Session



def auth(login: str, mdp: str) -> dict:
    """
    Contrôleur d'authentification.
    """

    if not login.strip() or not mdp:
        return {
            "success": False,
            "message": "Veuillez renseigner un e-mail et un mot de passe."
        }

    session = Session(login, mdp)
    session.login()

    if session.logged:
        session.persist()

        return {
            "success": True,
            "message": "Connexion réussie."
        }

    return {
        "success": False,
        "message": "Identifiants incorrects."
    }


def logout() -> dict:
    """
    Déconnecte l'utilisateur de la session Streamlit.
    """

    import streamlit as st

    st.session_state["email"] = ""

    return {
        "success": True,
        "message": "Déconnexion réussie."
    }