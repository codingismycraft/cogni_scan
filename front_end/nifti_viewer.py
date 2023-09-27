#!/usr/bin/env python3.10

import functools
import os
import sys
import tempfile
import uuid

from PIL import ImageTk
from tkinter import *
from tkinter import filedialog as fd
import PIL.Image
import cv2
import tkinter as tk
import tkinter.simpledialog
import tkinter.ttk as ttk

sys.path.insert(0, "/home/john/repos")

import cogni_scan.front_end.settings as settings
import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.modeler.model as model
import cogni_scan.src.nifti_mri as nifti_mri
import cogni_scan.src.utils as utils

EVENT_EXIT = "EXIT"
OPEN_FILE = "OPEN_FILE"
RUN_PREDICTIONS = "Predict"
SEPARATOR = "Separator"

MENU = {
    "File": [
        ("Open", OPEN_FILE),
        (SEPARATOR, None),
        ("Exit", EVENT_EXIT),
    ],
    "Options": [
        ("Make Predictions", RUN_PREDICTIONS),
    ]
}


def saveSlicesToDisk(scan):
    """Saves the slices for the passed in scan to disk."""
    prefix = str(uuid.uuid4())[:8]
    filenames = {}
    for index in [0, 1, 2]:
        if index == 0:
            distances = scan.getSliceDistances()
            distances = [-x for x in distances]
        elif index == 1:
            distances = 0, 0, 0
        elif index == 2:
            distances = scan.getSliceDistances()
            distances = [x for x in distances]

        base_dir = tempfile.gettempdir()

        for axis in [0, 1, 2]:
            filename = f"slice_{prefix}_{axis}_{index}.jpg"
            filename = os.path.join(base_dir, filename)
            filenames[(index, axis)] = filename
            img = scan.get_slice(
                distance_from_center=distances[axis],
                axis=axis,
                bounding_square=240
            )
            cv2.imwrite(filename, img)
    return filenames


