"""(Re)creates a SQLite db holding the Scan information."""
import os

import pandas as pd
import sqlite3

import constants

CREATE_MRI_TABLE = """
    CREATE TABLE mri(
        path TEXT PRIMARY KEY,
        axis_0 INTEGER DEFAULT 0,
        axis_1 INTEGER DEFAULT 1,
        axis_2 INTEGER DEFAULT 2,
        rotation TEXT
    );
"""

if __name__ == '__main__':
    with sqlite3.connect(constants.COGNI_DB) as conn:
        conn.execute(CREATE_MRI_TABLE)
