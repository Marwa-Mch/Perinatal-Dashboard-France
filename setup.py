"""Initialisation sans compte administrateur ni mot de passe par défaut."""
from src.models.database import Database
from src.models.build_data import rebuild_database
from src.config import ANALYSIS_DB

def main():
    if not ANALYSIS_DB.exists():
        rebuild_database()
    db = Database()
    db.close()
    print("Initialisation terminée. Créez votre compte depuis l’interface.")

if __name__ == "__main__":
    main()
