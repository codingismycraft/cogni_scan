import functools
import os
import tempfile

from PIL import ImageTk
import PIL.Image

from tkinter import *
from tkinter.constants import *

import cv2
import tkinter as tk
import tkinter.ttk as ttk

import cogni_scan.src.utils as cs
import cogni_scan.front_end.cfc.view as view
import cogni_scan.front_end.settings as settings



class RightView(view.View):

    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame

    def eventHandler(self, item_selected):
        print("here", item_selected)

    def remove_images(self):
        """Removes only the images from the frame.

        Will be used when the frame will be re-painted as the response
        to the user re-sizing the image size.
        """
        for widget in self.__parent_frame.winfo_children():
            if isinstance(widget, ttk.Scale):
                continue
            widget.destroy()

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.remove_images()
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        # Add the canvas where the slices are drawn.
        self.imgs = []
        self.img_canvas_width = 1250
        self.img_canvas_height = 400

        canvases = []
        for i in range(3):
            if i == 0:
                color = "red"
            if i ==1:
                color = "green"
            if i == 2:
                color = "blue"

            c = Canvas(
                self.__parent_frame,
                width=self.img_canvas_width,
                height=self.img_canvas_height,
                bg=settings.RIGHT_BACKGROUND_COLOR,
                highlightthickness = 0
            )
            canvases.append(c)

        for i, c in enumerate(canvases):
            c.grid(row=i, column=0)


        index = 0
        for canvas in canvases:
            self.update_scan(mri, canvas, index)
            index += 1

        #tk.Misc.lift(canvas)

    def update_scan(self, mri,canvas, index):
        imgs = [
            ImageTk.PhotoImage(PIL.Image.open(file))
            for file in self.saveSlicesToDisk(mri, index)
        ]
        x, y = 0, 230
        n = len(imgs)
        for img in imgs:
            canvas.create_image(x, y, anchor=W, image=img)
            x += self.img_canvas_width / n
        self.imgs.extend(imgs)

    def saveSlicesToDisk(self, scan, index):
        """Saves the slices for the passed in scan to disk."""
        doc = self.getDocument()
        base_dir = tempfile.gettempdir()
        filenames = []

        distances = doc.getSliceDistances()

        if index == 0:
            distances = doc.getSliceDistances()
            distances = [-x for x in distances]
        elif index == 1:
            distances = 0, 0, 0
        elif index == 2:
            distances = doc.getSliceDistances()
            distances = [x for x in distances]


        for axis in [0, 1, 2]:
            filename = f"slice_{axis}_{index}.jpg"
            filename = os.path.join(base_dir, filename)
            filenames.append(filename)
            img = scan.get_slice(
                distance_from_center=distances[axis],
                axis=axis,
                bounding_square=doc.getSliceSquareLength(),
            )
            cv2.imwrite(filename, img)
        return filenames



if __name__ == '__main__':
    v = RightView(None)
