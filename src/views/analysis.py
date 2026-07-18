# =====================================================
# PAGE ANALYSE — TABLEAU DE BORD DÉCISIONNEL
# =====================================================

import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.controllers.naissances_controller import (
    get_data_naissances
)
from src.controllers.analysis_controller import (
    get_mortinatalite_sql,
    get_requete_classement_regions,
    get_statistiques_regions
)
from src.models.session import get_current_user
from src.router import redirect


# =====================================================
# CONFIGURATION DES INDICATEURS
# =====================================================

INDICATEURS_NAISSANCES = {
    "Naissances totales": "naissances_totales",
    "Naissances vivantes": "naissances_vivantes"
}


INDICATEURS_MORTINATALITE = {
    "Mortinatalité totale": "mortinatalite_totale",
    "Mortinatalité spontanée": "mortinatalite_spontanee",
    "IMG": "img"
}


# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

def obtenir_annees_naissances(
    dataframe: pd.DataFrame
):
    """
    Recherche les années disponibles dans
    les données de naissances.
    """

    annees = []

    for colonne in dataframe.columns:

        resultat = re.match(
            r"^(\d{4})_naissances_totales$",
            str(colonne)
        )

        if resultat:
            annees.append(
                int(resultat.group(1))
            )

    return sorted(set(annees))


def obtenir_annees_mortinatalite(
    dataframe: pd.DataFrame
):
    """
    Recherche les années disponibles dans
    les données de mortinatalité.
    """

    annees = []

    for colonne in dataframe.columns:

        resultat = re.match(
            r"^(\d{4})_mortinatalite_totale$",
            str(colonne)
        )

        if resultat:
            annees.append(
                int(resultat.group(1))
            )

    return sorted(set(annees))


def trouver_colonne_effectif(
    dataframe: pd.DataFrame,
    annee: int
):
    """
    Recherche la colonne des effectifs de naissances.

    L'année 2013 utilise exceptionnellement :
    2013_effectifs_naissances.
    """

    colonne_singulier = (
        f"{annee}_effectif_naissances"
    )

    colonne_pluriel = (
        f"{annee}_effectifs_naissances"
    )

    if colonne_singulier in dataframe.columns:
        return colonne_singulier

    if colonne_pluriel in dataframe.columns:
        return colonne_pluriel

    return None


def preparer_naissances_france(
    dataframe: pd.DataFrame,
    indicateur_technique: str
):
    """
    Transforme la ligne France en série annuelle
    selon l'indicateur de naissances sélectionné.
    """

    annees = obtenir_annees_naissances(
        dataframe
    )

    resultat = []

    for annee in annees:

        colonne = (
            f"{annee}_{indicateur_technique}"
        )

        if colonne not in dataframe.columns:
            continue

        valeur = pd.to_numeric(
            dataframe[colonne].iloc[0],
            errors="coerce"
        )

        resultat.append(
            {
                "Année": annee,
                "Naissances": valeur
            }
        )

    resultat = pd.DataFrame(resultat)

    if resultat.empty:
        return resultat

    return resultat.dropna(
        subset=["Naissances"]
    )


def preparer_mortinatalite_france(
    dataframe: pd.DataFrame,
    indicateur_technique: str
):
    """
    Transforme la ligne France issue de SQLite
    en série annuelle.
    """

    annees = obtenir_annees_mortinatalite(
        dataframe
    )

    resultat = []

    for annee in annees:

        colonne = (
            f"{annee}_{indicateur_technique}"
        )

        if colonne not in dataframe.columns:
            continue

        valeur = pd.to_numeric(
            dataframe[colonne].iloc[0],
            errors="coerce"
        )

        resultat.append(
            {
                "Année": annee,
                "Mortinatalité": valeur
            }
        )

    resultat = pd.DataFrame(resultat)

    if resultat.empty:
        return resultat

    return resultat.dropna(
        subset=["Mortinatalité"]
    )


