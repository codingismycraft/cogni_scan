"""Facade to manage the details about model creation."""

import cogni_scan.src.modeler.impl.model_impl as model_impl
import cogni_scan.src.modeler.impl.dataset_impl as dataset_impl


def makeNewModel():
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    return model_impl.makeNewModel()


def getFeaturesForScan(scan_id, slices, db=None):
    """Returns the features for the given scan.

    The features returned will become the input to a model and used either
    for training or for prediction.

    The db object must be passed (should be a SimpleSQL instance) so we
    will avoid the need to reconnet to the database in case that we will
    have many repeated calls.

    The slices must be a list of strings each one describing the MRI
    slice to use (see the documentation of getFeatures for more).

    Raises ValueError.
    """
    return dataset_impl.getFeaturesForScan(scan_id, slices, db)


def getModels():
    """Returns a list of all the IModel instances from the database."""
    return model_impl.getModels()


def getModelByID(model_id):
    """Returns the model by its model id."""
    return model_impl.getModelByID(model_id)


def getDatasets():
    """Returns a list of all the databases from the database."""
    return dataset_impl.getDatasets()


def getDatasetByID(dataset_id):
    """Returns a dataset by its ID.

    raises: ValueError if the dataset does not exist.
    """
    return dataset_impl.getDatasetByID(dataset_id)
