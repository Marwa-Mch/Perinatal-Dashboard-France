from src.models.data_validation import validate_frame
# =====================================================
# MODEL — DONNÉES DE MORTINATALITÉ
# =====================================================

from pathlib import Path

import pandas as pd
import streamlit as st

# Racine du projet :
# parents[2] remonte de src/models vers le dossier principal
BASE_DIR = Path(__file__).resolve().parents[2]

# Dossier contenant les fichiers CSV nettoyés
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

@st.cache_data
def load_mortinatalite_data():
    """
    Charge les trois fichiers CSV nettoyés de mortinatalité.

    Returns
    -------
    tuple
        df_france, df_regions, df_drom
    """

    france_path = PROCESSED_DATA_DIR / "mortinatalite_france.csv"
    regions_path = PROCESSED_DATA_DIR / "mortinatalite_regions.csv"
    drom_path = PROCESSED_DATA_DIR / "mortinatalite_drom.csv"

    # Vérification de l'existence des fichiers
    fichiers_manquants = [
        str(path)
        for path in [france_path, regions_path, drom_path]
        if not path.exists()
    ]

    if fichiers_manquants:
        raise FileNotFoundError(
            "Fichiers de mortinatalité introuvables : "
            + ", ".join(fichiers_manquants)
        )

    df_france = validate_frame(pd.read_csv(france_path), "mortinatalite")
    df_regions = validate_frame(pd.read_csv(regions_path), "mortinatalite")
    df_drom = validate_frame(pd.read_csv(drom_path), "mortinatalite")

    return df_france, df_regions, df_drom 