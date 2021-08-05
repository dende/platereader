import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

from dende.platereader.layout import Settings
from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class TreatmentsFrame(TabbedFrame):
    centered_frame: ttk.Frame

    def __init__(self, root: tk.Tk, settings: Settings):
        super().__init__(root, settings, "Treatments")
        self.treatments = settings.treatments
        self.control = settings.treatment_control
        self.treatment_name_vars = []
        self.control_vars = []  # type: list[tk.BooleanVar]

        self.draw()

    def draw(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.centered_frame = ttk.Frame(self.frame, width=648)
        self.centered_frame.pack(fill=None, expand=None)

        for i, sample in enumerate(self.treatments):
            label = tk.Label(master=self.centered_frame, text=f'Treatment {i + 1}')
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')

            text_var = tk.StringVar()
            self.treatment_name_vars.append(text_var)
            entry = tk.Entry(master=self.centered_frame, bg='white', width='40', textvariable=text_var)
            text_var.set(sample)
            entry.grid(row=i, column=1, padx='5', pady='5', sticky='ew')

            control_var = tk.BooleanVar()
            control_var.set(False)
            self.control_vars.append(control_var)
            control_button = ttk.Checkbutton(master=self.centered_frame, text="Control", command=partial(self.toggle_control, i),
                                             variable=control_var)
            control_button.grid(row=i, column=2, padx='5', pady='5', )

        self.centered_frame.grid_columnconfigure(1, weight=1)

    def toggle_control(self, i):
        for j, control_var in enumerate(self.control_vars):
            if i != j:
                control_var.set(False)

    def collect_treatments(self):
        self.treatments.clear()
        self.control = None
        for i, treatment_name_var in enumerate(self.treatment_name_vars):
            treatment_name = treatment_name_var.get()
            if treatment_name and treatment_name != "":
                self.treatments.append(treatment_name)
                if self.control_vars[i].get():
                    self.control = treatment_name

        self.settings.treatments = self.treatments
        self.settings.treatment_control = self.control
