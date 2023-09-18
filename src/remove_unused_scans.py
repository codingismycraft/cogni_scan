"""Exposes the MRIs as a collection of objects."""

import os

import cogni_scan.src.dbutil as dbutil

_SQL_SELECT_ALL = """
Select scan_id, fullpath from scan 10;
"""

_SQL_DELETE_SCAN = "DELETE from scan where scan_id = {}"


def loadFromDb():
    not_existing_ids = []
    with dbutil.SimpleSQL() as db:
        for row in db.execute_query(_SQL_SELECT_ALL):
            scan_id, path = row
            print(scan_id, path)
            if not os.path.exists(path):
                not_existing_ids.append(scan_id)

    for row_id in not_existing_ids:
        with dbutil.SimpleSQL() as db:
            sql = _SQL_DELETE_SCAN.format(row_id)
            print(sql)
            db.execute_non_query(sql)


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("dummyscans")
    loadFromDb()
