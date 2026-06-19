# =====================================================
# PAGE DATASET — PRÉSENTATION DES DONNÉES
# =====================================================

import streamlit as st

from src.controllers.naissances_controller import get_data_naissances


def load_view():

    st.title("Jeu de données — Santé périnatale")

    st.markdown(
        """
        Ce projet analyse des indicateurs de santé périnatale en France,
        à partir de fichiers nettoyés dans le notebook.

        Pour cette première version, nous travaillons sur les données de naissances.
        """
    )

    df_france, df_regions, df_departements = get_data_naissances()

    st.header("Fichiers utilisés")

    st.markdown(
        """
        - `naissances_france.csv` : données France entière
        - `naissances_regions.csv` : données par région
        - `naissances_departements.csv` : données par département
        """
    )

    st.header("Aperçu France entière")
    st.dataframe(df_france.head())

    st.header("Aperçu régions")
    st.dataframe(df_regions.head())

    st.header("Aperçu départements")
    st.dataframe(df_departements.head())

    st.info(
        """
        Les données affichées ici proviennent des fichiers CSV déjà nettoyés.
        Le nettoyage principal a été réalisé dans le notebook `01_naissances.ipynb`.
        """
    )