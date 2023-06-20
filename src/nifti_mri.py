"""Exposes the MRIs as a collection of objects."""

import copy
import json
import os.path
import pickle

import cv2
import nibabel as nib
import numpy as np

import cogni_scan.src.dbutil as dbutil

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow import keras


class _FeatureExtractor:
    _ready = False

    def __call__(self, image):
        if not self._ready:
            self.__model_1 = VGG16(
                weights='imagenet', include_top=False, input_shape=(200, 200, 3)
            )
            self._ready = True

        features = self.__model_1.predict(np.array([image]))
        gavg = keras.layers.GlobalAveragePooling2D()(features)
        return keras.layers.Flatten()(gavg)


_feature_extractor = _FeatureExtractor()


def add_rgb_channels(imgs):
    """Adds the RGB channels to a collection of gray scale images.

    :param imgs: A numpy array holding a collection of gray scale images.
    :return: A numpy array holding RGB images.
    """
    if len(imgs) == 0:
        return imgs

    rgb = np.repeat(imgs, 3)
    return rgb.reshape(imgs.shape + (3,))


_SQL_SELECT_ALL = """
select
    scan_id, fullpath, days, patiend_id, origin,
    skipit, health_status, axis, rotation, sd0, sd1, sd2
from
    scan
order by patiend_id, days, scan_id
"""

_SQL_SELECT_NON_SKIPPED = """
select
    scan_id, fullpath, days, patiend_id, origin,
    skipit, health_status, axis, rotation, sd0, sd1, sd2
from
    scan
where skipit=0
order by patiend_id, days, scan_id
"""

_SQL_SELECT_EXIT_HEALTH_STATUS = """
select a.patient_id, a.health_status from diagnosis a, 
(Select patient_id, max(days) as days from diagnosis group by patient_id) b  
where a.patient_id = b.patient_id and a.days = b.days;
"""

_SQL_SELECT_ONE = """
select
    scan_id, fullpath, days, patiend_id, origin,
    skipit, health_status, axis, rotation, sd0, sd1, sd2
from
    scan
where scan_id={scan_id}
""".format

_SQL_INSERT_FEATURES = """
INSERT INTO scan_features (
    scan_id,
    distance_0,
    distance_1,
    distance_2,
    features_slice01,
    features_slice02,
    features_slice03,
    features_slice11,
    features_slice12,
    features_slice13,
    features_slice21,
    features_slice22,
    features_slice23
)
VALUES (
   {}, {}, {}, {}, '{}','{}','{}','{}','{}','{}','{}','{}','{}'
)
"""

_SQL_UPDATE_ONE = """
    Update
        Scan set skipit={skipit}, axis='{axis}', rotation='{rotation}',
        sd0 = {sd0}, sd1 = {sd1},  sd2 = {sd2}
    where
        fullpath='{fullpath}'
""".format

_SQL_SELECT_SCANS_WITH_FEATURES = """select scan_id from scan_features"""


def int2HealthStatus(value):
    if value == 0:
        return "H"
    elif value == 1:
        return "U"
    elif value == 2:
        return "D"
    else:
        return "?"


