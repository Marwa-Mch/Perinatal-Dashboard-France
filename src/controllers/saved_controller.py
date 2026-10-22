"""Autorisation et validation des configurations enregistrées."""
from src.models.session import get_current_user
from src.models import saved_analysis as repository
from src.controllers.analysis_controller import validate_selection


def current_owner():
    owner = get_current_user()
    if not owner:
        raise PermissionError("Veuillez vous connecter pour gérer vos analyses.")
    return owner


def validate_name(name):
    name = name.strip()
    if not 1 <= len(name) <= 80 or any(ord(char) < 32 for char in name):
        raise ValueError("Le nom doit contenir de 1 à 80 caractères, sans retour à la ligne.")
    return name


def list_saved():
    return repository.list_saved(current_owner())


def create_saved(name, year, indicator, limit):
    owner = current_owner()
    name = validate_name(name)
    validate_selection(year, indicator, limit)
    return repository.create_saved(owner, name, {"year": int(year), "indicator": indicator, "limit": int(limit)})


def rename_saved(identifier, name):
    return repository.rename_saved(current_owner(), identifier, validate_name(name))


def delete_saved(identifier):
    return repository.delete_saved(current_owner(), identifier)
