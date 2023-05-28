import functools
import os
import pathlib

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import cogni_scan.src.utils as cs

HOME_DIR = pathlib.Path.home()
OASIS3_ROOT = os.path.join(HOME_DIR, "oasis3-scans")


def discover_all_image_files(directory=None):
    """Discovers all the nifti files under the passed in directory.

    :param str directory: The directory to look up for nifti files.

    :returns: A list of all the nifti files found in the passed in directory.
    :rtype: list
    """
    if directory is None:
        directory = OASIS3_ROOT
    files = []
    for file in os.listdir(directory):
        fullpath = os.path.join(directory, file).strip()
        if os.path.isfile(fullpath):
            if fullpath.endswith("nii.gz"):
                files.append(fullpath)
        else:
            if fullpath:
                files.extend(discover_all_image_files(fullpath))
    return files

def discoverScans():
    return discover_all_image_files()




def make_menu_bar(root):
    def donothing():
        print("nothing")

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Filter Subjects", command=donothing)
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
    for patient in discoverScans():
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
        self.__scan_data = None
        self.__size_scale = None

    def clear(self):
        """Clears the frame from all widgets."""
        for widget in self.__parent_frame.winfo_children():
            widget.destroy()

    def remove_images(self):
        """Removes only the images from the frame.

        Will be used when the frame will be re-painted as the response
        to the user re-sizing the image size.
        """
        for widget in self.__parent_frame.winfo_children():
            if type(widget) is ttk.Scale:
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
        """Refreshes the scan images.

        Called either the first time that the right pane is update when
        the user selects a new scan from the tree view or when the user
        changes the image size using the scaler.
        """
        print(fullpath) 
        self.__scan_data = cs.loadMRI(fullpath) 
        self.remove_images()
        fig, axs = plt.subplots(1, 3, figsize=(85, 85))
        dfc1 = 0.5
        for index, axis in enumerate([0, 1, 2]):
            img = self.__scan_data.get_slice(axis=axis)
            axs[index].imshow(img)
            axs[index].set_title(f"slice: {-1 * dfc1} ")
        fig.subplots_adjust(hspace=1.2)
        canvas = FigureCanvasTkAgg(fig, master=self.__parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


def main():
    """Creates the whole application front end and starts the infinite loop."""
    root = tk.Tk()
    root.title("NIfTI File Viewer ")
    window_label = ttk.Label(root, text="Separating widget")
    window_label.pack()

    panedwindow = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)

    left_frame = ttk.Frame(panedwindow, width=100, height=300, relief=tk.SUNKEN)
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
    main()
