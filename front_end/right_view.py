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


def saveSlicesToDisk(scan):
    """Saves the slices for the passed in scan to disk."""
    base_dir = tempfile.gettempdir()
    filenames = []
    for axis in [0, 1, 2]:
        filename = f"slice_{axis}.jpg"
        filename = os.path.join(base_dir, filename)
        filenames.append(filename)
        img = scan.get_slice(axis=axis)
        cv2.imwrite(filename, img)
    return filenames

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
        self.img_canvas_width = 800
        self.img_canvas_height = 400

        self._image_canvas = Canvas(
            self.__parent_frame,
            width=self.img_canvas_width,
            height=self.img_canvas_height,
            bg=settings.RIGHT_BACKGROUND_COLOR
        )
        self._image_canvas.pack(fill=BOTH, expand=YES, side=BOTTOM)
        self._image_canvas.place(x=20, y=20)
        #tk.Misc.lift(canvas)
        self.update_scan(mri)

    def update_scan(self, mri):
        self.imgs = [
            ImageTk.PhotoImage(PIL.Image.open(file))
            for file in saveSlicesToDisk(mri)
        ]

        x, y = 0, 130
        n = len(self.imgs)
        for img in self.imgs:
            self._image_canvas.create_image(x, y, anchor=W, image=img)
            x += self.img_canvas_width / n


if __name__ == '__main__':
    v = RightView(None)
