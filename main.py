import streamlit as st

from src.router import get_route
from src.views import (
    analysis,
    saved,
    conclusion,
    dataset,
    home,
    login,
    logout,
    mortinatalite_views,
    naissance_views,
)

import utils as utl


st.set_page_config(
    page_title="Perinatal Dashboard France",
    page_icon="📊",
    layout="wide",
)


utl.inject_custom_css()
utl.navbar_component()
if st.sidebar.button("Mes analyses enregistrées", key="nav_saved"):
    from src.router import redirect
    redirect("/saved", reload=True)


def navigation():
    """
    Affiche la page correspondant à la route demandée.
    """

    route = get_route()

    if route == "/home":
        home.load_view()

    elif route == "/dataset":
        dataset.load_view()

    elif route == "/analysis":
        analysis.load_view()

    elif route == "/naissances":
        naissance_views.load_view()

    elif route == "/mortinatalite":
        mortinatalite_views.load_view()

    elif route == "/conclusion":
        conclusion.load_view()

    elif route == "/logout":
        logout.load_view()

    elif route == "/saved":
        saved.load_view()

    elif route == "/login":
        login.load_view()

    else:
        home.load_view()


try:
    navigation()
except (ValueError, PermissionError) as error:
    st.error(str(error))
except Exception:
    import logging
    logging.getLogger(__name__).exception("Erreur applicative")
    st.error("Le traitement n’a pas pu être effectué. Réessayez ou contactez la personne responsable de l’application.")
