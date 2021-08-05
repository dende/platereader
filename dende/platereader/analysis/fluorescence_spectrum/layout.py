import logging
import tkinter as tk
from typing import Dict

import pandas as pd

import dende.platereader.layout as layout
import dende.platereader.protocol_info as pi
import dende.platereader.analysis.fluorescence_spectrum.plot_frame as pf

logger = logging.getLogger(__name__)


class FlourescenceSpectrumLayout(layout.Layout):

    def __init__(self, root: tk.Tk, data: Dict[str, pd.DataFrame], proto_info: pi.ProtocolInfo):
        super().__init__(root, data, proto_info)

    def draw_plot_window(self):
        for widget in self.notebook.winfo_children():
            widget.destroy()
        plot_frame = pf.PlotFrame(self.root, self.well_plate)
        plot_frame.draw()
