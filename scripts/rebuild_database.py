"""python -m scripts.rebuild_database --force (application arrêtée)."""
import argparse
from src.config import ANALYSIS_DB
from src.models.build_data import rebuild_database

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Remplacer la base dérivée existante")
    args = parser.parse_args()
    if ANALYSIS_DB.exists() and not args.force:
        parser.error("La base existe. Arrêtez l’application puis utilisez --force pour la reconstruire.")
    rebuild_database()
    print("Base d’analyse reconstruite et contrôlée.")

if __name__ == "__main__":
    main()
