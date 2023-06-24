"""Exposes a class that implements the IDataset interface."""

import copy
import random

import numpy as np

import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.interfaces as interfaces

_VALID_SLICES = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]


class Dataset(interfaces.IDataset):
    """Wrapper class for the dataset table.

    The dataset table contains distinct datasets holding training, validation
    and testing data that can serve as the input for model creation.

    Datasets have a unique name and also a predefined breakdown of the
    data into training, validation, and testing data. Each of these collections
    is stored in the dataset table as dictionaries with two keys (scan_id and
    label).
    """
    _scan_pool = None  # class level map from scan_id to its patient id.

    def __init__(self, name, created_at, train, val, test):
        """Initialize the dataset."""
        self.__name = name
        self.__created_at = created_at
        self.__stats = self._makeStats(train, val, test)

    def __repr__(self):
        return f"Dataset('{self.__name}')"

    def getName(self):
        """Returns the name of the dataset."""
        return self.__name

    def creationTime(self):
        """Returns the creation time for he dataset."""
        return self.__created_at

    def getStats(self):
        """Returns statistical data for the dataset."""
        return copy.deepcopy(self.__stats)

    def getFeatures(self, slices):
        """Returns the features of the dataset.

        :param slices: A list that designates the slice that will be used. Each
        slice must be expresses as one of the following two digit strings (each
        one is refering to one slice, the first digit is the axis the second
        the slice with 2 been the center slice:

                01, 02, 03,
                11, 12, 13,
                21, 22, 23

        Returns a dict with the following structure:

        The features are grouped as key-value pairs following this format:
        {
            "X_train": [....],
            "Y_train": [....],
            "X_val": [....],
            "Y_val": [ 0, 1 ....],
            "X_test": [ 0, 1 ....],
            "Y_test": [ 0, 1 ....],
        }

        The X values consist of numpy arrays in the form [n, k] where k
        is the number of scans and k is the representation of the features
        for the scan as an array of numpy arrays: [  [..], [..] ... ].
        """
        dbo = dbutil.SimpleSQL()

        with dbo as db:
            sql = f"Select training_scan_ids, validation_scan_ids, " \
                  f"testing_scan_ids from datasets where name='{self.__name}'"

            is_valid = False
            for row in db.execute_query(sql):
                train, val, test = row
                is_valid = True

            random.shuffle(train)
            random.shuffle(val)
            random.shuffle(test)

            if not is_valid:
                raise ValueError(f"dataset: {name} not found.")

            X_train = [self._getFeatures(d['scan_id'], db, slices) for d in
                       train]
            X_train = np.array(X_train)
            Y_train = [[0] if d['label'] == 'HH' else [1] for d in train]
            Y_train = np.array(Y_train)

            X_val = [self._getFeatures(d['scan_id'], db, slices) for d in val]
            X_val = np.array(X_val)
            Y_val = [[0] if d['label'] == 'HH' else [1] for d in val]
            Y_val = np.array(Y_val)

            X_test = [self._getFeatures(d['scan_id'], db, slices) for d in test]
            X_test = np.array(X_test)
            Y_test = [[0] if d['label'] == 'HH' else [1] for d in test]
            Y_test = np.array(Y_test)

            return {
                "X_train": X_train,
                "Y_train": Y_train,
                "X_val": X_val,
                "Y_val": Y_val,
                "X_test": X_test,
                "Y_test": Y_test
            }

    def _getFeatures(self, scan_id, db, slices):
        """Returns the features from the scan for the passed in slices."""
        n = len(slices)
        assert n > 0
        slice_names = []
        for slice in slices:
            self._validateSlice(slice)
            slice_names.append(f"features_slice{slice}")
        sql = "SELECT " + ','.join(slice_names) + \
              f" from scan_features where scan_id={scan_id}"
        features = []
        for row in db.execute_query(sql):
            for i in range(n):
                features.extend(row[i][0])
        return features

    def _validateSlice(self, slice):
        """Validates the passed in slice description."""
        if slice not in _VALID_SLICES:
            raise ValueError(f"Invalid slice: {slice}")

    def _getStatsForCollection(self, collection):
        """Returns statistical info for a specific collection of scans."""
        stats = {}
        distinct_patients = set()

        for d in collection:
            label = d['label']
            scan_id = d['scan_id']
            patient_id = self._getPatientIdFromScanId(scan_id)
            if label not in stats:
                stats[label] = 1
                stats[f'distinct_patients-{label}'] = set()
                stats[f'distinct_patients-{label}'].add(patient_id)
            else:
                stats[label] += 1
                stats[f'distinct_patients-{label}'].add(patient_id)
            distinct_patients.add(patient_id)

        for k, v in stats.items():
            if k.startswith('distinct_patients-'):
                stats[k] = len(v)
        stats['distinct_patients'] = len(distinct_patients)

        return stats

    @classmethod
    def _getPatientIdFromScanId(cls, scan_id):
        """Returns the patient id for the passed in scan."""
        if not cls._scan_pool:
            # Load the scan to patient map.
            dbo = dbutil.SimpleSQL()
            with dbo as db:
                cls._scan_pool = {}
                sql = "select scan_id, patient_id from scan_features"
                for sid, patient_id in db.execute_query(sql):
                    cls._scan_pool[sid] = patient_id
        assert scan_id in cls._scan_pool
        return cls._scan_pool[scan_id]

    def _makeStats(self, train, val, test):
        """Returns statistical data for the dataset."""
        return {
            "training": self._getStatsForCollection(train),
            "val": self._getStatsForCollection(val),
            "test": self._getStatsForCollection(test)
        }
