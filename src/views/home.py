import streamlit as st


def load_view():

    st.title("Indicateurs de santé périnatale en France")

    st.markdown(
        """
        Bienvenue dans ce projet d'analyse de données consacré aux indicateurs
        de santé périnatale en France.

        L'objectif du projet est d'explorer l'évolution des naissances et,
        progressivement, d'autres indicateurs liés à la santé périnatale :
        mortalité périnatale, MFIU et IMG.

        Cette application a été construite avec Streamlit dans une architecture
        MVC afin de séparer clairement les données, la logique et l'affichage.
        """
    )

    st.header("Objectifs du projet")

    st.markdown(
        """
        - Étudier l'évolution des naissances en France.
        - Comparer les indicateurs entre régions.
        - Comparer les indicateurs entre départements.
        - Construire un tableau de bord clair et interactif.
        """
    )

    st.header("Structure de l'application")

    st.markdown(
        """
        - **Accueil** : présentation du projet.
        - **Jeu de données** : description et aperçu des fichiers utilisés.
        - **Analyse** : visualisations et interprétations.
        - **Conclusion** : synthèse des résultats.
        """
    )