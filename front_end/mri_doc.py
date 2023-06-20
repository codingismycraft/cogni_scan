from tkinter.messagebox import askyesno

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
    _hide_skipped = 1
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

    def getHideSkipped(self):
        return self._hide_skipped

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

    def load(self, **kwargs):
        """Loads the documentDelete the document's data without destroying the object.."""
        hide_skipped = True
        if 'hide_skipped' in kwargs:
            hide_skipped = kwargs.get('hide_skipped')
            assert hide_skipped in (0, 1)
            hide_skipped = bool(hide_skipped)

        show_labels = "ALL"
        if 'show_labels' in kwargs:
            show_labels = kwargs.get('show_labels')

        show_only_healthy = False
        if 'show_only_healthy' in kwargs:
            show_only_healthy = kwargs.get('show_only_healthy')
            assert show_only_healthy in (0, 1)
            show_only_healthy = bool(show_only_healthy)

        self.clear()
        self._active_mri_id = None
        self._patients = nifti_mri.PatientCollection()
        self._patients.loadFromDb(hide_skipped, show_labels, show_only_healthy)
        self._hide_skipped = 1 if hide_skipped else 0
        self._show_only_healthy = 1 if show_only_healthy else 0
        self._show_labels = show_labels
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

    def setIncludeSkiped(self, inlude_skipped=True):
        if includeSkiped != self._include_skiped:
            self._include_skiped = include_skiped
            self._main_frame.updateViews()

    def getPatientIDs(self):
        for patient_id, caption in self._patients.getPatientIDs():
            yield patient_id, caption

    def getMRIs(self, patient_id):
        return self._patients.getMrisByPatient(patient_id)


if __name__ == '__main__':
    m = MRIDocument()
