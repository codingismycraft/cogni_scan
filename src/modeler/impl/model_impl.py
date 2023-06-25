"""Implements the details of the model class."""

import copy

from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

import cogni_scan.src.modeler.interfaces as interfaces

_VALID_SLICES = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]

def makeNewModel():
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    return _Model()


def getModels():
    """Returns a list of all the IModel instances from the database."""
    assert False, "Not implemented yet."


def _getValidNextName(name):
    """Returns a valid model name based on the passed in name.

    Since models must have a unique name, if the name that the user is trying
    to use already exists, then this function adds to it a default suffix;
    called right before saving to the database.
    """


class _Model(interfaces.IModel):
    """Used to train, save and retrieve a NN model."""

    _name = "(not named yet)"
    _is_trained = False
    _is_dirty = False
    _slices = None
    _dataset_name = None
    _confusion_matrix = None
    _training_history = None
    _roc_curve = None
    _model = None

    def __repr__(self):
        """String representation of the instance"""
        return f"Model: {self._name}"

    def getName(self):
        """Returns the name of the model."""
        return self._name

    def isTrained(self):
        """Returns true if the model is trained."""
        return self._is_trained

    def isDirty(self):
        """Returns true if the model has unsaved changes."""
        return self._is_dirty

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
        return self._slices

    def getDatasetName(self):
        """Returns the dataset name used for the model."""
        return self._dataset_name

    def saveToDb(self):
        """Saves the model to the database."""

    def train(self, dataset, slices, max_epochs=120):
        """Train the model."""
        if not isinstance(dataset, interfaces.IDataset):
            raise ValueError

        if not isinstance(slices, list):
            raise ValueError(f"Slices must be a list.")

        for slice in slices:
            if slice not in _VALID_SLICES:
                raise ValueError(f"Slice: {slice} is not supported.")

        features = dataset.getFeatures(slices)

        X_train = features["X_train"]
        Y_train = features["Y_train"]

        X_val = features["X_val"]
        Y_val = features["Y_val"]

        X_test = features["X_test"]
        Y_test = features["Y_test"]

        self._model = tf.keras.Sequential()
        self._model.add(tf.keras.layers.Input(len(slices) * 512))
        self._model.add(tf.keras.layers.Dense(1000, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.3))
        self._model.add(tf.keras.layers.Dense(1000, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.3))
        self._model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

        optimizer = tf.optimizers.Adam(learning_rate=0.0001)

        self._model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=[tf.keras.metrics.AUC()]
        )

        early_stoppping = EarlyStopping(
            monitor='val_auc',
            patience=10,
            restore_best_weights=True
        )

        reduce_lr_on_plateau = ReduceLROnPlateau(
            monitor='val_auc', factor=0.1, patience=10
        )

        history = self._model.fit(
            X_train,
            Y_train,
            # batch_size=100,
            epochs=max_epochs,
            validation_data=(X_val, Y_val),
            # callbacks=[early_stoppping,reduce_lr_on_plateau],
            verbose=2
        )
        self._training_history = history.history

        y_pred = self._model.predict(X_test)

        y_pred_bin = [1 if p[0] > 0.5 else 0 for p in y_pred]

        conf_mat = confusion_matrix(Y_test, y_pred_bin)
        f1 = f1_score(Y_test, y_pred_bin)
        ac = accuracy_score(Y_test, y_pred_bin)

        # Save to the database.
        print("not implemented yet..")

    def predict(self, X):
        return self._model.predict(X)

    def getCunfusionMatrix(self):
        """Returns the confusion matrix of the model."""

    def getTrainingHistory(self):
        """Returns the training history of the model."""
        return self._training_history

    def getROCCurve(self):
        """Returns the ROC curve of the model."""
