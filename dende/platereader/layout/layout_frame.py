import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class LayoutFrame(TabbedFrame):
    selected_sample = None

    def __init__(self, notebook, settings, well_plate, continue_function=None):
        super().__init__(notebook, settings, "Layout")
        self.frame.grid_columnconfigure(1, weight=1)
        self.well_plate = well_plate
        self.well_plate.set_layout_frame(self)
        if not continue_function:
            logger.warning("No continue function provided to LayoutFrame")
        self.continue_function = continue_function
        self.preview = None
        self.fig = None
        self.ax = None

    def update_preview(self, well_row, well_colum):
        well_identifier = f"{well_row}{well_colum:02}"
        x = []
        y = []

        for data in self.well_plate.data.values():
            col = data[well_identifier]
            x = x + col.index.tolist()
            y = y + col.tolist()

        print(x)
        print(y)
        self.ax.clear()
        self.ax.plot(x, y)
        self.preview.draw() 


    def draw(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        samples = self.settings.get_samples()

        layout_bottom_frame = ttk.Frame(self.frame, height=20)
        layout_bottom_frame.pack(side=tk.BOTTOM, fill="x")

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side=tk.LEFT)

        i = 0
        radiovar = tk.IntVar()
        for sample in samples:
            radio = tk.Radiobutton(button_frame, text=sample.get_description(),
                                   command=partial(self.select_sample, sample),
                                   width=30, indicatoron=0, bg=self.well_plate.colors[i], val=i, variable=radiovar)
            radio.pack()
            i = i + 1

        self.well_plate.draw(self.frame)

        self.fig = plt.figure(figsize=(8, 8))
        t = np.arange(0, 3, .01)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(t, 2 * np.sin(2 * np.pi * t))
        self.preview = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.preview.get_tk_widget().pack(side=tk.RIGHT, fill='both', expand=1)

        continue_button = ttk.Button(layout_bottom_frame, text="Continue", command=self.handle_continue_button)
        continue_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def update(self):
        self.well_plate.update()

    def select_sample(self, sample):
        self.settings.selected_sample = sample

    def handle_continue_button(self, ):
        try:
            for column in self.well_plate.well_plate.columns:
                for index in self.well_plate.well_plate.index:
                    cell = self.well_plate.well_plate.loc[index][column]
                    if (isinstance(cell, np.bool_) or isinstance(cell, bool)) and cell:
                        raise Exception(f"Well {index} {column} is not assigned")
        except Exception as e:
            continue_anyway = tk.messagebox.askquestion("Continue Anyways?", f"{e}.\nDo you want to continue anyway?")
            if continue_anyway != "yes":
                return

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.continue_function()
