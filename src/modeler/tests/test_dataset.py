"""Tests the Dataset class.

We assume that the local data base already has the default dataset
named Dataset.
"""
import datetime
import uuid

import pytest

import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.modeler.interfaces as interfaces
import cogni_scan.src.modeler.model as model

_DBNAME = 'dummyscans'


def getExistingDatasetID():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dss = model.getDatasets()
    assert len(dss) > 0
    return dss[0].getDatasetID()


def test_getting_dataset_by_name():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert ds.getDatasetID() == dataset_id


def test_invalid_dataset_id():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    with pytest.raises(ValueError):
        ds = model.getDatasetByID(uuid.uuid4())


def test_getting_all_datasets():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dss = model.getDatasets()
    assert isinstance(dss, list)
    for ds in dss:
        assert isinstance(ds, interfaces.IDataset)


def test_get_by_patient_id():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert ds.getDatasetID() == dataset_id


def test_get_description():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    desc = ds.getDescription()
    assert isinstance(desc, dict)


def test_get_features():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    features = ds.getFeatures(["01"])
    assert isinstance(features, dict)


def test_get_get_scan_id():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    scan_ids = ds.getScanIDs()
    assert isinstance(scan_ids, dict)
    print(scan_ids)


def test_invalid_slices():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    with pytest.raises(ValueError):
        features = ds.getFeatures(["Invalid slice"])


def test_repr():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert dataset_id in str(ds)


def test_getting_features_for_invalid_scan():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    with pytest.raises(ValueError):
        model.getFeaturesForScan(9999999, ['01'])
