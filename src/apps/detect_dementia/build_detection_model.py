"""Builds a model to detect dementia."""

import random

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

import numpy as np
import tensorflow as tf

import cogni_scan.src.dbutil as dbutil

_SQL_SELECT_DEMENTED = """
select 
    a.scan_id, a.patient_id 
from 
    scan as a, scan_features b 
where 
        a.validation_status = 2 
    and a.scan_id = b.scan_id 
    and (a.health_status = 1 or a.health_status = 2) 
"""

_SQL_SELECT_HEALTHY = """
select 
    a.scan_id, a.patient_id
from 
    scan as a, scan_features b
where 
        a.validation_status = 2
    and a.scan_id = b.scan_id 
    and a.health_status = 0
and a.patient_id not in 
    (
        select patient_id from scan 
        where validation_status = 2 and (health_status = 1 or health_status = 2)
    )
"""

_VALID_SLICES = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]


def _getFeaturesForScan(scan_id, slices, db):
    """Returns the features from the scan for the passed in slices."""
    slices = sorted(slices)
    n = len(slices)
    assert n > 0, "You must select at least one slice."
    slice_names = []
    for slice in slices:
        assert slice in _VALID_SLICES
        slice_names.append(f"features_slice{slice}")
    sql = "SELECT " + ','.join(slice_names) + \
          f" from scan_features where scan_id={scan_id}"
    features = []
    for row in db.execute_query(sql):
        for i in range(n):
            features.extend(row[i][0])
    assert features, f"Could not find features for {scan_id}."
    return features


def _trainModel(number_of_slices,
                 X_train, Y_train,
                 X_val, Y_val,
                 X_test, Y_test,
                 max_epochs=120):
    """Trains and save the model."""

    input_size = number_of_slices * 512
    size_1 = input_size * 2
    hidden_size_2 = int(input_size /3)

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(input_size))
    model.add(tf.keras.layers.Dense(size_1, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(hidden_size_2, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.2))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    optimizer = tf.optimizers.Adam(learning_rate=0.0001)

    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=[tf.keras.metrics.AUC()]
    )

    early_stoppping = EarlyStopping(
        monitor='val_auc',
        patience=10,
        restore_best_weights=True
    )

    reduce_lr_on_plateau = ReduceLROnPlateau(
        monitor='val_auc', factor=0.1, patience=10
    )

    history = model.fit(
        X_train,
        Y_train,
        # batch_size=100,
        epochs=max_epochs,
        validation_data=(X_val, Y_val),
        callbacks=[early_stoppping,reduce_lr_on_plateau],
        verbose=2
    )

    training_history = history.history

    # Calculate the performance of the model.
    y_pred = model.predict(X_test)
    y_pred_bin = [1 if p[0] > 0.60 else 0 for p in y_pred]

    cm = confusion_matrix(Y_test, y_pred_bin)
    f1 = f1_score(Y_test, y_pred_bin)
    ac = accuracy_score(Y_test, y_pred_bin)
    roc = roc_auc_score(Y_test, y_pred)
    fpr, tpr, thresholds = roc_curve(Y_test, y_pred)

    return {
        "confussion_matrix": cm,
        "F1_score": f1,
        "Accuracy_score": ac,
        "ROC": roc,
        "fpr": fpr,
        "tpr": tpr,
        "thresholds": thresholds
    }



def _loadFeatures(db, sql, slices):
    """For the passed in sql returns the matching scan IDs.

    :param db: A database wrapper object.

    :param sql: The sql statement to execute (str).

    :param slices: A list of strings each of them holding a slice id (see the
    definition of the _VALID_SLICES to understand better).

    The returned scans are guaranteed to be valid and also guaranteed to
    have features in the database and also based on the passed in SQL statement
    we control whether it will return healthy or demented patients.

    See the SQL statements to better understand the logic behind the
    selection of the scans.

    :returns: A list of features based on the passed in slices.
    """
    rows = []
    for row in db.execute_query(sql):
        try:
            scan_id, patient_id = row[0], row[1]
            rows.append((scan_id, patient_id))
        except Exception as ex:
            print(ex, type(ex))
    random.shuffle(rows)

    # Use scan ids only once per patient!
    scan_ids = []
    used_patiend_ids = set()
    for scan_id, patient_id in rows:
        if True or patient_id not in used_patiend_ids:
            scan_ids.append(scan_id)
            used_patiend_ids.add(patient_id)

    # At this point scan_ids is an array of integers representing scan_ids.
    # For each of them we need to load the corresponding features from
    # the database (it is guaranteed that the features will exist based on
    # the passed in SQL statement) using the passed in slices.
    features = []

    for scan_id in scan_ids:
        features.append(_getFeaturesForScan(scan_id, slices, db))

    # Yes i know, I use list comprehension, ask me why i prefer this.
    return features


def _breakDown(data, label, train_ratio=0.7, test_ratio=0.15):
    assert label in (0, 1)
    assert 0 < train_ratio < 1.
    assert 0 < test_ratio < 1.
    val_ratio = 1. - (test_ratio + train_ratio)
    assert 0 < val_ratio < 1.

    i = int(len(data) * train_ratio)
    j = int(len(data) * (val_ratio + train_ratio))

    training_data = []
    val_data = []
    testing_data = []

    for index, d in enumerate(data):
        if index < i:
            training_data.append((d, [label]))
        elif index < j:
            val_data.append((d, [label]))
        else:
            testing_data.append((d, [label]))

    return training_data, val_data, testing_data


def buildModel(slices, balanced=False):
    slices = sorted(slices)
    with dbutil.SimpleSQL() as db:
        demented = _loadFeatures(db, _SQL_SELECT_DEMENTED, slices)
        healthy = _loadFeatures(db, _SQL_SELECT_HEALTHY, slices)
        if balanced:
            healthy = healthy[:len(demented)]

    demended_train, demended_val, demended_test = _breakDown(demented, 1)
    healthy_train, healthy_val, healthy_test = _breakDown(healthy, 0)

    train = demended_train + healthy_train
    val = demended_val + healthy_val
    test = demended_test + healthy_test

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    X_train, Y_train = [], []
    for x, y in train:
        X_train.append(x)
        Y_train.append(y)

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)

    X_val, Y_val = [], []
    for x, y in val:
        X_val.append(x)
        Y_val.append(y)

    X_val = np.array(X_val)
    Y_val = np.array(Y_val)

    X_test, Y_test = [], []
    for x, y in test:
        X_test.append(x)
        Y_test.append(y)

    X_test = np.array(X_test)

    # Uncomment the following to see what happens when the labels are random.
    # random.shuffle(Y_test)
    Y_test = np.array(Y_test)

    return _trainModel(len(slices), X_train, Y_train, X_val, Y_val, X_test, Y_test)


if __name__ == '__main__':
    slices = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]
    buildModel(slices)
