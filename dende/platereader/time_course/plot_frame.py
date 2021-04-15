import logging
import re
import tkinter as tk
from tkinter import ttk

import pandas as pd

from dende.platereader.layout.tabbed_frame import TabbedFrame
from dende.platereader.time_course.plot import plot, autofluorescence_plot, ratio_plot

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    data = None
    wavelengths = {}
    plot_vars = {}
    af_vars = {}
    ratio_vars = {}

    def __init__(self, notebook, settings, well_plate):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate
        self.data = self.get_data()

    def draw(self):

        plot_config_frame = ttk.Frame(self.frame, width=400)
        plot_config_frame.pack(side=tk.TOP, fill="y", expand=1)

        samples_label = ttk.Label(plot_config_frame, text="Samples")
        samples_label.grid(row=0, column=0, padx='5', pady='5', sticky='ew')
        i = 1
        for wavelength, desc in self.wavelengths.items():
            plot_label = ttk.Label(plot_config_frame, text=f"Plot {wavelength}?")
            plot_label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')
            i = i + 1

        autof_label = ttk.Label(plot_config_frame, text="Autofluorescence?")
        autof_label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')
        i = i + 1

        autof_label = ttk.Label(plot_config_frame, text="Plot Ratio")
        autof_label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')

        sep = ttk.Separator(plot_config_frame, orient=tk.HORIZONTAL)
        sep.grid(row=1, columnspan=i + 1, sticky="ew")

        i = 2
        self.plot_vars.clear()
        self.af_vars.clear()
        self.ratio_vars.clear()

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for sample in sorted(well_mapping.keys()):
            line, treatment = sample.split("$")
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
                ratio_checkbox.grid(row=i, column=j, padx='5', pady='5', )

            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_plot_button(self):

        column_names = []
        plain_plots = []
        autofluorescence_plots = []
        ratio_plots = []

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for wavelength, samples in self.plot_vars.items():
            for sample, plot_var in samples.items():
                af_var = self.af_vars.get(sample)
                if plot_var.get() == "1":
                    if af_var and af_var.get() == "1":
                        autofluorescence_plots.append(f"{wavelength}${sample}")
                        line, treatment = sample.split("$")
                        column_names.extend([f"{wavelength}${self.settings.control}${treatment}${i}"
                                             for i in range(len(well_mapping[f"{self.settings.control}${treatment}"]))])
                    else:
                        plain_plots.append(f"{wavelength}${sample}")

                    column_names.extend([f"{wavelength}${sample}${i}" for i in range(len(well_mapping[sample]))])

        for sample, ratio_var in self.ratio_vars.items():
            if ratio_var.get() == "1":
                ratio_plots.append(sample)
                line, treatment = sample.split("$")
                for wavelength in self.wavelengths:
                    column_names.extend([f"{wavelength}${sample}${i}" for i in range(len(well_mapping[sample]))])
                    column_names.extend([f"{wavelength}${self.settings.control}${treatment}${i}"
                                         for i in range(len(well_mapping[f"{self.settings.control}${treatment}"]))])

        # remove duplicates
        column_names = list(set(column_names))
        plot_data = self.data[column_names].copy()

        if ratio_plots:
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
