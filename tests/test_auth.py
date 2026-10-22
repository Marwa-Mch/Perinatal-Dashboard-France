import hashlib
import sqlite3
from unittest.mock import patch
import pytest
from src.models import database, session
from src.controllers.auth import auth, logout
from src.controllers.signup import signup

@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DATABASE_PATH', tmp_path / 'users.db')
    monkeypatch.setattr(session.st, 'session_state', {})

def test_registration_and_login():
    assert signup('test@example.fr', 'Une phrase longue!')['success']
    assert session.get_current_user() == 'test@example.fr'
    assert 'login_password' not in session.st.session_state
    row = session.Session('test@example.fr', '').find_user()
    assert row[1].startswith('$argon2id$')
    logout()
    assert not session.get_current_user()
    assert not auth('test@example.fr', 'mauvais')['success']
    assert auth('test@example.fr', 'Une phrase longue!')['success']

def test_validation_and_duplicate():
    assert not signup('incorrect', 'Une phrase longue!')['success']
    assert not signup('test@example.fr', 'court')['success']
    assert signup('test@example.fr', 'Une phrase longue!')['success']
    result = signup('test@example.fr', 'Une autre phrase!')
    assert not result['success'] and 'déjà utilisé' in result['message']

def test_old_password_migration():
    db = database.Database()
    db.execute('INSERT INTO users(email,password) VALUES (?,?)',
               ('old@example.fr', hashlib.sha256(b'ancien').hexdigest()))
    db.commit(); db.close()
    assert auth('old@example.fr', 'ancien')['success']
    assert session.Session('old@example.fr', '').find_user()[1].startswith('$argon2id$')

def test_rate_limit_across_sessions():
    for _ in range(5):
        assert not auth('absent@example.fr', 'incorrect')['success']
        session.st.session_state.clear()
    assert 'Trop de tentatives' in auth('absent@example.fr', 'incorrect')['message']
    with patch.object(session.time, 'time', return_value=session.time.time()+901):
        assert auth('absent@example.fr', 'incorrect')['message'] == 'Identifiants incorrects.'

def test_expiration_and_download():
    assert signup('test@example.fr', 'Une phrase longue!')['success']
    session.st.session_state['auth_last_seen'] -= 1801
    with patch.object(session.st, 'download_button') as button, patch.object(session.st, 'info'):
        assert not session.protected_download_button('test', data=b'x')
        button.assert_not_called()
    assert not session.get_current_user()

def test_absolute_expiration():
    signup('test@example.fr', 'Une phrase longue!')
    session.st.session_state['auth_started'] -= 28801
    assert not session.get_current_user()

def test_database_failure():
    with patch.object(session.Session, 'signup', side_effect=sqlite3.OperationalError('unavailable')):
        result = signup('test@example.fr', 'Une phrase longue!')
    assert not result['success']
    assert 'indisponible' in result['message'] and 'déjà' not in result['message']

def test_sql_input_cannot_login():
    assert not auth("' OR 1=1 --", 'incorrect')['success']

def test_random_salt():
    a = session.Session('test@example.fr', 'Une phrase longue!')
    assert a.hash_password() != a.hash_password()

def test_download_allowed_and_logout_cleans_inputs():
    signup('test@example.fr', 'Une phrase longue!')
    with patch.object(session.st, 'download_button', return_value=True) as button:
        assert session.protected_download_button('test', data=b'x')
        button.assert_called_once()
    session.st.session_state['login_password'] = 'secret'
    logout()
    assert 'login_password' not in session.st.session_state
