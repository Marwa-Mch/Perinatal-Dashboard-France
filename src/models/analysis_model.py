# =====================================================
# MODEL — ANALYSES SQL ET DONNÉES CROISÉES
# =====================================================

from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "data" / "perinatalite.db"


def verifier_base():
    """
    Vérifie que la base SQLite existe.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Base SQLite introuvable : {DATABASE_PATH}"
        )


@st.cache_data
def lire_table_sqlite(nom_table: str) -> pd.DataFrame:
    """
    Lit une table complète de la base SQLite.
    """

    verifier_base()

    tables_autorisees = {
        "mortinatalite_france",
        "mortinatalite_regions",
        "mortinatalite_drom"
    }

    if nom_table not in tables_autorisees:
        raise ValueError(
            f"Table non autorisée : {nom_table}"
        )

    connexion = sqlite3.connect(DATABASE_PATH.resolve().as_uri() + "?mode=ro", uri=True)

    try:
        requete = f"SELECT * FROM {nom_table}"

        return pd.read_sql_query(
            requete,
            connexion
        )

    finally:
        connexion.close()


@st.cache_data
def executer_requete_sql(
    requete: str, parameters=()
) -> pd.DataFrame:
    """
    Exécute une requête SQL de lecture.

    Cette fonction est utilisée uniquement avec des requêtes
    préparées dans le Controller, et non avec du SQL saisi
    librement par l'utilisateur.
    """

    verifier_base()

    requete_nettoyee = requete.strip().lower()

    if not requete_nettoyee.startswith("select"):
        raise ValueError(
            "Seules les requêtes SELECT sont autorisées."
        )

    connexion = sqlite3.connect(DATABASE_PATH.resolve().as_uri() + "?mode=ro", uri=True)

    try:
        return pd.read_sql_query(
            requete,
            connexion,
            params=parameters
        )

    finally:
        connexion.close()