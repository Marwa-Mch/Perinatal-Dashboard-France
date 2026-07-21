# =====================================================
# PAGE MORTINATALITÉ — PERINATAL DASHBOARD FRANCE
# =====================================================

from io import BytesIO
import zipfile

import pandas as pd
import plotly.express as px
import streamlit as st

from src.controllers.mortinatalite_controller import (
    get_data_mortinatalite
)
from src.models.session import get_current_user
from src.router import redirect


# =====================================================
# CONFIGURATION DES INDICATEURS
# =====================================================

INDICATEURS = {
    "Mortinatalité totale": "mortinatalite_totale",
    "Mortinatalité spontanée": "mortinatalite_spontanee",
    "IMG": "img"
}


# =====================================================
# FONCTIONS DE PRÉPARATION
# =====================================================

def obtenir_annees(dataframe: pd.DataFrame):
    """
    Récupère les années disponibles dans les colonnes
    de mortinatalité totale.
    """

    annees = []

    for colonne in dataframe.columns:

        if str(colonne).endswith("_mortinatalite_totale"):

            annee = str(colonne).split("_")[0]

            if annee.isdigit():
                annees.append(int(annee))

    return sorted(set(annees))


def trouver_colonne_effectif(
    dataframe: pd.DataFrame,
    annee: int
):
    """
    Recherche la colonne correspondant aux effectifs
    de naissances.

    En 2013, la colonne est écrite au pluriel :
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


def filtrer_periode(
    dataframe: pd.DataFrame,
    annee_debut: int,
    annee_fin: int
):
    """
    Filtre un tableau annuel selon l'intervalle choisi.
    """

    return dataframe[
        dataframe["Année"].between(
            annee_debut,
            annee_fin
        )
    ].copy()


def preparer_evolution_zone(
    dataframe: pd.DataFrame
):
    """
    Transforme une ligne géographique en tableau annuel.

    Résultat :
    Année | Mortinatalité totale | Mortinatalité spontanée
    | IMG | Effectif des naissances
    """

    annees = obtenir_annees(dataframe)
    resultats = []

    if dataframe.empty:
        return pd.DataFrame()

    ligne = dataframe.iloc[0]

    for annee in annees:

        colonne_totale = (
            f"{annee}_mortinatalite_totale"
        )

        colonne_spontanee = (
            f"{annee}_mortinatalite_spontanee"
        )

        colonne_img = f"{annee}_img"

        colonne_effectif = trouver_colonne_effectif(
            dataframe,
            annee
        )

        resultats.append(
            {
                "Année": annee,

                "Mortinatalité totale": pd.to_numeric(
                    ligne.get(colonne_totale),
                    errors="coerce"
                ),

                "Mortinatalité spontanée": pd.to_numeric(
                    ligne.get(colonne_spontanee),
                    errors="coerce"
                ),

                "IMG": pd.to_numeric(
                    ligne.get(colonne_img),
                    errors="coerce"
                ),

                "Effectif des naissances": (
                    pd.to_numeric(
                        ligne.get(colonne_effectif),
                        errors="coerce"
                    )
                    if colonne_effectif
                    else None
                )
            }
        )

    return pd.DataFrame(resultats)


def preparer_classement(
    dataframe: pd.DataFrame,
    annee: int,
    indicateur_technique: str
):
    """
    Prépare le classement des régions ou des DROM
    pour une année donnée.
    """

    colonne = (
        f"{annee}_{indicateur_technique}"
    )

    if colonne not in dataframe.columns:
        return pd.DataFrame()

    resultat = dataframe[
        [
            "zone_geographique",
            colonne
        ]
    ].copy()

    resultat[colonne] = pd.to_numeric(
        resultat[colonne],
        errors="coerce"
    )

    resultat = resultat.dropna(
        subset=[
            "zone_geographique",
            colonne
        ]
    )

    resultat = resultat.rename(
        columns={
            "zone_geographique": "Territoire",
            colonne: "Taux"
        }
    )

    return resultat.sort_values(
        by="Taux",
        ascending=False
    )


def preparer_comparaison_territoires(
    dataframe: pd.DataFrame,
    territoires_selectionnes: list,
    indicateur_affiche: str
):
    """
    Prépare l'évolution de plusieurs régions
    ou DROM pour les comparer.
    """

    resultats = []

    for territoire in territoires_selectionnes:

        ligne_territoire = dataframe[
            dataframe["zone_geographique"].astype(str)
            == str(territoire)
        ]

        if ligne_territoire.empty:
            continue

        evolution = preparer_evolution_zone(
            ligne_territoire
        )

        if evolution.empty:
            continue

        for _, ligne in evolution.iterrows():

            resultats.append(
                {
                    "Année": ligne["Année"],
                    "Territoire": territoire,
                    "Taux": ligne[indicateur_affiche]
                }
            )

    resultat = pd.DataFrame(resultats)

    if resultat.empty:
        return resultat

    return resultat.dropna(
        subset=["Taux"]
    )


def calculer_variation(
    valeur_initiale,
    valeur_finale
):
    """
    Calcule la différence en points entre
    la première et la dernière année.
    """

    if (
        pd.isna(valeur_initiale)
        or pd.isna(valeur_finale)
    ):
        return None

    return valeur_finale - valeur_initiale


def afficher_telechargement(
    dataframe: pd.DataFrame,
    nom_fichier: str,
    cle_bouton: str
):
    """
    Autorise le téléchargement uniquement
    lorsqu'un utilisateur est connecté.
    """

    st.divider()
    st.subheader("Téléchargement des données")

    utilisateur_connecte = get_current_user()

    if utilisateur_connecte:

        dataframe_export = dataframe.copy()

        colonnes_decimales = dataframe_export.select_dtypes(
            include="float"
        ).columns

        dataframe_export[colonnes_decimales] = (
            dataframe_export[colonnes_decimales].round(2)
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

        st.download_button(
            label=(
                "Télécharger les données affichées "
                "au format CSV"
            ),
            data=contenu_csv,
            file_name=nom_fichier,
            mime="text/csv",
            key=cle_bouton,
            use_container_width=True
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
            use_container_width=True
        ):
            st.session_state[
                "page_apres_connexion"
            ] = "/mortinatalite"

            redirect(
                "/login",
                reload=True
            )


def afficher_telechargement_comparaison(
    evolution: pd.DataFrame,
    tableau_synthese: pd.DataFrame,
    niveau_geographique: str,
    indicateur_affiche: str,
    annee_debut: int,
    annee_fin: int,
    nom_fichier: str,
    cle_bouton: str
):
    """
    Télécharge un dossier ZIP contenant deux fichiers :

    1. les données annuelles utilisées pour construire la courbe ;
    2. la synthèse calculée pour la période sélectionnée.
    """

    st.divider()
    st.subheader("Téléchargement des résultats filtrés")

    utilisateur_connecte = get_current_user()

    if utilisateur_connecte:

        donnees_courbe = evolution.copy()

        donnees_courbe.insert(
            1,
            "Niveau géographique",
            niveau_geographique
        )

        donnees_courbe = donnees_courbe.rename(
            columns={
                "Taux": indicateur_affiche
            }
        )

        donnees_courbe[indicateur_affiche] = (
            donnees_courbe[indicateur_affiche].round(2)
        )

        synthese_export = tableau_synthese.copy()

        synthese_export.insert(
            0,
            "Période",
            f"{annee_debut}-{annee_fin}"
        )

        synthese_export.insert(
            1,
            "Niveau géographique",
            niveau_geographique
        )

        colonnes_taux = [
            "Taux au début",
            "Taux à la fin",
            "Variation en points"
        ]

        for colonne in colonnes_taux:
            if colonne in synthese_export.columns:
                synthese_export[colonne] = (
                    synthese_export[colonne].round(2)
                )

        memoire_zip = BytesIO()

        with zipfile.ZipFile(
            memoire_zip,
            mode="w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            archive.writestr(
                "01_donnees_courbe.csv",
                donnees_courbe.to_csv(
                    index=False,
                    sep=";",
                    decimal=","
                ).encode("utf-8-sig")
            )

            archive.writestr(
                "02_synthese_periode.csv",
                synthese_export.to_csv(
                    index=False,
                    sep=";",
                    decimal=","
                ).encode("utf-8-sig")
            )

        st.success(
            f"Utilisateur connecté : {utilisateur_connecte}"
        )

        st.info(
            "Le fichier ZIP contient les données exactes de la courbe "
            "et le tableau de synthèse de la période sélectionnée."
        )

        st.download_button(
            label="Télécharger la courbe et la synthèse",
            data=memoire_zip.getvalue(),
            file_name=nom_fichier,
            mime="application/zip",
            key=cle_bouton,
            use_container_width=True
        )

    else:

        st.info(
            "La consultation des résultats est libre. "
            "Une connexion est nécessaire uniquement "
            "pour télécharger les résultats filtrés."
        )

        if st.button(
            "Se connecter pour télécharger",
            key=f"connexion_{cle_bouton}",
            use_container_width=True
        ):
            st.session_state[
                "page_apres_connexion"
            ] = "/mortinatalite"

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
    annee_debut: int,
    annee_fin: int
):
    """
    Affiche l'analyse nationale de la mortinatalité.
    """

    evolution = preparer_evolution_zone(
        dataframe
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
        indicateur_affiche
    ]

    valeur_finale = evolution.iloc[-1][
        indicateur_affiche
    ]

    variation = calculer_variation(
        valeur_initiale,
        valeur_finale
    )

    valeur_maximale = evolution[
        indicateur_affiche
    ].max()

    valeur_minimale = evolution[
        indicateur_affiche
    ].min()

    annee_maximale = int(
        evolution.loc[
            evolution[indicateur_affiche].idxmax(),
            "Année"
        ]
    )

    annee_minimale = int(
        evolution.loc[
            evolution[indicateur_affiche].idxmin(),
            "Année"
        ]
    )

    st.header("France entière")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            f"Taux en {annee_debut}",
            f"{valeur_initiale:.2f}"
        )

    with col2:
        st.metric(
            f"Taux en {annee_fin}",
            f"{valeur_finale:.2f}"
        )

    with col3:
        st.metric(
            "Variation",
            (
                f"{variation:+.2f} point(s)"
                if variation is not None
                else "Non disponible"
            )
        )

    with col4:
        st.metric(
            "Maximum de la période",
            f"{valeur_maximale:.2f}",
            f"Année {annee_maximale}"
        )

    st.subheader(
        f"Évolution de la {indicateur_affiche.lower()}"
    )

    figure = px.line(
        evolution,
        x="Année",
        y=indicateur_affiche,
        markers=True,
        title=(
            f"{indicateur_affiche} en France "
            f"de {annee_debut} à {annee_fin}"
        )
    )

    figure.update_layout(
        xaxis_title="Année",
        yaxis_title="Taux",
        hovermode="x unified"
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    st.markdown(
        f"""
        **Interprétation :** entre **{annee_debut}**
        et **{annee_fin}**, le taux a varié de
        **{variation:+.2f} point(s)**.

        La valeur maximale est observée en
        **{annee_maximale}** et la valeur minimale
        en **{annee_minimale}**.
        """
        if variation is not None
        else """
        **Interprétation :** la courbe permet
        d'observer l'évolution de l'indicateur
        sur la période sélectionnée.
        """
    )

    # =================================================
    # COMPARAISON DES TROIS COMPOSANTES
    # =================================================

    st.subheader(
        "Comparaison des composantes de la mortinatalité"
    )

    evolution_longue = evolution.melt(
        id_vars="Année",
        value_vars=[
            "Mortinatalité totale",
            "Mortinatalité spontanée",
            "IMG"
        ],
        var_name="Indicateur",
        value_name="Taux"
    )

    evolution_longue = evolution_longue.dropna(
        subset=["Taux"]
    )

    figure_composantes = px.line(
        evolution_longue,
        x="Année",
        y="Taux",
        color="Indicateur",
        markers=True,
        title=(
            "Évolution comparée des composantes "
            f"de {annee_debut} à {annee_fin}"
        )
    )

    figure_composantes.update_layout(
        xaxis_title="Année",
        yaxis_title="Taux",
        hovermode="x unified"
    )

    st.plotly_chart(
        figure_composantes,
        use_container_width=True
    )

    st.subheader("Tableau des résultats")

    st.dataframe(
        evolution,
        use_container_width=True,
        hide_index=True
    )

    afficher_telechargement(
        evolution,
        (
            f"mortinatalite_france_"
            f"{annee_debut}_{annee_fin}.csv"
        ),
        "download_mortinatalite_france"
    )


# =====================================================
# AFFICHAGE RÉGIONS OU DROM
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
    Affiche les analyses des régions ou des DROM.
    """

    if niveau_geographique == "Régions":

        nom_niveau = "région"
        nom_niveau_pluriel = "régions"
        nom_fichier = "regions"

    else:

        nom_niveau = "DROM"
        nom_niveau_pluriel = "DROM"
        nom_fichier = "drom"

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
        key=f"mode_mortinatalite_{nom_fichier}"
    )

    # =================================================
    # CLASSEMENT POUR UNE ANNÉE
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
            key=f"annee_classement_mortinatalite_{nom_fichier}"
        )

        classement = preparer_classement(
            dataframe,
            annee_classement,
            indicateur_technique
        )

        if classement.empty:
            st.warning(
                "Aucune donnée n'est disponible "
                "pour cette sélection."
            )
            return

        valeur_moyenne = classement["Taux"].mean()
        valeur_mediane = classement["Taux"].median()

        territoire_maximum = classement.iloc[0][
            "Territoire"
        ]

        valeur_maximum = classement.iloc[0][
            "Taux"
        ]

        territoire_minimum = classement.iloc[-1][
            "Territoire"
        ]

        valeur_minimum = classement.iloc[-1][
            "Taux"
        ]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Taux moyen",
                f"{valeur_moyenne:.2f}"
            )

        with col2:
            st.metric(
                "Taux médian",
                f"{valeur_mediane:.2f}"
            )

        with col3:
            st.metric(
                "Valeur la plus élevée",
                str(territoire_maximum),
                f"{valeur_maximum:.2f}"
            )

        with col4:
            st.metric(
                "Valeur la plus faible",
                str(territoire_minimum),
                f"{valeur_minimum:.2f}"
            )

        st.subheader(
            f"Classement des {nom_niveau_pluriel}"
        )

        figure_barres = px.bar(
            classement.sort_values(
                by="Taux",
                ascending=True
            ),
            x="Taux",
            y="Territoire",
            orientation="h",
            text_auto=".2f",
            title=(
                f"{indicateur_affiche} par "
                f"{nom_niveau} en {annee_classement}"
            )
        )

        figure_barres.update_layout(
            xaxis_title="Taux",
            yaxis_title=nom_niveau.capitalize(),
            height=max(
                450,
                len(classement) * 34
            )
        )

        st.plotly_chart(
            figure_barres,
            use_container_width=True
        )

        st.subheader("Tableau du classement")

        st.dataframe(
            classement,
            use_container_width=True,
            hide_index=True
        )

        afficher_telechargement(
            classement,
            (
                f"mortinatalite_{nom_fichier}_"
                f"{indicateur_technique}_"
                f"{annee_classement}.csv"
            ),
            f"download_classement_mortinatalite_{nom_fichier}"
        )

    # =================================================
    # COMPARAISON DE PLUSIEURS TERRITOIRES
    # =================================================

    else:

        territoires_disponibles = sorted(
            dataframe["zone_geographique"]
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
            key=f"comparaison_mortinatalite_{nom_fichier}"
        )

        st.caption(
            "Vous pouvez sélectionner autant de territoires que nécessaire. "
            "Pour garder une courbe lisible, une sélection raisonnable "
            "reste toutefois préférable."
        )

        if not territoires_selectionnes:
            st.info(
                f"Sélectionnez au moins un {nom_niveau}."
            )
            return

        evolution = preparer_comparaison_territoires(
            dataframe,
            territoires_selectionnes,
            indicateur_affiche
        )

        evolution = filtrer_periode(
            evolution,
            annee_debut,
            annee_fin
        )

        if evolution.empty:
            st.warning(
                "Aucune donnée n'est disponible "
                "pour les territoires sélectionnés."
            )
            return

        st.subheader(
            f"Comparaison des {nom_niveau_pluriel}"
        )

        figure_comparaison = px.line(
            evolution,
            x="Année",
            y="Taux",
            color="Territoire",
            markers=True,
            title=(
                f"{indicateur_affiche} de "
                f"{annee_debut} à {annee_fin}"
            )
        )

        figure_comparaison.update_layout(
            xaxis_title="Année",
            yaxis_title="Taux",
            legend_title=nom_niveau.capitalize(),
            hovermode="x unified"
        )

        st.plotly_chart(
            figure_comparaison,
            use_container_width=True
        )

        # =================================================
        # TABLEAU DE SYNTHÈSE
        # =================================================

        synthese = []

        for territoire in territoires_selectionnes:

            donnees_territoire = evolution[
                evolution["Territoire"] == territoire
            ].sort_values("Année")

            if donnees_territoire.empty:
                continue

            valeur_debut = donnees_territoire.iloc[0][
                "Taux"
            ]

            valeur_fin = donnees_territoire.iloc[-1][
                "Taux"
            ]

            variation = calculer_variation(
                valeur_debut,
                valeur_fin
            )

            synthese.append(
                {
                    "Territoire": territoire,
                    "Taux au début": valeur_debut,
                    "Taux à la fin": valeur_fin,
                    "Variation en points": variation
                }
            )

        tableau_synthese = pd.DataFrame(
            synthese
        )

        st.subheader("Synthèse de la période")

        st.dataframe(
            tableau_synthese,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Taux au début": st.column_config.NumberColumn(
                    format="%.2f"
                ),
                "Taux à la fin": st.column_config.NumberColumn(
                    format="%.2f"
                ),
                "Variation en points": st.column_config.NumberColumn(
                    format="%+.2f"
                )
            }
        )

        with st.expander(
            "Afficher toutes les données utilisées"
        ):
            st.dataframe(
                evolution,
                use_container_width=True,
                hide_index=True
            )

        afficher_telechargement_comparaison(
            evolution=evolution,
            tableau_synthese=tableau_synthese,
            niveau_geographique=niveau_geographique,
            indicateur_affiche=indicateur_affiche,
            annee_debut=annee_debut,
            annee_fin=annee_fin,
            nom_fichier=(
                f"comparaison_mortinatalite_"
                f"{nom_fichier}_"
                f"{indicateur_technique}_"
                f"{annee_debut}_{annee_fin}.zip"
            ),
            cle_bouton=(
                f"download_comparaison_mortinatalite_"
                f"{nom_fichier}"
            )
        )


