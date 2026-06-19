import streamlit as st


def load_view():

    st.title("Conclusion — Santé périnatale en France")

    st.header("Résumé du projet")

    st.markdown(
        """
        L'objectif de ce projet est d'analyser les indicateurs de santé
        périnatale en France à partir de données publiques.

        Dans cette première phase, nous avons étudié l'évolution des
        naissances entre 2012 et 2023 à différentes échelles :
        France entière, régions et départements.

        Les données ont été nettoyées et préparées à l'aide de Python
        et Pandas avant leur intégration dans une application Streamlit
        développée selon une architecture MVC.
        """
    )

    st.header("Principales découvertes")

    st.markdown(
        """
        - Le nombre total de naissances en France présente une tendance générale à la baisse.
        - Des différences importantes existent entre les régions françaises.
        - L'analyse régionale et départementale permet d'identifier des dynamiques territoriales spécifiques.
        """
    )

    st.header("Limites de l'étude")

    st.markdown(
        """
        - Cette première version se concentre uniquement sur les données de naissances.
        - Les indicateurs de mortalité périnatale, MFIU et IMG n'ont pas encore été intégrés.
        - Les résultats reposent sur les données actuellement disponibles et nécessitent une actualisation régulière.
        """
    )

    st.header("Perspectives")

    st.markdown(
        """
        Les prochaines étapes du projet consisteront à :

        - Intégrer les données de mortalité périnatale.
        - Intégrer les données de MFIU.
        - Intégrer les données d'IMG.
        - Développer davantage de visualisations interactives.
        - Construire un véritable tableau de bord d'aide à la décision en santé publique.
        """
    )

    st.success(
        "Ce projet constitue une première étape vers la création d'un observatoire interactif des indicateurs de santé périnatale en France."
    )