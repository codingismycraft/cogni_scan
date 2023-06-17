import functools

from PIL import ImageTk
import PIL.Image

from tkinter import *
from tkinter.constants import *

import cv2
import tkinter as tk
import tkinter.ttk as ttk

import cogni_scan.src.utils as cs
import cogni_scan.front_end.cfc.view as view


def saveSlicesToDisk(scan_data):
    filenames = []
    for axis in [0, 1, 2]:
        filename = f"slice_{axis}.jpg"
        filenames.append(filename)
        img = scan_data.get_slice(axis=axis)
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

        def updateSaveButtonState():
            self.getDocument().updateAllViews(self)
            if not self._save_button:
                return
            if mri and mri.isDirty():
                self._save_button["state"] = "normal"
            else:
                self._save_button["state"] = "disabled"

        # Add the save button.
        button_canvas = Canvas(
            self.__parent_frame,
            width=600,
            height=60,
            bg='orange')
        button_canvas.pack(fill=BOTH, expand=False, side=TOP)
        button_canvas.place(x=20, y=3)

        def saveChanges():
            self.getDocument().checkToSave()
            updateSaveButtonState()

        self._save_button = Button(
            button_canvas,
            text="Save",
            command=saveChanges)
        self._save_button.pack(pady=20, side=LEFT)

        # Add the buttons to change the axis orienation.
        canvas = Canvas(self.__parent_frame, width=600, height=60, bg='bisque')
        canvas.pack(fill=BOTH, expand=False, side=TOP)
        canvas.place(x=20, y=60)

        def changeAxis(axis_mapping):
            assert mri
            mri.setAxisMapping(axis_mapping)
            self.update_scan(mri)
            updateSaveButtonState()

        for axis in cs.getAxesOrientation():
            callback = functools.partial(changeAxis, axis)
            button = Button(canvas, text=axis, command=callback)
            button.pack(pady=20, side=LEFT)

        # Add the buttons to rotate the slices if needed.
        canvas1 = Canvas(self.__parent_frame, width=600, height=60, bg='green')
        canvas1.pack(fill=BOTH, expand=False, side=TOP)
        canvas1.place(x=20, y=130)

        def changeOrienation(axis):
            assert mri
            mri.changeOrienation(axis)
            self.update_scan(mri)
            updateSaveButtonState()

        for axis in [0, 1, 2]:
            callback = functools.partial(changeOrienation, axis)
            button = Button(canvas1, text="R", command=callback)
            button.pack(pady=20, side=LEFT)

        # Add the descriptive data
        text = Label(self.__parent_frame, text=mri.getHealthStatus())
        text.place(x=20, y=200)

        # Add the canvas where the slices are drawn.
        self.img_canvas_width = 800
        self.img_canvas_height = 400

        self._image_canvas = Canvas(
            self.__parent_frame,
            width=self.img_canvas_width,
            height=self.img_canvas_height,
            bg='blue'
        )

        self._image_canvas.pack(fill=BOTH, expand=YES, side=BOTTOM)
        self._image_canvas.place(x=20, y=290)

        tk.Misc.lift(canvas)
        self.update_scan(mri)
        updateSaveButtonState()

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
