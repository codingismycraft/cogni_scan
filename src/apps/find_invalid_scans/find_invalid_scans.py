"""Neural network to discover invalid scans.

In the Oasis3 dataset there are two kinds of scans that are considered invalid:

- Those that their full path contains the "TSE" substring.

- Some other scans that do not follow to an easy to identify pattern.

The purpose of this program is to train a model to identify the invalid
scans that that follow in the second category.

Prior to running this program we have already classify some of valid and
invalid scans using the a manual process so we will have enough data to
train the model.

After training the model we use it to discover the invalid scans among those
that are still unasssigned.
"""

import random
import pathlib
import os

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from tensorflow import keras
from tensorflow.keras.applications.vgg16 import VGG16
import cv2
import nibabel as nib
import numpy as np
import tensorflow as tf

import cogni_scan.src.dbutil as dbutil

_SQL_SELECT_INVALID = """
select fullpath from scan where 
validation_status = 1 and fullpath not like ('%TSE%')
"""

_SQL_SELECT_VALID = "select fullpath from scan where validation_status = 2"

_SQL_SELECT_UNDEFINED = "select fullpath, scan_id, patient_id from scan where validation_status=0"

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def add_rgb_channels(imgs):
    """Adds the RGB channels to a collection of gray scale images.

    :param imgs: A numpy array holding a collection of gray scale images.
    :return: A numpy array holding RGB images.
    """
    if len(imgs) == 0:
        return imgs

    rgb = np.repeat(imgs, 3)
    return rgb.reshape(imgs.shape + (3,))


def getModelFullPath():
    """Returns the path to the model that dicovers the invalid scans."""
    home_dir = pathlib.Path.home()
    return os.path.join(home_dir, '.cogni_scan', "discover-invalid-scans.h5")


class _FeatureExtractor:
    _ready = False

    def __call__(self, image):
        if not self._ready:
            self.__model_1 = VGG16(
                weights='imagenet', include_top=False, input_shape=(200, 200, 3)
            )
            self._ready = True

        features = self.__model_1.predict(np.array([image]))
        gavg = keras.layers.GlobalAveragePooling2D()(features)
        return keras.layers.Flatten()(gavg)


_feature_extractor = _FeatureExtractor()


def split(collection):
    """Splits the passed in collection to train, val and test subsets."""
    i = int(len(collection) * 0.7)
    j = int(len(collection) * 0.85)
    return collection[:i], collection[i:j], collection[j:]


def loadFeatures(fullpath, distance_from_center=0, axis=0, bounding_square=200):
    """Returns a list with the VGG16 features for the passed in image."""
    assert 0 <= axis <= 2
    assert -1. <= distance_from_center <= 1.

    img = nib.load(fullpath).get_fdata()
    n = int(int(img.shape[axis] / 2) * (1 + distance_from_center))

    if axis == 0:
        img = img[n, :, :]
    elif axis == 1:
        img = img[:, n, :]
    elif axis == 2:
        img = img[:, :, n]
    else:
        raise ValueError

    x, y = img.shape

    if x > y:
        ratio = y / x
        x = bounding_square
        y = bounding_square * ratio
    elif x < y:
        ratio = x / y
        y = bounding_square
        x = bounding_square * ratio
    else:
        x = y = bounding_square

    x = int(x)
    y = int(y)
    l_img = np.full((bounding_square, bounding_square), 0)
    x_offset = int((bounding_square - y) / 2)
    y_offset = int((bounding_square - x) / 2)
    s_img = cv2.resize(img, dsize=(y, x), interpolation=cv2.INTER_CUBIC)
    l_img[y_offset:y_offset + s_img.shape[0],
    x_offset:x_offset + s_img.shape[1]] = s_img

    img = add_rgb_channels(l_img)
    f = _feature_extractor(img)
    a = np.array(_feature_extractor(img))
    a = a.tolist()

    return a[0]


def findInvalidScans():
    fullpath = getModelFullPath()
    model = tf.keras.models.load_model(fullpath)
    output_file = os.path.join(_CURRENT_DIR, "scan-status-2.csv")
    with open(output_file, "w") as fout:
        with dbutil.SimpleSQL() as db:
            for row in db.execute_query(_SQL_SELECT_UNDEFINED):
                try:
                    path = row[0]
                    scan_id = row[1]
                    patient_id = row[2]
                    features = loadFeatures(path)
                    features = np.array([features])
                    y_pred = model.predict(features)
                    y_pred = y_pred[0][0]
                    if y_pred < 0.5:
                        print(f'{scan_id},{patient_id},valid')
                        fout.write(f'{scan_id},{patient_id},valid\n')
                    else:
                        print(f'{scan_id},{patient_id},invalid')
                        fout.write(f'{scan_id},{patient_id},invalid\n')
                except Exception as ex:
                    print(ex, type(ex))


def buildModel():
    """Creates the model that will be used to discover invalid scans."""
    with dbutil.SimpleSQL() as db:
        invalid = [(row[0], 1) for row in db.execute_query(_SQL_SELECT_INVALID)]
        valid = [(row[0], 0) for row in db.execute_query(_SQL_SELECT_VALID)]

        train, val, test = [], [], []

        x, y, z = split(invalid)
        train.extend(x)
        val.extend(y)
        test.extend(z)

        x, y, z = split(valid)
        train.extend(x)
        val.extend(y)
        test.extend(z)

        random.shuffle(train)
        random.shuffle(val)
        random.shuffle(test)

        X_train, Y_train = [], []
        X_val, Y_val = [], []
        X_test, Y_test = [], []

        for path, label in test:
            X_train.append(loadFeatures(path))
            Y_train.append(label)

        for path, label in val:
            X_val.append(loadFeatures(path))
            Y_val.append(label)

        for path, label in test:
            X_test.append(loadFeatures(path))
            Y_test.append(label)

        X_train = np.array(X_train)
        X_val = np.array(X_val)
        X_test = np.array(X_test)

        Y_train = np.array(Y_train)
        Y_val = np.array(Y_val)
        Y_test = np.array(Y_test)

        input_size = 512
        size_1 = input_size * 2
        hidden_size_2 = int(input_size / 2)

        model = tf.keras.Sequential()

        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Input(input_size))
        model.add(tf.keras.layers.Dense(size_1, activation='relu'))
        model.add(tf.keras.layers.Dropout(0.3))
        model.add(tf.keras.layers.Dense(hidden_size_2, activation='relu'))
        model.add(tf.keras.layers.Dropout(0.3))
        model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

        optimizer = tf.optimizers.Adam(learning_rate=0.0001)

        model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=[tf.keras.metrics.AUC()]
        )

        history = model.fit(
            X_train,
            Y_train,
            epochs=100,
            validation_data=(X_val, Y_val),
            verbose=2
        )

        y_pred = model.predict(X_test)
        y_pred_bin = [1 if p[0] > 0.5 else 0 for p in y_pred]

        cm = confusion_matrix(Y_test, y_pred_bin)
        f1 = f1_score(Y_test, y_pred_bin)
        asc = accuracy_score(Y_test, y_pred_bin)

        print('confusion matrix:', cm)
        print('f1 matrix:', f1)
        print('asc', asc)

        fullpath = getModelFullPath()
        print(f"Saving model to: {fullpath}")
        model.save(fullpath)


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("scans")
    # buildModel()
    findInvalidScans()
