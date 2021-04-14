import logging
import tkinter as tk
from tkinter import ttk

from dende.platereader.flourescence_spectrum.plot import plot
from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    plot_vars = {}
    af_vars = {}

    def __init__(self, notebook, settings, well_plate):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate

    def draw(self):

        plot_config_frame = ttk.Frame(self.frame, width=400)
        plot_config_frame.pack(side=tk.TOP, fill="y", expand=1)

        samples_label = ttk.Label(plot_config_frame, text="Samples")
        samples_label.grid(row=0, column=0, padx='5', pady='5', sticky='ew')
        plot_label = ttk.Label(plot_config_frame, text="Plot?")
        plot_label.grid(row=0, column=1, padx='5', pady='5', sticky='ew')
        autof_label = ttk.Label(plot_config_frame, text="Autofluorescence?")
        autof_label.grid(row=0, column=2, padx='5', pady='5', sticky='ew')
        sep = ttk.Separator(plot_config_frame, orient=tk.HORIZONTAL)
        sep.grid(row=1, columnspan=3, sticky="ew")

        i = 2
        self.plot_vars.clear()
        self.af_vars.clear()

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for sample in sorted(well_mapping.keys()):
            line, treatment = sample.split("$")
            label = ttk.Label(plot_config_frame, text=sample)
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')
            plot_var = tk.Variable()
            plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
            plot_checkbox.select()
            self.plot_vars[sample] = plot_var
            plot_checkbox.grid(row=i, column=1, padx='5', pady='5', )
            if self.settings.control and (line != self.settings.control):
                af_var = tk.Variable()
                af_checkbox = tk.Checkbutton(plot_config_frame, variable=af_var)
                af_checkbox.deselect()
                self.af_vars[sample] = af_var
                af_checkbox.grid(row=i, column=2, padx='5', pady='5', )

            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_plot_button(self):

        data = self.get_data()

        column_names = []
        plain_plots = []
        autofluorescence_plots = []

        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)
        for sample, plot_var in self.plot_vars.items():
            af_var = self.af_vars.get(sample)
            if plot_var.get() == "1":
                if af_var and af_var.get() == "1":
                    autofluorescence_plots.append(sample)
                    line, treatment = sample.split("$")
                    column_names.extend(
                        [f"{self.settings.control}${treatment}${i}"
                            for i in range(len(well_mapping[f"{self.settings.control}${treatment}"]))])
                else:
                    plain_plots.append(sample)

                column_names.extend([f"{sample}${i}" for i in range(len(well_mapping[sample]))])

        plot_data = data[column_names].copy()

        plot(plot_data, plain_plots, autofluorescence_plots, self.settings.control)

    def get_data(self):
        # todo (dende) this is unnecessary, just call it get_data and call the well from here
        data = self.well_plate.get_data()
        well_dict = self.well_plate.get_well_dict()
        well_mapping = self.well_plate.get_well_mapping(well_dict)

        for sample in well_mapping:
            well_mapping[sample] = sorted(well_mapping[sample])
            i = 0
            for col in well_mapping[sample]:
                data.iloc[0, col+1] = f"{sample}${i}"
                i = i + 1

        data = data.rename(columns=data.iloc[0]).drop(data.index[0])
        data = data.set_index(data.columns[0])
        return data.copy()
