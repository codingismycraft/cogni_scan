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
        self.getDocument().checkToSave(ask_to_save=False)
        self.updateSaveButtonState()

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

    def changeOrienation(self, axis):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        mri.changeOrienation(axis)
        self.updateSaveButtonState()
        self.getDocument().updateAllViews(self)

    def _updateCollectionData(self):
        """Paints screen with descriptive data."""
        activeCollection = self.getDocument().getActiveCollection()
        if not activeCollection:
            return
        canvas = Canvas(self.__parent_frame, height=60, bg='bisque')
        canvas.pack(side="left", fill="both", expand=False, padx=10)
        labels = []
        values = []
        for k, v in activeCollection.getDesctiptiveData().items():
            labels.append(tk.Label(canvas, text=k))
            values.append(tk.Label(canvas, text=str(v)))
        for row, label in enumerate(labels):
            label.grid(row=row, column=0, sticky=W)
        for row, label in enumerate(values):
            label.grid(row=row, column=1, sticky=W)

    def _updatePatientData(self):
        activePatient = self.getDocument().getActivePatient()
        if not activePatient:
            return
        canvas = Canvas(self.__parent_frame, height=60, bg='red')
        canvas.pack(side="left", fill="both", expand=False, padx=10)
        labels = []
        values = []
        for k, v in activePatient.getDescriptiveData().items():
            labels.append(tk.Label(canvas, text=k))
            values.append(tk.Label(canvas, text=str(v)))
        for row, label in enumerate(labels):
            label.grid(row=row, column=0, sticky=W)
        for row, label in enumerate(values):
            label.grid(row=row, column=1, sticky=W)

    def _updateScanData(self):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return

        canvas = Canvas(self.__parent_frame, height=60, bg='bisque')
        canvas.pack(side="left", fill="both", expand=False, padx=10)

        self._save_button = Button(
            canvas,
            text="Save",
            command=self.saveChanges)

        self._save_button.grid(row=0, column=0)
        self.updateSaveButtonState()

        # Add the buttons to change the Axes.
        for index, axis in enumerate(cs.getAxesOrientation()):
            callback = functools.partial(self.changeAxis, axis)
            button = Button(canvas, text=axis, command=callback)
            button.grid(row=1, column= index)

        # Add the buttons to rotate the slices if needed.
        for index, axis in enumerate([0, 1, 2]):
            callback = functools.partial(self.changeOrienation, axis)
            button = Button(canvas, text="R", command=callback)
            button.grid(row=2, column= index)

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.clear()
        self._updateCollectionData()
        self._updatePatientData()
        self._updateScanData()


if __name__ == '__main__':
    v = TopView(None)
