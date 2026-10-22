import logging
# =====================================================
# PAGE NAISSANCES — PERINATAL DASHBOARD FRANCE
# =====================================================

import re

import pandas as pd
import plotly.express as px
import streamlit as st

from src.controllers.naissances_controller import get_data_naissances
from src.models.session import get_current_user, protected_download_button
from src.router import redirect


# =====================================================
# CONFIGURATION DES INDICATEURS
# =====================================================

INDICATEURS = {
    "Naissances totales": "naissances_totales",
    "Naissances vivantes": "naissances_vivantes"
}


# =====================================================
# FONCTIONS DE PRÉPARATION
# =====================================================

def trouver_colonne_geographique(dataframe: pd.DataFrame):
    """
    Recherche la colonne qui contient le nom de la région
    ou du département.

    Les colonnes annuelles commencent par une année,
    par exemple : 2023_naissances_totales.
    """

    colonnes_geographiques = [
        colonne
        for colonne in dataframe.columns
        if not re.match(r"^\d{4}_", str(colonne))
    ]

    if not colonnes_geographiques:
        return None

    return colonnes_geographiques[0]


def obtenir_annees(dataframe: pd.DataFrame):
    """
    Récupère les années disponibles dans les colonnes
    de naissances totales.
    """

    annees = []

    for colonne in dataframe.columns:

        correspondance = re.match(
            r"^(\d{4})_naissances_totales$",
            str(colonne)
        )

        if correspondance:
            annees.append(
                int(correspondance.group(1))
            )

    return sorted(set(annees))


def filtrer_periode(
    dataframe: pd.DataFrame,
    annee_debut: int,
    annee_fin: int
):
    """
    Filtre un tableau déjà transformé au format annuel.
    """

    return dataframe[
        dataframe["Année"].between(
            annee_debut,
            annee_fin
        )
    ].copy()


def preparer_evolution_france(
    dataframe: pd.DataFrame,
    indicateur_technique: str
):
    """
    Transforme les données France entière en tableau annuel.

    Résultat :
    Année | Nombre de naissances
    """

    if dataframe.empty:
        return pd.DataFrame(columns=["Année", "Nombre de naissances"])
    annees = obtenir_annees(dataframe)
    resultats = []

    for annee in annees:

        colonne = f"{annee}_{indicateur_technique}"

        if colonne not in dataframe.columns:
            continue

        valeur = pd.to_numeric(
            dataframe[colonne].iloc[0],
            errors="coerce"
        )

        resultats.append(
            {
                "Année": annee,
                "Nombre de naissances": valeur
            }
        )

    resultat = pd.DataFrame(resultats, columns=["Année", "Nombre de naissances"])

    return resultat.dropna(
        subset=["Nombre de naissances"]
    )


def preparer_comparaison_annee(
    dataframe: pd.DataFrame,
    colonne_geographique: str,
    annee: int,
    indicateur_technique: str
):
    """
    Prépare le classement des territoires pour
    une année et un indicateur.
    """

    colonne_valeur = (
        f"{annee}_{indicateur_technique}"
    )

    if colonne_valeur not in dataframe.columns:
        return pd.DataFrame()

    resultat = dataframe[
        [
            colonne_geographique,
            colonne_valeur
        ]
    ].copy()

    resultat[colonne_valeur] = pd.to_numeric(
        resultat[colonne_valeur],
        errors="coerce"
    )

    resultat = resultat.dropna(
        subset=[
            colonne_geographique,
            colonne_valeur
        ]
    )

    resultat = resultat.rename(
        columns={
            colonne_geographique: "Territoire",
            colonne_valeur: "Nombre de naissances"
        }
    )

    return resultat.sort_values(
        by="Nombre de naissances",
        ascending=False
    )


def preparer_evolution_territoires(
    dataframe: pd.DataFrame,
    colonne_geographique: str,
    territoires_selectionnes: list,
    indicateur_technique: str
):
    """
    Prépare l'évolution de plusieurs régions
    ou départements sur toute la période.
    """

    annees = obtenir_annees(dataframe)
    resultats = []

    for territoire in territoires_selectionnes:

        lignes = dataframe[
            dataframe[colonne_geographique]
            .astype(str)
            == str(territoire)
        ]

        if lignes.empty:
            continue

        ligne = lignes.iloc[0]

        for annee in annees:

            colonne = (
                f"{annee}_{indicateur_technique}"
            )

            if colonne not in dataframe.columns:
                continue

            valeur = pd.to_numeric(
                ligne[colonne],
                errors="coerce"
            )

            resultats.append(
                {
                    "Année": annee,
                    "Territoire": territoire,
                    "Nombre de naissances": valeur
                }
            )

    resultat = pd.DataFrame(resultats)

    if resultat.empty:
        return resultat

    return resultat.dropna(
        subset=["Nombre de naissances"]
    )


