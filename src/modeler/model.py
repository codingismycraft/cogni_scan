"""Facade to manage the details about model creation."""

import cogni_scan.src.modeler.impl.model_impl as model_impl
import cogni_scan.src.modeler.impl.dataset_impl as dataset_impl


def makeNewModel():
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    return model_impl.makeNewModel()


def getModels():
    """Returns a list of all the IModel instances from the database."""
    return model_impl.getModels()


def getDatasets():
    """Returns a list of all the databases from the database."""
    return dataset_impl.getDatasets()


def getDatasetByID(dataset_id):
    """Returns a dataset by its ID.

    raises: ValueError if the dataset does not exist.
    """
    return dataset_impl.getDatasetByID(dataset_id)


if __name__ == '__main__':
    ds = getDatasetByName("Dataset")
    for k, v in ds.getDescription().items():
        print(k, v)

# for ds in getDatasets():
#     print(ds)
#     for k, v in ds.getDescription().items():
#         print(k, v)
#     print(ds.getFeatures(['01']))
