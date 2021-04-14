import logging
import tkinter as tk
from functools import partial
from tkinter import ttk

from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class SamplesFrame(TabbedFrame):
    samples = []
    control = None

    def __init__(self, notebook, settings):
        super().__init__(notebook, settings, "Samples")
        self.frame.grid_columnconfigure(1, weight=1)

    def draw(self):
        for widget in self.frame.grid_slaves():
            widget.grid_forget()
            widget.destroy()

        if not self.samples:
            self.samples = [""]

        i = 0
        for sample in self.samples:
            label = tk.Label(master=self.frame, text=f'Sample {i + 1}')
            label.grid(row=i * 2, column=0, padx='5', pady='5', sticky='ew')

            textvar = tk.StringVar()
            entry = tk.Entry(master=self.frame, bg='white', width='40', textvariable=textvar)
            textvar.set(sample)

            entry.grid(row=i * 2, column=1, padx='5', pady='5', sticky='ew')

            controlbutton = ttk.Checkbutton(master=self.frame,
                                            text="Control", command=partial(self.toggle_control, sample))
            controlbutton.state(["!alternate"])
            if self.control == sample:
                controlbutton.state(["selected"])
            controlbutton.grid(row=i * 2 + 1, column=0, padx='5', pady='5', )

            plus_button = ttk.Button(master=self.frame, text='+', width='2', command=self.add_sample)
            plus_button.grid(row=i * 2, column=2, padx='5', pady='5')
            # tk.Button zum Subtrahieren
            minus_button = ttk.Button(master=self.frame, text='-', width='2', command=partial(self.remove_sample, i))
            minus_button.grid(row=i * 2 + 1, column=2, padx='5', pady='5')
            i = i + 1

    def sync(self):
        self.settings.samples = self.samples
        self.settings.control = self.control

    def collect_samples(self):
        i = 0
        self.samples.clear()
        for widget in self.frame.winfo_children():
            if widget.winfo_class() == "Entry":
                i = i + 1
                sample = widget.get()
                if sample != "":
                    self.samples.append(sample)
        self.sync()

    def add_sample(self):
        logger.info(f"I'm in SamplesFrame.add_sample, self.samples. {self.samples}")
        self.collect_samples()
        self.samples.append("")
        self.draw()

    def remove_sample(self, i):
        self.collect_samples()
        sample = self.samples.pop(i)
        if self.control == sample:
            self.control = None
        self.draw()

    def toggle_control(self, sample):
        self.collect_samples()
        logger.info(f"I'm in SamplesFrame.toggle_control, self {self}, {sample}")
        if self.control == sample:
            self.control = None
        else:
            self.control = sample
        self.sync()
        self.draw()
