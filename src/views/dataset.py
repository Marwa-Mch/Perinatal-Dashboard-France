# =====================================================
# PAGE DATASET — PRÉSENTATION DES DONNÉES
# =====================================================

import streamlit as st

from src.controllers.naissances_controller import (
    get_data_naissances
)
from src.controllers.mortinatalite_controller import (
    get_data_mortinatalite
)


def load_view():
    """
    Présente les jeux de données utilisés,
    leur organisation et leur préparation.
    """

    # =====================================================
    # TITRE ET INTRODUCTION
    # =====================================================

    st.title("Jeux de données")

    st.markdown(
        """
        L'application **Perinatal Dashboard France** repose sur deux
        jeux de données publics consacrés à la santé périnatale :

        - les **naissances** ;
        - la **mortinatalité**.

        Les données couvrent la période **2012–2023** et ont été
        nettoyées avec Python et Pandas avant leur intégration
        dans l'application.
        """
    )

    # =====================================================
    # INDICATEURS GÉNÉRAUX
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Jeux de données",
            value="2"
        )

    with col2:
        st.metric(
            label="Années étudiées",
            value="12"
        )

    with col3:
        st.metric(
            label="Niveaux géographiques",
            value="3"
        )

    # =====================================================
    # CHARGEMENT DES DONNÉES
    # =====================================================

    try:

        (
            df_naissances_france,
            df_naissances_regions,
            df_naissances_departements
        ) = get_data_naissances()

        (
            df_mortinatalite_france,
            df_mortinatalite_regions,
            df_mortinatalite_drom
        ) = get_data_mortinatalite()

    except FileNotFoundError as erreur:

        st.error(
            "Un ou plusieurs fichiers de données sont introuvables."
        )

        st.code(str(erreur))
        return

    except Exception as erreur:

        st.error(
            "Les données n'ont pas pu être chargées."
        )

        st.code(str(erreur))
        return

    # =====================================================
    # ONGLETS
    # =====================================================

    tab_naissances, tab_mortinatalite = st.tabs(
        [
            "Naissances",
            "Mortinatalité"
        ]
    )

    # =====================================================
    # ONGLET NAISSANCES
    # =====================================================

    with tab_naissances:

        st.header("Données de naissances")

        st.markdown(
            """
            Les données de naissances ont été séparées
            en trois niveaux géographiques :

            - France entière ;
            - régions ;
            - départements.
            """
        )

        niveau_naissances = st.selectbox(
            "Choisissez le niveau géographique",
            [
                "France entière",
                "Régions",
                "Départements"
            ],
            key="dataset_niveau_naissances"
        )

        if niveau_naissances == "France entière":

            dataframe_naissances = (
                df_naissances_france
            )

        elif niveau_naissances == "Régions":

            dataframe_naissances = (
                df_naissances_regions
            )

        else:

            dataframe_naissances = (
                df_naissances_departements
            )

        st.subheader("Aperçu du fichier")

        st.dataframe(
            dataframe_naissances.head(5),
            use_container_width=True
        )

        st.caption(
            f"""
            Affichage des cinq premières lignes —
            {len(dataframe_naissances)} lignes et
            {len(dataframe_naissances.columns)} colonnes.
            """
        )

        with st.expander(
            "Afficher les fichiers CSV préparés"
        ):

            st.markdown(
                """
                - `naissances_france.csv`
                - `naissances_regions.csv`
                - `naissances_departements.csv`
                """
            )

    # =====================================================
    # ONGLET MORTINATALITÉ
    # =====================================================

    with tab_mortinatalite:

        st.header("Données de mortinatalité")

        st.markdown(
            """
            Les données de mortinatalité permettent
            d'étudier :

            - la mortinatalité totale ;
            - la mortinatalité spontanée ;
            - les interruptions médicales de grossesse ;
            - les effectifs de naissances.

            Les niveaux géographiques disponibles sont :

            - France entière ;
            - régions ;
            - DROM.
            """
        )

        niveau_mortinatalite = st.selectbox(
            "Choisissez le niveau géographique",
            [
                "France entière",
                "Régions",
                "DROM"
            ],
            key="dataset_niveau_mortinatalite"
        )

        if niveau_mortinatalite == "France entière":

            dataframe_mortinatalite = (
                df_mortinatalite_france
            )

        elif niveau_mortinatalite == "Régions":

            dataframe_mortinatalite = (
                df_mortinatalite_regions
            )

        else:

            dataframe_mortinatalite = (
                df_mortinatalite_drom
            )

        st.subheader("Aperçu du fichier")

        st.dataframe(
            dataframe_mortinatalite.head(5),
            use_container_width=True
        )

        st.caption(
            f"""
            Affichage des cinq premières lignes —
            {len(dataframe_mortinatalite)} lignes et
            {len(dataframe_mortinatalite.columns)} colonnes.
            """
        )

        with st.expander(
            "Afficher les fichiers CSV préparés"
        ):

            st.markdown(
                """
                - `mortinatalite_france.csv`
                - `mortinatalite_regions.csv`
                - `mortinatalite_drom.csv`
                """
            )

    # =====================================================
    # PIPELINE DE TRAITEMENT
    # =====================================================

    st.header("Pipeline de traitement")

    st.code(
        """
Fichiers sources Excel
        ↓
Lecture dans les notebooks
        ↓
Nettoyage avec Pandas
        ↓
Séparation des niveaux géographiques
        ↓
Création des fichiers CSV
        ↓
Création de la base SQLite
        ↓
Models et Controllers
        ↓
Application Streamlit
        """,
        language="text"
    )

    # =====================================================
    # TRAITEMENTS RÉALISÉS
    # =====================================================

    with st.expander(
        "Afficher les principales étapes de préparation"
    ):

        st.markdown(
            """
            La préparation des données a été réalisée
            dans les notebooks :

            1. `01_naissances.ipynb`
            2. `02_mortinatalite.ipynb`

            Les principaux traitements effectués sont :

            - lecture des fichiers Excel ;
            - nettoyage des noms de colonnes ;
            - conversion des variables numériques ;
            - contrôle des valeurs manquantes ;
            - distinction des niveaux géographiques ;
            - séparation des DataFrames ;
            - export au format CSV ;
            - création des tables SQLite ;
            - vérification des données avec SQL.
            """
        )

    st.info(
        """
        Cette page présente uniquement la structure
        et la préparation des données.

        Les graphiques, filtres et interprétations
        sont disponibles dans les pages Naissances,
        Mortinatalité et Analyse.
        """
    )