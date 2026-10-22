"""Authentification SQLite et état de connexion Streamlit."""
import sqlite3
import time
import streamlit as st
from src.models.database import Database
from src.models.security import HASHER, DUMMY_HASH, validate, verify_password

IDLE_TIMEOUT = 30 * 60
MAX_SESSION_AGE = 8 * 60 * 60
ATTEMPT_WINDOW = 15 * 60
MAX_ATTEMPTS = 5


class DuplicateEmailError(ValueError):
    pass


class TooManyAttemptsError(ValueError):
    pass


def clear_auth(clear_inputs=True):
    keys = ["email", "auth_started", "auth_last_seen"]
    if clear_inputs:
        keys += ["login_email", "login_password"]
    for key in keys:
        st.session_state.pop(key, None)


def reserve_attempt(email):
    """Compteur partagé entre sessions, transaction atomique SQLite."""
    db = Database()
    now = time.time()
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM auth_attempts WHERE window_start <= ?", (now - ATTEMPT_WINDOW,))
        row = db.execute("SELECT attempts FROM auth_attempts WHERE email = ?", (email.casefold(),)).fetchone()
        if row and row[0] >= MAX_ATTEMPTS:
            raise TooManyAttemptsError("Trop de tentatives. Réessayez après 15 minutes.")
        db.execute("""INSERT INTO auth_attempts VALUES (?, 1, ?)
            ON CONFLICT(email) DO UPDATE SET attempts = attempts + 1""", (email.casefold(), now))
        db.commit()
    finally:
        db.close()


class Session:
    def __init__(self, email: str, password: str):
        self.email = email.strip()
        self._password = password
        self.logged = False

    def hash_password(self):
        return HASHER.hash(self._password)

    def find_user(self):
        db = Database()
        try:
            return db.execute("SELECT uid, password FROM users WHERE email = ?", (self.email,)).fetchone()
        finally:
            db.close()

    def exists(self):
        return self.find_user() is not None

    def login(self, count_attempt=True):
        validate(self.email, self._password)
        self.logged = False
        if count_attempt:
            reserve_attempt(self.email)
        user = self.find_user()
        valid, rehash = verify_password(user[1] if user else DUMMY_HASH, self._password)
        if not user or not valid:
            return
        db = Database()
        try:
            if rehash:
                db.execute("UPDATE users SET password = ? WHERE uid = ?", (self.hash_password(), user[0]))
            db.execute("INSERT INTO logs (uid, action, value) VALUES (?, ?, ?)",
                       (user[0], "logged", str(int(time.time()))))
            db.execute("DELETE FROM auth_attempts WHERE email = ?", (self.email.casefold(),))
            db.commit()
            self.logged = True
        finally:
            db.close()

    def signup(self):
        validate(self.email, self._password, registration=True)
        reserve_attempt(self.email)
        db = Database()
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                       (self.email, self.hash_password()))
            db.commit()
            return True
        except sqlite3.IntegrityError:
            if self.exists():
                raise DuplicateEmailError("E-mail déjà utilisé. Veuillez vous connecter.")
            raise
        finally:
            db.close()

    def persist(self):
        if not self.logged:
            raise ValueError("Connexion requise.")
        clear_auth()
        now = time.time()
        st.session_state.update(email=self.email, auth_started=now, auth_last_seen=now)


def get_current_user():
    now = time.time()
    state = st.session_state
    email = state.get("email", "")
    started = state.get("auth_started", 0)
    last_seen = state.get("auth_last_seen", 0)
    if not email:
        return ""
    if now - last_seen >= IDLE_TIMEOUT or now - started >= MAX_SESSION_AGE:
        clear_auth(clear_inputs=False)
        return ""
    state["auth_last_seen"] = now
    return email


def protected_download_button(*args, **kwargs):
    """Contrôle renouvelé immédiatement avant de créer le téléchargement."""
    if not get_current_user():
        st.info("Veuillez vous connecter pour télécharger.")
        return False
    return st.download_button(*args, **kwargs)
