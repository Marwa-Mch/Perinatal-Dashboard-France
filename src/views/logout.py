from src.controllers.auth import logout
from src.router import redirect


def load_view():
    """
    Déconnecte l'utilisateur puis retourne à l'accueil.
    """

    logout()
    redirect("/home", reload=True)