import logging
import re
import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.colorchooser import askcolor

import matplotlib as plt
import pandas as pd

from dende.platereader.layout.tabbed_frame import TabbedFrame
from dende.platereader.time_course.plot import plot, autofluorescence_plot, ratio_plot

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    wavelengths = {}
    plot_vars = {}
    af_vars = {}
    ratio_vars = {}

    def __init__(self, notebook, settings, well_plate):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate
        self.data = self.get_data()
        self.labels = ["Samples"]
        for wavelength in self.wavelengths:
            self.labels = self.labels + [f"Plot {wavelength}", "Color"]
        self.labels = self.labels + ["Autofluorescence", "Plot Ratio", "Color"]
        self.colors = {wavelength: plt.rcParams['axes.prop_cycle'].by_key()['color']
                       for wavelength in self.wavelengths}
        self.color_buttons = {wavelength: [] for wavelength in self.wavelengths}
        self.ratio_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
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

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for k, sample in enumerate(sorted(well_mapping.keys())):
            try:
                line, _ = sample.split("$")
            except ValueError:
                line, _ = sample, None
            label = ttk.Label(plot_config_frame, text=sample)
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')
            j = 1
            for wavelength, desc in self.wavelengths.items():
                plot_var = tk.Variable()
                plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
                plot_checkbox.select()
                if wavelength not in self.plot_vars:
                    self.plot_vars[wavelength] = {}
                self.plot_vars[wavelength][sample] = plot_var
                plot_checkbox.grid(row=i, column=j, padx='5', pady='5')
                j = j + 1
                color = self.colors[wavelength][k % len(self.colors[wavelength])]
                color_button = tk.Button(plot_config_frame, bg=color, text=None,
                                         command=partial(self.handle_color_button, wavelength, k))
                color_button.grid(row=i, column=j, padx='5', pady='5', )
                self.color_buttons[wavelength].append(color_button)

                j = j + 1
            if self.settings.control and (line != self.settings.control):
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

            ratio_color = self.ratio_colors[k % len(self.ratio_colors)]
            ratio_color_button = tk.Button(plot_config_frame, bg=ratio_color, text=None,
                                           command=partial(self.handle_ratio_color_button, k))
            ratio_color_button.grid(row=i, column=j, padx='5', pady='5', )
            self.ratio_color_buttons.append(ratio_color_button)

            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_color_button(self, wavelength, i):
        old_color = self.colors[wavelength][i % len(self.colors[wavelength])]
        logger.info(self.colors)
        _, hexcolor = askcolor(old_color)
        if hexcolor is None:
            return
        self.colors[wavelength][i % len(self.colors[wavelength])] = hexcolor
        self.color_buttons[wavelength][i].configure(bg=hexcolor)
        logger.info(self.colors)

    def handle_ratio_color_button(self, i):
        old_ratio_color = self.ratio_colors[i % len(self.ratio_colors)]
        _, hexcolor = askcolor(old_ratio_color)
        self.ratio_colors[i % len(self.ratio_colors)] = hexcolor
        self.ratio_color_buttons[i].configure(bg=hexcolor)

    def handle_plot_button(self):
        column_names = []
        plain_plots = []
        autofluorescence_plots = []
        ratio_plots = {"plain": [], "af": []}

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for wavelength, samples in self.plot_vars.items():
            for i, (sample, plot_var) in enumerate(samples.items()):
                color = self.colors[wavelength][i % len(self.colors[wavelength])]
                af_var = self.af_vars.get(sample)
                if plot_var.get() == "1":
                    if af_var and af_var.get() == "1":
                        autofluorescence_plots.append([f"{wavelength}${sample}", color])
                        try:
                            line, treatment = sample.split("$")
                            column_names.extend([f"{wavelength}${self.settings.control}${treatment}${i}"
                                                 for i in
                                                 range(len(well_mapping[f"{self.settings.control}${treatment}"]))])

                        except ValueError:
                            column_names.extend([f"{wavelength}${self.settings.control}${i}"
                                                 for i in
                                                 range(len(well_mapping[f"{self.settings.control}"]))])

                    else:
                        plain_plots.append([f"{wavelength}${sample}", color])

                    column_names.extend([f"{wavelength}${sample}${i}" for i in range(len(well_mapping[sample]))])

        for i, (sample, ratio_var) in enumerate(self.ratio_vars.items()):
            if ratio_var.get() == "1":
                try:
                    _, treatment = sample.split("$")
                except ValueError:
                    treatment = None
                for wavelength in self.wavelengths:
                    column_names.extend([f"{wavelength}${sample}${i}" for i in range(len(well_mapping[sample]))])
                af_var = self.af_vars.get(sample)
                if af_var and af_var.get() == "1":
                    for wavelength in self.wavelengths:
                        if treatment:
                            column_names.extend([f"{wavelength}${self.settings.control}${treatment}${i}"
                                                 for i in
                                                 range(len(well_mapping[f"{self.settings.control}${treatment}"]))])
                        else:
                            column_names.extend([f"{wavelength}${self.settings.control}${i}"
                                                 for i in range(len(well_mapping[f"{self.settings.control}"]))])
                    ratio_plots["af"].append([sample, self.ratio_colors[i % len(self.ratio_colors)]])
                else:
                    ratio_plots["plain"].append([sample, self.ratio_colors[i % len(self.ratio_colors)]])

        # remove duplicates
        column_names = list(set(column_names))
        data = self.get_data()
        plot_data = data[column_names].copy()

        if ratio_plots["plain"] or ratio_plots["af"]:
            ratio_plot(plot_data, ratio_plots, sorted(self.wavelengths.keys()), self.settings.control)
        elif autofluorescence_plots:
            autofluorescence_plot(plot_data, autofluorescence_plots, self.settings.control)
        elif plain_plots:
            plot(plot_data, plain_plots)

    def get_data(self):
        xlsx = self.well_plate.get_xlsx()
        descs = xlsx.iloc[14:, 0].unique()

        pattern = r"Raw Data \(F: (?P<excitation_wavelength>\d+)-(?P<excitation_spread>\d+)/" \
                  r"F: (?P<emission_wavelength>\d+)-(?P<emission_spread>\d+) (?P<setting_number>\d+)\)"
        regex = re.compile(pattern)

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        wavelength_datas = []

        for desc in descs:
            # todo(dende): I'm sure there is a better way. but python regex is weird
            match = [m.groupdict() for m in regex.finditer(desc)][0]
            self.wavelengths[match["excitation_wavelength"]] = desc
            mask = xlsx.iloc[:, 0].str.contains(desc.strip(), regex=False, na=False)
            wavelength_data = xlsx[mask].copy()
            wavelength_data.columns = xlsx.iloc[13].copy()
            wavelength_data = wavelength_data.iloc[:, 1:]
            wavelength_data = wavelength_data.set_index(wavelength_data.columns[0])
            # column names are not mutable anymore once it belongs to df.columns so lets keep a mutable copy.
            # yes, i know this is shit code
            headers = xlsx.iloc[13, 2:].copy()
            headers = headers.values

            for sample in well_mapping:
                well_mapping[sample] = sorted(well_mapping[sample])
                i = 0
                for col in well_mapping[sample]:
                    headers[col] = f"{match['excitation_wavelength']}${sample}${i}"
                    i = i + 1
            wavelength_data.columns = headers
            wavelength_datas.append(wavelength_data.copy())

        data = pd.concat(wavelength_datas, axis=1)
        data = data.loc[:, ~data.columns.str.startswith('Sample ')]
        return data
