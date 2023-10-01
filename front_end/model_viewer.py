"""A UI application to show available models."""

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
import cogni_scan.src.modeler.model as model

import cogni_scan.front_end.settings as settings


def openModelWindow(parent, model_id, onDeleteModel=None):
    """Show the model descriptive data in a window."""
    active_model = model.getModelByID(model_id)

    width = 1400
    height = 1150
    upperX = 200
    upperY = 100

    # Open the window.
    modal_window = tk.Toplevel(parent)
    modal_window.title("Modal Window")
    modal_window.geometry(f"{width}x{height}+{upperX}+{upperY}")
    modal_window.resizable(False, False)
    modal_window.wait_visibility(modal_window)
    modal_window.grab_set()

    # Create the sections of the window.
    top = Canvas(modal_window, bg=settings.TOP_BACKGROUND_COLOR,
                 highlightthickness=0, height=60)
    middle = Canvas(modal_window, bg=settings.LEFT_BACKGROUND_COLOR,
                    highlightthickness=0)
    bottom = Canvas(modal_window, highlightthickness=0, height=60)

    top.pack(fill=BOTH, side=TOP, pady=10, padx=10)
    middle.pack(fill=BOTH, side=TOP, pady=10, padx=10)
    bottom.pack(fill=BOTH, side=TOP, pady=10, padx=10)

    # Build the top section,
    _buildTopView(top, active_model)

    # Build the middle section,
    _buildMiddleView(middle, active_model)

    # Build the botton section,
    def deleteModel():
        if not askyesno(
                title='Delete Model',
                message='Are you sure you want to delete the model?'):
            return
        mid = active_model.getModelID()
        active_model.reset()
        if onDeleteModel:
            onDeleteModel(mid)
        modal_window.destroy()

    close_button = tk.Button(bottom, text="Close", command=modal_window.destroy)
    close_button.grid(row=0, column=0)
    close_button = tk.Button(bottom, text="Delete Model", command=deleteModel)
    close_button.grid(row=0, column=1)


