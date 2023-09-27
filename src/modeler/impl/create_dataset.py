"""Inserts a new dataset to the dataset."""

import json
import random
import uuid

import cogni_scan.src.dbutil as dbutil

_SQL_LOAD_PATIENTS = """
select patient_id, count(*) as counter from scan_features 
where label='{label}' group by patient_id;
"""

_SQL_INSERT_DATASET = """
Insert into datasets (
    dataset_id,
    description,
    training_scan_ids ,
    validation_scan_ids,
    testing_scan_ids
    ) 
values (
    '{dataset_id}',
    '{description}',
    '{training_scan_ids}',
    '{validation_scan_ids}',
    '{testing_scan_ids}'
)
"""

_DEFAULT_SPLITS = 0.7, 0.15, 0.15


def insertNewDatasetToDB(*, dbname, splits=None, balance_rate=0.5):
    """Splits the available scans to train, validation and testing subsets.

    The subsets are created based on a given ratio, such as 70%, 15%, and 15%
    for training, validation, and testing respectively.

    The patient data are arranged in descending order based on the number of
    scans each patient has. This sorting ensures that patients with more scans
    are processed first, reducing the risk of one patient dominating the
    testing and validation subsets.

    After sorting, the function proceeds to sequentially allocate patients to
    the subsets. The patient with the most scans is selected first, followed by
    the patient with the second most scans, and so on until all patients are
    assigned to a subset.

    The allocation is done in a manner that preserves the given ratio for each
    subset. For example, if the ratio is 70% for training, 15% for validation,
    and 15% for testing, the function will allocate patients accordingly to
    achieve these proportions.

    The output of the function is stored in the database  in a separate table
    (datasets) that holds the patient ids, the corresponding subset that it
    belongs (train, validation, testing) and a name for the subset so these
    subsets can then be used for further processing or model creation.
    """
    assert 0. < balance_rate < 1.
    if balance_rate < 0.5:
        balance_rate = 1. - balance_rate
    assert 0.5 <= balance_rate < 1.

    dbutil.SimpleSQL.setDatabaseName(dbname)
    if splits is None:
        splits = _DEFAULT_SPLITS

    # Build the datasets using the data from the scan_features table.
    train_1, val_1, test_1 = _buildDatasets("HD")
    train_2, val_2, test_2 = _buildDatasets("HH")

    if balance_rate == 0.5:
        description = "Balanced"
    elif balance_rate is None:
        description = "User all."
    else:
        description = f"Ratio: {balance_rate}"

    train_1, train_2 = _balanceDatasets(train_1, train_2, balance_rate)
    val_1, val_2 = _balanceDatasets(val_1, val_2, balance_rate)
    test_1, test_2 = _balanceDatasets(test_1, test_2, balance_rate)

    # Merge the labeled datasets.
    train = train_1 + train_2
    val = val_1 + val_2
    test = test_1 + test_2

    print(len(train))
    print(len(val))
    print(len(test))

    print(train)

    # Save the datasets to the database.
    dataset_id = str(uuid.uuid4())
    print(dataset_id)

    sql = _SQL_INSERT_DATASET.format(
        dataset_id=dataset_id,
        description=description,
        training_scan_ids=json.dumps(train),
        validation_scan_ids=json.dumps(val),
        testing_scan_ids=json.dumps(test)
    )

    dbw = dbutil.SimpleSQL()
    with dbw as db:
        db.execute_non_query(sql)


def _balanceDatasets(ds1, ds2, balance_rate):
    """Balances the input datasets to ensure they have equal length."""
    assert 0.5 <= balance_rate < 1.
    if len(ds1) < len(ds2):
        m = int(len(ds1) * balance_rate / (1. - balance_rate))
        return ds1, ds2[:m]
    elif len(ds1) > len(ds2):
        m = int(len(ds2) * balance_rate / (1. - balance_rate))
        return ds2[len(ds1)], ds1
    else:
        return ds1, ds2


def _buildDatasets(label, splits=None):
    """Builds the train, val and testing datasets."""
    if splits is None:
        splits = _DEFAULT_SPLITS
    assert sum(splits) == 1.0

    dbw = dbutil.SimpleSQL()
    with dbw as db:
        sql = _SQL_LOAD_PATIENTS.format(label=label)
        patients = [
            (patient_id, count, random.randint(1, 100))
            for patient_id, count in db.execute_query(sql)
        ]

        patients.sort(key=lambda x: (x[1], x[2]), reverse=True)
        train_size, val_size, test_size = [int(len(patients) * s) for s in
                                           splits]
        training, validation, testing = [], [], []

        for patient_id, counter, _ in patients:
            if len(training) < train_size:
                training.append(patient_id)
            elif len(validation) < val_size:
                validation.append(patient_id)
            else:
                testing.append(patient_id)

        # Load the scan ids for the each selected patient.
        tr_scans, val_scans, test_scans = [], [], []

        for pid in training:
            tr_scans.extend(_getScansByPatientId(pid, db))

        for pid in validation:
            val_scans.extend(_getScansByPatientId(pid, db))

        for pid in testing:
            test_scans.extend(_getScansByPatientId(pid, db))

        random.shuffle(tr_scans)
        random.shuffle(val_scans)
        random.shuffle(test_scans)

        return tr_scans, val_scans, test_scans


def _getScansByPatientId(pid, db):
    """Returns all the scans for the passed in patient id."""
    sql = f"Select scan_id, label from scan_features where patient_id='{pid}'"
    return [
        {"scan_id": scan_id, "label": label}
        for scan_id, label in db.execute_query(sql)
    ]


if __name__ == '__main__':
    insertNewDatasetToDB(dbname="scans", balance_rate=0.6)
