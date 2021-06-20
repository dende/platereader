import logging
import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.colorchooser import askcolor
import matplotlib as plt

from dende.platereader.analysis.fluorescence_spectrum.plot import SpectrumPlot
from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    plot_vars = {}
    af_vars = {}

    def __init__(self, notebook, settings, well_plate):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate
        # this are only 10 colors, might be a problem in the future
        self.labels = ["Samples", "Plot", "Autofluorescence?", "Color"]
        stock_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.colors = stock_colors + stock_colors
        self.color_buttons = []

    def draw(self):

        plot_config_frame = ttk.Frame(self.frame, width=400)
        plot_config_frame.pack(side=tk.TOP, fill="y", expand=1)

        for i, text in enumerate(self.labels):
            label = ttk.Label(plot_config_frame, text=text)
            label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')

        sep = ttk.Separator(plot_config_frame, orient=tk.HORIZONTAL)
        sep.grid(row=1, columnspan=len(self.labels), sticky="ew")

        i = 2
        self.plot_vars.clear()
        self.af_vars.clear()

        well_mapping = self.well_plate.get_well_mapping()

        for j, sample in enumerate(sorted(well_mapping.keys())):
            label = ttk.Label(plot_config_frame, text=sample.get_description())
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')

            plot_var = tk.Variable()
            plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
            plot_checkbox.select()
            self.plot_vars[sample] = plot_var
            plot_checkbox.grid(row=i, column=1, padx='5', pady='5', )

            if self.settings.control and (not sample.material.control):
                af_var = tk.Variable()
                af_checkbox = tk.Checkbutton(plot_config_frame, variable=af_var)
                af_checkbox.deselect()
                self.af_vars[sample] = af_var
                af_checkbox.grid(row=i, column=2, padx='5', pady='5', )

            color = self.colors[j]
            color_button = tk.Button(plot_config_frame, bg=color, text=None,
                                     command=partial(self.handle_color_button, j))
            color_button.grid(row=i, column=3, padx='5', pady='5', )
            self.color_buttons.append(color_button)
            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_color_button(self, i):
        old_color = self.colors[i]
        _, hexcolor = askcolor(old_color)
        self.colors[i] = hexcolor
        self.color_buttons[i].configure(bg=hexcolor)

    def handle_plot_button(self):

        data = self.well_plate.get_named_data()
        data = data[list(data.keys())[0]]  # in flourescence spectrum data there is usually just one lens setting?
        # todo: maybe abstract the settings and always offer to plot all of them

        plain_plots = []
        autofluorescence_plots = []

        for i, (sample, plot_var) in enumerate(self.plot_vars.items()):
            color = self.colors[i]
            af_var = self.af_vars.get(sample)
            if plot_var.get() == "1":
                if af_var and af_var.get() == "1":
                    autofluorescence_plots.append([sample, color])
                else:
                    plain_plots.append([sample, color])

        plot_data = data.copy()
        spectrum_plot = SpectrumPlot(plot_data, plain_plots, autofluorescence_plots, self.settings.control)
        spectrum_plot.plot()
