# =====================================================
# MODEL — SESSION ET AUTHENTIFICATION
# =====================================================

from pathlib import Path
import hashlib
import json
import time

from src.models.database import Database


BASE_DIR = Path(__file__).resolve().parents[2]
SESSION_PATH = BASE_DIR / "session.json"


class Session:
    """
    Représente une tentative d'authentification utilisateur.
    """

    def __init__(self, email: str, password: str) -> None:
        self.logged = False
        self.email = email.strip()
        self._password = password

    def hash_password(self) -> str:
        """
        Transforme le mot de passe en empreinte SHA-256.

        Pour une application de production, il serait préférable
        d'utiliser bcrypt ou Argon2 avec un sel.
        """

        return hashlib.sha256(
            self._password.encode("utf-8")
        ).hexdigest()

    def find_user(self):
        """
        Recherche un utilisateur avec une requête paramétrée.
        """

        db = Database()

        try:
            result = db.execute(
                """
                SELECT uid
                FROM users
                WHERE email = ? AND password = ?
                """,
                (self.email, self.hash_password())
            )

            return result.fetchone()

        finally:
            db.close()

    def exists(self) -> bool:
        """
        Indique si l'utilisateur existe.
        """

        return self.find_user() is not None

    def get_uid(self):
        """
        Retourne l'identifiant de l'utilisateur connecté.
        """

        user = self.find_user()

        if user is None:
            return None

        return user[0]

    def login(self):
        """
        Connecte l'utilisateur si ses identifiants sont valides.
        """

        uid = self.get_uid()

        if uid is None:
            self.logged = False
            return

        db = Database()

        try:
            db.execute(
                """
                INSERT INTO logs (uid, action, value)
                VALUES (?, ?, ?)
                """,
                (uid, "logged", str(int(time.time())))
            )

            db.commit()
            self.logged = True

        finally:
            db.close()

    def signup(self) -> bool:
        """
        Crée un utilisateur lorsqu'il n'existe pas encore.
        """

        if self.exists():
            return False

        db = Database()

        try:
            db.execute(
                """
                INSERT INTO users (email, password)
                VALUES (?, ?)
                """,
                (self.email, self.hash_password())
            )

            db.commit()
            return True

        except Exception:
            return False

        finally:
            db.close()

    def persist(self):
        """
        Enregistre l'adresse e-mail de la session courante.
        """

        data = {"email": self.email}

        with open(SESSION_PATH, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile)

def get_current_user():
    """
    Retourne l'e-mail de l'utilisateur connecté.
    Retourne une chaîne vide si personne n'est connecté.
    """

    if not SESSION_PATH.exists():
        return ""

    try:
        with open(
            SESSION_PATH,
            "r",
            encoding="utf-8"
        ) as fichier:
            data = json.load(fichier)

        return data.get("email", "").strip()

    except (json.JSONDecodeError, OSError):
        return ""