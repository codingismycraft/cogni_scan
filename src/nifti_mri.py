import cv2
import nibabel as nib


class NiftiMri:

    def __init__(self, filepath):
        self.__img = None
        self.__axis_mapping = {0: 0, 1: 1, 2: 2}  # Oasis-3 axis
        self.__rotation = [0, 0, 0]
        self.__filepath = filepath
        self.__img = nib.load(self.__filepath).get_fdata()

    def getFilePath(self):
        return self.__filepath

    def changeOrienation(self, axis):
        assert 0 <= axis <= 2
        axis = self.__axis_mapping.get(axis)
        r = self.__rotation[axis]
        r += 1
        r = r % 4
        self.__rotation[axis] = r

    def setAxisMapping(self, axis_mapping):
        """Binds an axis mapping (used for Oasis-2 for example).

        :param tuple axis_mapping: Permutation of 0, 1, 2

        :raises ValueError: If axis mapping is not a permutation of 0,1,2.
        """
        self.__rotation = [0, 0, 0]
        tokens = axis_mapping.split('-')
        axis_mapping = tuple([int(x) for x in tokens])
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

        for _ in range(self.__rotation[axis]):
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return img

        # if axis in self.__size_trasnsformers:
        #     x, y = self.__size_trasnsformers[axis]
        #     return cv2.resize(
        #         img,
        #         dsize=(x, y),
        #         interpolation=cv2.INTER_CUBIC
        #     )
        # else:
        #     return img
