import functools

from tkinter import *
from tkinter.constants import *

import tkinter as tk
import tkinter.ttk as ttk

import cogni_scan.front_end.cfc.view as view
import cogni_scan.src.utils as cs

class TopView(view.View):

    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame

    def clear(self):
        """Removes only the images from the frame.

        Will be used when the frame will be re-painted as the response
        to the user re-sizing the image size.
        """
        for widget in self.__parent_frame.winfo_children():
            widget.destroy()

    def saveChanges(self):
        pass

    def updateSaveButtonState(self):
        if not self._save_button:
            return
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        if mri and mri.isDirty():
            self._save_button["state"] = "normal"
        else:
            self._save_button["state"] = "disabled"

    def changeAxis(self, axis_mapping):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        mri.setAxisMapping(axis_mapping)
        self.updateSaveButtonState()
        self.getDocument().updateAllViews(self)

    def _updateDescriptiveData(self):
        """Paints screen with descriptive data."""
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        canvas = Canvas(self.__parent_frame, width=600, height=60, bg='bisque')
        canvas.pack(anchor=W)

        l1 = tk.Label(canvas,  text="Patient ID")
        l2 = tk.Label(canvas,  text="Days since first visit")
        l3 = tk.Label(canvas,  text="Health Status")

        # l1.pack()
        # l2.pack()
        # l3.pack()

        l1.grid(row=0, column=0, sticky=W)
        l2.grid(row=1, column=0, sticky=W)
        l3.grid(row=2, column=0, sticky=W)


    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.clear()
        self._updateDescriptiveData()
        return

        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        l1 = tk.Label(self.__parent_frame,  text="Patient ID")
        l2 = tk.Label(self.__parent_frame,  text="Days since first visit")
        l3 = tk.Label(self.__parent_frame,  text="Health Status")


        patient_id = StringVar()
        patient_id.set(f"{mri.getPatientID()}")
        e1 = tk.Entry(self.__parent_frame, state="readonly",textvariable=patient_id, width=15)

        days = StringVar()
        days.set(f"{mri.getDays()}")
        e2 = tk.Entry(self.__parent_frame, state="readonly",textvariable=days, width=5)

        health_status = StringVar()
        health_status.set(f"{mri.getHealthStatus()}")
        e3 = tk.Entry(self.__parent_frame, state="readonly",textvariable=health_status, width=15)

        l1.grid(row=0, column=0,sticky=W, padx=8)
        l2.grid(row=1, column=0,sticky=W, padx=8)
        l3.grid(row=2, column=0,sticky=W, padx=8)

        e1.grid(row=0, column=1,sticky=W, padx=8)
        e2.grid(row=1, column=1,sticky=W, padx=8)
        e3.grid(row=2, column=1,sticky=W, padx=8)

        self._save_button = Button(
            self.__parent_frame,
            text="Save",
            command=self.saveChanges)

        self._save_button.grid(row=3, column=0)
        self.updateSaveButtonState()

        canvas = Canvas(self.__parent_frame, width=600, height=60, bg='bisque')
        canvas.grid(row=4, column=0)

        for axis in cs.getAxesOrientation():
            callback = functools.partial(self.changeAxis, axis)
            button = Button(canvas, text=axis, command=callback)
            button.pack(pady=20, side=LEFT)

if __name__ == '__main__':
    v = TopView(None)
