"""Base documentaire TinyDB pour les configurations personnelles d’analyse."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import uuid
from filelock import FileLock
from tinydb import TinyDB, Query
from tinydb.storages import Storage
from src.config import RUNTIME_DIR

DOCUMENT_PATH = RUNTIME_DIR / "saved_analyses.json"


class AtomicJSONStorage(Storage):
    """Écrit un document complet par remplacement atomique, sous verrou externe."""
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return None
        with self.path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def write(self, data):
        fd, path = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(path, self.path)
        finally:
            Path(path).unlink(missing_ok=True)


@contextmanager
def documents():
    DOCUMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(DOCUMENT_PATH) + ".lock", timeout=10):
        with TinyDB(DOCUMENT_PATH, storage=AtomicJSONStorage) as db:
            yield db


def list_saved(owner):
    with documents() as db:
        return [dict(row) for row in db.search(Query().owner == owner)]


def create_saved(owner, name, parameters):
    with documents() as db:
        if db.count(Query().owner == owner) >= 30 or len(db) >= 1000:
            raise ValueError("Limite d’analyses enregistrées atteinte. Supprimez une ancienne analyse.")
        identifier = str(uuid.uuid4())
        db.insert({"id": identifier, "owner": owner, "name": name,
                   "parameters": parameters, "created_at": datetime.now(timezone.utc).isoformat()})
        return identifier


def rename_saved(owner, identifier, name):
    with documents() as db:
        changed = db.update({"name": name}, (Query().owner == owner) & (Query().id == identifier))
        if not changed:
            raise ValueError("Analyse introuvable.")


def delete_saved(owner, identifier):
    with documents() as db:
        changed = db.remove((Query().owner == owner) & (Query().id == identifier))
        if not changed:
            raise ValueError("Analyse introuvable.")
