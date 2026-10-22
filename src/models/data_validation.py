"""Contrôles structurels sans imputation silencieuse."""
import re
import pandas as pd


def validate_frame(frame, kind):
    if frame.empty:
        raise ValueError("Le jeu de données est vide.")
    geography = "zone_géographique" if kind == "naissances" else "zone_geographique"
    if geography not in frame:
        raise ValueError(f"Colonne géographique absente : {geography}")
    if frame[geography].isna().any() or frame[geography].astype(str).str.strip().eq("").any():
        raise ValueError("Un territoire est manquant.")
    if frame[geography].duplicated().any():
        raise ValueError("Un territoire est présent plusieurs fois.")
    frame = frame.copy()
    columns = [c for c in frame if re.fullmatch(r"20\d{2}_.+", c)]
    if not columns:
        raise ValueError("Aucune colonne annuelle disponible.")
    for column in columns:
        cleaned = frame[column].astype("string").str.strip().str.replace(r"\*+$", "", regex=True).str.replace(",", ".", regex=False)
        numeric = pd.to_numeric(cleaned, errors="coerce")
        if (frame[column].notna() & numeric.isna()).any():
            raise ValueError(f"Valeur non numérique dans {column}")
        if (numeric.dropna() < 0).any() or numeric.isin([float("inf"), float("-inf")]).any():
            raise ValueError(f"Valeur négative ou infinie dans {column}")
        frame[column] = numeric
    return frame
