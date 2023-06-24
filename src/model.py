"""Facade to manage the details about model creation."""


import cogni_scan.src.impl.model_impl as model_impl

def makeModel(name, slices):
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """


def getModels():
    """Returns a list of all the IModel instances from the database."""


def getDatasets():
    """Returns a list of all the databases from the database."""
    return model_impl.getDatasets()
