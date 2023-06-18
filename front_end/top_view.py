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

    def _updateFiltering(self):
        """Updates the filters applied to the collection of Mri objects."""
        activeCollection = self.getDocument().getActiveCollection()
        if not activeCollection:
            return
        canvas = Canvas(self.__parent_frame, height=60, bg='bisque')
        canvas.pack(side="left", fill="both", expand=False, padx=10)

        self._hide_skiped_var = tk.IntVar()
        doc = self.getDocument()
        self._hide_skiped_var.set(doc.getHideSkipped())
        skipit_checkbox = tk.Checkbutton(
            canvas, text="Hide skipped",
            variable=self._hide_skiped_var, command=self.hideSkipped)
        skipit_checkbox.grid(row=0, column=0)

    def hideSkipped(self):
        value = self._hide_skiped_var.get()
        doc = self.getDocument()
        doc.load(hide_skipped=value)
        print("dont know how to do it", value)

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
        column = 0
        for axis in cs.getAxesOrientation():
            callback = functools.partial(self.changeAxis, axis)
            button = Button(canvas, text=axis, command=callback)
            button.grid(row=1, column=column)
            column += 1

        # Add the buttons to rotate the slices if needed.
        for axis in [0, 1, 2]:
            callback = functools.partial(self.changeOrienation, axis)
            button = Button(canvas, text="R", command=callback)
            button.grid(row=1, column=column)
            column += 1

        # Add the skip-it or not.
        self._skipit_checkbox_var = tk.IntVar()
        self._skipit_checkbox_var.set(mri.shouldBeSkiped())
        skipit_checkbox = tk.Checkbutton(
            canvas, text="Should Be Skipped",
            variable=self._skipit_checkbox_var, command=self.changeSkipIt)
        skipit_checkbox.grid(row=2, column=0)

    def changeSkipIt(self):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        value = self._skipit_checkbox_var.get()
        mri.setShouldBeSkiped(value)

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.clear()
        self._updateFiltering()
        self._updateCollectionData()
        self._updatePatientData()
        self._updateScanData()


if __name__ == '__main__':
    v = TopView(None)