class PatientCollection:
    """Holds all the available MRI objects.

    Attributes

    __patients: Maps patient IDs to Patient objects.
    __mri_id_to_mri: Maps scan IDs to corresponding Scan objects.
    __was_loaded: a flag indicating whether the data was successfully loaded.
    """

    def __init__(self):
        """Initialize the object with default values."""
        self.__patients = {}
        self.__mri_id_to_mri = {}
        self.__was_loaded = False

    def loadFromDb(self, hide_skipped=False, show_labels="ALL",
                   show_only_healthy=False):
        """Load data from the database and populate the patient collection.

        Each row from the database is processed to create a new Scan object,
        which is then associated with the corresponding Patient. Additionally,
        a mapping from Scan ID to Scan object is created for faster searches.
        """
        self.__patients = {}
        self.__mri_id_to_mri = {}
        self.__was_loaded = False

        # Load the scan ids that have VGG features in the database.
        having_vgg_features = set()
        for row in dbutil.execute_query(_SQL_SELECT_SCANS_WITH_FEATURES):
            scan_id = row[0]
            having_vgg_features.add(scan_id)

        # Load the scans from the database.
        if hide_skipped:
            sql = _SQL_SELECT_NON_SKIPPED
        else:
            sql = _SQL_SELECT_ALL

        for row in dbutil.execute_query(sql):
            (scan_id, fullpath, days, patient_id, origin,
             skipit, health_status, axis, rotation, sd0, sd1, sd2) = row

            if patient_id not in self.__patients:
                self.__patients[patient_id] = Patient(patient_id)

            scan = Scan(scan_id, fullpath, days, patient_id, origin, skipit,
                        health_status, axis, rotation, sd0, sd1, sd2)

            # Set the has VGG features if needed.
            if scan.getScanID() in having_vgg_features:
                scan.setToHasVGGFeatures()

            self.__patients[patient_id].addScan(scan)
            self.__mri_id_to_mri[scan.getScanID()] = scan

        # Assign the exit health status to all the patients.
        for row in dbutil.execute_query(_SQL_SELECT_EXIT_HEALTH_STATUS):
            patient_id, health_status = row
            if patient_id in self.__patients:
                self.__patients[patient_id].setExitHealthStatus(health_status)

        if show_only_healthy:
            for _, v in self.__patients.items():
                v.keepOnlyHealthyScans()

        # Filter by selected label.
        if show_labels != "ALL":
            labels = show_labels.split("-")
            temp = {}
            for k, v in self.__patients.items():
                l = v.getLabel()
                if v.getLabel() in labels:
                    temp[k] = v
            self.__patients = temp

        self.__was_loaded = True

    def saveLabelsToDb(self):
        dbutil.execute_non_query("delete from patient")
        for patient_id, patient in self.__patients.items():
            label = patient.getLabel()
            sql = f"INSERT INTO " \
                  f"patient (patient_id,label) values" \
                  f"('{patient_id}', '{label}')"
            print(sql)
            dbutil.execute_non_query(sql)

    def getPatient(self, patiend_id):
        if not self.__was_loaded:
            self.loadFromDb()
        assert self.__was_loaded
        if patiend_id in self.__patients:
            return self.__patients[patiend_id]
        else:
            raise ValueError

    def getPatientIDs(self):
        """Yields patient IDs from the patient collection."""
        if not self.__was_loaded:
            self.loadFromDb()
        assert self.__was_loaded
        for patiend_id, patient in self.__patients.items():
            yield patiend_id, patient.getTitle()

    def getMrisByPatient(self, patient_id):
        if not self.__was_loaded:
            self.loadFromDb()
        assert self.__was_loaded
        assert patient_id in self.__patients
        patient = self.__patients[patient_id]
        count = patient.numberOfScans()
        for i in range(count):
            yield patient.getScan(i)

    def getDesctiptiveData(self):

        hh_count = 0
        hd_count = 0
        total_scans = 0
        patients_with_vgg_features = 0

        for patient in self.__patients.values():
            if patient.getLabel() == "HH":
                hh_count += 1
            elif patient.getLabel() == "HD":
                hd_count += 1
            total_scans += patient.numberOfScans()

            if patient.hasVGGFeatures():
                patients_with_vgg_features += 1

        return {
            "Number of Patients .........": len(self.__patients),
            "Number of HH Patients.......": hh_count,
            "Number of HD Patients.......": hd_count,
            "Total Number of Scans.......": total_scans,
            "Distinct Days ..............": self.numberOfDistinctDays(),
            "Patients with VGG features...": patients_with_vgg_features
        }

    def getMriByMriID(self, mri_id):
        assert mri_id in self.__mri_id_to_mri
        return self.__mri_id_to_mri[mri_id]

    def getDesctiptiveDataForPatient(self, patient_id):
        if not self.__was_loaded:
            self.loadFromDb()
        assert self.__was_loaded
        assert patient_id in self.__patients
        patient = self.__patients[patient_id]
        return patient.getDescriptiveData()

    def numberOfDistinctDays(self):
        count = 0
        for _, v in self.__patients.items():
            count += v.numberOfDistinctDays()
        return count

    def saveVGG16Features(self):
        for k, v in self.__patients.items():
            v.saveVGG16Features()