def calculer_variation(
    valeur_initiale,
    valeur_finale
):
    """
    Calcule la variation en pourcentage
    entre deux valeurs.
    """

    if (
        pd.isna(valeur_initiale)
        or pd.isna(valeur_finale)
        or valeur_initiale == 0
    ):
        return None

    return (
        (valeur_finale - valeur_initiale)
        / valeur_initiale
    ) * 100


def formater_nombre(valeur):
    """
    Affiche les grands nombres avec des espaces.
    """

    if pd.isna(valeur):
        return "Non disponible"

    return f"{valeur:,.0f}".replace(",", " ")


def preparer_export_naissances(dataframe: pd.DataFrame):
    """
    Prépare un fichier CSV lisible et compatible avec Excel :
    - séparateur point-virgule ;
    - nombres de naissances sans décimales ;
    - années converties en entiers ;
    - autres nombres arrondis à deux décimales.
    """

    export = dataframe.copy()

    for colonne in export.select_dtypes(include="number").columns:
        nom_colonne = str(colonne).lower()

        if (
            colonne == "Année"
            or "naissance" in nom_colonne
            or colonne in {"Valeur début", "Valeur fin"}
        ):
            export[colonne] = pd.to_numeric(
                export[colonne],
                errors="coerce"
            ).round(0).astype("Int64")
        else:
            export[colonne] = pd.to_numeric(
                export[colonne],
                errors="coerce"
            ).round(2)

    return export


def afficher_telechargement(
    dataframe: pd.DataFrame,
    nom_fichier: str,
    cle_bouton: str
):
    """
    Autorise le téléchargement uniquement
    pour les utilisateurs connectés.
    """

    st.divider()
    st.subheader("Téléchargement des données")

    utilisateur_connecte = get_current_user()

    if utilisateur_connecte:

        dataframe_export = preparer_export_naissances(
            dataframe
        )

        contenu_csv = dataframe_export.to_csv(
            index=False,
            sep=";",
            decimal=","
        ).encode("utf-8-sig")

        st.success(
            f"Utilisateur connecté : "
            f"{utilisateur_connecte}"
        )

        protected_download_button(
            label=(
                "Télécharger les données affichées "
                "au format CSV"
            ),
            data=contenu_csv,
            file_name=nom_fichier,
            mime="text/csv",
            key=cle_bouton,
            width="stretch"
        )

    else:

        st.info(
            "La consultation des résultats est libre. "
            "Une connexion est nécessaire uniquement "
            "pour télécharger les données."
        )

        if st.button(
            "Se connecter pour télécharger",
            key=f"connexion_{cle_bouton}",
            width="stretch"
        ):
            # Mémorise la page Naissances afin d'y revenir
            # automatiquement après la connexion.
            st.session_state[
                "page_apres_connexion"
            ] = "/naissances"

            redirect(
                "/login",
                reload=True
            )


# =====================================================
# AFFICHAGE FRANCE ENTIÈRE
# =====================================================

