import functools
import os

from tkinter import *
import tkinter as tk
import tkinter.simpledialog
import tkinter.ttk as ttk

import cogni_scan.front_end.cfc.view as view
import cogni_scan.front_end.left_view as left_view
import cogni_scan.front_end.mri_doc as model
import cogni_scan.front_end.right_view as right_view
import cogni_scan.front_end.settings as settings
import cogni_scan.front_end.top_view as top_view

EVENT_EXIT = "EXIT"
EVENT_FILTER = "FILTER"
SEPARATOR = "Separator"
EVENT_ABOUT = "About"

MENU = {
    "File": [
        ("Exit", EVENT_EXIT),
    ],
    "Options": [
        ("Filter", EVENT_FILTER),
        (SEPARATOR, None),
        ("Filter", EVENT_FILTER),
    ],
    "Help": [
        ("Filter", EVENT_FILTER),
        (SEPARATOR, None),
        ("About", EVENT_ABOUT),
    ]
}

TopView = top_view.TopView
LeftView = left_view.LeftView
RightView = right_view.RightView
MRIDocument = model.MRIDocument

class MyDialog(tkinter.simpledialog.Dialog):

    def body(self, master):
        tk.Label(master, text="First:").grid(row=0)
        tk.Label(master, text="Second:").grid(row=1)
        self.checkbutton_value = tk.BooleanVar(value=False)

        self.b1 = tk.Checkbutton(master, text='Hide Skiped',
                                 variable=self.checkbutton_value)
        self.b1.grid(row=2)
        # b1.pack()

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

        return self.e1  # initial focus

    def apply(self):
        first = self.e1.get()
        second = self.e2.get()
        y = self.checkbutton_value.get()
        print(first, second, y)

class AboutDialog(tkinter.simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Cogni Scan Editor").grid(row=0)


class MainFrame(view.View):
    _root = None
    _views = None
    _document = None

    def processEvent(self, event, data=None):
        if event == EVENT_EXIT:
            self._root.quit()
            self._root = None
        elif event == EVENT_FILTER:
            d = MyDialog(self._root)
        elif event == EVENT_ABOUT:
            d = AboutDialog(self._root)

    def update(self):
        active_path = "No selection."
        mri = self.getDocument().getActiveMri()
        if mri:
            active_path = mri.getFilePath()
        self._caption.set(active_path)

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

    def main(self, title="n/a", menu=None, width=1600, height=800, upperX=200,
             upperY=100, zoomed=False):
        self._document = MRIDocument()
        self._root = tk.Tk()
        self._root.title(title)

        self._caption = StringVar()
        self._caption.set("New Text!")
        window_label = tk.Label(self._root, textvariable=self._caption)
        window_label.pack()

        # Color Styles..
        self.s = ttk.Style()
        self.s.configure('TFrame', background=settings.LEFT_BACKGROUND_COLOR)

        self.s1 = ttk.Style()
        self.s1.configure('right.TFrame', background=settings.RIGHT_BACKGROUND_COLOR)

        self.s1 = ttk.Style()
        self.s1.configure('bottom.TFrame', background='#AAC5CD')

        self.s1 = ttk.Style()
        self.s1.configure('bottom.TFrame', background='#AAC5CD')

        self.s1 = ttk.Style()
        self.s1.configure('top.TFrame', background=settings.TOP_BACKGROUND_COLOR)

        # Adds the meny if needed.
        if menu:
            self._root.config(menu=self.buildMenu(menu))

        # Sizes and places the main window.
        if zoomed:
            self._root.attributes('-zoomed', True)
        else:
            self._root.geometry(f"{width}x{height}+{upperX}+{upperY}")

        # Adds the top frame.
        panedwindow1 = ttk.Panedwindow(self._root, orient=tk.VERTICAL)
        panedwindow1.pack(fill=tk.BOTH, expand=False)
        top_frame = ttk.Frame(
            panedwindow1,
            height=200,
            relief=tk.SUNKEN,
            style='top.TFrame',
        )

        panedwindow1.add(top_frame)
        panedwindow = ttk.Panedwindow(self._root, orient=tk.HORIZONTAL)
        panedwindow.pack(fill=tk.BOTH, expand=True)

        # Adds the left frame.
        left_frame = ttk.Frame(
            panedwindow,
            width=100,
            height=300,
            relief=tk.SUNKEN,
            style='TFrame'
        )
        panedwindow.add(left_frame)

        # Adds the right frame.
        right_frame = ttk.Frame(
            panedwindow,
            width=1230,
            height=520,
            relief=tk.SUNKEN,
            style='right.TFrame',
        )

        panedwindow.add(right_frame)

        # Adds the views...

        # Add the top view.
        top = TopView(top_frame)
        self._document.addView(top)

        # Add the left view.
        subject_view = LeftView(left_frame)
        subject_view.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self._document.addView(subject_view)

        # Add the right view.
        right_view = RightView(right_frame)
        self._document.addView(right_view)

        # Self is also a view so lets add it to the document.
        self._document.addView(self)

        # Load the document and start the loop.
        self._document.load()
        self._root.mainloop()


if __name__ == '__main__':
    mf = MainFrame()
    mf.main(settings.APP_NAME, MENU)