def creer_base_100(
    dataframe: pd.DataFrame,
    colonne: str
):
    """
    Transforme une série en indice base 100.

    La première valeur de la période devient 100.
    """

    resultat = dataframe.copy()

    if resultat.empty:
        return resultat

    valeur_depart = resultat[colonne].iloc[0]

    nouvelle_colonne = (
        f"{colonne} — base 100"
    )

    if (
        pd.isna(valeur_depart)
        or valeur_depart == 0
    ):
        resultat[nouvelle_colonne] = np.nan

    else:
        resultat[nouvelle_colonne] = (
            resultat[colonne]
            / valeur_depart
        ) * 100

    return resultat


def creer_heatmap_regions(
    dataframe: pd.DataFrame,
    indicateur_technique: str,
    annee_debut: int,
    annee_fin: int
):
    """
    Prépare une table longue pour la heatmap
    régions × années.
    """

    lignes = []

    for _, region in dataframe.iterrows():

        nom_region = region[
            "zone_geographique"
        ]

        for annee in range(
            annee_debut,
            annee_fin + 1
        ):

            colonne = (
                f"{annee}_{indicateur_technique}"
            )

            if colonne not in dataframe.columns:
                continue

            valeur = pd.to_numeric(
                region[colonne],
                errors="coerce"
            )

            lignes.append(
                {
                    "Région": nom_region,
                    "Année": annee,
                    "Taux": valeur
                }
            )

    resultat = pd.DataFrame(lignes)

    if resultat.empty:
        return resultat

    return resultat.dropna(
        subset=["Taux"]
    )


def creer_distribution_regions(
    dataframe: pd.DataFrame,
    indicateur_technique: str,
    annee_debut: int,
    annee_fin: int
):
    """
    Prépare les distributions régionales par année
    pour construire un boxplot.
    """

    resultat = []

    for annee in range(
        annee_debut,
        annee_fin + 1
    ):

        colonne = (
            f"{annee}_{indicateur_technique}"
        )

        if colonne not in dataframe.columns:
            continue

        for _, ligne in dataframe.iterrows():

            valeur = pd.to_numeric(
                ligne[colonne],
                errors="coerce"
            )

            if pd.isna(valeur):
                continue

            resultat.append(
                {
                    "Année": str(annee),
                    "Région": ligne[
                        "zone_geographique"
                    ],
                    "Taux": valeur
                }
            )

    return pd.DataFrame(resultat)


def creer_scatter_regions(
    dataframe: pd.DataFrame,
    annee: int,
    indicateur_technique: str
):
    """
    Prépare la relation entre l'effectif des naissances
    et le taux de mortinatalité par région.
    """

    colonne_taux = (
        f"{annee}_{indicateur_technique}"
    )

    colonne_effectif = trouver_colonne_effectif(
        dataframe,
        annee
    )

    if (
        colonne_taux not in dataframe.columns
        or colonne_effectif is None
    ):
        return pd.DataFrame()

    resultat = dataframe[
        [
            "zone_geographique",
            colonne_taux,
            colonne_effectif
        ]
    ].copy()

    resultat[colonne_taux] = pd.to_numeric(
        resultat[colonne_taux],
        errors="coerce"
    )

    resultat[colonne_effectif] = pd.to_numeric(
        resultat[colonne_effectif],
        errors="coerce"
    )

    resultat = resultat.rename(
        columns={
            "zone_geographique": "Région",
            colonne_taux: "Taux de mortinatalité",
            colonne_effectif: "Effectif des naissances"
        }
    )

    return resultat.dropna(
        subset=[
            "Taux de mortinatalité",
            "Effectif des naissances"
        ]
    )


def afficher_telechargement(
    dataframe: pd.DataFrame,
    nom_fichier: str,
    cle: str
):
    """
    Autorise le téléchargement uniquement
    lorsqu'un utilisateur est connecté.
    """

    st.divider()
    st.subheader("Téléchargement des résultats")

    utilisateur = get_current_user()

    if utilisateur:

        contenu = dataframe.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.success(
            f"Utilisateur connecté : {utilisateur}"
        )

        st.download_button(
            label="Télécharger les résultats affichés",
            data=contenu,
            file_name=nom_fichier,
            mime="text/csv",
            key=cle,
            use_container_width=True
        )

    else:

        st.info(
            "Une connexion est nécessaire uniquement "
            "pour télécharger les résultats."
        )

        if st.button(
            "Se connecter pour télécharger",
            key=f"login_{cle}",
            use_container_width=True
        ):
            redirect(
                "/login",
                reload=True
            )


