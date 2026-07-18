from pathlib import Path
import json

from src.models.session import Session


BASE_DIR = Path(__file__).resolve().parents[2]
SESSION_PATH = BASE_DIR / "session.json"


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
    Efface la session courante.
    """

    with open(SESSION_PATH, "w", encoding="utf-8") as outfile:
        json.dump({"email": ""}, outfile)

    return {
        "success": True,
        "message": "Déconnexion réussie."
    }