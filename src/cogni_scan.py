
import nibabel as nib

import cogni_scan.src.imp

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


def loadMRI(filepath):
    return nib.load(filepath).get_fdata()


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
    saveMri("junk-path")
