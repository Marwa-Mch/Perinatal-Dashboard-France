# =====================================================
# IMPORTATION DES BIBLIOTHÈQUES
# =====================================================

# Pandas permet de lire et manipuler les fichiers CSV
import pandas as pd

# Streamlit permet d'utiliser le cache
import streamlit as st


# =====================================================
# CHARGEMENT DES DONNÉES FRANCE ENTIÈRE
# =====================================================

# Le cache évite de relire le fichier CSV
# à chaque interaction utilisateur
@st.cache_data
def charger_naissances_france():

    """
    Charge le fichier des naissances
    pour la France entière.
    """

    # Lecture du fichier CSV
    df = pd.read_csv(
        "data/processed/naissances_france.csv"
    )

    # Retourne le dataframe
    return df


# =====================================================
# CHARGEMENT DES DONNÉES RÉGIONS
# =====================================================

@st.cache_data
def charger_naissances_regions():

    """
    Charge le fichier des naissances
    par région.
    """

    # Lecture du fichier CSV
    df = pd.read_csv(
        "data/processed/naissances_regions.csv"
    )

    # Retourne le dataframe
    return df


# =====================================================
# CHARGEMENT DES DONNÉES DÉPARTEMENTS
# =====================================================

@st.cache_data
def charger_naissances_departements():

    """
    Charge le fichier des naissances
    par département.
    """

    # Lecture du fichier CSV
    df = pd.read_csv(
        "data/processed/naissances_departements.csv"
    )

    # Retourne le dataframe
    return df