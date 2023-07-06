"""Defines the interfaces to use for the model managment."""
import abc

DEFAULT_MAX_EPOCHS = 120


class IDataset(abc.ABC):
    """Abstract base class for datasets."""

    @abc.abstractmethod
    def getDatasetID(self):
        """Returns the dataset_id of the dataset."""

    @abc.abstractmethod
    def getDescription(self):
        """Get the description of the dataset.

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

        Exceptions:

        If the passed in slices are invlid (based on the previous description
        then a ValueError is raised.
        """


class IModel(abc.ABC):
    """Used to train, save and retrieve a NN model."""

    @abc.abstractmethod
    def getModelID(self):
        """Returns the name of the model."""

    @abc.abstractclassmethod
    def getStorageDir(cls):
        """Returns the path to the directory where modesls are stored."""

    @abc.abstractclassmethod
    def setStorageDir(cls, dir_path):
        """Sets the path to the directory where modesls are stored."""

    @abc.abstractmethod
    def isTrained(self):
        """Returns true if the model is trained."""

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
    def getDatasetID(self):
        """Returns the dataset ID used for the model."""

    @abc.abstractmethod
    def trainAndSave(self, dataset, slices, max_epochs=DEFAULT_MAX_EPOCHS):
        """Trains and saves the model.

        raises: ValueError
        """

    @abc.abstractmethod
    def reset(self):
        """Deletes it from the database and from h4 and resets its state."""

    @abc.abstractmethod
    def getConfusionMatrix(self):
        """Returns the confusion matrix of the model."""

    @abc.abstractmethod
    def getTrainingHistory(self):
        """Returns the training history of the model."""

    @abc.abstractmethod
    def getROCCurve(self):
        """Returns the ROC curve of the model."""

    @abc.abstractmethod
    def getAccuracyScore(self):
        """Returns the accuracy score statistic for the model."""

    @abc.abstractmethod
    def getTestingPredictions(self):
        """Returns the testing predictions for the model."""

    @abc.abstractmethod
    def predict(self, scan_id, db=None):
        """Predicts the label of the passed in scan id."""

    @abc.abstractmethod
    def predictFromScan(self, scan):
        """Predicts the label of the passed in scan object."""

    @abc.abstractmethod
    def unloadWeights(self):
        """Unloads the model weights to keep the memory lean."""
