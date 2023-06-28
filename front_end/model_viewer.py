"""A UI application to show available models."""

import functools
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import RocCurveDisplay
from tkinter import *
from tkinter.messagebox import askyesno
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import tkinter.simpledialog
import tkinter.ttk as ttk

import cogni_scan.front_end.settings as settings
import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.modeler.model as model


class ModelViewer:

    def plotTrainingHistory(self, history, image_holder):
        """Plots the passed in model training history object.

        :param history: Holds the model's training history.
        """
        fig, ax1 = plt.subplots()
        min_value, max_value = 1000, 0
        for key in history.keys():
            ax1.plot(history[key], label=key)
            min_value = min(min_value, min(history[key]))
            max_value = max(max_value, max(history[key]))

        plt.ylim([0, max_value])
        plt.xlabel('Epoch')
        plt.ylabel('Error')
        plt.legend()
        plt.grid(True)
        canvas = FigureCanvasTkAgg(fig, master=image_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH,
                                    expand=1)

    def callback(self, event):
        for widget in self._right_frame.winfo_children():
            widget.destroy()
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            model_id = event.widget.get(index)
            active_model = self._model_map[model_id]

            # Add labels.
            labels_holder = Canvas(
                self._right_frame,
                bg=settings.LABEL_BACKGROUND_COLOR,
                height=50,
                highlightthickness=0,
            )

            labels_holder.grid(row=0, column=0, sticky=W)

            labels = []
            values = []

            labels.append(
                tk.Label(
                    labels_holder, text="Accuracy",
                    bg=settings.LABEL_BACKGROUND_COLOR,
                    fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10)
            )

            txt = f"{active_model.getAccuracyScore():0.02}"
            values.append(
                tk.Label(labels_holder, text=txt,
                         bg=settings.LABEL_BACKGROUND_COLOR,
                         fg=settings.VALUE_FRONT_COLOR,
                         font=('Helvetica', 12, 'bold'))
            )

            labels.append(
                tk.Label(
                    labels_holder, text="F1",
                    bg=settings.LABEL_BACKGROUND_COLOR,
                    fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10)
            )

            txt = f"{active_model.getF1():0.02}"
            values.append(
                tk.Label(labels_holder, text=txt,
                         bg=settings.LABEL_BACKGROUND_COLOR,
                         fg=settings.VALUE_FRONT_COLOR,
                         font=('Helvetica', 12, 'bold'))
            )

            slices = '-'.join(active_model.getSlices())

            labels.append(
                tk.Label(
                    labels_holder, text="Slices",
                    bg=settings.LABEL_BACKGROUND_COLOR,
                    fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10)
            )

            values.append(
                tk.Label(labels_holder, text=slices,
                         bg=settings.LABEL_BACKGROUND_COLOR,
                         fg=settings.VALUE_FRONT_COLOR,
                         font=('Helvetica', 12, 'bold'))
            )

            column = 0
            for label, value in zip(labels, values):
                label.grid(row=0, column=column, sticky=W)
                column += 1
                value.grid(row=0, column=column, sticky=W)
                column += 1

            # Add images.
            image_holder = Canvas(self._right_frame,
                                  bg=settings.TOP_BACKGROUND_COLOR,
                                  highlightthickness=0)
            image_holder.grid(row=1, column=0)

            # Adds the confusion Matrix.
            cm = active_model.getConfusionMatrix()
            fig = ConfusionMatrixDisplay(cm).plot()

            canvas = FigureCanvasTkAgg(fig.figure_, master=image_holder)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tkinter.LEFT)

            # Adds the ROC Curve.
            fpr, tpr = active_model.getROCCurve()
            roc_display = RocCurveDisplay(fpr=fpr, tpr=tpr).plot()

            canvas_1 = FigureCanvasTkAgg(roc_display.figure_,
                                         master=image_holder)
            canvas_1.draw()
            canvas_1.get_tk_widget().pack(side=tkinter.LEFT)

            self.plotTrainingHistory(active_model.getTrainingHistory(), image_holder)

    def main(self, title="n/a", menu=None, width=1710, height=940, upperX=200,
             upperY=100, zoomed=False):
        self._root = tk.Tk()
        self._root.title("Create New Model")

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
        all_models = model.getModels()
        for index, m in enumerate(all_models):
            Lb1.insert(index + 0, m.getModelID())

        self._model_map = {m.getModelID(): m for m in all_models}

        Lb1.pack(fill=tk.BOTH, expand=True)
        Lb1.bind("<<ListboxSelect>>", self.callback)

        # Add the right view.
        self._root.geometry(f"{width}x{height}+{upperX}+{upperY}")

        self._root.mainloop()


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("dummyscans")
    mc = ModelViewer()
    mc.main()