class MainFrame:
    _root = None
    _scan = None
    _predictionsRectangle = None

    def processEvent(self, event, data=None):
        if event == EVENT_EXIT:
            self._root.quit()
            self._root = None
        elif event == OPEN_FILE:
            filename = fd.askopenfilename(initialdir="/home/john/nifti-samples")
            self.setNiftiFile(filename)
        elif event == RUN_PREDICTIONS:
            self._runPredictions()

    def _runPredictions(self):
        if not self._scan:
            print("No Scan is available..")
            return
        all_models = model.getModels()
        self._root.config(cursor="watch")
        self._root.update()
        predictions = []
        for m in all_models:
            prediction = m.predictFromScan(self._scan)
            self._updateTreeViewWithPrediction(m.getModelID(), prediction)
            print(prediction)
            predictions.append(int(prediction * 100))
        self._root.config(cursor="")
        # self._updatePredictionsBar(predictions)
        self._updatePredictionsRectangle(predictions)

    def _updatePredictionsRectangle(self, values):
        canvas = self._predictionsRectangle
        if not canvas:
            return

        upper_x = 10
        upper_y = 10
        lower_x = 380
        lower_y = 160

        assert isinstance(values, list) and len(values) > 0
        for v in values:
            assert 0. <= v <= 100.
        values.sort()
        width = (lower_x - upper_x) / len(values)
        assert width > 0
        height = lower_y - upper_y
        assert height > 0
        x, y = upper_x, upper_y
        for v in values:
            y = height * (100 - v) / 100
            canvas.create_rectangle(x, upper_y, x + width, upper_y + y,
                                    outline="black", fill="green", width=2)
            canvas.create_rectangle(x, upper_y + y, x + width, upper_y + height,
                                    outline="black", fill="red", width=2)
            x += width

        x0, y0 = upper_x, lower_y + 15
        x1, y1 = x, lower_y + 45
        green = 100 * len(values) - sum( 100 - z for z in values)

        x = green * (x1 -x0) / 100 + x0

        canvas.create_rectangle(x0, y0, x, y1,
                                outline="black", fill="green", width=2)

        canvas.create_rectangle(x, y0, x1, y1,
                            outline="black", fill="red", width=2)

    def _updatePredictionsBar(self, values):
        canvas = self._predictionsRectangle
        if not canvas:
            return

        upper_x = 10
        upper_y = 10
        lower_x = 200
        lower_y = 200

        assert isinstance(values, list) and len(values) > 0
        for v in values:
            assert 0. <= v <= 100.

        red_area = sum(values)
        green_area = 100 * len(values) - sum(values)

        L = green_area / red_area

        y1 = (L * lower_y + upper_y) / (1 - L)

        width = 10
        height = lower_y - upper_y
        x, y = upper_x, upper_y
        v = red_area
        y = height * (100 - v) / 100
        canvas.create_rectangle(x, upper_y, x + width, upper_y + y1,
                                outline="black", fill="green", width=2)
        canvas.create_rectangle(x, upper_y + y, lower_x, upper_y + y1,
                                outline="black", fill="red", width=2)

    def setNiftiFile(self, filename):
        self._root.title(f"Current Nifti file: {filename}")
        self._scan = nifti_mri.Scan(filename)
        self.updateImages()
        self.updateTop()

    def updateImages(self):
        self._imgs_cache = []
        filenames = saveSlicesToDisk(self._scan)
        for k, filename in filenames.items():
            img = ImageTk.PhotoImage(PIL.Image.open(filename))
            x, y = 0, 90
            canvas = self._slice_canvas[k]
            canvas.create_image(x, y, anchor=W, image=img)
            # x += self.img_canvas_width / n
            self._imgs_cache.append(img)

    def buildMenu(self, menu):
        menubar = tk.Menu(self._root)
        for main_option, sub_options in menu.items():
            menu = tk.Menu(menubar, tearoff=0)
            for option, event_name in sub_options:
                if option == SEPARATOR:
                    menu.add_separator()
                else:
                    callback = functools.partial(
                        self.processEvent, event_name)
                    menu.add_command(label=option, command=callback)
            menubar.add_cascade(label=main_option, menu=menu)
        return menubar

    def changeAxis(self, axis_mapping):
        if not self._scan:
            return
        self._scan.setAxisMapping(axis_mapping)
        self.updateImages()

    def changeOrienation(self, axis):
        if not self._scan:
            return
        self._scan.changeOrienation(axis)
        self.updateImages()

    def _updateTreeViewWithPrediction(self, model_id, prediction):
        percent = int(prediction * 100)
        prediction = f"To become Sick: {percent}%"
        self._treeview.set(model_id, column="Prediction", value=prediction)

    def updateTop(self):
        # Add the buttons to change the Axes.
        left_canvas = Canvas(self._top, bg="red")
        self._predictionsRectangle = Canvas(self._top, bg="black")
        right_canvas = Canvas(self._top, bg="white")

        left_canvas.grid(row=0, column=0)
        self._predictionsRectangle.grid(row=0, column=1)
        right_canvas.grid(row=0, column=2)

        # All all the available models in the right canvas.
        all_slices = ['01', '02', '03', '11', '12', '13', '21', '22', '23']
        columns = all_slices + ['accuracy', 'F1', "Prediction"]

        self._treeview = ttk.Treeview(left_canvas, columns=columns,
                                      show='headings')
        self._treeview.pack()

        for s in all_slices:
            self._treeview.column(s, minwidth=0, width=30, stretch=NO)

        self._treeview.column('accuracy', minwidth=0, width=40, stretch=NO)
        self._treeview.column('F1', minwidth=0, width=40, stretch=NO)
        self._treeview.column('Prediction', minwidth=0, width=300, stretch=NO)

        # Treeview headings
        for s in all_slices:
            self._treeview.heading(s, text=s)

        self._treeview.heading('accuracy', text="Acc.")
        self._treeview.heading('F1', text="F1")
        self._treeview.heading('Prediction', text="Prediction")

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
            prediction = 'n/a'

            self._treeview.insert(
                parent="",
                index="end",
                iid=iid,
                values=slices + [accuracy, f1, prediction]
            )

        # Place the tranformation buttons
        buttons = []
        for axis in utils.getAxesOrientation():
            callback = functools.partial(self.changeAxis, axis)
            button = Button(right_canvas, text=axis, command=callback)
            buttons.append(button)

        column = 0
        for b in buttons:
            b.grid(row=0, column=column, pady=8)
            column += 1

        # Add the buttons to rotate the slices if needed.
        for axis in [0, 1, 2]:
            callback = functools.partial(self.changeOrienation, axis)
            button = Button(right_canvas, text="R", command=callback)
            button.grid(row=0, column=column, pady=8)
            column += 1

    def updateBottom(self):
        self._slice_canvas = {}
        for row in (0, 1, 2):
            for col in (0, 1, 2):
                c = Canvas(self._bottom, bg=settings.RIGHT_BACKGROUND_COLOR)
                c.grid(row=row, column=col, pady=(10, 10), padx=(10, 10))
                self._slice_canvas[(row, col)] = c

    def main(self, title="n/a", width=1600, height=800, upperX=200,
             upperY=100, zoomed=False, filename=None):
        self._root = tk.Tk()
        self._root.title(title)

        self._top = Canvas(self._root, bg="white", highlightthickness=0,
                           height=60)
        self._bottom = Canvas(self._root, bg="black", highlightthickness=0)

        self._top.pack(fill=BOTH, side=TOP, pady=10, padx=10)
        self._bottom.pack(fill=BOTH, side=TOP, pady=10, padx=10)

        # Add the menu.
        self._root.config(menu=self.buildMenu(MENU))

        # Paint the details of the canvases.
        self.updateTop()
        self.updateBottom()

        # If a file was passed in open it..
        if filename:
            self.setNiftiFile(filename)

        # Start the loop.
        self._root.mainloop()


if __name__ == '__main__':
    dbname = utils.getDabaseName()
    dbutil.SimpleSQL.setDatabaseName(dbname)
    mf = MainFrame()
    filename = None if len(sys.argv) <= 1 else sys.argv[1]
    mf.main("View NIFTI File", filename=filename)
