# =====================================================
# MODEL — BASE DE DONNÉES UTILISATEURS
# =====================================================

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "data" / "users.db"


class Database:
    """
    Gère la connexion et les opérations simples
    sur la base SQLite des utilisateurs.
    """

    def __init__(self) -> None:
        self.__db = sqlite3.connect(DATABASE_PATH)
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