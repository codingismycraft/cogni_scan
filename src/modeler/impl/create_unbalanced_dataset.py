import copy
import json
import random
import uuid

import cogni_scan.src.dbutil as dbutil

_SQL_SORT_LABELS = """
select label, count(*) from scan_features 
where label in ({labels})   group by label order by 2;
"""

_SQL_LOAD_PATIENTS = """
select patient_id, count(*) as counter from scan_features 
where label='{label}' group by patient_id;
"""

_SQL_SCANS_BY_PATIENT = """
Select scan_id, label from scan_features where patient_id='{pid}'
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


class DatasetCreator:
    _DEFAULT_SPLITS = 0.7, 0.15, 0.15
    _DEFAULT_LABELS = ["HH", "HD"]
    _MAX_SCANS_PER_PATIENT = 3

    def __init__(self, labels=None, splits=None, balance_rate=0.8):
        if not splits:
            self._splits = self._DEFAULT_SPLITS
        assert len(self._splits) == 3
        assert sum(self._splits) == 1.0
        if not labels:
            labels = self._DEFAULT_LABELS
        self._labels = copy.deepcopy(labels)
        assert len(self._labels) == 2
        assert 0.5 <= balance_rate <= .9
        self._balance_rate = balance_rate

    def saveInDb(self):
        assert len(self._labels) == 2
        self._sortLabelsByNumberOfPatients()
        label_1, label_2 = self._labels
        train_1, val_1, test_1 = self._buildSmallerDataset(label_1)

        s1, s2, s3 = len(train_1), len(val_1), len(test_1)
        train_2, val_2, test_2 = self._buildLargerDataset(label_2, s1, s2, s3)

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

        if self._balance_rate == 0.5:
            description = "Balanced"
        elif self._balance_rate is None:
            description = "User all."
        else:
            description = f"Ratio: {self._balance_rate}"

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

    def _buildLargerDataset(self, label, s1, s2, s3):
        f = self._balance_rate / (1. - self._balance_rate)
        s1 = int(s1 * f)
        s2 = int(s2 * f)
        s3 = int(s3 * f)

        dbw = dbutil.SimpleSQL()
        train, val, test = [], [], []
        with dbw as db:
            sql = _SQL_LOAD_PATIENTS.format(label=label)
            index = 0
            for pid, _ in db.execute_query(sql):
                scans = self._getScansByPatientId(pid, db)
                scans = scans[:self._MAX_SCANS_PER_PATIENT]
                i = index % 3
                if i == 0:
                    train.extend(scans)
                elif i == 1:
                    val.extend(scans)
                else:
                    test.extend(scans)
                index += 1

            random.shuffle(train)
            random.shuffle(test)
            random.shuffle(val)

            train = train[:s1]
            val = val[:s2]
            test = test[:s3]

        return train, val, test

    def _buildSmallerDataset(self, label):
        """Builds the smaller set of the train, val and testing datasets."""
        splits = self._splits
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
                tr_scans.extend(self._getScansByPatientId(pid, db))

            for pid in validation:
                val_scans.extend(self._getScansByPatientId(pid, db))

            for pid in testing:
                test_scans.extend(self._getScansByPatientId(pid, db))

            random.shuffle(tr_scans)
            random.shuffle(val_scans)
            random.shuffle(test_scans)

            return tr_scans, val_scans, test_scans

    def _sortLabelsByNumberOfPatients(self):
        labels = ','.join([f"'{l}'" for l in self._labels])
        sql = _SQL_SORT_LABELS.format(labels=labels)
        with dbutil.SimpleSQL() as db:
            labels = []
            for row in db.execute_query(sql):
                labels.append(row[0])
        self._labels = labels

    def _getScansByPatientId(self, pid, db):
        """Returns all the scans for the passed in patient id."""
        sql = _SQL_SCANS_BY_PATIENT.format(pid=pid)
        return [
            {"scan_id": scan_id, "label": label}
            for scan_id, label in db.execute_query(sql)
        ]


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("scans")
    dc = DatasetCreator()
    dc.saveInDb()
