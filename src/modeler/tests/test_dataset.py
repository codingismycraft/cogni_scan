"""Tests the Dataset class.

We assume that the local data base already has the default dataset
named Dataset.
"""
import datetime
import uuid

import pytest

import cogni_scan.src.modeler.model as model
import cogni_scan.src.modeler.interfaces as interfaces

_DEAFAULT_DATASET_NAME = 'Dataset'


def getExistingDatasetID():
    dss = model.getDatasets()
    assert len(dss) > 0
    return dss[0].getDatasetID()


def test_getting_dataset_by_name():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert ds.getDatasetID() == dataset_id


def test_invalid_dataset_id():
    with pytest.raises(ValueError):
        ds = model.getDatasetByID(uuid.uuid4())


def test_getting_all_datasets():
    dss = model.getDatasets()
    assert isinstance(dss, list)
    for ds in dss:
        assert isinstance(ds, interfaces.IDataset)


def test_get_by_patient_id():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert ds.getDatasetID() == dataset_id


def test_get_description():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    desc = ds.getDescription()
    assert isinstance(desc, dict)


def test_get_features():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    features = ds.getFeatures(["01"])
    assert isinstance(features, dict)


def test_invalid_slices():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    with pytest.raises(ValueError):
        features = ds.getFeatures(["Invalid slice"])


def test_repr():
    dataset_id = getExistingDatasetID()
    ds = model.getDatasetByID(dataset_id)
    assert dataset_id in str(ds)
