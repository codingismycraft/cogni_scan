import psycopg2
import sys

DEFAULT_CONN_STR = "postgresql://postgres:test@localhost:5433/scans"


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