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
        if result is None:
            return None
        return dict(result.items())

    def execute(self, sql, *multiparams, **params):
        return self._execute(sql, *multiparams, **params)

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

    def findone(self, tablename, conditions={}, **kwargs):
        conditions = dict(conditions, **kwargs)
        table = _table(tablename, conditions.keys())
        return self.fetchone(_where(sa.select([sa.text('*')]).select_from(table), conditions, table))

    def findall(self, tablename, conditions={}, **kwargs):
        conditions = dict(conditions, **kwargs)
        table = _table(tablename, conditions.keys())
        return self.fetchall(_where(sa.select([sa.text('*')]).select_from(table), conditions, table))

    def finditer(self, tablename, conditions={}, **kwargs):
        conditions = dict(conditions, **kwargs)
        table = _table(tablename, conditions.keys())
        return self.fetchiter(_where(sa.select([sa.text('*')]).select_from(table), conditions, table))

    def insert(self, tablename, data):
        return self.fetchone(_table(tablename, data.keys()).insert().values(data).returning(sa.text('*')))

    def update(self, tablename, data, conditions={}, **kwargs):
        conditions = dict(conditions, **kwargs)
        cols = list(conditions.keys())
        cols.extend(data.keys())
        return self.fetchone(_where(_table(tablename, cols).update().values(data).returning(sa.text('*')), conditions))

    def delete(self, tablename, conditions={}, **kwargs):
        conditions = dict(conditions, **kwargs)
        return self.fetchone(_where(_table(tablename, conditions.keys()).delete().returning(sa.text('*')), conditions))


def _table(name, cols):
    return sa.table(name, *[sa.column(c) for c in cols])


def _where(whereable, conditions, table=None):
    if table is None:
        table = whereable.table
    if len(conditions):
        return whereable.where(sa.and_(*[getattr(table.c, k) == v for k, v in conditions.items()]))
    return whereable
