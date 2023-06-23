"""Facade to manage the details about model creation."""


def makeModel(name, slices):
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """


def loadModels():
    """Returns a list of all the IModel instances from the database."""


def loadDatasets():
    """Returns a list of all the IDataset instances from the database."""
