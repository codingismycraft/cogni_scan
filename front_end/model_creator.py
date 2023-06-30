from itertools import chain, combinations
import functools
import os

from tkinter import *
from tkinter.messagebox import askyesno
import tkinter as tk
import tkinter.simpledialog
import tkinter.ttk as ttk

import cogni_scan.front_end.settings as settings
import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.modeler.model as model


def powerset(collection):
    """Returns all possible subsets for the passed in collection."""
    collection = sorted(collection)
    all = []
    for i in range(1, len(collection) + 2):
        for c in list(combinations(collection, i)):
            all.append(list(c))
    return all

class ModelCreator:

    def callback(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            dataset_id = event.widget.get(index)
            ds = model.getDatasetByID(dataset_id)
            print(ds.getDescription())

            for widget in self._right_frame.winfo_children():
                widget.destroy()

            canvas_1 = Canvas(self._right_frame,
                              height=90,
                              bg=settings.TOP_BACKGROUND_COLOR,
                              highlightthickness=0)
            canvas_1.grid(row=0, column=0)

            canvas_col = 0
            canvas_row = 0
            for title, properties in ds.getDescription().items():
                canvas = Canvas(canvas_1,
                                height=90,
                                bg=settings.TOP_BACKGROUND_COLOR,
                                highlightthickness=0)

                canvas.grid(row=canvas_row, column=canvas_col, padx=4)
                canvas_col += 1

                title_label = tk.Label(canvas, text=title.upper(),
                                       bg='black',
                                       fg='white',
                                       pady=4)

                title_label.grid(row=0, column=0, sticky=EW)
                labels = []
                values = []
                for k, v in properties.items():
                    labels.append(
                        tk.Label(canvas, text=k,
                                 bg=settings.LABEL_BACKGROUND_COLOR,
                                 fg=settings.LABEL_FRONT_COLOR, padx=4,
                                 pady=4)
                    )
                    values.append(tk.Label(canvas, text=str(v),
                                           bg=settings.LABEL_BACKGROUND_COLOR,
                                           fg=settings.VALUE_FRONT_COLOR,
                                           font=('Helvetica', 12, 'bold')))
                    for row, label in enumerate(labels):
                        label.grid(row=row + 1, column=0, sticky=W)
                    for row, label in enumerate(values):
                        label.grid(row=row + 1, column=1, sticky=W)

            def getSelectedSlices():
                labels = []
                for k, v in cb_vars.items():
                    if v.get() == 1:
                        labels.append(k)
                return labels

            def createModelClicked():
                if not askyesno(
                        title='Build New Model',
                        message='Are you sure you want to build a new model?'):
                    return

                self._root.config(cursor="watch")
                self._root.update()
                slices = getSelectedSlices()
                new_model = model.makeNewModel()
                new_model.trainAndSave(ds, slices)
                self._root.config(cursor="")
                print("done")

            def createPowerModelClicked():
                if not askyesno(
                        title='Build All the models.',
                        message='Build models for all possible combos of slices?'):
                    return
                self._root.config(cursor="watch")
                self._root.update()
                for slices in powerset(getSelectedSlices()):
                    new_model = model.makeNewModel()
                    new_model.trainAndSave(ds, slices)
                self._root.config(cursor="")
                print("done")

            def updateButtonState():
                if len(getSelectedSlices()) > 0:
                    create_model_button["state"] = "normal"
                else:
                    create_model_button["state"] = "disabled"

                if len(getSelectedSlices()) > 1:
                    create_model_button_1["state"] = "normal"
                else:
                    create_model_button_1["state"] = "disabled"

            canvas_2 = Canvas(self._right_frame,
                              height=90,
                              bg=settings.RIGHT_BACKGROUND_COLOR,
                              highlightthickness=0)
            canvas_2.grid(row=2, column=0, sticky=W, pady=10)

            cb_vars = {}
            for row, i in enumerate([1, 2, 3]):
                for col, j in enumerate([0, 1, 2]):
                    txt = f'{j}{i}'
                    cb_vars[txt] = tk.IntVar()
                    cb = tk.Checkbutton(
                        canvas_2,
                        text=txt,
                        variable=cb_vars[txt],
                        onvalue=1,
                        offvalue=0,
                        command=updateButtonState
                    )
                    cb.grid(row=row, column=col)

            canvas_3 = Canvas(self._right_frame,
                              height=90,
                              bg=settings.RIGHT_BACKGROUND_COLOR,
                              highlightthickness=0)
            canvas_3.grid(row=3, column=0, sticky=W, pady=10)

            create_model_button = Button(canvas_3, text="Create Model",
                                         command=createModelClicked)
            create_model_button.grid(row=0, column=1, sticky=W)

            create_model_button_1 = Button(canvas_3, text="Create Power Model",
                                         command=createPowerModelClicked)
            create_model_button_1.grid(row=0, column=2, sticky=W)

            updateButtonState()

    def main(self, title="n/a", menu=None, width=710, height=340, upperX=200,
             upperY=100, zoomed=False):

        ds = model.getDatasets()

        if len(ds) == 0:
            title = "Create New Model: There are no data sets available."
        else:
            title = f"Create New Model (there are {len(ds)} datasets)."

        self._root = tk.Tk()
        self._root.title(title)

        self.s = ttk.Style()
        self.s.configure('TFrame', background=settings.LEFT_BACKGROUND_COLOR)
        self.s1 = ttk.Style()
        self.s1.configure('right.TFrame',
                          background=settings.RIGHT_BACKGROUND_COLOR)

        self.s1 = ttk.Style()
        self.s1.configure('bottom.TFrame', background='#AAC5CD')

        self.s1 = ttk.Style()
        self.s1.configure('bottom.TFrame', background='#AAC5CD')

        panedwindow = ttk.Panedwindow(self._root, orient=tk.HORIZONTAL)
        panedwindow.pack(fill=tk.BOTH, expand=True)

        # Adds the left frame.
        self._left_frame = ttk.Frame(
            panedwindow,
            width=400,
            height=300,
            relief=tk.SUNKEN,
            style='TFrame'
        )
        panedwindow.add(self._left_frame)

        # Adds the right frame.
        self._right_frame = ttk.Frame(
            panedwindow,
            width=1230,
            height=520,
            relief=tk.SUNKEN,
            style='right.TFrame',
        )

        panedwindow.add(self._right_frame)

        Lb1 = Listbox(self._left_frame)
        dss = model.getDatasets()
        for index, ds in enumerate(dss):
            Lb1.insert(index + 0, ds.getDatasetID())

        Lb1.pack(fill=tk.BOTH, expand=True)
        Lb1.bind("<<ListboxSelect>>", self.callback)

        # Add the right view.
        self._root.geometry(f"{width}x{height}+{upperX}+{upperY}")

        self._root.mainloop()


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("scans")
    mc = ModelCreator()
    mc.main()
