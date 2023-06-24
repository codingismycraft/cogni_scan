"""Implements the details of the model class."""

import cogni_scan.src.interfaces as interfaces


def makeNewModel(name, slices):
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    assert False, "Not implemented yet."


def getModels():
    """Returns a list of all the IModel instances from the database."""
    assert False, "Not implemented yet."


class _Model(interfaces.IModel):
    """Used to train, save and retrieve a NN model."""

    def getName(self):
        """Returns the name of the model."""

    def isTrained(self):
        """Returns true if the model is trained."""

    def isDirty(self):
        """Returns true if the model has unsaved changes."""

    def getSlices(self):
        """Returns the slices used from the model.

        The returned value is a list that designates the slices used by the
        model.

        Each slice i expressed as one of the following two digit
        strings each one is refering to one slice, the first digit is the axis
        the second the slice with 2 been the center slice:

                01, 02, 03,
                11, 12, 13,
                21, 22, 23
        """

    def getDataset(self):
        """Returns the dataset used for the model.

        The dataset must be an instance of the Dataset interface and should be
        coming from the database table datasets.
        """

    def saveToDb(self):
        """Saves the model to the database."""

    def train(self):
        """Train the model."""

    def getCunfusionMatrix(self):
        """Returns the confusion matrix of the model."""

    def getTrainingHistory(self):
        """Returns the training history of the model."""

    def getROCCurve(self):
        """Returns the ROC curve of the model."""
