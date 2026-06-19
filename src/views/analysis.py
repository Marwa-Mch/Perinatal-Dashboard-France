# =====================================================
# IMPORTATION DES BIBLIOTHÈQUES
# =====================================================

# Streamlit sert à afficher la page web
import streamlit as st

# Matplotlib sert à créer les graphiques
import matplotlib.pyplot as plt

# On importe la fonction du Controller
# Elle récupère les 3 fichiers CSV propres
from src.controllers.naissances_controller import get_data_naissances


# =====================================================
# PAGE ANALYSE
# =====================================================

def load_view():

    """
    Page d'analyse du projet.
    Ici, on affiche les graphiques à partir des données nettoyées.
    """

    # Titre principal de la page
    st.title("Analyse des indicateurs de santé périnatale")

    # Texte d'introduction
    st.markdown(
        """
        Cette page présente les premières visualisations réalisées à partir
        des fichiers nettoyés dans le notebook.
        """
    )

    # =====================================================
    # CHARGEMENT DES DONNÉES
    # =====================================================

    # On récupère les 3 DataFrames depuis le Controller
    df_france, df_regions, df_departements = get_data_naissances()

    # =====================================================
    # SECTION 1 : NAISSANCES FRANCE ENTIÈRE
    # =====================================================

    st.header("1. Évolution des naissances en France")

    # Listes vides pour construire le graphique
    annees = []
    valeurs = []

    # On parcourt toutes les colonnes du DataFrame France
    for colonne in df_france.columns:

        # On sélectionne seulement les colonnes des naissances totales
        if "naissances_totales" in colonne:

            # Exemple :
            # colonne = "2012_naissances_totales"
            # split("_")[0] permet de récupérer "2012"
            annee = colonne.split("_")[0]

            # On ajoute l'année dans la liste
            annees.append(annee)

            # df_france contient une seule ligne
            # iloc[0] récupère la valeur de cette ligne
            valeur = df_france[colonne].iloc[0]

            # On ajoute la valeur dans la liste
            valeurs.append(valeur)

    # Création du graphique
    fig, ax = plt.subplots()

    # Courbe d'évolution
    ax.plot(
        annees,
        valeurs,
        marker="o"
    )

    # Titre et axes
    ax.set_title("Évolution des naissances totales en France")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de naissances")

    # Grille de lecture
    ax.grid(True)

    # Affichage dans Streamlit
    st.pyplot(fig)

    # Petite interprétation
    st.markdown(
        """
        **Interprétation :**  
        Ce graphique permet d'observer l'évolution du nombre total de naissances
        en France sur la période disponible dans le fichier.
        """
    )