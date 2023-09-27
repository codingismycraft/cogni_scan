import datetime
import os
import functools
import pathlib
import json

import nibabel as nib
import cogni_scan.src.nifti_mri as nm

AXES = [
    (0, 1, 2),
    (0, 2, 1),
    (1, 0, 2),
    (1, 2, 0),
    (2, 1, 0),
    (2, 0, 1)
]

ROTATE_90_CLOCKWISE = "ROTATE_90_CLOCKWISE"
ROTATE_90_COUNTERCLOCKWISED = "ROTATE_90_COUNTERCLOCKWISED"
ROTATE_180 = "ROTATE_180"

ROTATIONS = [
    ROTATE_90_CLOCKWISE,
    ROTATE_90_COUNTERCLOCKWISED,
    ROTATE_180,
    ''
]


def getDabaseName():
    home_dir = pathlib.Path.home()
    filename = os.path.join(home_dir, '.cogni_scan', 'settings.json')
    with open(filename) as fin:
        settings = json.load(fin)
        return settings["database_name"]


def getPsqlConnectionString():
    home_dir = pathlib.Path.home()
    filename = os.path.join(home_dir, '.cogni_scan', 'settings.json')
    with open(filename) as fin:
        settings = json.load(fin)
        dbname = settings["database_name"]
        port = settings["postgres_port"]
        password = settings["postgres_password"]
        return f"postgresql://postgres:{password}@localhost:{port}/{dbname}"


def getAxesOrientation():
    axes = []
    for a1, a2, a3 in AXES:
        axes.append(f"{a1}-{a2}-{a3}")
    return axes


def loadMRI(filepath):
    return nm.NiftiMri(filepath)


def timeit(foo):
    @functools.wraps(foo)
    def inner(*args, **kwargs):
        t1 = datetime.datetime.now()
        try:
            return foo(*args, **kwargs)
        except:
            raise
        finally:
            t2 = datetime.datetime.now()
            print("Duration: ", (t2 - t1).total_seconds())

    return inner


def saveMri(path, axes=None, rotation=None):
    """Saves the transforation data for the passed in path to MRI.

    (str) path: The full path to an mri image.
    (tuple) axes: Permutation of 0, 1, 2
    (str) rotation: The CV based rotation to apply.
    """
    if axes is None:
        axes = 0, 1, 2
    if rotation is None:
        ratation = ''
    if axes not in AXES or rotation not in ROTATIONS:
        raise ValueError

    axis_0, axis_1, axis_2 = axes

    sql = f"""
        INSERT INTO
            mri(path,axis_0,axis_1,axis_2,rotation)
        VALUES
            ('{path}', {axis_0}, {axis_1}, {axis_2}, '{rotation}' )
        ON CONFLICT(path) DO
        UPDATE SET
            axis_0={axis_0},
            axis_1={axis_1},
            axis_2={axis_2},
            rotation={rotation};
    """

    print(sql)


if __name__ == '__main__':
    print (getDabaseName())
    print(getPsqlConnectionString())
