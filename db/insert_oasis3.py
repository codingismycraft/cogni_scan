"""Initilizes the database with all the oasis3 scripts.+"""

import os
import csv
import pathlib

import cogni_scan.src.nifti_mri as nifti_mri

HOME_DIR = pathlib.Path.home()
OASIS3_ROOT = os.path.join(HOME_DIR, "oasis3-scans")


def insert_oasis3_files():
    origin = "oasis3"
    with open("oasis3_subjects.csv") as fin:
        for index, tokens in enumerate(csv.reader(fin)):
            if index == 0:
                continue
            subject_id, path, days, status = tokens
            health_status = int(status)
            days = int(days)
            print(subject_id, health_status, path, days)
            nifti_mri.insert_to_db(
                path, days, origin, subject_id, health_status
            )


if __name__ == '__main__':
    insert_oasis3_files()
