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

    def plotTrainingHistory(self, active_model, image_holder, row, column):
        """Plots the passed in model training history object.

        :param history: Holds the model's training history.
        """
        parent_canvas = Canvas(image_holder,
                               bg=settings.TOP_BACKGROUND_COLOR,
                               width=200,
                               highlightthickness=0)
        parent_canvas.grid(row=row, column=column)

        history = active_model.getTrainingHistory()
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
        canvas = FigureCanvasTkAgg(fig, master=parent_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH,
                                    expand=1)

    def plotConfusionMatrix(self, active_model, parent, row, column):
        """Plots the confusion matrix"""
        parent_canvas = Canvas(parent,
                               bg=settings.TOP_BACKGROUND_COLOR,
                               width=200,
                               highlightthickness=0)
        parent_canvas.grid(row=row, column=column)

        cm = active_model.getConfusionMatrix()
        fig = ConfusionMatrixDisplay(cm).plot()
        canvas = FigureCanvasTkAgg(fig.figure_, master=parent_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.LEFT)

    def plotROCCurve(self, active_model, parent, row, column):
        parent_canvas = Canvas(parent,
                               width=200,
                               bg=settings.TOP_BACKGROUND_COLOR,
                               highlightthickness=0)
        parent_canvas.grid(row=row, column=column)
        # Adds the ROC Curve.
        fpr, tpr = active_model.getROCCurve()
        roc_display = RocCurveDisplay(fpr=fpr, tpr=tpr).plot()

        canvas_1 = FigureCanvasTkAgg(roc_display.figure_,
                                     master=parent_canvas)
        canvas_1.draw()
        canvas_1.get_tk_widget().pack(side=tkinter.LEFT)

    def callback(self, event):
        for widget in self._right_frame.winfo_children():
            widget.destroy()
        model_id = event.widget.focus()
        if model_id:
            # Add labels.
            active_model = self._model_map[model_id]
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

            row, column = 0, 0

            self.plotConfusionMatrix(active_model, image_holder, row, column)
            column += 1

            self.plotROCCurve(active_model, image_holder, row, column)

            row += 1
            column = 0

            self.plotTrainingHistory(active_model, image_holder, row, column)
            column += 1

    def main(self, title="n/a", menu=None, width=1810, height=1040, upperX=200,
             upperY=100, zoomed=False):
        self._root = tk.Tk()
        self._root.title("Model Viewer (all available models).")

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

        self.scrollbar = ttk.Scrollbar(self._left_frame)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self._treeview = ttk.Treeview(
            self._left_frame,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=(1, 2, 3, 4),
            height=10,
        )
        self._treeview.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self._treeview.yview)

        # Treeview columns
        self._treeview.column("#0", anchor="w", width=120)
        self._treeview.column(1, anchor="e", width=120)
        self._treeview.column(2, anchor="e", width=80)
        self._treeview.column(3, anchor="e", width=80)
        self._treeview.column(4, anchor="e", width=80)

        # Treeview headings
        self._treeview.heading("#0", text="ID", anchor="center")
        self._treeview.heading(1, text="Slices", anchor="center")
        self._treeview.heading(2, text="Accuracy", anchor="center")
        self._treeview.heading(3, text="F1", anchor="center")

        treeview_data = []
        all_models = model.getModels()

        for index, m in enumerate(all_models):
            f1 = f"{m.getF1():0.02}"
            accuracy = f"{m.getAccuracyScore():0.02}"
            treeview_data.append(
                ("",
                 m.getModelID()[:8],
                 (
                     str(m.getSlices()),
                     accuracy,
                     f1
                 ))
            )

        # Insert treeview data
        for item in treeview_data:
            self._treeview.insert(
                parent=item[0], index="end", iid=item[1], text=item[1],
                values=item[2]
            )

        self._treeview.bind('<<TreeviewSelect>>', self.callback)

        all_models = model.getModels()
        self._model_map = {m.getModelID()[:8]: m for m in all_models}
        self._root.geometry(f"{width}x{height}+{upperX}+{upperY}")
        self._root.mainloop()


if __name__ == '__main__':
    dbutil.SimpleSQL.setDatabaseName("scans")
    mc = ModelViewer()
    mc.main()
