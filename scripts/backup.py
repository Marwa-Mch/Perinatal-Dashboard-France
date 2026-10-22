"""Sauvegarde et restauration des données privées, application arrêtée."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from filelock import FileLock
from src.config import RUNTIME_DIR
from src.models.database import DATABASE_PATH


def backup(destination, user_db=DATABASE_PATH, document_db=None):
    destination = Path(destination)
    document_db = Path(document_db) if document_db else RUNTIME_DIR / "saved_analyses.json"
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    files = []
    if Path(user_db).exists():
        with sqlite3.connect(Path(user_db).resolve().as_uri() + "?mode=ro", uri=True) as source:
            with sqlite3.connect(destination / "users.db") as target:
                source.backup(target)
        (destination / "users.db").chmod(0o600)
        files.append("users.db")
    with FileLock(str(document_db) + ".lock", timeout=10):
        if document_db.exists():
            with document_db.open(encoding="utf-8") as stream:
                json.load(stream)
            shutil.copyfile(document_db, destination / "saved_analyses.json")
            (destination / "saved_analyses.json").chmod(0o600)
            files.append("saved_analyses.json")
    (destination / "manifest.json").write_text(json.dumps({"version": 1, "files": files}), encoding="utf-8")
    return files


def restore(source, user_db=DATABASE_PATH, document_db=None):
    source = Path(source)
    document_db = Path(document_db) if document_db else RUNTIME_DIR / "saved_analyses.json"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != 1 or set(manifest.get("files", [])) - {"users.db", "saved_analyses.json"}:
        raise ValueError("Manifeste de sauvegarde invalide.")
    # Valider tous les fichiers avant toute écriture.
    for name in manifest["files"]:
        file = source / name
        if name == "users.db":
            with sqlite3.connect(file.resolve().as_uri() + "?mode=ro", uri=True) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("Sauvegarde SQLite invalide.")
                db.execute("SELECT uid,email,password FROM users LIMIT 1")
        else:
            data = json.loads(file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Sauvegarde documentaire invalide.")
    for name in manifest["files"]:
        target = Path(user_db) if name == "users.db" else document_db
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=target.parent)
        os.close(fd)
        try:
            shutil.copyfile(source / name, temporary)
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "restore"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--confirm-stopped", action="store_true", help="Confirmer l’arrêt de l’application")
    args = parser.parse_args()
    if not args.confirm_stopped:
        parser.error("Arrêtez l’application puis ajoutez --confirm-stopped.")
    if args.action == "create":
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        files = backup(args.directory)
        print(f"Sauvegarde terminée : {len(files)} fichier(s).")
    else:
        restore(args.directory)
        print("Restauration terminée. Redémarrez l’application.")

if __name__ == "__main__":
    main()