def afficher_france(
    dataframe: pd.DataFrame,
    indicateur_affiche: str,
    indicateur_technique: str,
    annee_debut: int,
    annee_fin: int
):
    """
    Affiche l'analyse des naissances
    pour la France entière.
    """

    evolution = preparer_evolution_france(
        dataframe,
        indicateur_technique
    )

    evolution = filtrer_periode(
        evolution,
        annee_debut,
        annee_fin
    )

    if evolution.empty:
        st.warning(
            "Aucune donnée n'est disponible "
            "pour la période sélectionnée."
        )
        return

    valeur_initiale = evolution.iloc[0][
        "Nombre de naissances"
    ]

    valeur_finale = evolution.iloc[-1][
        "Nombre de naissances"
    ]

    variation = calculer_variation(
        valeur_initiale,
        valeur_finale
    )

    valeur_maximale = evolution[
        "Nombre de naissances"
    ].max()

    annee_maximale = int(
        evolution.loc[
            evolution["Nombre de naissances"].idxmax(),
            "Année"
        ]
    )

    st.header("France entière")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            f"Valeur en {annee_debut}",
            formater_nombre(valeur_initiale)
        )

    with col2:
        st.metric(
            f"Valeur en {annee_fin}",
            formater_nombre(valeur_finale)
        )

    with col3:
        st.metric(
            "Évolution",
            (
                f"{variation:+.1f} %"
                if variation is not None
                else "Non disponible"
            )
        )

    with col4:
        st.metric(
            "Maximum de la période",
            formater_nombre(valeur_maximale),
            f"Année {annee_maximale}"
        )

    st.subheader(
        f"Évolution des {indicateur_affiche.lower()}"
    )

    figure = px.line(
        evolution,
        x="Année",
        y="Nombre de naissances",
        markers=True,
        title=(
            f"{indicateur_affiche} en France "
            f"de {annee_debut} à {annee_fin}"
        )
    )

    figure.update_layout(
        xaxis_title="Année",
        yaxis_title="Nombre de naissances",
        hovermode="x unified"
    )

    figure.update_traces(
        hovertemplate=(
            "Année : %{x}<br>"
            "Naissances : %{y:,.0f}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        figure,
        width="stretch"
    )

    st.markdown(
        f"""
        **Interprétation :** sur la période sélectionnée
        de **{annee_debut} à {annee_fin}**, la variation
        des {indicateur_affiche.lower()} est de
        **{variation:+.1f} %**.
        """
        if variation is not None
        else """
        **Interprétation :** la courbe permet d'observer
        l'évolution des naissances sur la période choisie.
        """
    )

    st.subheader("Tableau des résultats")

    st.dataframe(
        evolution,
        width="stretch",
        hide_index=True
    )

    export_france = evolution.rename(
        columns={
            "Nombre de naissances": indicateur_affiche
        }
    ).copy()

    export_france.insert(
        1,
        "Niveau géographique",
        "France entière"
    )

    afficher_telechargement(
        export_france,
        (
            f"naissances_france_"
            f"{indicateur_technique}_"
            f"{annee_debut}_{annee_fin}.csv"
        ),
        "download_naissances_france"
    )


# =====================================================
# AFFICHAGE RÉGIONS OU DÉPARTEMENTS
# =====================================================

def afficher_territoires(
    dataframe: pd.DataFrame,
    niveau_geographique: str,
    indicateur_affiche: str,
    indicateur_technique: str,
    annee_debut: int,
    annee_fin: int
):
    """
    Affiche les analyses régionales ou départementales.
    """

    colonne_geographique = trouver_colonne_geographique(
        dataframe
    )

    if colonne_geographique is None:
        st.error(
            "La colonne géographique n'a pas été trouvée."
        )
        return

    if niveau_geographique == "Régions":
        nom_niveau = "région"
        nom_niveau_pluriel = "régions"
        nom_fichier = "regions"

    else:
        nom_niveau = "département"
        nom_niveau_pluriel = "départements"
        nom_fichier = "departements"

    st.header(
        f"Analyse par {nom_niveau}"
    )

    mode_analyse = st.radio(
        "Type d'analyse",
        [
            "Classement pour une année",
            "Évolution et comparaison de territoires"
        ],
        horizontal=True,
        key=f"mode_{nom_fichier}"
    )

    # =================================================
    # MODE 1 : CLASSEMENT POUR UNE ANNÉE
    # =================================================

    if mode_analyse == "Classement pour une année":

        annees_intervalle = list(
            range(
                annee_debut,
                annee_fin + 1
            )
        )

        annee_classement = st.select_slider(
            "Choisissez l'année du classement",
            options=annees_intervalle,
            value=annee_fin,
            key=f"annee_classement_{nom_fichier}"
        )

        comparaison = preparer_comparaison_annee(
            dataframe,
            colonne_geographique,
            annee_classement,
            indicateur_technique
        )

        if comparaison.empty:
            st.warning(
                "Aucune donnée n'est disponible "
                "pour cette sélection."
            )
            return

        nombre_maximum = min(
            30,
            len(comparaison)
        )

        nombre_territoires = st.slider(
            f"Nombre de {nom_niveau_pluriel} à afficher",
            min_value=5,
            max_value=nombre_maximum,
            value=min(15, nombre_maximum),
            key=f"nombre_{nom_fichier}"
        )

        valeur_totale = comparaison[
            "Nombre de naissances"
        ].sum()

        valeur_moyenne = comparaison[
            "Nombre de naissances"
        ].mean()

        territoire_maximum = comparaison.iloc[0][
            "Territoire"
        ]

        valeur_maximum = comparaison.iloc[0][
            "Nombre de naissances"
        ]

        territoire_minimum = comparaison.iloc[-1][
            "Territoire"
        ]

        valeur_minimum = comparaison.iloc[-1][
            "Nombre de naissances"
        ]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                f"Total en {annee_classement}",
                formater_nombre(valeur_totale)
            )

        with col2:
            st.metric(
                f"Moyenne par {nom_niveau}",
                formater_nombre(valeur_moyenne)
            )

        with col3:
            st.metric(
                f"{nom_niveau.capitalize()} en tête",
                str(territoire_maximum),
                formater_nombre(valeur_maximum)
            )

        with col4:
            st.metric(
                "Valeur la plus faible",
                str(territoire_minimum),
                formater_nombre(valeur_minimum)
            )

        comparaison_affichee = comparaison.head(
            nombre_territoires
        )

        st.subheader(
            f"Classement des {nom_niveau_pluriel}"
        )

        figure_barres = px.bar(
            comparaison_affichee.sort_values(
                by="Nombre de naissances",
                ascending=True
            ),
            x="Nombre de naissances",
            y="Territoire",
            orientation="h",
            text_auto=".3s",
            title=(
                f"{indicateur_affiche} par "
                f"{nom_niveau} en {annee_classement}"
            )
        )

        figure_barres.update_layout(
            xaxis_title="Nombre de naissances",
            yaxis_title=nom_niveau.capitalize(),
            height=max(
                500,
                nombre_territoires * 32
            )
        )

        st.plotly_chart(
            figure_barres,
            width="stretch"
        )

        st.subheader("Tableau du classement")

        st.dataframe(
            comparaison,
            width="stretch",
            hide_index=True
        )

        export_classement = comparaison.rename(
            columns={
                "Nombre de naissances": indicateur_affiche
            }
        ).copy()

        export_classement.insert(
            0,
            "Rang",
            range(1, len(export_classement) + 1)
        )
        export_classement.insert(
            1,
            "Année",
            annee_classement
        )
        export_classement.insert(
            2,
            "Niveau géographique",
            nom_niveau.capitalize()
        )

        afficher_telechargement(
            export_classement,
            (
                f"naissances_{nom_fichier}_"
                f"{indicateur_technique}_"
                f"{annee_classement}.csv"
            ),
            f"download_classement_{nom_fichier}"
        )

    # =================================================
    # MODE 2 : COMPARAISON DE TERRITOIRES
    # =================================================

    else:

        territoires_disponibles = sorted(
            dataframe[colonne_geographique]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        territoires_par_defaut = (
            territoires_disponibles[:3]
            if len(territoires_disponibles) >= 3
            else territoires_disponibles
        )

        territoires_selectionnes = st.multiselect(
            f"Choisissez les {nom_niveau_pluriel} à comparer",
            options=territoires_disponibles,
            default=territoires_par_defaut,
            max_selections=5,
            key=f"territoires_{nom_fichier}"
        )

        if not territoires_selectionnes:
            st.info(
                f"Sélectionnez au moins un {nom_niveau}."
            )
            return

        evolution = preparer_evolution_territoires(
            dataframe,
            colonne_geographique,
            territoires_selectionnes,
            indicateur_technique
        )

        if evolution.empty:
            st.warning(
                "Aucune donnée n'est disponible "
                "pour les territoires sélectionnés."
            )
            return

        evolution = filtrer_periode(
            evolution,
            annee_debut,
            annee_fin
        )

        st.subheader(
            f"Comparaison des {nom_niveau_pluriel}"
        )

        figure_comparaison = px.line(
            evolution,
            x="Année",
            y="Nombre de naissances",
            color="Territoire",
            markers=True,
            title=(
                f"Comparaison des {indicateur_affiche.lower()} "
                f"de {annee_debut} à {annee_fin}"
            )
        )

        figure_comparaison.update_layout(
            xaxis_title="Année",
            yaxis_title="Nombre de naissances",
            legend_title=nom_niveau.capitalize(),
            hovermode="x unified"
        )

        st.plotly_chart(
            figure_comparaison,
            width="stretch"
        )

        # Comparaison entre début et fin de période
        synthese = []

        for territoire in territoires_selectionnes:

            donnees_territoire = evolution[
                evolution["Territoire"] == territoire
            ].sort_values("Année")

            if donnees_territoire.empty:
                continue

            valeur_debut = donnees_territoire.iloc[0][
                "Nombre de naissances"
            ]

            valeur_fin = donnees_territoire.iloc[-1][
                "Nombre de naissances"
            ]

            variation = calculer_variation(
                valeur_debut,
                valeur_fin
            )

            synthese.append(
                {
                    "Territoire": territoire,
                    "Valeur début": valeur_debut,
                    "Valeur fin": valeur_fin,
                    "Variation (%)": variation
                }
            )

        tableau_synthese = pd.DataFrame(
            synthese
        )

        st.subheader(
            "Synthèse de la période"
        )

        st.dataframe(
            tableau_synthese,
            width="stretch",
            hide_index=True,
            column_config={
                "Valeur début": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Valeur fin": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Variation (%)": st.column_config.NumberColumn(
                    format="%.1f %%"
                )
            }
        )

        with st.expander(
            "Afficher toutes les données utilisées"
        ):
            st.dataframe(
                evolution,
                width="stretch",
                hide_index=True
            )

        export_comparaison = evolution.rename(
            columns={
                "Nombre de naissances": indicateur_affiche
            }
        ).copy()

        export_comparaison.insert(
            1,
            "Niveau géographique",
            nom_niveau.capitalize()
        )

        afficher_telechargement(
            export_comparaison,
            (
                f"comparaison_naissances_"
                f"{nom_fichier}_"
                f"{indicateur_technique}_"
                f"{annee_debut}_{annee_fin}.csv"
            ),
            f"download_comparaison_{nom_fichier}"
        )


# =====================================================
# VUE PRINCIPALE
# =====================================================

def load_view():
    """
    Affiche la page interactive complète
    consacrée aux naissances.
    """

    st.title("Analyse des naissances en France")

    st.markdown(
        """
        Cette page permet d'explorer les données de naissances
        entre **2012 et 2023**.

        Utilisez les filtres pour choisir :

        - le niveau géographique ;
        - le type de naissances ;
        - une période d'étude ;
        - une année de classement ;
        - un ou plusieurs territoires à comparer.
        """
    )

    # =====================================================
    # CHARGEMENT DES DONNÉES
    # =====================================================

    try:
        df_france, df_regions, df_departements = (
            get_data_naissances()
        )

    except FileNotFoundError as erreur:
        st.error(
            "Un fichier de naissances est introuvable."
        )
        logging.getLogger(__name__).exception("Erreur de traitement des données")
        return

    except Exception as erreur:
        st.error(
            "Une erreur est survenue pendant "
            "le chargement des données."
        )
        logging.getLogger(__name__).exception("Erreur de traitement des données")
        return

    annees = obtenir_annees(df_france)

    if not annees:
        st.error(
            "Aucune année n'a été trouvée "
            "dans les données de naissances."
        )
        return

    # =====================================================
    # FILTRES GÉNÉRAUX DANS LA BARRE LATÉRALE
    # =====================================================

    st.sidebar.header("Filtres — Naissances")

    niveau_geographique = st.sidebar.selectbox(
        "Niveau géographique",
        [
            "France entière",
            "Régions",
            "Départements"
        ],
        key="niveau_naissances"
    )

    indicateur_affiche = st.sidebar.selectbox(
        "Indicateur",
        list(INDICATEURS.keys()),
        key="indicateur_naissances"
    )

    indicateur_technique = INDICATEURS[
        indicateur_affiche
    ]

    annee_debut, annee_fin = st.sidebar.select_slider(
        "Période étudiée",
        options=annees,
        value=(
            annees[0],
            annees[-1]
        ),
        key="periode_naissances"
    )

    st.sidebar.caption(
        f"Période sélectionnée : "
        f"{annee_debut} à {annee_fin}"
    )

    # =====================================================
    # AFFICHAGE SELON LE NIVEAU
    # =====================================================

    if niveau_geographique == "France entière":

        afficher_france(
            df_france,
            indicateur_affiche,
            indicateur_technique,
            annee_debut,
            annee_fin
        )

    elif niveau_geographique == "Régions":

        afficher_territoires(
            df_regions,
            niveau_geographique,
            indicateur_affiche,
            indicateur_technique,
            annee_debut,
            annee_fin
        )

    else:

        afficher_territoires(
            df_departements,
            niveau_geographique,
            indicateur_affiche,
            indicateur_technique,
            annee_debut,
            annee_fin
        )