# =====================================================
# VUE PRINCIPALE
# =====================================================

def load_view():
    """
    Affiche la page interactive complète
    consacrée à la mortinatalité.
    """

    st.title("Analyse de la mortinatalité en France")

    st.markdown(
        """
        Cette page permet d'étudier les indicateurs de
        mortinatalité entre **2012 et 2023**.

        Utilisez les filtres pour sélectionner :

        - le niveau géographique ;
        - l'indicateur ;
        - une période d'étude ;
        - une année de classement ;
        - plusieurs territoires à comparer.
        """
    )

    # =====================================================
    # CHARGEMENT DES DONNÉES
    # =====================================================

    try:

        df_france, df_regions, df_drom = (
            get_data_mortinatalite()
        )

    except FileNotFoundError as erreur:

        st.error(
            "Un fichier de mortinatalité est introuvable."
        )
        st.code(str(erreur))
        return

    except Exception as erreur:

        st.error(
            "Une erreur est survenue pendant "
            "le chargement des données."
        )
        st.code(str(erreur))
        return

    annees = obtenir_annees(
        df_france
    )

    if not annees:
        st.error(
            "Aucune année n'a été trouvée "
            "dans les données de mortinatalité."
        )
        return

    # =====================================================
    # FILTRES GÉNÉRAUX
    # =====================================================

    st.sidebar.header(
        "Filtres — Mortinatalité"
    )

    niveau_geographique = st.sidebar.selectbox(
        "Niveau géographique",
        [
            "France entière",
            "Régions",
            "DROM"
        ],
        key="niveau_mortinatalite"
    )

    indicateur_affiche = st.sidebar.selectbox(
        "Indicateur",
        list(INDICATEURS.keys()),
        key="indicateur_mortinatalite"
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
        key="periode_mortinatalite"
    )

    st.sidebar.caption(
        f"Période sélectionnée : "
        f"{annee_debut} à {annee_fin}"
    )

    # =====================================================
    # AFFICHAGE DU NIVEAU CHOISI
    # =====================================================

    if niveau_geographique == "France entière":

        afficher_france(
            df_france,
            indicateur_affiche,
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
            df_drom,
            niveau_geographique,
            indicateur_affiche,
            indicateur_technique,
            annee_debut,
            annee_fin
        )