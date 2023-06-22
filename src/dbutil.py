import psycopg2
import sys

DEFAULT_CONN_STR = "postgresql://postgres:test@localhost:5433/scans"


class SimpleSQL:

    def __init__(self, connstr=None):
        self._connection = None
        self._connstr = connstr or DEFAULT_CONN_STR

    def __enter__(self):
        assert self._connection is None
        self._connection = psycopg2.connect(self._connstr)
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

def execute_query(sql, conn_str=None):
    conn_str = conn_str or DEFAULT_CONN_STR
    con = None
    try:
        con = psycopg2.connect(conn_str)
        cursor = con.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        for row in records:
            yield row
    except Exception as e:
        raise e
    finally:
        if con:
            con.close()


def execute_non_query(sql, conn_str=None):
    """Executes a non select statement.

    :param sql: the sql to execute

    :raise:psycopg2.DatabaseError
    """
    conn_str = conn_str or DEFAULT_CONN_STR
    con = None
    try:
        con = psycopg2.connect(conn_str)
        con.autocommit = True
        cur = con.cursor()
        cur.execute(sql)
    except Exception as e:
        raise e
    finally:
        if con:
            con.close()


if __name__ == '__main__':
    import random

    features = [random.uniform(0, 1.0) for i in range(10)]
    print(features)
    sql = """insert into scan_features (scan_id) values (111) """
    execute_non_query(sql)
