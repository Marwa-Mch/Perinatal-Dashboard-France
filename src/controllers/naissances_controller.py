# =====================================================
# IMPORTATION DU MODEL
# =====================================================

# On importe les fonctions qui chargent les 3 fichiers CSV propres
from src.models.naissances_model import (
    charger_naissances_france,
    charger_naissances_regions,
    charger_naissances_departements
)


# =====================================================
# CONTRÔLEUR DES DONNÉES NAISSANCES
# =====================================================

def get_data_naissances():

    """
    Récupère les données de naissance depuis le Model.
    """

    # Charge les données France entière
    df_france = charger_naissances_france()

    # Charge les données par région
    df_regions = charger_naissances_regions()

    # Charge les données par département
    df_departements = charger_naissances_departements()

    # Retourne les 3 DataFrames à la View
    return df_france, df_regions, df_departements