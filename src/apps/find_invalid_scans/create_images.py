"""Reads the valid/ invalid scans file and stores them as images."""

import csv
import os

import cv2
import nibabel as nib
import numpy as np
import tensorflow as tf

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def saveImage(fullpath, destination, distance_from_center=0, axis=0,
              bounding_square=200):
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
    print(destination)
    cv2.imwrite(destination, l_img)


def main(path_to_statuses):
    valid_dir = os.path.join(_CURRENT_DIR, "valid")
    invalid_dir = os.path.join(_CURRENT_DIR, "invalid")

    if not os.path.isdir(valid_dir):
        os.mkdir(valid_dir)

    if not os.path.isdir(invalid_dir):
        os.mkdir(invalid_dir)

    with open(path_to_statuses) as fin:
        for tokens in csv.reader(fin):
            scan_id = tokens[0]
            path = tokens[1]
            status = tokens[3]
            destination = os.path.join(_CURRENT_DIR, status, f'{scan_id}.png')
            saveImage(path, destination)


if __name__ == '__main__':
    main(os.path.join(_CURRENT_DIR, "scan-status-2.csv"))
