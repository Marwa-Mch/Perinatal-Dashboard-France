import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from src.models import saved_analysis as repository
from src.models import session
from src.controllers import saved_controller as controller

@pytest.fixture(autouse=True)
def isolated_documents(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "DOCUMENT_PATH", tmp_path / "private" / "saved.json")
    monkeypatch.setattr(session.st, "session_state", {})
    monkeypatch.setattr(controller, "get_current_user", lambda: "a@example.fr")


def test_document_crud_and_isolation(monkeypatch):
    identifier = controller.create_saved("Mon classement", 2023, "img", 5)
    assert controller.list_saved()[0]["parameters"]["year"] == 2023
    monkeypatch.setattr(controller, "get_current_user", lambda: "b@example.fr")
    assert controller.list_saved() == []
    with pytest.raises(ValueError):
        controller.rename_saved(identifier, "Vol")
    with pytest.raises(ValueError):
        controller.delete_saved(identifier)
    monkeypatch.setattr(controller, "get_current_user", lambda: "a@example.fr")
    controller.rename_saved(identifier, "Nouveau nom")
    assert controller.list_saved()[0]["name"] == "Nouveau nom"
    controller.delete_saved(identifier)
    assert controller.list_saved() == []


def test_requires_login(monkeypatch):
    monkeypatch.setattr(controller, "get_current_user", lambda: "")
    for action in [controller.list_saved, lambda: controller.create_saved("x",2023,"img",5),
                   lambda: controller.rename_saved("x","y"), lambda: controller.delete_saved("x")]:
        with pytest.raises(PermissionError):
            action()


@pytest.mark.parametrize("name", ["", " "*4, "x"*81, "bad\nname"])
def test_invalid_names(name):
    with pytest.raises(ValueError):
        controller.create_saved(name,2023,"img",5)


def test_persistence_and_quota():
    for index in range(30):
        controller.create_saved(str(index),2023,"img",5)
    assert len(repository.list_saved("a@example.fr")) == 30
    with pytest.raises(ValueError):
        controller.create_saved("overflow",2023,"img",5)


def test_concurrent_writes():
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda index: repository.create_saved("a@example.fr",str(index),{}), range(12)))
    assert len(repository.list_saved("a@example.fr")) == 12
    assert isinstance(json.loads(repository.DOCUMENT_PATH.read_text()), dict)
