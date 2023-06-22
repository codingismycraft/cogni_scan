import os
import tempfile

import cv2
from tkinter.messagebox import askyesno

import cogni_scan.constants as constants
import cogni_scan.front_end.cfc.document as document
import cogni_scan.src.nifti_mri as nifti_mri


class MRIDocument(document.Document):
    """Holds the MRI related information.

    :ivar int _active_mri_id: The active mri id.
    """
    _active_mri_id = None
    _needs_to_update_all = True
    _patients = None
    _active_patient_id = None
    _validation_status = constants.ALL_SCANS
    _show_only_healthy = False
    _show_labels = "ALL"
    _slice_square_length = 400

    def clear(self):
        """Delete the document's data without destroying the object."""
        self._active_mri_id = None
        self._needs_to_update_all = True
        self._patients = None
        self._active_patient_id = None

    def getPatientById(self, patient_id):
        """Returns the patient object for the passed in patent id."""
        return self._patients.getPatient(patient_id)

    def getMriByMriID(self, mri_id):
        return self._patients.getMriByMriID(mri_id)

    def getValidationStatus(self):
        return self._validation_status

    def getShowOnlyHealthy(self):
        return self._show_only_healthy

    def getLabelsToShow(self):
        return self._show_labels

    def saveLabelsToDb(self):
        if self._patients:
            self._patients.saveLabelsToDb()

    def saveVGG16Features(self):
        if self._patients:
            self._patients.saveVGG16Features()

    def makeMovie(self, axis=1):
        """Plays a video using the current MRI and the passed in axis."""
        mri = self.getActiveMri()
        if not mri:
            return

        base_dir = tempfile.gettempdir()

        # Delete old movie files.
        for item in os.listdir(base_dir):
            if item.startswith("movie"):
                os.remove(os.path.join(base_dir, item))

        # Create the slices.
        distance = -0.9
        index = 0
        step = 0.02

        while distance < 1.0:
            index += 1
            filename = f"movie_slice_{index:02}.jpg"
            filename = os.path.join(base_dir, filename)
            img = mri.get_slice(
                distance_from_center=distance,
                axis=axis,
                bounding_square=200
            )
            cv2.imwrite(filename, img)
            distance += step

        # Create the movie.
        video_name =  os.path.join(base_dir, 'movie.avi')

        images = [img for img in os.listdir(base_dir) if
                  img.endswith(".jpg") and img.startswith("movie_slice")]
        images.sort()
        frame = cv2.imread(os.path.join(base_dir, images[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, 0, 5, (width, height))
        for image in images:
            video.write(cv2.imread(os.path.join(base_dir, image)))
        cv2.destroyAllWindows()
        video.release()

        # Play the video.
        cap = cv2.VideoCapture(video_name)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(video_name, frame)
            if cv2.waitKey(150) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()


    def load(self, **kwargs):
        """Loads the documentDelete the document's data without destroying the object.."""
        show_labels = "ALL"
        if 'show_labels' in kwargs:
            show_labels = kwargs.get('show_labels')

        show_only_healthy = False
        if 'show_only_healthy' in kwargs:
            show_only_healthy = kwargs.get('show_only_healthy')
            assert show_only_healthy in (0, 1)
            show_only_healthy = bool(show_only_healthy)

        validation_status = constants.ALL_SCANS
        if 'validation_status' in kwargs:
            validation_status = kwargs.get('validation_status')

        self.clear()
        self._active_mri_id = None
        self._patients = nifti_mri.PatientCollection()

        self._patients.loadFromDb(
            show_labels,
            show_only_healthy,
            validation_status
        )
        self._show_only_healthy = 1 if show_only_healthy else 0
        self._show_labels = show_labels
        self._validation_status = validation_status
        self._needs_to_update_all = True
        self.updateAllViews()

    def getNeedsToUpdateAll(self):
        return self._needs_to_update_all

    def setNeedsToUpdateAll(self, value):
        self._needs_to_update_all = value

    def getActiveCollection(self):
        return self._patients

    def setActivePatientID(self, patient_id):
        if patient_id is not self._active_patient_id:
            self._active_patient_id = patient_id
            self._active_mri_id = None

    def makeSliceLarger(self):
        x = self._slice_square_length
        if x >= 500:
            return
        x += x * 0.1
        self._slice_square_length = int(x)

    def makeSliceSmaller(self):
        x = self._slice_square_length
        if x <= 100:
            return
        x -= x * 0.1
        self._slice_square_length = int(x)

    def getSliceSquareLength(self):
        return self._slice_square_length

    def getActivePatient(self):
        if not self._active_patient_id:
            return None
        else:
            return self._patients.getPatient(self._active_patient_id)

    def getActiveMri(self):
        if self._active_mri_id:
            return self._patients.getMriByMriID(self._active_mri_id)

    def setActiveMri(self, mri_id, sender=None):
        self.checkToSave()
        self._active_mri_id = mri_id
        mri = self._patients.getMriByMriID(mri_id)
        self._active_patient_id = mri.getPatientID()
        self.updateAllViews(sender)

    def checkToSave(self, ask_to_save=True):
        mri = self.getActiveMri()
        if mri and mri.isDirty():
            if ask_to_save:
                if not askyesno(
                        title='MRI info was changed.',
                        message='Do you want to save your changes?'):
                    mri.restoreOriginalState()
                    return
            mri.saveToDb()

    def isDirty(self):
        """Determine modification since it was last saved."""
        mri = self.getActiveMri()
        return mri and mri.isDirty()

    def save(self):
        """Saves the document if modified."""
        mri = self.getActiveMri()
        if mri and mri.isDirty():
            mri.saveToDb()

    def getPatientIDs(self):
        for patient_id, caption in self._patients.getPatientIDs():
            yield patient_id, caption

    def getMRIs(self, patient_id):
        return self._patients.getMrisByPatient(patient_id)


if __name__ == '__main__':
    m = MRIDocument()
