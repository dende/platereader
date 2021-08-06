import abc
import logging
import tkinter as tk
from abc import ABC
from tkinter import ttk
from typing import Dict

import pandas as pd

import dende.platereader.plates as plates
import dende.platereader.protocol_info as protocol_info
from . import Settings, SamplesFrame, TreatmentsFrame, LayoutFrame

logger = logging.getLogger(__name__)


class Layout(ABC):
    root: tk.Tk
    frame: ttk.Frame
    notebook: ttk.Notebook
    settings: Settings

    samples_frame: SamplesFrame
    treatments_frame: TreatmentsFrame
    layout_frame: LayoutFrame

    def __init__(self, root: tk.Tk, data: Dict[str, pd.DataFrame], proto_info: protocol_info.ProtocolInfo):
        self.root = root
        self.frame = root.nametowidget("bottomrow")
        self.notebook = ttk.Notebook(self.frame, name="notebook")
        self.treatments = ["No Treatment", "H202", "DTT", "", ""]
        self.settings = Settings(treatments=self.treatments, treatment_control=self.treatments[0])

        self.well_plate = plates.create_well_plate(data, proto_info, self.settings)

        self.samples_frame = SamplesFrame(self.root, self.settings)
        self.treatments_frame = TreatmentsFrame(self.root, self.settings)
        self.layout_frame = LayoutFrame(self.root, self.well_plate, continue_function=self.draw_plot_window)

        self.notebook.pack(expand=1, fill="both")
        self.notebook.bind('<<NotebookTabChanged>>', self.tab_change)

    def tab_change(self, event):
        tab = None
        try:
            tab = event.widget.tab('current')
            tab = tab['text']
        except Exception as e:
            # tab not found, probably because we deleted all tabs
            logger.warning(f"could not find the tab {e}")

        logger.info(f"changed to tab {tab}")

        if tab == "Layout":
            self.samples_frame.collect_samples()
            self.treatments_frame.collect_treatments()
            self.layout_frame.draw()

    @abc.abstractmethod
    def draw_plot_window(self):
        return
