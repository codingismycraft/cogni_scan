"""Tests the Dataset class.

We assume that the local data base already has the default dataset
named Dataset.
"""
import datetime

import pytest

import cogni_scan.src.modeler.model as model
import cogni_scan.src.modeler.interfaces as interfaces

_DEAFAULT_DATASET_NAME = 'Dataset'


def test_getting_dataset_by_name():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)


def test_invalid_dataset_name():
    with pytest.raises(ValueError):
        ds = model.getDatasetByName("very-junk")


def test_getting_all_datasets():
    dss = model.getDatasets()
    assert isinstance(dss, list)
    for ds in dss:
        assert isinstance(ds, interfaces.IDataset)


def test_get_name():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    assert ds.getName() == _DEAFAULT_DATASET_NAME

    s = str(ds)
    assert _DEAFAULT_DATASET_NAME in s


def test_creation_time():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    ct = ds.getCreationTime()
    assert isinstance(ct, datetime.datetime)


def test_get_description():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    desc = ds.getDescription()
    assert isinstance(desc, dict)


def test_get_features():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    features = ds.getFeatures(["01"])
    assert isinstance(features, dict)

def test_invalid_slices():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    with pytest.raises(ValueError):
        features = ds.getFeatures(["Invalid slice"])
