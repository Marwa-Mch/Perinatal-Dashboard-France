from src.models.session import Session


def signup(login: str, mdp: str) -> dict:
    """
    Contrôleur d'inscription.
    """

    if not login.strip() or not mdp:
        return {
            "success": False,
            "message": "Veuillez renseigner un e-mail et un mot de passe."
        }

    session = Session(login, mdp)

    created = session.signup()

    if not created:
        return {
            "success": False,
            "message": "E-mail déjà utilisé. Veuillez vous connecter."
        }

    session.login()

    if session.logged:
        session.persist()

        return {
            "success": True,
            "message": "Compte créé et connecté avec succès."
        }

    return {
        "success": False,
        "message": "Impossible de se connecter après l'inscription."
    }