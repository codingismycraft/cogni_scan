"""Tests the model class."""

import os
import uuid

import pytest

import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.modeler.model as model
import cogni_scan.src.nifti_mri as nifti_mri
import cogni_scan.constants as constants

_DBNAME = 'dummyscans'
_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
_STORAGE_DIR = os.path.join(_CURRENT_DIR, 'dummystorage')


def getExistingDatasetID():
    """Returns the dataset ID for the first dataset."""
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    dss = model.getDatasets()
    assert len(dss) > 0
    return dss[0].getDatasetID()


def checkModelFileExists(m):
    """Returns True if the weights for the passed in model exist."""
    fullpath = os.path.join(_STORAGE_DIR, f'{m.getModelID()}.h5')
    return os.path.isfile(fullpath)


def removeAllModels():
    """Removes all models both from the database and the filesystem."""
    # Remove the dummy storage directory.
    assert "dummy" in _STORAGE_DIR
    os.system(f"rm -rf {_STORAGE_DIR}")

    # Remove all the models from the database.
    assert "dummy" in _DBNAME
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    with dbutil.SimpleSQL() as db:
        db.execute_non_query("delete from models")


def test_new_model():
    """Tests the state of a new model."""
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    m = model.makeNewModel()

    assert not m.isTrained()
    assert not m.getSlices()
    assert not m.getConfusionMatrix()
    assert not m.getTrainingHistory()
    assert not m.getROCCurve()
    assert not m.getF1()
    assert not m.getAccuracyScore()

    m.unloadWeights()


def test_invalid_dataset():
    """Tests training while passing invalid dataset name."""
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave("", None)


def test_invalid_slice_type():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave(ds, {})


def test_invalid_slices():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    with pytest.raises(ValueError):
        m.trainAndSave(ds, ["junk"])


def test_get_slices():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    count_before = len(model.getModels())
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    m.setStorageDir(_STORAGE_DIR)

    # Train and save.
    m.trainAndSave(ds, ["01"], max_epochs=1)
    slices = m.getSlices()
    assert isinstance(slices, list)

    dsid = m.getDatasetID()
    assert isinstance(dsid, str)

    # Verify that it was saved to the database.
    count_after = len(model.getModels())
    assert count_after - count_before == 1

    # Verify the the h5 file was created successfully.
    assert checkModelFileExists(m)

    # delete the model
    m.reset()

    # verify that it was deleted from the dataset.
    count_after = len(model.getModels())
    assert count_after == count_before

    # Verify the the h5 file was deleted.
    assert not checkModelFileExists(m)


def test_repr():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    m = model.makeNewModel()
    s = str(m)
    assert m.getModelID() in s


def getScan():
    """Returns a random scan that can be used to test the predict.

    The parameters passed to loadFromDb assure that we have valid
    scans and assuming that we have updated the VGG16 features we
    should be able to to make predictions based on it.
    """
    patients = nifti_mri.PatientCollection()
    patients.loadFromDb("ALL", False, 2)
    pids = list(patients.getPatientIDs())
    pid = pids[0][0]
    mris = list(patients.getMrisByPatient(pid))
    mri = mris[0]

    return mri


def test_request_invalid_model_id():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    model_id = uuid.uuid4()
    with pytest.raises(ValueError):
        model.getModelByID(model_id)


def test_predict_from_db():
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    count_before = len(model.getModels())
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    m.setStorageDir(_STORAGE_DIR)
    m.trainAndSave(ds, ["01", "11"], max_epochs=1)
    m = model.getModelByID(m.getModelID())
    roc_curve = m.getROCCurve()
    assert len(roc_curve) == 2
    predictions = m.getTestingPredictions()
    assert isinstance(predictions, list)
    scan = getScan()
    prediction = m.predict(scan.getScanID())
    assert 0 <= prediction <= 1.
    m.reset()
    count_after = len(model.getModels())
    assert count_after == count_before


def test_predict_from_file():
    removeAllModels()
    dbutil.SimpleSQL.setDatabaseName(_DBNAME)
    # Create a new model to use for predictions.
    ds = model.getDatasetByID(getExistingDatasetID())
    m = model.makeNewModel()
    m.setStorageDir(_STORAGE_DIR)
    m.trainAndSave(ds, ["01", "11"], max_epochs=1)
    filename = os.path.join(constants.DIR_TESTING_DATA, "mri-1.nii.gz")
    scan = nifti_mri.Scan(filename)
    prediction = m.predictFromScan(scan)
    assert 0 <= prediction <= 1
    m.reset()
