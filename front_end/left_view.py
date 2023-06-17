import json
import logging

import tkinter.ttk as ttk
import tkinter as tk

import cogni_scan.front_end.cfc.view as view

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LeftView(ttk.Treeview, view.View):

    def eventHandler(self, item_selected):
        cur_item = self.focus()
        values = self.item(cur_item)
        tags = values["tags"]
        if tags:
            # The user clicked on an MRI item.
            mri_id = tags[0]
            self.getDocument().setActiveMri(mri_id, self)

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        doc = self.getDocument()
        if not doc.getNeedsToUpdateAll():
            return
        logger.info("Loading the whole document..")
        self.heading('#0', text='Subject ID', anchor=tk.W)
        self.delete(*self.get_children())
        for patiend_id, caption in doc.getPatientIDs():
            self.insert(
                '',
                tk.END,
                text=caption,
                iid=patiend_id,
                open=False
            )
        for patiend_id, _ in doc.getPatientIDs():
            for index, mri in enumerate(doc.getMRIs(patiend_id)):
                mri_id = mri.getMriID()
                self.insert(
                    '', tk.END, text=mri_id, iid=mri_id, tags=(mri.getScanID(),)
                )
                self.move(mri_id, patiend_id, index=index)
        self.bind('<<TreeviewSelect>>', self.eventHandler)
        doc.setNeedsToUpdateAll(False)
        logger.info("Done with loading the whole document..")


if __name__ == '__main__':
    v = LeftView()
