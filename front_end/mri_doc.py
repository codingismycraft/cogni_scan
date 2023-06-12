import cogni_scan.front_end.cfc.document as document
import cogni_scan.src.nifti_mri as nifti_mri


class MRIDocument(document.Document):
    _mris = {}
    _include_skiped = True
    _active_path = None

    def clear(self):
        """Delete the document's data without destroying the object."""
        self._mris = {}
        self._active_path = None

    def load(self, **kwargs):
        """Loads the documentDelete the document's data without destroying the object.."""
        self._active_path = None
        self._mris = nifti_mri.load_from_db()
        assert isinstance(self._mris, dict)
        self._active_path = list(self._mris.keys())[0]
        self.updateAllViews()

    def getActiveMri(self):
        if self._active_path:
            assert self._active_path in self._mris
            return self._mris[self._active_path]

    def setActiveMri(self, filepath, sender=None):
        assert filepath in self._mris
        self._active_path = filepath
        self.updateAllViews(sender)

    def isDirty(self):
        """Determine modification since it was last saved."""
        raise NotImplementedError

    def save(self):
        """Saves the document if modified."""
        raise NotImplementedError

    def setIncludeSkiped(self, inlude_skipped=True):
        if includeSkiped != self._include_skiped:
            self._include_skiped = include_skiped
            self._main_frame.updateViews()

    def getMRIs(self):
        for path in self._mris:
            yield self._mris[path]


if __name__ == '__main__':
    m = MRIDocument()
