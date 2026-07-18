# =====================================================
# PAGE CONCLUSION — PERINATAL DASHBOARD FRANCE
# =====================================================

import streamlit as st


def load_view():
    """
    Affiche la conclusion générale du projet.

    Cette page présente :
    - les objectifs atteints ;
    - les compétences techniques mobilisées ;
    - les fonctionnalités développées ;
    - les limites ;
    - les perspectives d'amélioration.
    """

    # =====================================================
    # TITRE
    # =====================================================

    st.title("Conclusion du projet")

    st.markdown(
        """
        **Perinatal Dashboard France** est une application interactive
        consacrée à l'analyse des indicateurs de santé périnatale
        en France entre **2012 et 2023**.

        Le projet repose actuellement sur deux ensembles de données :

        - les naissances ;
        - la mortinatalité.

        L'objectif principal était de transformer des données publiques
        complexes en informations plus lisibles, comparables et
        accessibles à travers un tableau de bord interactif.
        """
    )

    # =====================================================
    # INDICATEURS DU PROJET
    # =====================================================

    st.header("Le projet en quelques chiffres")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Jeux de données",
            value="2"
        )

    with col2:
        st.metric(
            label="Années analysées",
            value="12"
        )

    with col3:
        st.metric(
            label="Niveaux géographiques",
            value="3"
        )

    with col4:
        st.metric(
            label="Modules d'analyse",
            value="3"
        )

    st.caption(
        """
        Les niveaux géographiques étudiés sont la France entière,
        les régions et, selon les données disponibles,
        les départements ou les DROM.
        """
    )

    # =====================================================
    # OBJECTIFS ATTEINTS
    # =====================================================

    st.header("Objectifs atteints")

    st.markdown(
        """
        Le développement de l'application a permis de :

        - nettoyer et restructurer les fichiers sources ;
        - séparer les données selon leur niveau géographique ;
        - créer des fichiers CSV propres et réutilisables ;
        - intégrer les données de mortinatalité dans une base SQLite ;
        - exécuter des requêtes SQL depuis l'application ;
        - développer des filtres interactifs ;
        - afficher des indicateurs clés ;
        - comparer plusieurs territoires ;
        - produire des graphiques interactifs ;
        - réaliser des analyses statistiques descriptives ;
        - mettre en relation les naissances et la mortinatalité ;
        - permettre le téléchargement des résultats après connexion.
        """
    )

    # =====================================================
    # COMPÉTENCES TECHNIQUES
    # =====================================================

    st.header("Compétences techniques mobilisées")

    tab_donnees, tab_developpement, tab_visualisation, tab_projet = st.tabs(
        [
            "Données",
            "Développement",
            "Visualisation",
            "Gestion du projet"
        ]
    )

    with tab_donnees:

        st.subheader("Préparation et analyse des données")

        st.markdown(
            """
            - **Python** pour le traitement général ;
            - **Pandas** pour le nettoyage et la transformation ;
            - conversion des types de données ;
            - traitement des valeurs manquantes ;
            - renommage et sélection des colonnes ;
            - séparation des niveaux géographiques ;
            - création de fichiers CSV ;
            - calculs statistiques descriptifs ;
            - corrélation exploratoire.
            """
        )

    with tab_developpement:

        st.subheader("Développement de l'application")

        st.markdown(
            """
            - **Streamlit** pour l'interface web ;
            - architecture **MVC** ;
            - création de Models, Controllers et Views ;
            - navigation avec un routeur ;
            - gestion des utilisateurs ;
            - inscription et connexion ;
            - stockage des utilisateurs dans SQLite ;
            - protection du téléchargement par authentification ;
            - gestion des erreurs de chargement.
            """
        )

    with tab_visualisation:

        st.subheader("Visualisations et tableau de bord")

        st.markdown(
            """
            - **Plotly** pour les graphiques interactifs ;
            - courbes d'évolution ;
            - graphiques en barres ;
            - nuages de points ;
            - boxplots ;
            - heatmaps ;
            - comparaison en base 100 ;
            - indicateurs avec `st.metric()` ;
            - tableaux interactifs ;
            - filtres par période, indicateur et territoire.
            """
        )

    with tab_projet:

        st.subheader("Organisation et suivi")

        st.markdown(
            """
            - développement progressif selon une démarche Agile ;
            - utilisation de **Git** et **GitHub** ;
            - sauvegarde régulière des versions ;
            - organisation des dossiers du projet ;
            - documentation dans les notebooks ;
            - préparation des tests fonctionnels ;
            - construction progressive de l'application.
            """
        )

    # =====================================================
    # ARCHITECTURE
    # =====================================================

    st.header("Architecture mise en place")

    st.code(
        """
Utilisateur
    ↓
Interface Streamlit — Views
    ↓
Controllers
    ↓
Models
    ↓
CSV / SQLite
    ↓
Pandas / SQL
    ↓
Plotly / Tableaux / Indicateurs
        """,
        language="text"
    )

    st.markdown(
        """
        Cette architecture permet de séparer clairement :

        - l'affichage ;
        - la logique de traitement ;
        - l'accès aux données.

        Elle facilite la maintenance, les tests et l'évolution
        future de l'application.
        """
    )

    # =====================================================
    # FONCTIONNALITÉS
    # =====================================================

    st.header("Fonctionnalités développées")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Module Naissances")

        st.markdown(
            """
            - analyse France entière ;
            - analyse régionale ;
            - analyse départementale ;
            - sélection d'une période ;
            - choix de l'indicateur ;
            - classement annuel ;
            - comparaison de plusieurs territoires ;
            - tableau des résultats ;
            - téléchargement au format CSV.
            """
        )

    with col2:

        st.subheader("Module Mortinatalité")

        st.markdown(
            """
            - analyse France entière ;
            - comparaison des régions ;
            - analyse des DROM ;
            - choix de la période ;
            - mortinatalité totale ;
            - mortinatalité spontanée ;
            - IMG ;
            - classement et évolution territoriale ;
            - téléchargement au format CSV.
            """
        )

    st.subheader("Module Analyse croisée")

    st.markdown(
        """
        Le module Analyse constitue la partie décisionnelle
        et technique du tableau de bord. Il permet notamment :

        - de comparer l'évolution des naissances et de la mortinatalité ;
        - de normaliser les séries en base 100 ;
        - de calculer une corrélation exploratoire ;
        - d'étudier les disparités régionales ;
        - d'afficher un boxplot ;
        - de construire une heatmap ;
        - d'exécuter des requêtes SQL ;
        - de visualiser les résultats SQL avec Plotly.
        """
    )

    # =====================================================
    # PRINCIPAUX CONSTATS
    # =====================================================

    st.header("Principaux constats")

    st.markdown(
        """
        Les analyses réalisées mettent notamment en évidence :

        - une tendance générale à la baisse du nombre de naissances
          sur la période étudiée ;
        - des différences importantes entre les régions et
          les départements ;
        - une évolution moins régulière des indicateurs
          de mortinatalité ;
        - des disparités territoriales qui justifient
          une analyse régionale ;
        - l'intérêt de comparer les données nationales
          et territoriales dans un même outil.

        Les résultats affichés sont descriptifs et exploratoires.
        Ils ne permettent pas, à eux seuls, d'établir un lien
        de causalité entre les indicateurs.
        """
    )

    # =====================================================
    # LIMITES
    # =====================================================

    st.header("Limites du projet")

    st.markdown(
        """
        Plusieurs limites doivent être prises en compte :

        - l'application repose sur des données agrégées ;
        - les données ne concernent pas des situations individuelles ;
        - certains indicateurs ne sont pas disponibles
          aux mêmes niveaux géographiques ;
        - les fichiers sources contenaient des structures complexes ;
        - certaines colonnes présentaient des intitulés différents ;
        - la corrélation observée reste une analyse exploratoire ;
        - l'authentification actuelle correspond à une version pédagogique ;
        - l'application n'est pas encore déployée sur un environnement
          de production.
        """
    )

    st.warning(
        """
        Les résultats de l'application ne constituent pas
        un outil de diagnostic médical. Ils servent uniquement
        à l'analyse descriptive de données publiques agrégées.
        """
    )

    # =====================================================
    # PERSPECTIVES
    # =====================================================

    st.header("Perspectives d'amélioration")

    st.markdown(
        """
        Plusieurs évolutions pourront être envisagées :

        - intégrer de nouveaux indicateurs de santé périnatale ;
        - ajouter des données sur l'âge maternel ;
        - développer une cartographie interactive ;
        - automatiser l'actualisation des données ;
        - améliorer l'authentification avec bcrypt ou Argon2 ;
        - permettre l'export des graphiques ;
        - générer un rapport PDF ;
        - renforcer les tests automatisés ;
        - déployer l'application sur le Cloud ;
        - créer une API de consultation ;
        - développer des analyses prédictives
          uniquement si les données disponibles le permettent.
        """
    )

    st.info(
        """
        La priorité future reste l'amélioration de la qualité,
        de la fiabilité et de l'accessibilité de l'application,
        avant l'ajout de fonctionnalités plus complexes.
        """
    )

    # =====================================================
    # BILAN PERSONNEL
    # =====================================================

    st.header("Bilan du projet")

    st.markdown(
        """
        Ce projet m'a permis de mobiliser l'ensemble des compétences
        acquises pendant la formation de Data Analyst, depuis la
        préparation des données jusqu'à leur restitution dans une
        application interactive.

        Il m'a également permis de relier mon expérience dans le domaine
        de la santé à de nouvelles compétences en analyse de données
        et en développement d'applications.

        **Perinatal Dashboard France** constitue ainsi une première étape
        vers des projets plus avancés dans le domaine de la Data Science
        appliquée à la santé publique.
        """
    )

    st.success(
        """
        Le projet aboutit à une application fonctionnelle,
        interactive et structurée, capable de transformer
        des données publiques en informations accessibles
        et utiles à l'analyse.
        """
    )