class Patient:
    """Holds the information about a patient.

    Allows us to sort / search for patients for specific health statuses,
    origin of Mris (like Oasis3, Oasis2, ADNI etc).

    Attributes

    __label: Labels the patient with a string of two letters in
    the format AB where A and B represent the health status for the patient
    as he entered and exited the system.

    H: healthy
    D: demented
    U: Uncertain.
    """

    def __init__(self, patient_id):
        self.__patient_id = patient_id
        self.__scans = []
        self.__exit_health_status = '?'
        self.__has_scans_with_vgg_features = False

    def hasVGGFeatures(self):
        return self.__has_scans_with_vgg_features

    def getDescriptiveData(self):
        return {
            "Patient ID": self.__patient_id,
            "Health Status": self.getLabel(),
            "Number Of Scans": self.numberOfScans(),
            "Distinct Days": self.numberOfDistinctDays(),
        }

    def keepOnlyHealthyScans(self):
        self.__scans = [
            scan for scan in self.__scans if scan.getHealthStatus() == 0]

    def addScan(self, scan):
        self.__scans.append(scan)
        self.__scans.sort(key=lambda x: x.getDays())
        if scan.hasVGGFeatures():
            self.__has_scans_with_vgg_features = True

    def getTitle(self):
        return f'{self.__patient_id} {self.getLabel()}'

    def getExitHealthStatus(self):
        return self.__exit_health_status

    def setExitHealthStatus(self, health_status):
        assert 0 <= health_status <= 2
        self.__exit_health_status = health_status

    def getLabel(self):
        exit_status = int2HealthStatus(self.__exit_health_status)
        try:
            enter_status = int2HealthStatus(self.__scans[0].getHealthStatus())
        except Exception as ex:
            enter_status = '?'
        label = f'{enter_status}' \
                f'{exit_status}'
        return label

    def numberOfScans(self):
        return len(self.__scans)

    def numberOfDistinctDays(self):
        days = set()
        for scan in self.__scans:
            days.add(scan.getDays())
        return len(days)

    def getScan(self, index):
        assert 0 <= index < len(self.__scans)
        return self.__scans[index]

    def saveVGG16Features(self):
        for scan in self.__scans:
            scan.saveVGG16Features()


