"""Tests SQLite isolés : ne jamais écrire dans les comptes réels."""
import sqlite3
import pytest
from src.models import database

@pytest.fixture
def path(tmp_path, monkeypatch):
    target = tmp_path / "users.db"
    monkeypatch.setattr(database, "DATABASE_PATH", target)
    return target


def test_commit_persists(path):
    db = database.Database()
    db.execute("INSERT INTO users(email,password) VALUES (?,?)", ("a@example.fr", "empreinte-test"))
    db.commit()
    db.close()
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT email FROM users").fetchone()[0] == "a@example.fr"


def test_unique_constraint(path):
    db = database.Database()
    try:
        db.execute("INSERT INTO users(email,password) VALUES (?,?)", ("a@example.fr", "x"))
        db.commit()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO users(email,password) VALUES (?,?)", ("a@example.fr", "y"))
    finally:
        db.close()


def test_foreign_keys(path):
    db = database.Database()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO logs(uid,action,value) VALUES (999,'logged','0')")
    finally:
        db.close()


def test_parameterized_query(path):
    db = database.Database()
    try:
        db.execute("INSERT INTO users(email,password) VALUES (?,?)", ("a@example.fr", "x"))
        db.commit()
        assert db.execute("SELECT uid FROM users WHERE email=?", ("' OR 1=1 --",)).fetchone() is None
    finally:
        db.close()