# =====================================================
# VUE PRINCIPALE
# =====================================================

def load_view():
    """
    Affiche la page d'analyse croisée
    de Perinatal Dashboard France.
    """

    st.title(
        "Analyse croisée et tableau de bord décisionnel"
    )

    st.markdown(
        """
        Cette page met en relation les données de
        **naissances** et de **mortinatalité**.

        Elle présente également des analyses régionales,
        des statistiques descriptives et des requêtes SQL.

        **Chaîne technique utilisée :**

        `SQLite → SQL → Pandas → statistiques → Plotly → Streamlit`
        """
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
            df_mort_france,
            df_mort_regions,
            df_mort_drom
        ) = get_mortinatalite_sql()

    except Exception as erreur:

        st.error(
            "Impossible de charger les données nécessaires."
        )

        st.code(str(erreur))
        return

    annees_naissances = obtenir_annees_naissances(
        df_naissances_france
    )

    annees_mortinatalite = (
        obtenir_annees_mortinatalite(
            df_mort_france
        )
    )

    annees_communes = sorted(
        set(annees_naissances)
        & set(annees_mortinatalite)
    )

    if not annees_communes:

        st.error(
            "Aucune période commune n'a été trouvée."
        )
        return

    # =====================================================
    # FILTRES GÉNÉRAUX
    # =====================================================

    st.sidebar.header(
        "Filtres — Analyse croisée"
    )

    annee_debut, annee_fin = (
        st.sidebar.select_slider(
            "Période étudiée",
            options=annees_communes,
            value=(
                annees_communes[0],
                annees_communes[-1]
            ),
            key="periode_analyse"
        )
    )

    indicateur_naissances_affiche = (
        st.sidebar.selectbox(
            "Indicateur de naissances",
            list(
                INDICATEURS_NAISSANCES.keys()
            ),
            key="indicateur_naissances_analyse"
        )
    )

    indicateur_naissances_technique = (
        INDICATEURS_NAISSANCES[
            indicateur_naissances_affiche
        ]
    )

    indicateur_mortinatalite_affiche = (
        st.sidebar.selectbox(
            "Indicateur de mortinatalité",
            list(
                INDICATEURS_MORTINATALITE.keys()
            ),
            key="indicateur_mortinatalite_analyse"
        )
    )

    indicateur_mortinatalite_technique = (
        INDICATEURS_MORTINATALITE[
            indicateur_mortinatalite_affiche
        ]
    )

    st.sidebar.info(
        f"""
        **Période sélectionnée**

        {annee_debut} à {annee_fin}

        **Naissances**

        {indicateur_naissances_affiche}

        **Mortinatalité**

        {indicateur_mortinatalite_affiche}
        """
    )

    # =====================================================
    # ONGLETS
    # =====================================================

    (
        tab_national,
        tab_regions,
        tab_distribution,
        tab_sql
    ) = st.tabs(
        [
            "Vue nationale",
            "Analyse régionale",
            "Distribution et heatmap",
            "SQL et SQLite"
        ]
    )

    # =====================================================
    # ONGLET 1 — VUE NATIONALE
    # =====================================================

    with tab_national:

        naissances = preparer_naissances_france(
            df_naissances_france,
            indicateur_naissances_technique
        )

        mortinatalite = (
            preparer_mortinatalite_france(
                df_mort_france,
                indicateur_mortinatalite_technique
            )
        )

        naissances = naissances[
            naissances["Année"].between(
                annee_debut,
                annee_fin
            )
        ].copy()

        mortinatalite = mortinatalite[
            mortinatalite["Année"].between(
                annee_debut,
                annee_fin
            )
        ].copy()

        donnees_croisees = pd.merge(
            naissances,
            mortinatalite,
            on="Année",
            how="inner"
        )

        if donnees_croisees.empty:

            st.warning(
                "Aucune donnée croisée n'est disponible "
                "pour cette sélection."
            )

        else:

            debut_naissances = (
                donnees_croisees[
                    "Naissances"
                ].iloc[0]
            )

            fin_naissances = (
                donnees_croisees[
                    "Naissances"
                ].iloc[-1]
            )

            debut_mortinatalite = (
                donnees_croisees[
                    "Mortinatalité"
                ].iloc[0]
            )

            fin_mortinatalite = (
                donnees_croisees[
                    "Mortinatalité"
                ].iloc[-1]
            )

            variation_naissances = (
                (
                    fin_naissances
                    - debut_naissances
                )
                / debut_naissances
            ) * 100

            variation_mortinatalite = (
                fin_mortinatalite
                - debut_mortinatalite
            )

            correlation = (
                donnees_croisees[
                    [
                        "Naissances",
                        "Mortinatalité"
                    ]
                ]
                .corr()
                .iloc[0, 1]
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            with col1:

                st.metric(
                    (
                        f"{indicateur_naissances_affiche} "
                        f"en {annee_fin}"
                    ),
                    f"{fin_naissances:,.0f}".replace(
                        ",",
                        " "
                    )
                )

            with col2:

                st.metric(
                    "Évolution des naissances",
                    f"{variation_naissances:+.1f} %"
                )

            with col3:

                st.metric(
                    (
                        f"{indicateur_mortinatalite_affiche} "
                        f"en {annee_fin}"
                    ),
                    f"{fin_mortinatalite:.2f}"
                )

            with col4:

                st.metric(
                    "Variation du taux",
                    (
                        f"{variation_mortinatalite:+.2f} "
                        "point(s)"
                    )
                )

            # =================================================
            # DEUX GRAPHIQUES NATIONAUX
            # =================================================

            st.subheader(
                "Évolution nationale des deux indicateurs"
            )

            col_gauche, col_droite = (
                st.columns(2)
            )

            with col_gauche:

                figure_naissances = px.line(
                    donnees_croisees,
                    x="Année",
                    y="Naissances",
                    markers=True,
                    title=(
                        f"Évolution des "
                        f"{indicateur_naissances_affiche.lower()}"
                    )
                )

                figure_naissances.update_layout(
                    xaxis_title="Année",
                    yaxis_title="Nombre de naissances",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    figure_naissances,
                    use_container_width=True
                )

            with col_droite:

                figure_mortinatalite = px.line(
                    donnees_croisees,
                    x="Année",
                    y="Mortinatalité",
                    markers=True,
                    title=(
                        indicateur_mortinatalite_affiche
                    )
                )

                figure_mortinatalite.update_layout(
                    xaxis_title="Année",
                    yaxis_title="Taux",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    figure_mortinatalite,
                    use_container_width=True
                )

            # =================================================
            # BASE 100
            # =================================================

            st.subheader(
                "Comparaison des évolutions en base 100"
            )

            donnees_base = creer_base_100(
                donnees_croisees,
                "Naissances"
            )

            donnees_base = creer_base_100(
                donnees_base,
                "Mortinatalité"
            )

            donnees_base_longues = (
                donnees_base.melt(
                    id_vars="Année",
                    value_vars=[
                        "Naissances — base 100",
                        "Mortinatalité — base 100"
                    ],
                    var_name="Indicateur",
                    value_name="Indice base 100"
                )
            )

            figure_base = px.line(
                donnees_base_longues,
                x="Année",
                y="Indice base 100",
                color="Indicateur",
                markers=True,
                title=(
                    f"Évolution comparée de "
                    f"{annee_debut} à {annee_fin}"
                )
            )

            figure_base.add_hline(
                y=100,
                line_dash="dash"
            )

            figure_base.update_layout(
                xaxis_title="Année",
                yaxis_title="Indice base 100",
                hovermode="x unified"
            )

            st.plotly_chart(
                figure_base,
                use_container_width=True
            )

            st.info(
                """
                La base 100 permet de comparer l'évolution
                de deux indicateurs qui ne sont pas exprimés
                dans la même unité.

                La première année sélectionnée prend la valeur 100.
                """
            )

            # =================================================
            # CORRÉLATION
            # =================================================

            st.subheader(
                "Relation exploratoire entre les indicateurs"
            )

            figure_correlation = px.scatter(
                donnees_croisees,
                x="Naissances",
                y="Mortinatalité",
                text="Année",
                trendline="ols",
                title=(
                    f"{indicateur_naissances_affiche} et "
                    f"{indicateur_mortinatalite_affiche.lower()}"
                )
            )

            figure_correlation.update_traces(
                textposition="top center"
            )

            figure_correlation.update_layout(
                xaxis_title=indicateur_naissances_affiche,
                yaxis_title=indicateur_mortinatalite_affiche
            )

            st.plotly_chart(
                figure_correlation,
                use_container_width=True
            )

            st.metric(
                "Coefficient de corrélation de Pearson",
                f"{correlation:.3f}"
            )

            st.warning(
                """
                Cette corrélation est exploratoire.

                Une association statistique entre deux séries
                nationales ne permet pas d'établir un lien
                de causalité.
                """
            )

            st.subheader(
                "Tableau des données croisées"
            )

            st.dataframe(
                donnees_croisees,
                use_container_width=True,
                hide_index=True
            )

            afficher_telechargement(
                donnees_croisees,
                (
                    f"analyse_croisee_france_"
                    f"{annee_debut}_{annee_fin}.csv"
                ),
                "download_analyse_nationale"
            )

    # =====================================================
    # ONGLET 2 — ANALYSE RÉGIONALE
    # =====================================================

    with tab_regions:

        annee_regionale = st.select_slider(
            "Choisissez l'année de l'analyse régionale",
            options=list(
                range(
                    annee_debut,
                    annee_fin + 1
                )
            ),
            value=annee_fin,
            key="annee_regionale_dans_onglet"
        )

        st.header(
            f"Analyse régionale — {annee_regionale}"
        )

        donnees_scatter = creer_scatter_regions(
            df_mort_regions,
            annee_regionale,
            indicateur_mortinatalite_technique
        )

        if donnees_scatter.empty:

            st.warning(
                "Les données régionales ne sont pas disponibles."
            )

        else:

            moyenne = donnees_scatter[
                "Taux de mortinatalité"
            ].mean()

            mediane = donnees_scatter[
                "Taux de mortinatalité"
            ].median()

            minimum = donnees_scatter[
                "Taux de mortinatalité"
            ].min()

            maximum = donnees_scatter[
                "Taux de mortinatalité"
            ].max()

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            with col1:

                st.metric(
                    "Moyenne régionale",
                    f"{moyenne:.2f}"
                )

            with col2:

                st.metric(
                    "Médiane régionale",
                    f"{mediane:.2f}"
                )

            with col3:

                st.metric(
                    "Minimum",
                    f"{minimum:.2f}"
                )

            with col4:

                st.metric(
                    "Maximum",
                    f"{maximum:.2f}"
                )

            st.subheader(
                "Effectif des naissances et mortinatalité"
            )

            figure_scatter = px.scatter(
                donnees_scatter,
                x="Effectif des naissances",
                y="Taux de mortinatalité",
                text="Région",
                size="Effectif des naissances",
                hover_name="Région",
                title=(
                    f"Analyse régionale en "
                    f"{annee_regionale}"
                )
            )

            figure_scatter.update_traces(
                textposition="top center"
            )

            st.plotly_chart(
                figure_scatter,
                use_container_width=True
            )

            correlation_regionale = (
                donnees_scatter[
                    [
                        "Effectif des naissances",
                        "Taux de mortinatalité"
                    ]
                ]
                .corr()
                .iloc[0, 1]
            )

            st.metric(
                "Corrélation régionale",
                f"{correlation_regionale:.3f}"
            )

            st.subheader(
                "Tableau régional"
            )

            st.dataframe(
                donnees_scatter.sort_values(
                    "Taux de mortinatalité",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

            afficher_telechargement(
                donnees_scatter,
                (
                    f"analyse_regionale_"
                    f"{annee_regionale}.csv"
                ),
                "download_analyse_regionale"
            )

    # =====================================================
    # ONGLET 3 — DISTRIBUTION ET HEATMAP
    # =====================================================

    with tab_distribution:

        distribution = (
            creer_distribution_regions(
                df_mort_regions,
                indicateur_mortinatalite_technique,
                annee_debut,
                annee_fin
            )
        )

        heatmap = creer_heatmap_regions(
            df_mort_regions,
            indicateur_mortinatalite_technique,
            annee_debut,
            annee_fin
        )

        if distribution.empty:

            st.warning(
                "Aucune donnée n'est disponible "
                "pour le boxplot."
            )

        else:

            st.subheader(
                "Distribution des taux régionaux"
            )

            figure_boxplot = px.box(
                distribution,
                x="Année",
                y="Taux",
                points="outliers",
                hover_name="Région",
                title=(
                    f"Distribution régionale de "
                    f"{indicateur_mortinatalite_affiche.lower()}"
                )
            )

            st.plotly_chart(
                figure_boxplot,
                use_container_width=True
            )

            st.markdown(
                """
                Le boxplot permet d'observer :

                - la médiane ;
                - la dispersion des taux ;
                - les valeurs atypiques ;
                - les différences entre les années.
                """
            )

        if heatmap.empty:

            st.warning(
                "Aucune donnée n'est disponible "
                "pour la heatmap."
            )

        else:

            st.subheader(
                "Heatmap des régions et des années"
            )

            matrice = heatmap.pivot(
                index="Région",
                columns="Année",
                values="Taux"
            )

            figure_heatmap = px.imshow(
                matrice,
                aspect="auto",
                labels={
                    "x": "Année",
                    "y": "Région",
                    "color": "Taux"
                },
                title=(
                    f"Heatmap — "
                    f"{indicateur_mortinatalite_affiche}"
                )
            )

            st.plotly_chart(
                figure_heatmap,
                use_container_width=True
            )

            afficher_telechargement(
                heatmap,
                (
                    f"heatmap_regions_"
                    f"{indicateur_mortinatalite_technique}_"
                    f"{annee_debut}_{annee_fin}.csv"
                ),
                "download_heatmap"
            )

    # =====================================================
    # ONGLET 4 — SQL ET SQLITE
    # =====================================================

    with tab_sql:

        st.header(
            "Analyse avec SQL et SQLite"
        )

        annee_sql = st.select_slider(
            "Choisissez l'année de l'analyse SQL",
            options=list(
                range(
                    annee_debut,
                    annee_fin + 1
                )
            ),
            value=annee_fin,
            key="annee_sql"
        )

        nombre_regions = st.slider(
            "Nombre de régions à afficher",
            min_value=5,
            max_value=18,
            value=10,
            key="nombre_regions_sql"
        )

        try:

            (
                requete_classement,
                resultat_classement
            ) = get_requete_classement_regions(
                annee_sql,
                indicateur_mortinatalite_technique,
                nombre_regions
            )

            (
                requete_statistiques,
                resultat_statistiques
            ) = get_statistiques_regions(
                annee_sql,
                indicateur_mortinatalite_technique
            )

        except Exception as erreur:

            st.error(
                "Impossible d'exécuter les requêtes SQL."
            )

            st.code(str(erreur))
            return

        st.subheader(
            "Requête SQL de classement"
        )

        st.code(
            requete_classement,
            language="sql"
        )

        st.dataframe(
            resultat_classement,
            use_container_width=True,
            hide_index=True
        )

        if not resultat_classement.empty:

            figure_sql = px.bar(
                resultat_classement.sort_values(
                    "valeur",
                    ascending=True
                ),
                x="valeur",
                y="region",
                orientation="h",
                title=(
                    f"Classement SQL des régions "
                    f"en {annee_sql}"
                )
            )

            figure_sql.update_layout(
                xaxis_title="Taux",
                yaxis_title="Région"
            )

            st.plotly_chart(
                figure_sql,
                use_container_width=True
            )

        st.subheader(
            "Requête SQL de statistiques"
        )

        st.code(
            requete_statistiques,
            language="sql"
        )

        st.dataframe(
            resultat_statistiques,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            """
            Cette section présente une chaîne complète :

            1. exécution d'une requête dans SQLite ;
            2. récupération du résultat avec Pandas ;
            3. affichage dans Streamlit ;
            4. visualisation interactive avec Plotly.
            """
        )

        afficher_telechargement(
            resultat_classement,
            (
                f"classement_sql_regions_"
                f"{annee_sql}.csv"
            ),
            "download_resultat_sql"
        )