# =====================================================
# CONTROLLER — ANALYSES TECHNIQUES
# =====================================================

from src.models.analysis_model import (
    lire_table_sqlite,
    executer_requete_sql
)


def get_mortinatalite_sql():
    """
    Charge les trois tables de mortinatalité depuis SQLite.
    """

    france = lire_table_sqlite(
        "mortinatalite_france"
    )

    regions = lire_table_sqlite(
        "mortinatalite_regions"
    )

    drom = lire_table_sqlite(
        "mortinatalite_drom"
    )

    return france, regions, drom


def get_requete_classement_regions(
    annee: int,
    indicateur: str,
    limite: int = 10
):
    """
    Retourne la requête SQL et son résultat pour
    le classement régional.
    """

    indicateurs_autorises = {
        "mortinatalite_totale",
        "mortinatalite_spontanee",
        "img"
    }

    if indicateur not in indicateurs_autorises:
        raise ValueError(
            "Indicateur non autorisé."
        )

    if annee < 2012 or annee > 2023:
        raise ValueError(
            "Année non autorisée."
        )

    colonne = f"{annee}_{indicateur}"

    requete = f"""
        SELECT
            zone_geographique AS region,
            "{colonne}" AS valeur
        FROM mortinatalite_regions
        WHERE "{colonne}" IS NOT NULL
        ORDER BY "{colonne}" DESC
        LIMIT {int(limite)}
    """

    resultat = executer_requete_sql(
        requete
    )

    return requete, resultat


def get_statistiques_regions(
    annee: int,
    indicateur: str
):
    """
    Calcule en SQL les principales statistiques régionales.
    """

    indicateurs_autorises = {
        "mortinatalite_totale",
        "mortinatalite_spontanee",
        "img"
    }

    if indicateur not in indicateurs_autorises:
        raise ValueError(
            "Indicateur non autorisé."
        )

    colonne = f"{annee}_{indicateur}"

    requete = f"""
        SELECT
            COUNT("{colonne}") AS nombre_regions,
            AVG("{colonne}") AS moyenne,
            MIN("{colonne}") AS minimum,
            MAX("{colonne}") AS maximum
        FROM mortinatalite_regions
        WHERE "{colonne}" IS NOT NULL
    """

    return requete, executer_requete_sql(
        requete
    )