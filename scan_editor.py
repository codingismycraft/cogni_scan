import functools
import os
import pathlib
import datetime

from PIL import ImageTk
import PIL.Image
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog
from tkinter import *
from tkinter.constants import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cv2

import cogni_scan.src.nifti_mri as nifti_mri
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import cogni_scan.src.utils as cs
import cogni_scan.oasis_2_mri as oasis_2_mri

HOME_DIR = pathlib.Path.home()
OASIS3_ROOT = os.path.join(HOME_DIR, "oasis3-scans")


def saveSlicesToDisk(scan_data):
    filenames = []
    for axis in [0, 1, 2]:
        filename = f"slice_{axis}.jpg"
        filenames.append(filename)
        img = scan_data.get_slice(axis=axis)
        cv2.imwrite(filename, img)
    return filenames


def skip_marked_as_skipped():
    global MRIS
    MRIS = nifti_mri.load_from_db(skip=True)
    main()

def make_menu_bar(root):
    def donothing():
        print("nothing")

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Skip Marked as skipped", command=skip_marked_as_skipped)
    menubar.add_cascade(label="Options", menu=helpmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)

    return menubar


def make_subject_tree(parent):
    """Creates and returns a Tree that is populated with the subject's data.

    :param parent: The frame (paned window) where the tree will be placed to.

    :returns: The tree view widget that is created here.
    """
    tree = ttk.Treeview(parent)
    tree.heading('#0', text='Subject ID', anchor=tk.W)
    for patient in MRIS:
        label = patient
        caption = patient
        tree.insert('', tk.END, text=caption, iid=patient, open=False)
    return tree


def tree_item_selected(tree_view_ctrl, right_view, window_label, event):
    """Called whenever the user clicks on an itme in the tree view.

    :param tree_view_ctrl: The tree view object that triggered the event.
    :param right_view: The right pane view.
    :param event: The virtual event (unused).
    """
    path = tree_view_ctrl.selection()[0]
    right_view.select_scan(path)
    window_label.config(text=path)


class RightPaneView:
    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame
        self._scan_data = None
        self.__size_scale = None
        self._image_canvas = None

    def clear(self):
        """Clears the frame from all widgets."""
        for widget in self.__parent_frame.winfo_children():
            widget.destroy()
        self._image_canvas = None

    def remove_images(self):
        """Removes only the images from the frame.

        Will be used when the frame will be re-painted as the response
        to the user re-sizing the image size.
        """
        for widget in self.__parent_frame.winfo_children():
            if isinstance(widget, ttk.Scale):
                continue
            widget.destroy()

    def select_scan(self, full_path):
        """Binds the view to the passed in scan.

        :param full_path: The path to the scan file.
        """
        self.refresh_images(full_path)

    def resize_event_callback(self, event):
        """Event handler to resize the scan images."""
        s = int(self.__size_scale.get())
        self.refresh_images(image_size=(s, s))

    def add_scale(self):
        """Adds the scale control for the size of the image."""
        self.__size_scale = ttk.Scale(
            self.__parent_frame,
            from_=64,
            to=512,
            orient=tk.HORIZONTAL
        )
        self.__size_scale.set(199)
        self.__size_scale.bind("<ButtonRelease-1>", self.resize_event_callback)
        self.__size_scale.pack()

    def refresh_images(self, fullpath):
        """Refreshes the scan images."""
        print(fullpath)
        # Load the Mri object if needed.
        if not self._scan_data or self._scan_data.getFilePath() != fullpath:
            self._scan_data = MRIS[fullpath]
        self._save_button = None

        # Clean up existing images.
        self.remove_images()

        def updateSaveButtonState():
            if not self._save_button:
                return
            if self._scan_data and self._scan_data.isDirty():
                self._save_button["state"] = "normal"
            else:
                self._save_button["state"] = "disabled"

        # Add the save button.
        button_canvas = Canvas(self.__parent_frame, width=600, height=60,
                               bg='orange')
        button_canvas.pack(fill=BOTH, expand=False, side=TOP)
        button_canvas.place(x=20, y=3)

        def saveChanges():
            if self._scan_data:
                self._scan_data.saveToDb()
            updateSaveButtonState()

        self._save_button = Button(button_canvas, text="Save",
                                   command=saveChanges)
        self._save_button.pack(pady=20, side=LEFT)

        # Add the buttons to change the axis orienation.
        canvas = Canvas(self.__parent_frame, width=600, height=60, bg='bisque')
        canvas.pack(fill=BOTH, expand=False, side=TOP)
        canvas.place(x=20, y=60)

        def changeAxis(axis_mapping):
            assert self._scan_data
            self._scan_data.setAxisMapping(axis_mapping)
            self.update_scan()
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
            assert self._scan_data
            self._scan_data.changeOrienation(axis)
            self.update_scan()
            updateSaveButtonState()

        for axis in [0, 1, 2]:
            callback = functools.partial(changeOrienation, axis)
            button = Button(canvas1, text="R", command=callback)
            button.pack(pady=20, side=LEFT)

        # Add the descriptive data
        text = Label(self.__parent_frame, text=self._scan_data.getHealthStatus())
        text.place(x=20, y=200);


        # Add the canvas where the slices are drawn.
        self.img_canvas_width = 800
        self.img_canvas_height = 600

        self._image_canvas = Canvas(
            self.__parent_frame,
            width=self.img_canvas_width,
            height=self.img_canvas_height,
            bg='blue'
        )

        self._image_canvas.pack(fill=BOTH, expand=YES, side=BOTTOM)
        self._image_canvas.place(x=20, y=290)

        tk.Misc.lift(canvas)
        self.update_scan()
        updateSaveButtonState()



    def update_scan(self):
        self.imgs = [
            ImageTk.PhotoImage(PIL.Image.open(file))
            for file in saveSlicesToDisk(self._scan_data)
        ]

        x, y = 0, 130
        n = len(self.imgs)

        for img in self.imgs:
            self._image_canvas.create_image(x, y, anchor=W, image=img)
            x += self.img_canvas_width / n


def main():
    """Creates the whole application front end and starts the infinite loop."""
    root = tk.Tk()
    root.title("NIfTI File Viewer ")
    window_label = ttk.Label(root, text="Separating widget")
    window_label.pack()

    panedwindow = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)

    left_frame = ttk.Frame(
        panedwindow,
        width=100,
        height=300,
        relief=tk.SUNKEN)
    right_frame = ttk.Frame(panedwindow, width=400, height=400,
                            relief=tk.SUNKEN)

    panedwindow.add(left_frame, weight=4)
    panedwindow.add(right_frame, weight=4)

    subject_tree = make_subject_tree(left_frame)
    right_view = RightPaneView(right_frame)

    callback = functools.partial(tree_item_selected, subject_tree, right_view,
                                 window_label)
    subject_tree.bind('<<TreeviewSelect>>', callback)
    subject_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    root.config(menu=make_menu_bar(root))
    root.attributes('-zoomed', True)
    left_frame.config(width=50)
    root.mainloop()


if __name__ == '__main__':
    MRIS = nifti_mri.load_from_db()
    main()
