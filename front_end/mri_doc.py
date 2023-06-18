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


    def clear(self):
        """Delete the document's data without destroying the object."""
        self._active_mri_id = None
        self._needs_to_update_all = True
        self._patients = None
        self._active_patient_id = None

    def load(self, **kwargs):
        """Loads the documentDelete the document's data without destroying the object.."""
        self.clear()
        self._active_mri_id = None
        self._patients = nifti_mri.PatientCollection()
        self._patients.loadFromDb()
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
        mri =  self._patients.getMriByMriID(mri_id)
        self._active_patient_id = mri.getPatientID()
        self.updateAllViews(sender)

    def checkToSave(self, ask_to_save=True):
        mri = self.getActiveMri()
        if mri and mri.isDirty():
            if ask_to_save:
                if not askyesno(
                        title='MRI info was changed.',
                        message='Do you want to save your changes?'):
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
