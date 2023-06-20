import json
import logging

import tkinter.ttk as ttk
import tkinter as tk

import cogni_scan.front_end.settings as settings
import cogni_scan.front_end.cfc.view as view
import cogni_scan.src.utils as utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_HAS_VGG_FEATURES = 'has-vgg-features'
_IS_MRI = 'is-MRI'


class LeftView(ttk.Treeview, view.View):

    def eventHandler(self, item_selected):
        cur_item = self.focus()
        values = self.item(cur_item)
        tags = values["tags"]
        if tags and tags[0] == _IS_MRI:
            # The user clicked on an MRI item.
            mri_id = tags[1]
            self.getDocument().setActiveMri(mri_id, self)
        else:
            self.getDocument().setActivePatientID(cur_item)
            self.getDocument().updateAllViews(self)

    @utils.timeit
    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        ttk.Style().configure("Treeview",
                              background=settings.LEFT_BACKGROUND_COLOR,
                              foreground="white", fieldbackground="black")

        doc = self.getDocument()
        if not doc.getNeedsToUpdateAll():
            return
        logger.info("Loading the whole document..")
        self.heading('#0', text='Subject ID', anchor=tk.W)
        self.delete(*self.get_children())
        for patient_id, caption in doc.getPatientIDs():
            patient = doc.getPatientById(patient_id)
            tags = ()
            if patient.hasVGGFeatures():
                tags = (_HAS_VGG_FEATURES,)
            self.insert(
                '',
                tk.END,
                text=caption,
                iid=patient_id,
                open=False,
                tags=tags
            )
        for patient_id, _ in doc.getPatientIDs():
            for index, mri in enumerate(doc.getMRIs(patient_id)):
                mri_id = mri.getMriID()
                self.insert(
                    '', tk.END, text=mri_id, iid=mri_id,
                    tags=(_IS_MRI, mri.getScanID(), _HAS_VGG_FEATURES)
                )
                self.move(mri_id, patient_id, index=index)
        self.bind('<<TreeviewSelect>>', self.eventHandler)
        doc.setNeedsToUpdateAll(False)
        self.tag_configure(_HAS_VGG_FEATURES, background='green')
        logger.info("Done with loading the whole document..")


if __name__ == '__main__':
    v = LeftView()
