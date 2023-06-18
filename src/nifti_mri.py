"""Exposes the MRIs as a collection of objects."""

import json
import os.path

import cv2
import nibabel as nib

import cogni_scan.src.dbutil as dbutil

_SQL_UPDATE_ONE = """
    Update
        Scan set skipit={skipit}, axis='{axis}', rotation='{rotation}'
    where
        fullpath='{fullpath}'
""".format

_SQL_SELECT_ALL = """
select
    scan_id, fullpath, days, patiend_id, origin,
    skipit, health_status, axis, rotation
from
    scan
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
    skipit, health_status, axis, rotation
from
    scan
where scan_id={scan_id}
""".format

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

    def loadFromDb(self):
        """Load data from the database and populate the patient collection.

        Each row from the database is processed to create a new Scan object,
        which is then associated with the corresponding Patient. Additionally,
        a mapping from Scan ID to Scan object is created for faster searches.
        """
        self.__patients = {}
        self.__mri_id_to_mri = {}
        self.__was_loaded = False

        for row in dbutil.execute_query(_SQL_SELECT_ALL):
            (scan_id, fullpath, days, patient_id, origin,
             skipit, health_status, axis, rotation) = row

            if patient_id not in self.__patients:
                self.__patients[patient_id] = Patient(patient_id)

            scan = Scan(scan_id, fullpath, days, patient_id, origin, skipit,
                        health_status, axis, rotation)

            self.__patients[patient_id].addScan(scan)
            self.__mri_id_to_mri[scan.getScanID()] = scan

        # Assign the exit health status to all the patients.
        for row in dbutil.execute_query(_SQL_SELECT_EXIT_HEALTH_STATUS):
            patient_id, health_status = row
            if patient_id in self.__patients:
                self.__patients[patient_id].setExitHealthStatus(health_status)

        self.__was_loaded = True

    def getPatient(self, patiend_id):
        if not self.__was_loaded:
            self._loadFromDb()
        assert self.__was_loaded
        if patiend_id in self.__patients:
            return self.__patients[patiend_id]
        else:
            raise ValueError

    def getPatientIDs(self):
        """Yields patient IDs from the patient collection."""
        if not self.__was_loaded:
            self._loadFromDb()
        assert self.__was_loaded
        for patiend_id, patient in self.__patients.items():
            yield patiend_id, patient.getTitle()

    def getMrisByPatient(self, patient_id):
        if not self.__was_loaded:
            self._loadFromDb()
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
        for patient in self.__patients.values():
            if patient.getLabel() == "HH":
                hh_count += 1
            elif patient.getLabel() == "HD":
                hd_count += 1
            total_scans += patient.numberOfScans()

        return {
            "Number of Patients": len(self.__patients),
            "Number of HH Patients": hh_count,
            "Number of HD Patients": hd_count,
            "Total Number of Scans": total_scans,
        }

    def getMriByMriID(self, mri_id):
        assert mri_id in self.__mri_id_to_mri
        return self.__mri_id_to_mri[mri_id]

    def getDesctiptiveDataForPatient(self, patient_id):
        if not self.__was_loaded:
            self._loadFromDb()
        assert self.__was_loaded
        assert patient_id in self.__patients
        patient = self.__patients[patient_id]
        return patient.getDescriptiveData()


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

    def getDescriptiveData(self):
        return {
            "Patient ID": self.__patient_id,
            "Health Status": self.getLabel(),
            "Number Of Scans": self.numberOfScans(),
            "Distinct Days": self.numberOfDistinctDays(),
        }

    def addScan(self, scan):
        self.__scans.append(scan)
        self.__scans.sort(key=lambda x: x.getDays())

    def getTitle(self):
        return f'{self.__patient_id} {self.getLabel()}'

    def getExitHealthStatus(self):
        return self.__exit_health_status

    def setExitHealthStatus(self, health_status):
        assert 0 <= health_status <= 2
        self.__exit_health_status = health_status

    def getLabel(self):
        exit_status = int2HealthStatus(self.__exit_health_status)
        enter_status = int2HealthStatus(self.__scans[0].getHealthStatus())
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


class Scan:

    def __init__(self, scan_id, fullpath, days, patient_id,
                 origin, skipit, health_status, axis, rotation):
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
        self.__is_dirty = False


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
        axis = json.dumps(self.__axis_mapping)
        rotation = json.dumps(self.__rotation)
        sql = _SQL_UPDATE_ONE(
            skipit=self.__skipit,
            axis=axis,
            rotation=rotation,
            fullpath=self.__filepath
        )
        dbutil.execute_non_query(sql)
        self.__is_dirty = False

    def getScanID(self):
        return self.__scan_id

    def getPatientID(self):
        return self.__patient_id

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
