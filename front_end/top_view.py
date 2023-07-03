import functools

from tkinter import *
from tkinter.constants import *

import tkinter as tk
import tkinter.ttk as ttk

import cogni_scan.constants as constants
import cogni_scan.front_end.cfc.view as view
import cogni_scan.front_end.settings as settings
import cogni_scan.front_end.model_viewer as model_viewer
import cogni_scan.src.modeler.model as model
import cogni_scan.src.utils as utils


class TopView(view.View):

    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame
        self.__background_color = "bisque"

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

    def _updateModels(self):
        # All all the available models in the right canvas.
        canvas = Canvas(
            self.__parent_frame,
            width=400,
            height=60,
            bg=settings.TOP_BACKGROUND_COLOR,
            highlightthickness=0
        )
        canvas.pack(side="left", fill=BOTH, expand=False, padx=10, pady=10)

        model_label = tk.Label(
            canvas,
            text="Available Models",
            bg=settings.LABEL_BACKGROUND_COLOR,
            fg=settings.LABEL_FRONT_COLOR
        )

        model_label.place(relx=0, rely=0, x=10, width=110, height=30)

        all_slices = ['01', '02', '03', '11', '12', '13', '21', '22', '23']

        columns = all_slices + ['accuracy', 'F1']
        # Treeview
        self._treeview = ttk.Treeview(canvas, columns=columns, show='headings')
        self._treeview.place(relx=0, rely=0.1, width=350, height=500)

        for s in all_slices:
            self._treeview.column(s, minwidth=0, width=30, stretch=NO)

        self._treeview.column('accuracy', minwidth=0, width=40, stretch=NO)
        self._treeview.column('F1', minwidth=0, width=40, stretch=NO)

        # Treeview headings
        for s in all_slices:
            self._treeview.heading(s, text=s)

        self._treeview.heading('accuracy', text="Acc.")
        self._treeview.heading('F1', text="F1")

        treeview_data = []
        all_models = model.getModels()

        for index, m in enumerate(all_models):
            iid = m.getModelID()

            slices = []
            for s in all_slices:
                if s in m.getSlices():
                    slices.append('X')
                else:
                    slices.append(' ')

            f1 = f"{m.getF1():0.02}"
            accuracy = f"{m.getAccuracyScore():0.02}"

            self._treeview.insert(
                parent="",
                index="end",
                iid=iid,
                values=slices + [accuracy, f1]
            )

        def removeModelFromTree(model_id):
            for item in self._treeview.get_children():
                if item == model_id:
                    self._treeview.delete(item)

        def OnDoubleClick(event):
            iid = self._treeview.focus()
            model_viewer.openModelWindow(self.__parent_frame, iid, removeModelFromTree)


        self._treeview.bind("<Double-1>", OnDoubleClick)

    def _updateFiltering(self):
        """Updates the filters applied to the collection of Mri objects."""
        activeCollection = self.getDocument().getActiveCollection()
        if not activeCollection:
            return
        doc = self.getDocument()
        canvas = Canvas(
            self.__parent_frame,
            height=60, bg=settings.TOP_BACKGROUND_COLOR,
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=False, padx=10)

        # Select the labels to display.
        self._current_health_label = tk.StringVar()
        self._current_health_label.set(doc.getLabelsToShow())
        labels_combo = ttk.Combobox(
            canvas,
            values=["ALL", "HH-HD", "HH-HD-HU", "HH", "HD", "HU",
                    "DH", "DU", "DD", "UH", "UU", "UD"],
            textvariable=self._current_health_label
        )
        labels_combo.grid(row=0, column=0, pady=8)
        labels_combo.bind('<<ComboboxSelected>>', self.refreshDisplay)

        # Add a checkbox to only use healthy scans.
        self._show_healthy_only_var = tk.IntVar()
        doc = self.getDocument()
        self._show_healthy_only_var.set(doc.getShowOnlyHealthy())
        show_only_healthy_checkbox = tk.Checkbutton(
            canvas,
            text="Show Only Healthy Scans",
            variable=self._show_healthy_only_var,
            command=self.refreshDisplay,
            bg=settings.TOP_BACKGROUND_COLOR,
            highlightthickness=0
        )
        show_only_healthy_checkbox.grid(row=1, column=0, pady=8)

        # Add the radio buttons to select scans based on their valid status.
        self._validation_status_var = IntVar()
        self._validation_status_var.set(doc.getValidationStatus())

        rb_1 = Radiobutton(canvas, text="Undefined",
                           variable=self._validation_status_var,
                           value=constants.UNDEFINED_SCAN,
                           command=self.refreshDisplay)
        rb_1.grid(row=3, column=0, pady=8)

        rb_2 = Radiobutton(canvas, text="Valid",
                           variable=self._validation_status_var,
                           value=constants.VALID_SCAN,
                           command=self.refreshDisplay)
        rb_2.grid(row=4, column=0, pady=8)

        rb_3 = Radiobutton(canvas, text="Invalid",
                           variable=self._validation_status_var,
                           value=constants.INVALID_SCAN,
                           command=self.refreshDisplay)
        rb_3.grid(row=5, column=0, pady=8)

        rb_4 = Radiobutton(canvas, text="All",
                           variable=self._validation_status_var,
                           value=constants.ALL_SCANS,
                           command=self.refreshDisplay)
        rb_4.grid(row=6, column=0, pady=8)

    def refreshDisplay(self, *args, **kwargs):
        labels = self._current_health_label.get()
        show_only_healthy = self._show_healthy_only_var.get()
        validation_status = self._validation_status_var.get()
        doc = self.getDocument()
        doc.load(
            show_labels=labels,
            show_only_healthy=show_only_healthy,
            validation_status=validation_status
        )

    def _updateCollectionData(self):
        """Paints screen with descriptive data."""
        activeCollection = self.getDocument().getActiveCollection()
        if not activeCollection:
            return
        canvas = Canvas(self.__parent_frame, height=90,
                        bg=settings.TOP_BACKGROUND_COLOR, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        labels = []
        values = []
        for k, v in activeCollection.getDesctiptiveData().items():
            labels.append(
                tk.Label(canvas, text=k, bg=settings.LABEL_BACKGROUND_COLOR,
                         fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10))
            values.append(tk.Label(canvas, text=str(v),
                                   bg=settings.LABEL_BACKGROUND_COLOR,
                                   fg=settings.VALUE_FRONT_COLOR,
                                   font=('Helvetica', 12, 'bold')))
        for row, label in enumerate(labels):
            label.grid(row=row, column=0, sticky=W)
        for row, label in enumerate(values):
            label.grid(row=row, column=1, sticky=W)

    def _updatePatientData(self):
        activePatient = self.getDocument().getActivePatient()
        if not activePatient:
            return
        canvas = Canvas(self.__parent_frame, height=90,
                        bg=settings.TOP_BACKGROUND_COLOR, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        labels = []
        values = []
        for k, v in activePatient.getDescriptiveData().items():
            labels.append(
                tk.Label(canvas, text=k, bg=settings.LABEL_BACKGROUND_COLOR,
                         fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10))
            values.append(tk.Label(canvas, text=str(v),
                                   bg=settings.LABEL_BACKGROUND_COLOR,
                                   fg=settings.VALUE_FRONT_COLOR,
                                   font=('Helvetica', 12, 'bold')))
        for row, label in enumerate(labels):
            label.grid(row=row, column=0, sticky=W)
        for row, label in enumerate(values):
            label.grid(row=row, column=1, sticky=W)

    def _updateScanData(self):
        """Updates the view with Scan specific data."""
        mri = self.getDocument().getActiveMri()
        if not mri:
            return

        main_canvas = Canvas(
            self.__parent_frame, height=60, bg=settings.TOP_BACKGROUND_COLOR
        )
        main_canvas.pack(side="left", fill="both", expand=False, padx=10)

        left_canvas = Canvas(main_canvas, height=60,
                             bg=settings.TOP_BACKGROUND_COLOR)
        left_canvas.pack(side="left", fill="both", expand=False, padx=10)

        middle_canvas = Canvas(main_canvas, height=60,
                               bg=settings.TOP_BACKGROUND_COLOR)
        middle_canvas.pack(side="left", fill="both", expand=False, padx=10)

        right_canvas = Canvas(main_canvas, height=60,
                              bg=settings.TOP_BACKGROUND_COLOR)
        right_canvas.pack(side="left", fill="both", expand=False, padx=10)

        self._save_button = Button(
            left_canvas,
            text="Save",
            command=self.saveChanges)

        self._save_button.grid(row=0, column=0)
        self.updateSaveButtonState()

        # Add the buttons to change the Axes.
        column = 0
        buttons = []
        for axis in utils.getAxesOrientation():
            callback = functools.partial(self.changeAxis, axis)
            button = Button(left_canvas, text=axis, command=callback)
            buttons.append(button)

        for b in buttons:
            b.grid(row=1, column=column, pady=8)
            column += 1

        # Add the buttons to rotate the slices if needed.
        for column, axis in enumerate([0, 1, 2]):
            callback = functools.partial(self.changeOrienation, axis)
            button = Button(left_canvas, text="R", command=callback)
            button.grid(row=2, column=column, pady=8)

        # Add the buttons to make the slices larger or smaller.
        button = Button(left_canvas, text="M", command=self.make_slice_larger)
        button.grid(row=2, column=3, pady=8)

        button = Button(left_canvas, text="S", command=self.make_slice_smaller)
        button.grid(row=2, column=4, pady=8)

        # Select the distances of the secondary slices.
        self._slice_dist_labels = []
        distances = mri.getSliceDistances()
        for i in range(3):
            label = tk.StringVar()
            label.set(f"{distances[i]}")
            self._slice_dist_labels.append(label)
            dist_combo = ttk.Combobox(
                left_canvas,
                values=[f'0.{i}' for i in range(1, 10)],
                textvariable=label,
                width=3
            )
            dist_combo.grid(row=4, column=1 + i, pady=8)
            dist_combo.bind('<<ComboboxSelected>>', self.changeSliceDistance)

        # Add the radio buttons to select scans based on their valid status.
        self._validation_status_for_scan_var = IntVar()
        self._validation_status_for_scan_var.set(mri.getValidationStatus())
        rb_1 = Radiobutton(middle_canvas, text="Set to Undefined",
                           variable=self._validation_status_for_scan_var,
                           value=constants.UNDEFINED_SCAN,
                           command=self.changeValidationStatusForSelectedScan)
        rb_1.grid(row=0, column=0, pady=8)
        rb_2 = Radiobutton(middle_canvas, text="Set to Invalid",
                           variable=self._validation_status_for_scan_var,
                           value=constants.INVALID_SCAN,
                           command=self.changeValidationStatusForSelectedScan)
        rb_2.grid(row=1, column=0, pady=8)
        rb_3 = Radiobutton(middle_canvas, text="Set to Valid",
                           variable=self._validation_status_for_scan_var,
                           value=constants.VALID_SCAN,
                           command=self.changeValidationStatusForSelectedScan)
        rb_3.grid(row=2, column=0, pady=8)

    def changeValidationStatusForSelectedScan(self):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        value = self._validation_status_for_scan_var.get()
        mri.setValidationStatus(value, autosave=True)
        self.updateSaveButtonState()

    def changeSliceDistance(self, *args, **kwargs):
        doc = self.getDocument()
        mri = doc.getActiveMri()
        if not mri:
            return
        for index, v in enumerate(self._slice_dist_labels):
            mri.setSliceDistance(index, float(v.get()))
        self.updateSaveButtonState()
        doc.updateAllViews(self)

    def make_slice_larger(self):
        doc = self.getDocument()
        doc.makeSliceLarger()
        doc.updateAllViews(self)

    def make_slice_smaller(self):
        doc = self.getDocument()
        doc.makeSliceSmaller()
        doc.updateAllViews(self)

    def changeIsValid(self):
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        value = self._is_valid_checkbox_var.get()
        mri.setIsValid(value)
        self.updateSaveButtonState()

    @utils.timeit
    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.clear()
        self._updateModels()
        self._updateFiltering()
        self._updateCollectionData()
        self._updatePatientData()
        self._updateScanData()


if __name__ == '__main__':
    v = TopView(None)
