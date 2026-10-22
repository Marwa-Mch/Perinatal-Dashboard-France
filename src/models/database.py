# =====================================================
# MODEL — BASE DE DONNÉES UTILISATEURS
# =====================================================

from pathlib import Path
import sqlite3
from src.config import RUNTIME_DIR


BASE_DIR = Path(__file__).resolve().parents[2]
LEGACY_PATH = BASE_DIR / "data" / "users.db"
DATABASE_PATH = LEGACY_PATH if LEGACY_PATH.exists() else RUNTIME_DIR / "users.db"


class Database:
    """
    Gère la connexion et les opérations simples
    sur la base SQLite des utilisateurs.
    """

    def __init__(self) -> None:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.__db = sqlite3.connect(DATABASE_PATH, timeout=10)
        try:
            DATABASE_PATH.chmod(0o600)
        except OSError:
            pass  # Les droits Windows doivent être configurés sur l'hébergement.
        self.__db.execute("PRAGMA foreign_keys = ON")
        self.setup()

    def setup(self):
        """
        Crée les tables si elles n'existent pas.
        """

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,
                action TEXT,
                value TEXT,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
            """
        )

        self.execute("""
            CREATE TABLE IF NOT EXISTS auth_attempts (
                email TEXT PRIMARY KEY,
                attempts INTEGER NOT NULL,
                window_start REAL NOT NULL
            )
        """)
        self.commit()

    def execute(self, query: str, parameters=()):
        """
        Exécute une requête SQL avec des paramètres sécurisés.
        """

        return self.__db.execute(query, parameters)

    def commit(self):
        """
        Valide les modifications dans la base.
        """

        self.__db.commit()

    def close(self):
        """
        Ferme la connexion à SQLite.
        """

        self.__db.close()