"""Validation et hachage des mots de passe."""
import hashlib
import hmac
import re
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

HASHER = PasswordHasher()
DUMMY_HASH = HASHER.hash("dummy-password-for-timing-only")


def validate(email, password, registration=False):
    email = email.strip()
    if len(email) > 254 or not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", email):
        raise ValueError("Veuillez saisir une adresse e-mail valide.")
    if not password or len(password) > 1024:
        raise ValueError("Le mot de passe doit contenir entre 1 et 1 024 caractères.")
    if registration and len(password) < 12:
        raise ValueError("Choisissez un mot de passe d’au moins 12 caractères.")
    return email


def verify_password(stored, password):
    if re.fullmatch(r"[0-9a-f]{64}", stored):
        return hmac.compare_digest(stored, hashlib.sha256(password.encode()).hexdigest()), True
    try:
        HASHER.verify(stored, password)
        return True, HASHER.check_needs_rehash(stored)
    except (VerificationError, InvalidHashError):
        return False, False
