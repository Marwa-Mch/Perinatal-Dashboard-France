from src.models.data_validation import validate_frame
# =====================================================
# MODEL — DONNÉES DE NAISSANCES
# =====================================================

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


def verifier_fichiers(fichiers):
    """
    Vérifie que tous les fichiers attendus existent.
    """

    fichiers_manquants = [
        str(fichier)
        for fichier in fichiers
        if not fichier.exists()
    ]

    if fichiers_manquants:
        raise FileNotFoundError(
            "Fichiers de naissances introuvables : "
            + ", ".join(fichiers_manquants)
        )


@st.cache_data
def charger_naissances_france():
    """
    Charge les données de naissances pour la France entière.
    """

    fichier = PROCESSED_DATA_DIR / "naissances_france.csv"
    verifier_fichiers([fichier])

    return validate_frame(pd.read_csv(fichier), "naissances")


@st.cache_data
def charger_naissances_regions():
    """
    Charge les données de naissances par région.
    """

    fichier = PROCESSED_DATA_DIR / "naissances_regions.csv"
    verifier_fichiers([fichier])

    return validate_frame(pd.read_csv(fichier), "naissances")


@st.cache_data
def charger_naissances_departements():
    """
    Charge les données de naissances par département.
    """

    fichier = PROCESSED_DATA_DIR / "naissances_departements.csv"
    verifier_fichiers([fichier])

    return validate_frame(pd.read_csv(fichier), "naissances")