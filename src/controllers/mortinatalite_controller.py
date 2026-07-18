# =====================================================
# CONTROLLER — DONNÉES DE MORTINATALITÉ
# =====================================================

from src.models.mortinatalite_model import load_mortinatalite_data


def get_data_mortinatalite():
    """
    Demande au Model de charger les données de mortinatalité
    puis les transmet aux Views.
    """

    return load_mortinatalite_data()