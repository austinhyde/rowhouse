# Rowhouse - For when you just want to write SQL

Rowhouse is a SQLAlchemy wrapper that attempts to strike a happy medium between using raw database bindings like
psycopg2 and using the full SQLAlchemy API.

Use it when:

* You don't want to mess with connections, cursors, sessions, etc
* You don't need or want an ORM or repository
* You don't want to look up SQLAlchemy's expression language every time you need a non-trivial query
* You just want to write some SQL, and work with plain old dicts and lists
* You want some convenient helper functions for common operations

## Install

```
pip install rowhouse
```

## Basic Usage

```python
from rowhouse import Connection
db = Connnection('pgsql://localhost/mydatabase')

# Run some SQL
row = db.fetchone('SELECT * FROM users WHERE username = %s', ('mreynolds',))
print('Name = ' + row['fullname'])

for row in db.fetchiter('SELECT * FROM users'):
    print('User: ' + row['fullname'])

db.begin()
db.execute('CREATE TABLE groups (...)')
db.execute('INSERT INTO groups VALUES (%s, %s)', ('firefly', 'mreynolds'))
db.commit()

# Some convenient helpers
with db.transaction():
  row = db.findone('users', username='mreynolds')
  db.update('users', row['id'], {
    'role': 'captain'
  })
  newrow = db.insert('users', {
    'fullname': 'Zoe Washburne',
    'username': 'zwashburne',
    'role': 'first_mate'
  })
```
