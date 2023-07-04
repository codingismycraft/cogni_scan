import functools
import os
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

import cogni_scan.front_end.settings as settings
import cogni_scan.src.nifti_mri as nifti_mri
import cogni_scan.src.utils as utils

EVENT_EXIT = "EXIT"
OPEN_FILE = "OPEN_FILE"
SEPARATOR = "Separator"

MENU = {
    "File": [
        ("Open", OPEN_FILE),
        (SEPARATOR, None),
        ("Exit", EVENT_EXIT),
    ],
}

JUNK_PATH = "/home/john/ADNI/ADNI/003_S_1074/Total_Intracranial_Volume_Brain_Mask/2006-12-04_12_29_02.0/I345144/ADNI_003_S_1074_MR_Total_Intracranial_Volume_Brain_Mask_Br_20121107220305810_S23534_I345144.nii"


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

    def processEvent(self, event, data=None):
        if event == EVENT_EXIT:
            self._root.quit()
            self._root = None
        elif event == OPEN_FILE:
            filename = fd.askopenfilename(initialdir="/home/john/junk/ADNI")
            self.setNiftiFile(filename)

    def setNiftiFile(self, filename):
        self._scan = nifti_mri.Scan(filename)
        self.updateImages()

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
        if not self._scan :
            return
        self._scan.setAxisMapping(axis_mapping)
        self.updateImages()

    def changeOrienation(self, axis):
        if not self._scan :
            return
        self._scan.changeOrienation(axis)
        self.updateImages()

    def updateTop(self):
        # Add the buttons to change the Axes.
        buttons = []
        for axis in utils.getAxesOrientation():
            callback = functools.partial(self.changeAxis, axis)
            button = Button(self._top, text=axis, command=callback)
            buttons.append(button)

        column = 0
        for b in buttons:
            b.grid(row=0, column=column, pady=8)
            column += 1

        # Add the buttons to rotate the slices if needed.
        for axis in [0, 1, 2]:
            callback = functools.partial(self.changeOrienation, axis)
            button = Button(self._top, text="R", command=callback)
            button.grid(row=0, column=column, pady=8)
            column += 1

    def updateBottom(self):
        self._slice_canvas = {}
        for row in (0, 1, 2):
            for col in (0, 1, 2):
                c = Canvas(self._bottom, bg="blue")
                c.grid(row=row, column=col, pady=(10, 10), padx=(10, 10))
                self._slice_canvas[(row, col)] = c

    def main(self, title="n/a", width=1600, height=800, upperX=200,
             upperY=100, zoomed=False):
        self._root = tk.Tk()
        self._root.title(title)

        self._top = Canvas(self._root, bg="red", highlightthickness=0,
                           height=60)
        self._bottom = Canvas(self._root, bg="green", highlightthickness=0)

        self._top.pack(fill=BOTH, side=TOP, pady=10, padx=10)
        self._bottom.pack(fill=BOTH, side=TOP, pady=10, padx=10)

        # Add the menu.
        self._root.config(menu=self.buildMenu(MENU))

        # Paint the details of the canvases.
        self.updateTop()
        self.updateBottom()

        # Start the loop.
        self._root.mainloop()


if __name__ == '__main__':
    mf = MainFrame()
    mf.main("View NIFTI File")
