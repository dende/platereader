import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class TreatmentsFrame(TabbedFrame):
    treatments = ["No Treatment", "H202", "DTT"]
    control = treatments[0]

    def __init__(self, notebook, settings):
        super().__init__(notebook, settings, "Treatments")
        self.frame.grid_columnconfigure(1, weight=1)

    def draw(self):
        logger.info("in TreatmentsFrame.draw()")
        if not self.treatments:
            self.treatments = [""]

        for widget in self.frame.grid_slaves():
            widget.grid_forget()
            widget.destroy()

        i = 0
        for treatment in self.treatments:
            label = tk.Label(master=self.frame, text=f'Treatment {i + 1}')
            label.grid(row=i * 2, column=0, padx='5', pady='5', sticky='ew')

            textvar = tk.StringVar()
            entry = tk.Entry(master=self.frame, bg='white', width='40', textvariable=textvar)
            textvar.set(treatment)

            entry.grid(row=i * 2, column=1, padx='5', pady='5', sticky='ew')

            controlbutton = ttk.Checkbutton(master=self.frame, text="Control",
                                            command=partial(self.check_control_treatment, treatment))
            controlbutton.state(["!alternate"])
            if self.control == treatment:
                controlbutton.state(["selected"])
            controlbutton.grid(row=i * 2 + 1, column=0, padx='5', pady='5', )

            plus_button = ttk.Button(master=self.frame, text='+', width='2', command=self.add_treatment)
            plus_button.grid(row=i * 2, column=2, padx='5', pady='5')
            # tk.Button zum Subtrahieren
            minus_button = ttk.Button(master=self.frame, text='-', width='2',
                                      command=partial(self.remove_treatment, i))
            minus_button.grid(row=i * 2 + 1, column=2, padx='5', pady='5')
            i = i + 1

    def collect_treatments(self):
        i = 0
        self.treatments.clear()
        for widget in self.frame.winfo_children():
            if widget.winfo_class() == "Entry":
                i = i + 1
                treatment = widget.get()
                if treatment != "":
                    self.treatments.append(treatment)
        self.sync()

    def sync(self):
        self.settings.treatments = self.treatments
        self.settings.treatment_control = self.control

    def check_control_treatment(self):
        pass

    def add_treatment(self):
        pass

    def remove_treatment(self):
        pass
