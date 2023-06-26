"""Simple wrapper around the psycopg."""

import psycopg2
import sys

_CONN_STR = "postgresql://postgres:test@localhost:5433/{dbname}"


class SimpleSQL:
    _dbname = None

    @classmethod
    def setDatabaseName(cls, dbname):
        cls._dbname = dbname

    @classmethod
    def getConnString(cls):
        return _CONN_STR.format(dbname=cls._dbname)

    def __enter__(self):
        assert self._dbname, "You must provide a database name."
        self._connection = psycopg2.connect(self.getConnString())
        return self

    def __exit__(self, exc_type, exc_value, trace):
        assert self._connection
        self._connection.close()
        self._connection = None

    def execute_query(self, sql):
        assert self._connection
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            records = cursor.fetchall()
            for row in records:
                yield row

    def execute_non_query(self, sql):
        """Executes a non select statement.

        :param sql: the sql to execute

        :raise:psycopg2.DatabaseError
        """
        assert self._connection
        self._connection.autocommit = True
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
