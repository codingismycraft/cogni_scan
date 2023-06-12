import json
import os.path

import cv2
import nibabel as nib
import psycopg2

import cogni_scan.src.dbutil as dbutil

INSERT_SQL = """
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
        '{fullpath}', {days} ,'{patiend_id}', '{origin}', 
        {skipit}, {health_status}, '{axis}', '{rotation}'
    )
""".format


UPDATE_SQL = """
    Update 
        Scan set skipit={skipit}, axis='{axis}', rotation='{rotation}'
    where
        fullpath='{fullpath}'
""".format

SELECT_SQL = """
    Select axis, rotation 
    from scan 
    where fullpath = '{fullpath}';
""".format

DEFAULT_AXIS_MAPPING = json.dumps({0: 0, 1: 1, 2: 2})
DEFAULT_ORIENTATION = json.dumps([0, 0, 0])


def insert_to_db(fullpath, days, origin, patiend_id, health_status):
    assert os.path.isfile(fullpath)
    assert 0 <= health_status <= 2
    sql = INSERT_SQL(
        fullpath=fullpath,
        days=days,
        patiend_id=patiend_id,
        origin=origin,
        skipit=0,
        health_status=health_status,
        axis=DEFAULT_AXIS_MAPPING,
        rotation=DEFAULT_ORIENTATION
    )
    dbutil.execute_non_query(sql)


def load_from_db(skip=False):
    mris = {}
    sql = "select fullpath, days, patiend_id, origin, skipit, health_status, axis, rotation from scan where skipit = 0 order by fullpath"
    for row in dbutil.execute_query(sql):
        mris[row[0]] = NiftiMri(*row)
    return mris

def load_only_converted():
    pass


class NiftiMri:

    def __init__(self, fullpath, days, patiend_id,
                 origin, skipit, health_status, axis, rotation):
        self.__img = None
        self.__filepath = fullpath
        self.__days = days
        self.__patient_id = patiend_id
        self.__origin = origin
        self.__skipit = skipit
        self.__health_status = health_status
        self.__axis_mapping = {int(k): v for k, v in axis.items()}
        self.__rotation = rotation
        self.__img = None
        self.__is_dirty = False

    def __repr__(self):
        return f'NiftiMri({self.__filepath})'

    def saveToDb(self):
        axis = json.dumps(self.__axis_mapping)
        rotation = json.dumps(self.__rotation)
        sql = UPDATE_SQL(
            skipit=self.__skipit,
            axis=axis,
            rotation=rotation,
            fullpath=self.__filepath
        )
        dbutil.execute_non_query(sql)
        self.__is_dirty = False

    def shouldBeSkiped(self):
        return self.__skipit

    def getOrigin(self):
        return self.__origin

    def getDays(self):
        return self.__days

    def getFilePath(self):
        return self.__filepath

    def getPatientID(self):
        return self.__patient_id

    def getCaption(self):
        return f'{self.__patient_id}:{self.__days}'

    def _loadFromDb(self):
        sql = SELECT_SQL(fullpath=self.__filepath)
        for row in dbutil.execute_query(sql):
            axis = row[0]
            self.__axis_mapping = {int(k): v for k, v in axis.items()}
            self.__rotation = row[1]

    def isDirty(self):
        return self.__is_dirty

    def getFilePath(self):
        return self.__filepath

    def getHealthStatus(self):
        if self.__health_status == 0:
            return "healthy"
        elif self.__health_status == 1:
            return "uncertain"
        elif self.__health_status == 2:
            return "demented"
        else:
            return "unknown"

    def changeOrienation(self, axis):
        assert 0 <= axis <= 2
        axis = self.__axis_mapping.get(axis)
        r = self.__rotation[axis]
        r += 1
        r = r % 4
        self.__rotation[axis] = r
        self.__is_dirty = True

    def setAxisMapping(self, axis_mapping):
        """Binds an axis mapping (used for Oasis-2 for example).

        :param tuple axis_mapping: Permutation of 0, 1, 2

        :raises ValueError: If axis mapping is not a permutation of 0,1,2.
        """
        self.__rotation = [0, 0, 0]
        tokens = axis_mapping.split('-')
        axis_mapping = tuple([int(x) for x in tokens])
        if not isinstance(axis_mapping, tuple):
            raise ValueError
        if not len(axis_mapping) == 3:
            raise ValueError
        if not 0 in axis_mapping:
            raise ValueError
        if not 1 in axis_mapping:
            raise ValueError
        if not 2 in axis_mapping:
            raise ValueError

        self.__axis_mapping = {
            index: value
            for index, value in enumerate(axis_mapping)
        }
        self.__is_dirty = True

    @property
    def axis_mapping(self):
        return self.__axis_mapping.copy()

    def get_slice(self, distance_from_center=0, axis=2):
        if self.__img is None:
            self.__img = nib.load(self.__filepath).get_fdata()
        axis = self.__axis_mapping.get(axis)
        assert self.__img is not None
        assert -1. <= distance_from_center <= 1.
        n = int(int(self.__img.shape[axis] / 2) * (1 + distance_from_center))
        if axis == 0:
            img = self.__img[n, :, :]
        elif axis == 1:
            img = self.__img[:, n, :]
        elif axis == 2:
            img = self.__img[:, :, n]
        else:
            return ValueError

        for _ in range(self.__rotation[axis]):
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return img

        # if axis in self.__size_trasnsformers:
        #     x, y = self.__size_trasnsformers[axis]
        #     return cv2.resize(
        #         img,
        #         dsize=(x, y),
        #         interpolation=cv2.INTER_CUBIC
        #     )
        # else:
        #     return img


if __name__ == '__main__':
    a = load_from_db()
    for x in a:
        print(x)
    # f = "/home/john/repos/cogni_scan/src/impl/tests/testing_data/mri-1.nii.gz"
    # nm = NiftiMri(f)
    # nm.saveToDb()