def _makeCorrectWrongView(active_model):
    """Adds a figure holding the correct and wrong predictions summary."""
    counts = {}
    for p in active_model.getTestingPredictions():
        pred = p["pred"]
        label = p["label"]
        scan_id = p["scan_id"]
        if label not in counts:
            counts[label] = [0, 0]
        if label == "HH":
            is_correct = 1 if pred <= 0.5 else 0
            if is_correct:
                counts[label][0] += 1
            else:
                counts[label][1] += 1
        elif label == "HD":
            is_correct = 1 if pred > 0.5 else 0
            if is_correct:
                counts[label][0] += 1
            else:
                counts[label][1] += 1
        else:
            assert False, f"Invalid label: {label}."
    labels = list(counts.keys())
    counter = {
        'Correct': np.array([counts["HH"][0], counts["HD"][0]]),
        'Wrong': np.array([counts["HH"][1], counts["HD"][1]]),
    }
    width = 0.4
    fig, ax = plt.subplots(figsize=(4, 2))
    bottom = np.zeros(2)
    for key, count in counter.items():
        p = ax.bar(labels, count, width, label=key, bottom=bottom)
        bottom += count
        ax.bar_label(p, label_type='center')
    ax.set_title('Correct/Wrong Predictions in Testing Dataset')
    ax.legend()

    def onclick(event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

    fig.canvas.mpl_connect('button_press_event', onclick)
    return fig


def _buildMiddleView(parent, active_model):
    """Builds the middle view holding confustion, ROC, training history etc."""
    colors = "red", "green", "blue", "yellow"
    canvases = [
        Canvas(parent, bg=color, highlightthickness=0, height=60)
        for color in colors
    ]
    canvases[0].grid(row=0, column=0, pady=(10, 10), padx=(10, 10))
    canvases[1].grid(row=0, column=1, pady=(10, 10), padx=(10, 10))
    canvases[2].grid(row=1, column=0, pady=(10, 10), padx=(10, 10))
    canvases[3].grid(row=1, column=1, pady=(10, 10), padx=(10, 10))

    # Add the confusion matrix.
    cm = active_model.getConfusionMatrix()
    fig = ConfusionMatrixDisplay(cm).plot()
    canvas = FigureCanvasTkAgg(fig.figure_, master=canvases[0])
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.LEFT)

    # Add the ROC curve.
    fpr, tpr = active_model.getROCCurve()
    roc_display = RocCurveDisplay(fpr=fpr, tpr=tpr).plot()
    canvas = FigureCanvasTkAgg(roc_display.figure_, master=canvases[1])
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.LEFT)

    # Add the training history.
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
    canvas = FigureCanvasTkAgg(fig, master=canvases[2])
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    # Add the dataset description data.
    dsi = active_model.getDatasetID()
    ds = model.getDatasetByID(dsi)

    upper_canvas = Canvas(canvases[3], bg=settings.TOP_BACKGROUND_COLOR,
                          highlightthickness=0)
    upper_canvas.pack(fill=BOTH, side=TOP)

    lower_canvas = Canvas(canvases[3], bg=settings.TOP_BACKGROUND_COLOR,
                          highlightthickness=0)
    upper_canvas.pack(fill=BOTH, side=TOP)
    lower_canvas.pack(fill=BOTH, side=TOP)

    title = tk.Label(
        upper_canvas,
        text="Dataset Stats.",
        bg=settings.LABEL_BACKGROUND_COLOR,
        fg=settings.LABEL_FRONT_COLOR, padx=10, pady=10
    )
    title.grid(row=0, column=0)
    desc = ds.getDescription()
    for column, name in enumerate(desc):
        d = desc[name]
        labels = [f'HD-{d["HD"]}', f'HH-{d["HH"]}']
        sizes = [d["HD"], d["HH"]]
        explode = (0, 0.1)
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.pie(sizes, labels=labels, explode=explode)

        fig.suptitle(name.title(), fontsize=12)
        canvas = FigureCanvasTkAgg(fig, master=upper_canvas)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=column)

    fig = _makeCorrectWrongView(active_model)
    canvas = FigureCanvasTkAgg(fig, master=lower_canvas)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)


def _buildTopView(parent, active_model):
    """Builds the top view holding descriptive data about the model."""
    desc_data = {
        "ModelID": active_model.getModelID(),
        "Accuracy": f"{active_model.getAccuracyScore():0.02}",
        "F1": f"{active_model.getF1():0.02}",
        "Slices": str(active_model.getSlices())
    }

    column = 0
    back = settings.LABEL_BACKGROUND_COLOR
    fore = settings.LABEL_FRONT_COLOR
    highlight_font = ('Helvetica', 12, 'bold')

    for k, v in desc_data.items():
        label = tk.Label(parent, text=k, bg=back, fg=fore, padx=10, pady=10)
        label.grid(row=0, column=column)
        column += 1

        label = tk.Label(parent, text=v, bg=back, fg=fore, font=highlight_font)
        label.grid(row=0, column=column)
        column += 1


if __name__ == '__main__':
    import cogni_scan.src.dbutil as dbutil


    class _ModelViewer:
        def main(self, title="n/a", menu=None, width=300, height=300,
                 upperX=200,
                 upperY=100, zoomed=False):
            self._root = tk.Tk()
            self._root.title("Model Viewer (all available models).")

            def foo():
                openModelWindow(self._root,
                                'c8d4fa20-4076-4ca4-a330-a931b61acd7f')

            close_button = tk.Button(self._root, text="open", command=foo)
            close_button.pack()

            self._root.geometry(f"{width}x{height}+{upperX}+{upperY}")
            self._root.mainloop()


    mc = _ModelViewer()
    mc.main()
    model_id = 'c8d4fa20-4076-4ca4-a330-a931b61acd7f'
    m = model.getModelByID(model_id)
    print(m)
