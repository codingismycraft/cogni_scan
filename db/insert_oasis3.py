"""Initilizes the database with all the oasis3 MRIS.

Assumes that we have already downloaded the oasis3 MRIS files and also
we have createed a csv file holding the descriptive data that will be
added to the database.

To open the scans database:
psql postgresql://postgres:test@localhost:5433/scans

To recreate the database from scratch:

$ dropdb scans
$ createdb scans
$ cd cogni_scan/db
$ ./create_db.sh
"""

import csv
import json
import os
import pathlib

import cogni_scan.src.dbutil as dbutil

_INSERT_SQL = """
    INSERT INTO scan (
        fullpath,
        days,
        patiend_id,
        origin,
        skipit,
        health_status,
        axis, 
        rotation
    )
    VALUES ( 
        '{path}', {days} ,'{patiend_id}', '{origin}', 
        {skipit}, {health_status}, '{axis}', '{rotation}'
    )
""".format

_DEFAULT_AXIS_MAPPING = json.dumps({0: 0, 1: 1, 2: 2})
_DEFAULT_ORIENTATION = json.dumps([0, 0, 0])

def insert_oasis3_files(filepath="oasis3_subjects.csv"):
    """Inserts the OASIS3 desccriptive data into the the database."""
    origin = "oasis3"
    with open(filepath) as fin:
        for index, tokens in enumerate(csv.reader(fin)):
            if index == 0:
                continue
            subject_id, path, days, status = tokens
            health_status = int(status)
            days = int(days)
            print(subject_id, health_status, path, days)
            assert os.path.isfile(path)
            assert 0 <= health_status <= 2
            sql = _INSERT_SQL(
                path=path,
                days=days,
                patiend_id=subject_id,
                origin=origin,
                skipit=0,
                health_status=health_status,
                axis=_DEFAULT_AXIS_MAPPING,
                rotation=_DEFAULT_ORIENTATION
            )
            dbutil.execute_non_query(sql)


if __name__ == '__main__':
    insert_oasis3_files()
