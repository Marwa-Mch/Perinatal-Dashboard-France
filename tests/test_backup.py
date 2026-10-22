import sqlite3
from pathlib import Path
import pytest
from scripts.backup import backup, restore


def test_backup_and_restore(tmp_path):
    source = tmp_path / "users.db"
    with sqlite3.connect(source) as db:
        db.execute("CREATE TABLE users(uid INTEGER, email TEXT, password TEXT)")
        db.execute("INSERT INTO users VALUES (1,'a@example.fr','test-hash')")
    documents = tmp_path / "saved.json"
    documents.write_text('{"_default":{}}')
    folder = tmp_path / "backup"
    assert len(backup(folder, source, documents)) == 2
    restored = tmp_path / "restored"
    restore(folder, restored / "users.db", restored / "saved.json")
    with sqlite3.connect(restored / "users.db") as db:
        assert db.execute("SELECT email FROM users").fetchone()[0] == 'a@example.fr'
    assert (restored / "saved.json").read_text() == documents.read_text()
    with pytest.raises(FileExistsError):
        backup(folder,source,documents)


def test_invalid_manifest(tmp_path):
    folder = tmp_path / "backup"; folder.mkdir()
    (folder / "manifest.json").write_text('{"version":1,"files":["../danger"]}')
    with pytest.raises(ValueError):
        restore(folder,tmp_path/"users.db",tmp_path/"saved.json")
