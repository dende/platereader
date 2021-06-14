import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

import numpy as np

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

    def draw(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        samples = self.settings.get_samples()

        if self.settings.treatments:
            sample_list = [f"{sample}${treatment}"
                           for sample in self.settings.materials for treatment in self.settings.treatments]
        else:
            sample_list = [f"{sample}" for sample in self.settings.materials]

        layout_bottom_frame = ttk.Frame(self.frame, height=20)
        layout_bottom_frame.pack(side=tk.BOTTOM, fill="x")

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side=tk.RIGHT)

        i = 0
        radiovar = tk.IntVar()
        for sample in sample_list:
            radio = tk.Radiobutton(button_frame, text=sample, command=partial(self.select_sample, sample),
                                   width=20, indicatoron=0, bg=self.well_plate.colors[i], val=i, variable=radiovar)
            radio.pack()
            i = i + 1

        self.well_plate.draw(self.frame)

        continue_button = ttk.Button(layout_bottom_frame, text="Continue", command=self.handle_continue_button)
        continue_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

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

        self.continue_function()
