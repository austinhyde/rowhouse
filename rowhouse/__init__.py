import sqlalchemy as sa
from contextlib import contextmanager

class Connection:
    def __init__(self, url):
        self._db = sa.create_engine(url).connect()
        self._db.execution_options(autocommit=True, stream_results=True)
        self._tx = None
        self.open = True

    def close(self):
        self._db.close()
        self.open = False

    def _execute(self, sql, *multiparams, **params):
        return self._db.execute(sql, *multiparams, **params)

    def _unwrap(self, result):
        return dict(result.items())

    def execute(self, sql, *multiparams, **params):
        self._execute(sql, *multiparams, **params)

    def fetchone(self, sql, *multiparams, **params):
        return self._unwrap(self._execute(sql, *multiparams, **params).first())

    def fetchall(self, sql, *multiparams, **params):
        return [self._unwrap(r) for r in self._execute(sql, *multiparams, **params).fetchall()]

    def fetchiter(self, sql, *multiparams, **params):
        result = self._execute(sql, *multiparams, **params)
        row = result.fetchone()
        while row:
            yield self._unwrap(row)
            row = result.fetchone()

    def begin(self):
        if not self._tx:
            self._tx = self._db.begin()

    def commit(self):
        if self._tx:
            self._tx.commit()
            self._tx = None

    def rollback(self):
        if self._tx:
            self._tx.rollback()
            self._tx = None

    @contextmanager
    def transaction(self):
        with self._db.begin():
            yield
