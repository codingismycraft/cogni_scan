"""Implements the details of the model class."""

import copy
import json
import os
import pathlib
import uuid

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.utils as utils
import cogni_scan.src.modeler.impl.dataset_impl as dataset_impl
import cogni_scan.src.modeler.interfaces as interfaces
import cogni_scan.src.nifti_mri as nifti_mri

_VALID_SLICES = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]


def makeNewModel():
    """Create a new model based on the given name and slices.

    returns an instance of the IModel interface.

    raises: ValueError if the name already exists or invalid slices are passed.
    """
    return _Model()


def getModels():
    """Returns a list of all the IModel instances from the database."""
    with dbutil.SimpleSQL() as db:
        sql = "select model_id, dataset_id, slices," \
              " descriptive_data, model_name from models"
        return [_Model(*row) for row in db.execute_query(sql)]


def getModelByID(model_id):
    """Returns the model by its model id."""
    with dbutil.SimpleSQL() as db:
        sql = f"select model_id, dataset_id, slices, descriptive_data " \
              f"from models where model_id = '{model_id}' "
        for row in db.execute_query(sql):
            return _Model(*row)
    raise ValueError(f"Could not find model: {model_id}")


class _Model(interfaces.IModel):
    """Used to train, save and retrieve a NN model."""

    # Class level attributes.
    _STORAGE_PATH = None

    # Instance level attributes.
    _model_id = None
    _model_name = None
    _dataset_id = None
    _slices = None
    _training_history = None
    _confusion_matrix = None
    _roc_curve = None
    _f1 = None
    _accuracy_score = None
    _roc_auc_score = None
    _model = None
    _fpr = None
    _tpr = None
    _thresholds = None
    _testing_predictions = None

    def __init__(self, model_id=None,
                 dataset_id=None, slices=None, descriptive_data=None,
                 model_name=None):
        """Initializes the Model object.

        If the model_id is passed as None, this means that we need to create
        a new instance, thus we will only assign a new model id and keep the
        rest of the fields as None(s) until the user will train the model.

        If non None values are passed then the model instance will be created
        with these data but without loading the model weights (to keep the
        size small); the weights will be loaded in the case that the user
        will call the predict method.
        """
        self._model = None
        if model_id is None:
            # Build a new model.
            self._model_id = str(uuid.uuid4())
            self._clear()
        else:
            self._model_id = model_id
            self._model_name = model_name
            self._dataset_id = dataset_id
            self._slices = slices
            self._confusion_matrix = np.array(
                descriptive_data["confusion_matrix"])
            self._training_history = descriptive_data["training_history"]
            self._f1 = descriptive_data["f1"]
            self._accuracy_score = descriptive_data["accuracy_score"]
            self._fpr = np.array(descriptive_data["fpr"])
            self._tpr = np.array(descriptive_data["tpr"])
            self._roc_auc_score = descriptive_data["roc_auc_score"]
            self._testing_predictions = descriptive_data["predictions"]
            self._thresholds = np.array(descriptive_data["thresholds"])

    def _clear(self):
        """Clears all the internal data (except the model id)."""
        self._slices = None
        self._dataset_id = None
        self._training_history = None
        self._confusion_matrix = None
        self._roc_curve = None
        self._f1 = None
        self._accuracy_score = None
        self._roc_auc_score = None
        self._fpr = None
        self._tpr = None
        self._thresholds = None
        self._testing_predictions = None
        self._model = None

    def __repr__(self):
        """String representation of the instance"""
        return f"Model: {self._model_id}"

    @classmethod
    def getStorageDir(cls):
        """Returns the path to the directory where modesls are stored."""
        if cls._STORAGE_PATH:
            return cls._STORAGE_PATH
        else:
            home_dir = pathlib.Path.home()
            return os.path.join(home_dir, '.cogni_scan')

    @classmethod
    def setStorageDir(cls, dir_path):
        """Sets the path to the directory where modesls are stored."""
        cls._STORAGE_PATH = dir_path

    def getModelID(self):
        """Returns the name of the model."""
        return self._model_id

    def getModelName(self):
        """Returns the name of the model."""
        return self._model_name

    def isTrained(self):
        """Returns true if ready to make predictions."""
        return self._model is not None

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
        return copy.deepcopy(self._slices)

    def getDatasetID(self):
        """Returns the dataset name used for the model."""
        return self._dataset_id

    def reset(self):
        """Deletes it from the database and from h4 and resets its state."""
        # Delete from the datasase.
        with dbutil.SimpleSQL() as db:
            sql = f"delete from models where model_id = '{self._model_id}'"
            db.execute_non_query(sql)

        # Delete the weights from the filesystem.
        fullpath = self.getStorageFullPath()
        if os.path.isfile(fullpath):
            os.remove(fullpath)

        # Now reset the state of the object.
        self._model_id = str(uuid.uuid4())
        self._clear()

    def _save(self):
        """Saves the model to the database.

        The model weights is saved in the filesystem while its descriptive
        data are stored in the datase.
        """
        assert self._model
        self._saveWeights()
        self._saveToDb()

    def _saveToDb(self):
        """Saves the descriptive data of the model to the database."""
        dbo = dbutil.SimpleSQL()
        with dbo as db:
            sql = f"delete from models where model_id = '{self._model_id}'"
            db.execute_non_query(sql)

            desc_data = json.dumps(
                {
                    "training_history": self._training_history,
                    "f1": self._f1,
                    "accuracy_score": self._accuracy_score,
                    "confusion_matrix": self._confusion_matrix.tolist(),
                    "roc_auc_score": self._roc_auc_score,
                    "fpr": self._fpr.tolist(),
                    "tpr": self._tpr.tolist(),
                    "thresholds": self._thresholds.tolist(),
                    "predictions": self._testing_predictions
                }
            )

            slices = json.dumps(self._slices)
            model_name = utils.GetRandomName()

            sql = f"insert into models " \
                  f"(model_id, dataset_id, slices, " \
                  f"descriptive_data, model_name) " \
                  f"values ('{self._model_id}', " \
                  f"'{self.getDatasetID()}', '{slices}' , " \
                  f"'{desc_data}', '{model_name}' ) "


            db.execute_non_query(sql)

    def getStorageFullPath(self):
        """Returns the full path to the h5 file containing the weights."""
        assert self._model_id
        cogni_scan_dir = self.getStorageDir()
        if not os.path.isdir(cogni_scan_dir):
            os.mkdir(cogni_scan_dir)
        return os.path.join(cogni_scan_dir, f'{self._model_id}.h5')

    def _saveWeights(self):
        """Saves the model's weights as a file."""
        full_path = self.getStorageFullPath()
        self._model.save(full_path)

    def trainAndSave(self, dataset, slices, max_epochs=120):
        """Trains and save the model."""
        # TODO: check how it behaves in the case of an exception..
        self._clear()
        if not isinstance(dataset, interfaces.IDataset):
            raise ValueError

        if not isinstance(slices, list):
            raise ValueError(f"Slices must be a list.")

        for slice in slices:
            if slice not in _VALID_SLICES:
                raise ValueError(f"Slice: {slice} is not supported.")

        self._slices = slices

        features = dataset.getFeatures(self._slices)

        X_train = features["X_train"]
        Y_train = features["Y_train"]

        X_val = features["X_val"]
        Y_val = features["Y_val"]

        X_test = features["X_test"]
        Y_test = features["Y_test"]
        test_scans = features["test_scans"]

        input_size = len(self._slices) * 512
        size_1 = input_size * 2
        hidden_size_2 = int(input_size / 2)

        self._model = tf.keras.Sequential()
        self._model.add(tf.keras.layers.Input(input_size))
        self._model.add(tf.keras.layers.Dense(size_1, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.3))
        self._model.add(tf.keras.layers.Dense(hidden_size_2, activation='relu'))
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
        self._dataset_id = dataset.getDatasetID()

        self._training_history = history.history

        # Calculate the performance of the model.
        y_pred = self._model.predict(X_test)

        y_pred_bin = [1 if p[0] > 0.5 else 0 for p in y_pred]

        self._testing_predictions = []
        for scan_info, prediction in zip(test_scans, y_pred):
            scan_info["pred"] = float(prediction[0])
            self._testing_predictions.append(scan_info)

        self._confusion_matrix = confusion_matrix(Y_test, y_pred_bin)
        self._f1 = f1_score(Y_test, y_pred_bin)
        self._accuracy_score = accuracy_score(Y_test, y_pred_bin)
        self._roc_auc_score = roc_auc_score(Y_test, y_pred)
        self._fpr, self._tpr, self._thresholds = roc_curve(Y_test, y_pred)

        self._save()

    def getConfusionMatrix(self):
        """Returns the confusion matrix of the model."""
        return self._confusion_matrix

    def getTrainingHistory(self):
        """Returns the training history of the model."""
        return self._training_history

    def getF1(self):
        """Returns the F1 statistic for the model."""
        return self._f1

    def getAccuracyScore(self):
        """Returns the accuracy score statistic for the model."""
        return self._accuracy_score

    def getROCCurve(self):
        """Returns the ROC curve of the model."""
        if self._fpr is not None:
            return self._fpr, self._tpr
        else:
            return None

    def getTestingPredictions(self):
        """Returns the testing predictions for the model."""
        return copy.deepcopy(self._testing_predictions)

    def _loadWeightsIfNeeded(self):
        """Loads the model's weights from the corresponding file."""
        if not self._model:
            full_path = self.getStorageFullPath()
            self._model = tf.keras.models.load_model(full_path)

    def unloadWeights(self):
        """Unloads the model weights to keep the memory lean."""
        self._model = None

    def predict(self, scan_id, db=None):
        """Predicts the label of the passed in scan.

        We need the VGG16 features and the model to make the predictions.
        """
        slices = self.getSlices()
        features = dataset_impl.getFeaturesForScan(scan_id, slices, db)
        self._loadWeightsIfNeeded()
        features = np.array([features])
        y_pred = self._model.predict(features)
        return y_pred[0][0]

    def predictFromScan(self, scan):
        """Predicts the label of the passed in scan object."""
        assert isinstance(scan, nifti_mri.Scan)
        self._loadWeightsIfNeeded()
        assert self._model
        slices = sorted(self.getSlices())
        distances = scan.getSliceDistances()
        features = None

        for slice_desc in slices:
            # slice_desc can be something like '01', '22' etc.
            image_axis = int(slice_desc[0])
            slice_index = int(slice_desc[1])
            abs_distance =float(distances[image_axis])

            # Based on the slice find the distance from the center slice
            if slice_index == 1:
                distance = -1 * abs_distance
            elif slice_index == 2:
                distance = 0
            elif slice_index == 3:
                distance = abs_distance
            else:
                assert 1 <= slice_index <= 3

            # Accumulate VGG16 features.
            if features is None:
                features = scan.getVGG16Features(distance, image_axis)
            else:
                f1 = scan.getVGG16Features(distance, axis=image_axis)
                features = np.concatenate((features, f1), axis=0)

        features = features.flatten()
        features = np.array([features])
        y_pred = self._model.predict(features)
        print(y_pred[0][0])
        return y_pred[0][0]


def getAllModelsAsJson():
    """Returns all models as JSON (Used from Sibyl UI)."""
    slice_labels = ["01", "02", "03", "11", "12", "13", "21", "22", "23"]
    models = []
    for model in getModels():
        selected_slices = set(model.getSlices())
        slices = [ 1  if s in selected_slices else 0 for s in slice_labels]
        confusion_matrix = model.getConfusionMatrix().tolist()
        models.append({
            "model_id": model.getModelID()[:8],
            "weights_path": model.getStorageFullPath(),
            "slices": slices,
            "accuracy": model.getAccuracyScore(),
            "F1": model.getF1(),
            "model_name": model.getModelName(),
            "confusion_matrix": confusion_matrix

        })

    data = {
        "slice_labels": slice_labels,
        "models": models
    }
    return data
