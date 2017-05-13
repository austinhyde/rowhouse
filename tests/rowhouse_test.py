import pytest
from types import GeneratorType
from os import getenv
from rowhouse import Connection

DB_URL = getenv('ROWHOUSE_DB_URL')
if not DB_URL:
    print('Environment var ROWHOUSE_DB_URL not present or empty')
    exit(1)

USERS = [
    ('mal', 'Mal Reynolds', 'Captain'),
    ('zoe', 'Zoe Washburne', 'First Mate'),
    ('wash', 'Hoban Washburne', 'Pilot'),
]


@pytest.fixture
def db():
    db = Connection(DB_URL)
    db.begin()
    db.execute('CREATE TABLE users (id serial PRIMARY KEY, username varchar(50), name varchar(50), role varchar(20))')
    db.execute('INSERT INTO users (username, name, role) VALUES %s' % ','.join(["('%s','%s','%s')" % u for u in USERS]))
    yield db
    db.rollback()


def test_fetchone_result(db):
    for (username, name, role) in USERS:
        row = db.fetchone('SELECT * FROM users WHERE username = %s', username)
        assert isinstance(row, dict)
        assert row['username'] == username
        assert row['name'] == name
        assert row['role'] == role


def test_fetchone_empty(db):
    row = db.fetchone('SELECT * FROM users WHERE username = \'simon\'')
    assert row is None


def test_fetchall_many(db):
    rows = db.fetchall('SELECT * FROM users')
    assert isinstance(rows, list)
    assert len(rows) == len(USERS)

    byUsername = {u['username']: u for u in rows}
    for (username, name, role) in USERS:
        assert username in byUsername
        assert byUsername[username]['username'] == username
        assert byUsername[username]['name'] == name
        assert byUsername[username]['role'] == role


def test_fetchall_empty(db):
    rows = db.fetchall('SELECT * FROM users WHERE username = \'simon\'')
    assert isinstance(rows, list)
    assert len(rows) == 0


def test_fetchiter_many(db):
    rows = db.fetchiter('SELECT * FROM users')
    assert isinstance(rows, GeneratorType)
    assert len(list(rows)) == len(USERS)


def test_fetchiter_empty(db):
    rows = db.fetchiter('SELECT * FROM users WHERE username = \'simon\'')
    assert isinstance(rows, GeneratorType)
    assert len(list(rows)) == 0


def test_findone_result(db):
    for (username, name, role) in USERS:
        row = db.findone('users', username=username)
        assert isinstance(row, dict)
        assert row['username'] == username
        assert row['name'] == name
        assert row['role'] == role


def test_findone_empty(db):
    row = db.findone('users', username='simon')
    assert row is None


def test_findall_many(db):
    rows = db.findall('users')
    assert isinstance(rows, list)
    assert len(rows) == len(USERS)


def test_findall_empty(db):
    rows = db.findall('users', username='simon')
    assert isinstance(rows, list)
    assert len(rows) == 0


def test_finditer_many(db):
    rows = db.finditer('users')
    assert isinstance(rows, GeneratorType)
    assert len(list(rows)) == len(USERS)


def test_finditer_empty(db):
    rows = db.finditer('users', username='simon')
    assert isinstance(rows, GeneratorType)
    assert len(list(rows)) == 0


def test_insert(db):
    newrow = db.insert('users', {'name': 'Jayne Cobb', 'username': 'jayne', 'role': 'Muscle'})
    assert isinstance(newrow, dict)
    assert 'id' in newrow
    assert newrow['id'] > 0
    assert newrow['username'] == 'jayne'
    assert newrow['name'] == 'Jayne Cobb'
    assert newrow['role'] == 'Muscle'

    row = db.findone('users', username='jayne')
    assert row == newrow


def test_update(db):
    newrow = db.update('users', {'role': 'Comic Relief'}, username='wash')
    assert isinstance(newrow, dict)
    assert 'id' in newrow
    assert newrow['id'] > 0
    assert newrow['username'] == 'wash'
    assert newrow['role'] == 'Comic Relief'

    row = db.findone('users', username='wash')
    assert row == newrow


def test_delete(db):
    oldrow = db.delete('users', username='wash')
    assert isinstance(oldrow, dict)
    assert 'id' in oldrow
    assert oldrow['id'] > 0
    assert oldrow['username'] == 'wash'
    assert oldrow['role'] == 'Pilot'

    row = db.findone('users', username='wash')
    assert row is None
