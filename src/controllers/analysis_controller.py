"""Sélections validées et requêtes sur le modèle relationnel normalisé."""
from numbers import Integral
from src.models.analysis_model import lire_table_sqlite, executer_requete_sql
INDICATORS = {"mortinatalite_totale", "mortinatalite_spontanee", "img"}


def validate_selection(annee, indicateur, limite=10):
    if isinstance(annee, bool) or not isinstance(annee, Integral) or not 2012 <= annee <= 2023:
        raise ValueError("L’année doit être un entier entre 2012 et 2023.")
    if indicateur not in INDICATORS:
        raise ValueError("Indicateur non autorisé.")
    if isinstance(limite, bool) or not isinstance(limite, Integral) or not 1 <= limite <= 100:
        raise ValueError("Le nombre de territoires doit être compris entre 1 et 100.")


def get_mortinatalite_sql():
    return tuple(lire_table_sqlite(f"mortinatalite_{level}") for level in ("france", "regions", "drom"))


def get_requete_classement_regions(annee, indicateur, limite=10):
    validate_selection(annee, indicateur, limite)
    query = """SELECT t.name AS region, o.value AS valeur
        FROM observations o JOIN territories t ON t.id = o.territory_id
        WHERE t.level = 'regions' AND o.year = ? AND o.indicator_code = ?
          AND o.value IS NOT NULL
        ORDER BY o.value DESC, t.name ASC LIMIT ?"""
    return query, executer_requete_sql(query, (int(annee), indicateur, int(limite)))


def get_statistiques_regions(annee, indicateur):
    validate_selection(annee, indicateur)
    query = """SELECT COUNT(o.value) AS nombre_regions, AVG(o.value) AS moyenne,
        MIN(o.value) AS minimum, MAX(o.value) AS maximum
        FROM observations o JOIN territories t ON t.id = o.territory_id
        WHERE t.level = 'regions' AND o.year = ? AND o.indicator_code = ?
          AND o.value IS NOT NULL"""
    return query, executer_requete_sql(query, (int(annee), indicateur))
