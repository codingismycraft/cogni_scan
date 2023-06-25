"""Tests the model class."""

import pytest

import cogni_scan.src.modeler.model as model


def getExistingDatasetID():
    dss = model.getDatasets()
    assert len(dss) > 0
    return dss[0].getDatasetID()


def test_new_model():
    """Tests the state of a new model."""
    m = model.makeNewModel()

    assert not m.isTrained()
    assert not m.getSlices()
    assert not m.getConfusionMatrix()
    assert not m.getTrainingHistory()
    assert not m.getROCCurve()
    assert not m.getF1()
    assert not m.getAccuracyScore()


def test_invalid_dataset():
    """Tests training while passing invalid dataset name."""
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave("", None)


def test_invalid_slice_type():
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave(ds, {})


def test_invalid_slices():
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave(ds, ["junk"])


def test_get_slices():
    models = model.getModels()
    slices = models[0].getSlices()
    assert isinstance(slices, list)


def test_get_dataset_id():
    models = model.getModels()
    m = models[0]
    dsid = m.getDatasetID()
    assert isinstance(dsid, str)


def test_repr():
    m = model.makeNewModel()
    s = str(m)
    assert m.getModelID() in s


def test_train_and_save():
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    slices = ["01"]
    m.trainAndSave(ds, slices, max_epochs=1)
    print(m.getTrainingHistory())


def test_get_models():
    models = model.getModels()
    assert isinstance(models, list)
