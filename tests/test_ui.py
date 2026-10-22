"""Tests fonctionnels Streamlit dans le moteur AppTest, sans navigateur réel."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from src.models import database, saved_analysis

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(autouse=True)
def private_data(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH",tmp_path/"users.db")
    monkeypatch.setattr(saved_analysis,"DOCUMENT_PATH",tmp_path/"saved.json")


@pytest.mark.parametrize("route", ["/home","/dataset","/naissances","/mortinatalite","/analysis","/login","/saved","/conclusion"])
def test_pages(route):
    app = AppTest.from_file(str(ROOT/"main.py"),default_timeout=30)
    app.query_params['nav'] = route
    app.run()
    assert not app.exception, list(app.exception)
    assert not app.error, [error.value for error in app.error]


def test_signup_login_logout():
    app = AppTest.from_file(str(ROOT/"main.py"), default_timeout=30)
    app.query_params['nav'] = '/login'
    app.run()
    app.text_input(key='login_email').set_value('ui@example.fr')
    app.text_input(key='login_password').set_value('Une phrase longue!')
    next(b for b in app.button if b.label == "S’inscrire" or b.label == "S'inscrire").click().run()
    assert not app.exception
    assert app.session_state['email'] == 'ui@example.fr'
    app.query_params['nav']='/saved'; app.run()
    app.text_input[0].set_value('Test personnel')
    next(b for b in app.button if b.label=='Enregistrer').click().run()
    assert not app.exception
    assert any('Test personnel' in item.options for item in app.selectbox)
    app.query_params['nav']='/logout';app.run()
    assert not app.exception
    assert 'email' not in app.session_state

@pytest.mark.parametrize('route,key,value', [
    ('/naissances','niveau_naissances','Régions'),
    ('/naissances','niveau_naissances','Départements'),
    ('/mortinatalite','niveau_mortinatalite','Régions'),
    ('/mortinatalite','niveau_mortinatalite','DROM'),
    ('/naissances','indicateur_naissances','Naissances vivantes'),
    ('/mortinatalite','indicateur_mortinatalite','IMG')])
def test_filters(route,key,value):
    app = AppTest.from_file(str(ROOT/'main.py'),default_timeout=30)
    app.query_params['nav']=route;app.run()
    app.selectbox(key=key).set_value(value).run()
    assert not app.exception
    assert not app.error, [error.value for error in app.error]
