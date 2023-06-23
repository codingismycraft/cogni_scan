"""Exposes the funcionality to retrieve the dataset from the db."""

import random

import numpy as np

import cogni_scan.src.dbutil as dbutil

_VALID_SLICES = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]


def loadScanFeatures(name, slices=None):
    """Loads and returns the features that will be user for the model creation.

    :param name: The name of the dataset as it stored in the database.

    :param slices: A list that designates the slice that will be used. Each
    slice must be expresses as one of the following two digit strings (each
    one is refering to one slice, the first digit is the axis the second
    the slice with 2 been the center slice:

                01, 02, 03,
                11, 12, 13,
                21, 22, 23

    returns:
        list for training features (X_train)
        list of training labels (Y_train), a label can take the values
        0: HH and 1: HD

        list for validation features (X_val)
        list of validation labels (Y_val)

        list for testing features (X_test)
        list of testing labels (Y_test)

        {
            "X_train": [....],
            "X_train": [....],
            "X_val": [....],
            "Y_val": [ 0, 1 ....],
            "X_test": [ 0, 1 ....],
            "Y_test": [ 0, 1 ....],
        }

    :raises: ValueError
    """
    if not slices:
        slices = ["02"]

    dbo = dbutil.SimpleSQL()

    with dbo as db:
        sql = f"Select training_scan_ids, validation_scan_ids, " \
              f"testing_scan_ids from datasets where name='{name}'"

        is_valid = False
        for row in db.execute_query(sql):
            train, val, test = row
            is_valid = True

        random.shuffle(train)
        random.shuffle(val)
        random.shuffle(test)

        if not is_valid:
            raise ValueError(f"dataset: {name} not found.")

        X_train = [getFeatures(d['scan_id'], db, slices) for d in train]
        X_train =np.array(X_train)
        Y_train = [[0] if d['label'] == 'HH' else [1] for d in train]
        Y_train =np.array(Y_train)

        X_val = [getFeatures(d['scan_id'], db, slices) for d in val]
        X_val =np.array(X_val)
        Y_val = [[0] if d['label'] == 'HH' else [1] for d in val]
        Y_val =np.array(Y_val)

        X_test = [getFeatures(d['scan_id'], db, slices) for d in test]
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


def getFeatures(scan_id, db, slices):
    n = len(slices)
    assert n > 0
    slice_names = []
    for slice in slices:
        _validateSlice(slice)
        slice_names.append(f"features_slice{slice}")
    sql = "SELECT " + ','.join(slice_names) + \
          f" from scan_features where scan_id={scan_id}"
    features = []
    for row in db.execute_query(sql):
        for i in range(n):
            features.extend(row[i][0])
    return features


def _validateSlice(slice):
    if slice not in _VALID_SLICES:
        raise ValueError(f"Invalid slice: {slice}")


if __name__ == '__main__':
    # scan_id = 305
    # dbo = dtraiwbutil.SimpleSQL()
    # with dbo as db:
    #     getFeatures(scan_id, db, ['01', '22', '13'])

    loadScanFeatures(name="Dataset")
