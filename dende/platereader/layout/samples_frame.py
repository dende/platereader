import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class SamplesFrame(TabbedFrame):
    samples = ["", "", "", "", "", ""]
    control = None

    def __init__(self, notebook, settings):
        super().__init__(notebook, settings, "Samples")

        self.sample_name_vars = []  # type: list[tk.StringVar]
        self.control_vars = []  # type: list[tk.BooleanVar]

        for i, sample in enumerate(self.samples):
            label = tk.Label(master=self.frame, text=f'Sample {i + 1}')
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')

            text_var = tk.StringVar()
            self.sample_name_vars.append(text_var)
            entry = tk.Entry(master=self.frame, bg='white', width='40', textvariable=text_var)
            text_var.set(sample)
            entry.grid(row=i, column=1, padx='5', pady='5', sticky='ew')

            control_var = tk.BooleanVar()
            control_var.set(False)
            self.control_vars.append(control_var)
            control_button = ttk.Checkbutton(master=self.frame, text="Control", command=partial(self.toggle_control, i),
                                             variable=control_var)
            control_button.grid(row=i, column=2, padx='5', pady='5', )

        self.frame.grid_columnconfigure(1, weight=1)

    def toggle_control(self, i):
        for j, control_var in enumerate(self.control_vars):
            if i != j:
                control_var.set(False)

    def collect_samples(self):
        self.samples.clear()
        self.control = None
        for i, sample_name_var in enumerate(self.sample_name_vars):
            sample_name = sample_name_var.get()
            if sample_name and sample_name != "":
                self.samples.append(sample_name)
                if self.control_vars[i].get():
                    self.control = sample_name

        self.settings.samples = self.samples
        self.settings.control = self.control
