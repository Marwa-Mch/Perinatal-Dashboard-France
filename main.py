import streamlit as st

from src.router import get_route
from src.views import (
    analysis,
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
    page_icon="👶",
    layout="wide",
)


utl.inject_custom_css()
utl.navbar_component()


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

    elif route == "/login":
        login.load_view()

    else:
        home.load_view()


navigation()