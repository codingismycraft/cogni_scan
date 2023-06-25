"""Tests the model class."""

import pytest

import cogni_scan.src.modeler.model as model

_DEAFAULT_DATASET_NAME = 'Dataset'

def test_new_model():
    """Tests the state of a new model."""
    m = model.makeNewModel()

    assert not m.isTrained()
    assert not m.isDirty()
    assert not m.getSlices()
    assert not m.getDatasetName()
    assert not m.getCunfusionMatrix()
    assert not m.getTrainingHistory()
    assert not m.getROCCurve()


def test_invalid_dataset():
    """Tests training while passing invalid dataset name."""
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.train("", None)

def test_invalid_slice_type():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.train(ds, {})

def test_invalid_slices():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.train(ds, ["junk"])

def test_repr():
    m = model.makeNewModel()
    s = str(m)
    assert m.getName() in s

def test_train():
    ds = model.getDatasetByName(_DEAFAULT_DATASET_NAME)
    m = model.makeNewModel()
    slices = ["01", "02"]

    m.train(ds, slices, max_epochs=1)
    print(m.getTrainingHistory())























