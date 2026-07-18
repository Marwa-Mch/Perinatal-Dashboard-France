import streamlit as st


def load_view():
    """
    Page d'accueil de l'application.

    Cette vue présente :
    - le contexte du projet ;
    - les objectifs ;
    - les indicateurs analysés ;
    - les principales technologies utilisées.
    """

    st.title("Perinatal Dashboard France")

    st.subheader(
        "Tableau de bord interactif des indicateurs de santé périnatale"
    )

    st.markdown(
        """
        Cette application permet d'explorer plusieurs indicateurs de santé
        périnatale en France à partir de données publiques.

        Le projet porte actuellement sur deux axes principaux :

        - l'évolution des **naissances** ;
        - l'évolution de la **mortinatalité**.

        Les résultats peuvent être étudiés à différentes échelles géographiques
        selon les données disponibles : France entière, régions et départements.
        """
    )

    st.header("Problématique")

    st.markdown(
        """
        Comment rendre les données publiques de santé périnatale plus lisibles,
        comparables et accessibles grâce à une application interactive ?
        """
    )

    st.header("Objectifs du projet")

    st.markdown(
        """
        - Nettoyer et structurer des données publiques avec Python et Pandas.
        - Organiser les données par niveau géographique.
        - Stocker et interroger certaines données dans une base SQLite.
        - Étudier l'évolution des naissances entre 2012 et 2023.
        - Étudier les indicateurs de mortinatalité.
        - Comparer les résultats entre les territoires.
        - Proposer des visualisations interactives et compréhensibles.
        - Permettre la consultation et le téléchargement des résultats.
        """
    )

    st.header("Fonctionnalités de l'application")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Analyse des naissances")
        st.markdown(
            """
            - Évolution nationale.
            - Comparaison des régions.
            - Analyse départementale.
            - Sélection d'une année.
            - Affichage des données.
            """
        )

    with col2:
        st.subheader("Analyse de la mortinatalité")
        st.markdown(
            """
            - Évolution des taux en France.
            - Comparaison entre régions.
            - Analyse selon l'année.
            - Visualisations statistiques.
            - Consultation des résultats SQL.
            """
        )

    st.header("Architecture et technologies")

    st.markdown(
        """
        L'application a été développée avec une architecture **MVC** afin de
        séparer les responsabilités :

        - **Models** : chargement et accès aux données ;
        - **Controllers** : traitement et transmission des données ;
        - **Views** : affichage des pages Streamlit.

        Les principales technologies utilisées sont :

        `Python` · `Pandas` · `SQLite` · `SQL` · `Streamlit` ·
        `Matplotlib` · `Plotly` · `Git` · `GitHub`
        """
    )

    st.info(
        """
        Cette application est un projet pédagogique réalisé dans le cadre
        de la préparation au titre professionnel Concepteur Développeur
        d'Applications.
        """
    )