# =====================================================
# IMPORTATION DES BIBLIOTHÈQUES
# =====================================================

# Streamlit permet de créer l'interface de l'application
import streamlit as st

# Matplotlib permet de créer des graphiques
import matplotlib.pyplot as plt

# On importe la fonction du Controller
# Cette fonction va récupérer les données depuis le Model
from src.controllers.naissances_controller import get_data_naissances


# =====================================================
# PAGE STREAMLIT : NAISSANCES
# =====================================================

def load_view():

    """
    Cette fonction affiche la page consacrée
    à l'analyse des naissances.
    """

    # Titre principal de la page
    st.title("Analyse des naissances en France")

    # On récupère les 3 DataFrames depuis le Controller
    df_france, df_regions, df_departements = get_data_naissances()

    # =====================================================
    # APERÇU DES DONNÉES FRANCE ENTIÈRE
    # =====================================================

    # Sous-titre
    st.subheader("Aperçu des données France entière")

    # Affichage du tableau France entière
    st.dataframe(df_france)

    # =====================================================
    # GRAPHIQUE : ÉVOLUTION DES NAISSANCES EN FRANCE
    # =====================================================

    # Sous-titre du graphique
    st.subheader("Évolution des naissances totales en France")

    # Liste vide pour stocker les années
    annees = []

    # Liste vide pour stocker les valeurs des naissances
    valeurs = []

    # On parcourt toutes les colonnes du DataFrame France
    for colonne in df_france.columns:

        # On garde seulement les colonnes contenant "naissances_totales"
        if "naissances_totales" in colonne:

            # Exemple : "2012_naissances_totales"
            # split("_") découpe le texte :
            # ["2012", "naissances", "totales"]
            # [0] récupère seulement l'année
            annee = colonne.split("_")[0]

            # On ajoute l'année dans la liste annees
            annees.append(annee)

            # On récupère la valeur de la colonne
            # iloc[0] car df_france contient une seule ligne
            valeur = df_france[colonne].iloc[0]

            # On ajoute cette valeur dans la liste valeurs
            valeurs.append(valeur)

    # Création d'une figure Matplotlib
    fig, ax = plt.subplots()

    # Création de la courbe
    ax.plot(
        annees,
        valeurs,
        marker="o"
    )

    # Titre du graphique
    ax.set_title("Évolution des naissances totales en France")

    # Nom de l'axe horizontal
    ax.set_xlabel("Année")

    # Nom de l'axe vertical
    ax.set_ylabel("Nombre de naissances")

    # Ajout d'une grille pour mieux lire le graphique
    ax.grid(True)

    # Affichage du graphique dans Streamlit
    st.pyplot(fig)