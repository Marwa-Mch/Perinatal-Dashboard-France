"""Traitement du formulaire d'authentification."""
import logging
import sqlite3
from src.models.session import Session, clear_auth, DuplicateEmailError, TooManyAttemptsError
from src.models.security import validate


def signup(login: str, mdp: str) -> dict:
    try:
        login = validate(login, mdp, registration=True)
        session = Session(login, mdp)
        session.signup()
        session.login(count_attempt=False)
        if session.logged:
            session.persist()
            return {"success": True, "message": "Compte créé et connecté avec succès."}
        return {"success": False, "message": "Identifiants incorrects."}
    except (ValueError, DuplicateEmailError, TooManyAttemptsError) as exc:
        return {"success": False, "message": str(exc)}
    except sqlite3.Error:
        logging.getLogger(__name__).exception("Erreur de base lors de l'authentification")
        return {"success": False, "message": "Service momentanément indisponible. Réessayez plus tard."}