class Scan:

    def __init__(self, scan_id, fullpath, days, patient_id,
                 origin, skipit, health_status, axis, rotation, sd0, sd1, sd2):
        self.__scan_id = scan_id
        self.__img = None
        self.__filepath = fullpath
        self.__days = days
        self.__patient_id = patient_id
        self.__origin = origin
        self.__skipit = skipit
        self.__health_status = health_status
        self.__axis_mapping = {int(k): v for k, v in axis.items()}
        self.__rotation = rotation
        self.__img = None
        self.__slice_distances = [sd0, sd1, sd2]
        self.__is_dirty = False
        self.__has_VGG_features = False

    def hasVGGFeatures(self):
        return self.__has_VGG_features

    def setToHasVGGFeatures(self):
        self.__has_VGG_features = True

    def __repr__(self):
        return f'NiftiMri({self.__filepath})'

    def restoreOriginalState(self):
        """Called when the state changes need to be restored.

        Re-Loads the details of the MRI from the database.
        """
        sql = _SQL_SELECT_ONE(scan_id=self.__scan_id)
        for row in dbutil.execute_query(sql):
            self.__init__(*row)

    def saveToDb(self):
        sd0, sd1, sd2 = self.__slice_distances
        axis = json.dumps(self.__axis_mapping)
        rotation = json.dumps(self.__rotation)
        sql = _SQL_UPDATE_ONE(
            skipit=self.__skipit,
            axis=axis,
            rotation=rotation,
            fullpath=self.__filepath,
            sd0=sd0,
            sd1=sd1,
            sd2=sd2
        )
        dbutil.execute_non_query(sql)
        self.__is_dirty = False

    def getScanID(self):
        return self.__scan_id

    def getPatientID(self):
        return self.__patient_id

    def getSliceDistances(self):
        return copy.deepcopy(self.__slice_distances)

    def setSliceDistance(self, index, slice_distance):
        assert 0 <= index <= 2
        assert 0. <= slice_distance < 1.0
        if self.__slice_distances[index] == slice_distance:
            return
        self.__slice_distances[index] = slice_distance
        self.__is_dirty = True

    def shouldBeSkiped(self):
        return self.__skipit

    def setShouldBeSkiped(self, value):
        assert value in (0, 1)
        if self.__skipit != value:
            self.__skipit = value
            self.__is_dirty = True

    def getMriID(self):
        hs = int2HealthStatus(self.getHealthStatus())
        return f"{self.__scan_id}:{self.__days:5}:{hs}"

    def getOrigin(self):
        return self.__origin

    def getDays(self):
        return self.__days

    def getFilePath(self):
        return self.__filepath

    def isDirty(self):
        return self.__is_dirty

    def getFilePath(self):
        return self.__filepath

    def getHealthStatus(self):
        return int(self.__health_status)

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
        if 0 not in axis_mapping:
            raise ValueError
        if 1 not in axis_mapping:
            raise ValueError
        if 2 not in axis_mapping:
            raise ValueError

        self.__axis_mapping = {
            index: value
            for index, value in enumerate(axis_mapping)
        }
        self.__is_dirty = True

    @property
    def axis_mapping(self):
        return self.__axis_mapping.copy()

    def get_slice(self, distance_from_center=0, axis=2, bounding_square=400):
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

        x, y = img.shape

        if x > y:
            ratio = y / x
            x = bounding_square
            y = bounding_square * ratio
        elif x < y:
            ratio = x / y
            y = bounding_square
            x = bounding_square * ratio
        else:
            x = y = bounding_square

        # See also: https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv

        x = int(x)
        y = int(y)
        l_img = np.full((bounding_square, bounding_square), 0)
        x_offset = int((bounding_square - y) / 2)
        y_offset = int((bounding_square - x) / 2)
        s_img = cv2.resize(img, dsize=(y, x), interpolation=cv2.INTER_CUBIC)
        l_img[y_offset:y_offset + s_img.shape[0],
        x_offset:x_offset + s_img.shape[1]] = s_img
        return l_img

    def saveVGG16Features(self):
        print(self.__scan_id)
        scan_id = self.__scan_id
        d0, d1, d2 = self.__slice_distances
        features = []
        for axis in [0, 1, 2]:
            dist = self.__slice_distances[axis]
            for d in [-dist, 0, dist]:
                slice = self.get_slice(
                    distance_from_center=d, axis=axis, bounding_square=200
                )
                img = add_rgb_channels(slice)
                a = np.array(_feature_extractor(img))
                jsn = json.dumps(a.tolist())
                features.append(jsn)

        sql = _SQL_INSERT_FEATURES.format(
            scan_id, d0, d1, d2, *features
        )

        print("Inserting to the database: ", self.__scan_id)
        dbutil.execute_non_query(sql)


if __name__ == '__main__':
    patients = PatientCollection()
    # ids = list(patients.getPatientIDs())
    # for x in ids:
    #     p = patients.getPatient(x[0])
    #     label = p.getLabel()
    #     if label == 'HD':
    #          print(p.getTitle())

    patient_id = 'OAS30326'
    print(patients.getDesctiptiveDataForPatient(patient_id))

    # patient = patients.getPatient(patient_id)
    # print(patient.getLabel())
    #
    # for x in patients.getMrisByPatient(patient_id):
    #     print(x.getMriID())
