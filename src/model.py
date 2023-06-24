"""Facade to manage the details about model creation."""

import cogni_scan.src.impl.model_impl as model_impl
import cogni_scan.src.impl.dataset_impl as dataset_impl


def makeNewModel(name, slices):
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    return model_impl.makeNewModel(name, slices)


def getModels():
    """Returns a list of all the IModel instances from the database."""
    return model_impl.getModels()


def getDatasets():
    """Returns a list of all the databases from the database."""
    return dataset_impl.getDatasets()


if __name__ == '__main__':
    for ds in getDatasets():
        print(ds)
        for k, v in ds.getDescription().items():
            print(k, v)
        print(ds.getFeatures(['01']))
