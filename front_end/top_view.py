from tkinter import *
from tkinter.constants import *

import tkinter as tk
import tkinter.ttk as ttk

import cogni_scan.front_end.cfc.view as view

class TopView(view.View):

    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame

    def clear(self):
        """Removes only the images from the frame.

        Will be used when the frame will be re-painted as the response
        to the user re-sizing the image size.
        """

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        mri = self.getDocument().getActiveMri()
        if not mri:
            return
        l1 = tk.Label(self.__parent_frame, text="Full Path")
        l2 = tk.Label(self.__parent_frame,  text="Days since first visit")

        eText = StringVar()
        eText.set(mri.getFilePath())
        e1 = tk.Entry(self.__parent_frame, state="readonly",textvariable=eText, width=120)

        eText2 = StringVar()
        eText2.set(f"{mri.getDays()}")
        e2 = tk.Entry(self.__parent_frame, state="readonly",textvariable=eText2, width=5)

        l1.grid(row=0, column=0,sticky=W, padx=8)
        l2.grid(row=1, column=0,sticky=W, padx=8)
        e1.grid(row=0, column=1,sticky=W, padx=8)
        e2.grid(row=1, column=1,sticky=W, padx=8)


if __name__ == '__main__':
    v = TopView(None)
