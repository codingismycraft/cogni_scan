"""Defines the interfaces to use for the model managment."""
import abc


class IDataset(abc.ABC):
    """Abstract base class for datasets."""

    @abc.abstractmethod
    def getName(self):
        """Returns the name of the dataset."""

    @abc.abstractmethod
    def creationTime(self):
        """Get the creation time of the dataset."""

    @abc.abstractmethod
    def getStats(self):
        """Get statistics of the dataset.

        Returns:
            dict: A dictionary containing statistics of the dataset. This
            dict can look as follows:

            {
                'training_scans': 124,
                'labels': {
                    'train': { "HH": 120, "HD": 12 }
                }
                ...
            }
        """

    @abc.abstractmethod
    def getFeatures(self, slices):
        """Returns the features of the dataset.

        :param slices: A list that designates the slice that will be used. Each
        slice must be expresses as one of the following two digit strings (each
        one is refering to one slice, the first digit is the axis the second
        the slice with 2 been the center slice:

                01, 02, 03,
                11, 12, 13,
                21, 22, 23

        Returns a dict with the following structure:

        The features are grouped as key-value pairs following this format:
        {
            "X_train": [....],
            "Y_train": [....],
            "X_val": [....],
            "Y_val": [ 0, 1 ....],
            "X_test": [ 0, 1 ....],
            "Y_test": [ 0, 1 ....],
        }

        The X values consist of numpy arrays in the form [n, k] where k
        is the number of scans and k is the representation of the features
        for the scan as an array of numpy arrays: [  [..], [..] ... ].
        """


class IModel(abc.ABC):
    """Used to train, save and retrieve a NN model."""

    @abc.abstractmethod
    def getName(self):
        """Returns the name of the model."""

    @abc.abstractmethod
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

    @abc.abstractmethod
    def getDataset(self):
        """Returns the dataset used for the model.

        The dataset must be an instance of the Dataset interface and should be
        coming from the database table datasets.
        """
        pass

    @abc.abstractmethod
    def saveToDb(self):
        """Saves the model to the database."""

    @abc.abstractmethod
    def train(self):
        """Train the model."""

    @abc.abstractmethod
    def getCunfusionMatrix(self):
        """Returns the confusion matrix of the model."""

    @abc.abstractmethod
    def getTrainingHistory(self):
        """Returns the training history of the model."""

    @abc.abstractmethod
    def getROCCurve(self):
        """Returns the ROC curve of the model."""
