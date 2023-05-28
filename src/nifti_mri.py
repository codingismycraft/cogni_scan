import cv2

import nibabel as nib

import cogni_scan.src.interfaces as cs


class NiftiMri(cs.IMri):

    def __init__(self):
        initialize()

    def initialize():
        self.__img = None
        self.__axis_mapping = {0: 0, 1: 1, 2: 2}  # Oasis-3 axis
        self.__rotation = None 
        self.__size_trasnsformers = {}
        
    def load(self, filepath):
        """Loads the MRI from the disk.

        There are two main cases to check here:

        (1) The passed in filepath does not exist in the db.
        Axis mappings and roation use the default values.

        (2) The passed in filepath already exist in the db.
        Axis mappings and roation are loaded from the db.
        """
        initialize()
        if existsInDB(filepath):
            self.__axis_mapping, self.__rotation = loadFromDb() 
        self.__img = nib.load(filepath).get_fdata()

    def bind_size_transformer(self, axis, x, y):
        self.__size_trasnsformers[axis] = (x, y)

    def bind_axis_mapping(self, axis_mapping):
        """Binds an axis mapping (used for Oasis-2 for example).

        :param tuple axis_mapping: Permutation of 0, 1, 2

        :raises ValueError: If axis mapping is not a permutation of 0,1,2.
        """
        if not isinstance(axis_mapping, tuple):
            raise ValueError
        if not len(axis_mapping) == 3:
            raise ValueError
        if not 0 in axis_mapping:
            raise ValueError
        if not 1 in axis_mapping:
            raise ValueError
        if not 2 in axis_mapping:
            raise ValueError

        self.__axis_mapping = {
            index: value
            for index, value in enumerate(axis_mapping)
        }

    @property
    def axis_mapping(self):
        return self.__axis_mapping.copy()

    def get_slice(self, distance_from_center=0, axis=2):
        axis = self.__axis_mapping.get(axis)
        assert self.__img is not None
        assert -1. <= distance_from_center <= 1.
        n = int(int(self.__img.shape[axis] / 2) * (1 + distance_from_center))
        if axis == 0:
            img = self.__img[n, :, :]
        elif axis == 1:
            img = self.__img[:, n, :]
        elif axis == 2:
            img = self.__img[:, :, n]
        else:
            return ValueError
        if axis in self.__size_trasnsformers:
            x, y = self.__size_trasnsformers[axis]
            return cv2.resize(
                img,
                dsize=(x, y),
                interpolation=cv2.INTER_CUBIC
            )
        else:
            return img
