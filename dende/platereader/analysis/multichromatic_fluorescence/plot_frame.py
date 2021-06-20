import logging
import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.colorchooser import askcolor

import matplotlib as plt

from dende.platereader.layout.tabbed_frame import TabbedFrame
from dende.platereader.analysis.multichromatic_fluorescence.plot import plot, autofluorescence_plot, ratio_plot

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    wavelengths = {}
    plot_vars = {}
    af_vars = {}
    ratio_vars = {}

    def __init__(self, notebook, settings, well_plate):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate
        self.data = self.well_plate.get_named_data()
        self.labels = ["Samples"]
        for lens_setting in self.data:
            label = lens_setting.split("(")[1][:-1]
            self.labels = self.labels + [label, "Color"]
        self.labels = self.labels + ["Autofluorescence", "Plot Ratio", "Color"]
        stock_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        # todo: turn colors etc into dataframes like for luminescence
        self.colors = {lens_setting: stock_colors + stock_colors
                       for lens_setting in list(self.data.keys())}
        self.color_buttons = {lens_setting: [] for lens_setting in list(self.data.keys())}
        self.ratio_colors = stock_colors + stock_colors
        self.ratio_color_buttons = []

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
        self.ratio_vars.clear()

        for k, sample in enumerate(sorted(self.well_plate.get_well_mapping())):

            label = ttk.Label(plot_config_frame, text=sample.get_description())
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')
            j = 1
            for lens_setting in self.data:
                plot_var = tk.Variable()
                plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
                plot_checkbox.select()
                if lens_setting not in self.plot_vars:
                    self.plot_vars[lens_setting] = {}
                self.plot_vars[lens_setting][sample] = plot_var
                plot_checkbox.grid(row=i, column=j, padx='5', pady='5')
                j = j + 1
                color = self.colors[lens_setting][k]
                color_button = tk.Button(plot_config_frame, bg=color, text=None,
                                         command=partial(self.handle_color_button, lens_setting, k))
                color_button.grid(row=i, column=j, padx='5', pady='5', )
                self.color_buttons[lens_setting].append(color_button)

                j = j + 1

            if self.settings.control and (not sample.material.control):
                af_var = tk.Variable()
                af_checkbox = tk.Checkbutton(plot_config_frame, variable=af_var)
                af_checkbox.deselect()
                self.af_vars[sample] = af_var
                af_checkbox.grid(row=i, column=j, padx='5', pady='5', )
            j = j + 1

            ratio_var = tk.Variable()
            ratio_checkbox = tk.Checkbutton(plot_config_frame, variable=ratio_var)
            ratio_checkbox.deselect()
            self.ratio_vars[sample] = ratio_var
            ratio_checkbox.grid(row=i, column=j, padx='1', pady='5', )

            j = j + 1

            ratio_color = self.ratio_colors[k]
            ratio_color_button = tk.Button(plot_config_frame, bg=ratio_color, text=None,
                                           command=partial(self.handle_ratio_color_button, k))
            ratio_color_button.grid(row=i, column=j, padx='5', pady='5', )
            self.ratio_color_buttons.append(ratio_color_button)

            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_color_button(self, wavelength, i):
        old_color = self.colors[wavelength][i]
        _, hexcolor = askcolor(old_color)
        if hexcolor is None:
            return
        self.colors[wavelength][i] = hexcolor
        self.color_buttons[wavelength][i].configure(bg=hexcolor)

    def handle_ratio_color_button(self, i):
        old_ratio_color = self.ratio_colors[i]
        _, hexcolor = askcolor(old_ratio_color)
        self.ratio_colors[i] = hexcolor
        self.ratio_color_buttons[i].configure(bg=hexcolor)

    def handle_plot_button(self):
        plain_plots = []
        autofluorescence_plots = []
        ratio_plots = {"plain": [], "af": []}

        for lens_setting, samples in self.plot_vars.items():
            for i, (sample, plot_var) in enumerate(samples.items()):
                color = self.colors[lens_setting][i]
                af_var = self.af_vars.get(sample)
                if plot_var.get() == "1":
                    if af_var and af_var.get() == "1":
                        autofluorescence_plots.append([sample, lens_setting, color])
                    else:
                        plain_plots.append([sample, lens_setting, color])

        for i, (sample, ratio_var) in enumerate(self.ratio_vars.items()):
            if ratio_var.get() == "1":
                af_var = self.af_vars.get(sample)
                if af_var and af_var.get() == "1":
                    ratio_plots["af"].append([sample, self.ratio_colors[i]])
                else:
                    ratio_plots["plain"].append([sample, self.ratio_colors[i]])

        # remove duplicates

        merged_data = self.well_plate.get_merged_data()
        named_data = self.well_plate.get_named_data()

        if ratio_plots["plain"] or ratio_plots["af"]:
            ratio_plot(merged_data, ratio_plots, sorted(named_data.keys()), self.settings.control)
        elif autofluorescence_plots:
            autofluorescence_plot(merged_data, autofluorescence_plots, self.settings.control)
        elif plain_plots:
            plot(merged_data, plain_plots)

