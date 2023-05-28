import os
import unittest

import cogni_scan.src.impl.nifti_mri as nifti_mri

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
_DUMMY_MRI = os.path.join(_CURRENT_DIR, "testing_data", "mri-1.nii.gz")
_DUMMY_OASIS2_MRI = os.path.join(_CURRENT_DIR, "testing_data", "oasis-2-mri")


class NiftiMriTest(unittest.TestCase):
    def test_invalid_filepath(self):
        m = nifti_mri.NiftiMri()
        with self.assertRaises(FileNotFoundError):
            m.load("junk_path")

    def test_load(self):
        m = nifti_mri.NiftiMri()
        m.load(_DUMMY_MRI)

    def test_getting_slice(self):
        m = nifti_mri.NiftiMri()
        m.load(_DUMMY_MRI)
        print(m.get_slice())

    def test_multiple_slices(self):
        distances = [.9, .5, .3, 0, -.3, -.5, -.9]
        m = nifti_mri.NiftiMri()
        m.load(_DUMMY_MRI)
        for d in distances:
            _ = m.get_slice(distance_from_center=d)

    def test_oasis2_file(self):
        m = nifti_mri.NiftiMri()
        x = os.path.join(_DUMMY_OASIS2_MRI, "mpr-3.nifti.img")
        m.load(x)

    def test_bind_invalid_axis_mapping(self):
        m = nifti_mri.NiftiMri()
        invalid_mappings = [
            [] ,(2,), (2, 2, 2), (1, 2, 0, 4), tuple(), ('a', 'b')
        ]
        for mapping in invalid_mappings:
            with self.assertRaises(ValueError):
                m.bind_axis_mapping(mapping)

    def test_bind_axis_mapping(self):
        m = nifti_mri.NiftiMri()
        expected ={0: 2, 1: 0, 2: 1}
        m.bind_axis_mapping((2, 0, 1))
        self.assertDictEqual(expected, m.axis_mapping)


if __name__ == '__main__':
    unittest.main()
