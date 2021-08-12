import logging
import tkinter as tk
from functools import partial
from itertools import cycle
from tkinter import ttk
from tkcolorpicker import askcolor

import pandas as pd

import dende.platereader.layout
import dende.platereader.layout.tabbed_frame as tf
from dende.platereader.analysis.multichromatic_fluorescence.plot import MultichromaticFluorescencePlot
from dende.platereader.analysis.multichromatic_fluorescence.settings import MultichromaticFluorescenceSettings as mfs
from dende.platereader.plates.nunc96.well_plate import WellPlate

logger = logging.getLogger(__name__)


class PlotFrame(tf.TabbedFrame):

    def __init__(self, root: tk.Tk, well_plate: WellPlate):
        self.root = root
        self.settings = well_plate.settings
        self.notebook = self.root.nametowidget("bottomrow.notebook")
        self.listbox = self.root.nametowidget("toprow.details_list")
        super().__init__(root, self.settings, "Plot")
        self.well_plate = well_plate
        self.data = self.well_plate.get_named_data()
        self.colorcycle = cycle(dende.platereader.layout.PALETTE)
        self.multichromatic_fluorescence_settings = self.well_plate.proto_info.settings  # type: mfs
        self.presets = self.multichromatic_fluorescence_settings.optic_settings.presets
        self.listbox.delete(0, tk.END)

        self.labels = ["Samples"]
        for i, (preset_number, setting) in enumerate(self.presets.items()):
            self.labels.append(f"Preset {setting.preset_number}")
            self.labels.append("Color")
            self.listbox.insert(i, f"Preset {setting.preset_number}: {setting}")

        preset_numbers = list(self.presets.keys())
        k1 = preset_numbers[0]
        k2 = preset_numbers[1]
        self.ratios = [f"{k1}÷{k2}", f"{k2}÷{k1}"]
        self.labels.append(f"Preset {k1}÷{k2}")
        self.labels.append("Color")
        self.labels.append(f"Preset {k2}÷{k1}")
        self.labels.append("Color")

        if self.well_plate.has_autofluorescence():
            self.labels = self.labels + ["Autofluorescence"]

        columns = preset_numbers + ["autofluorescence"] + self.ratios
        self.samples = sorted(self.settings.get_samples())
        self.plot_vars = pd.DataFrame(index=self.samples, columns=columns)
        self.colors = pd.DataFrame(index=self.samples, columns=columns)
        self.color_buttons = pd.DataFrame(index=self.samples, columns=columns)

        for sample in self.samples:
            self.colors.loc[sample, :] = [next(self.colorcycle) for _ in range(self.colors.shape[1])]
            for column in columns:
                self.plot_vars.loc[sample, column] = tk.Variable()

    def draw(self):

        plot_config_frame = ttk.Frame(self.frame, width=400)
        plot_config_frame.pack(side=tk.TOP, fill="y", expand=1)

        for i, text in enumerate(self.labels):
            label = ttk.Label(plot_config_frame, text=text)
            label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')

        sep = ttk.Separator(plot_config_frame, orient=tk.HORIZONTAL)
        sep.grid(row=1, columnspan=len(self.labels), sticky="ew")

        i = 2

        for k, sample in enumerate(sorted(self.well_plate.get_assigned_samples())):

            label = ttk.Label(plot_config_frame, text=sample.get_description())
            label.grid(row=i, column=0, padx='5', pady='5', sticky='ew')
            j = 1
            for preset_number in list(self.presets.keys()):
                plot_var = self.plot_vars.loc[sample, preset_number]
                plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
                plot_checkbox.grid(row=i, column=j, padx='5', pady='5')
                plot_checkbox.deselect()
                j = j + 1
                color = self.colors.loc[sample, preset_number]
                color_button = tk.Button(plot_config_frame, bg=color, text=None,
                                         command=partial(self.handle_color_button, sample, preset_number))
                color_button.grid(row=i, column=j, padx='5', pady='5', )
                self.color_buttons.loc[sample, preset_number] = color_button

                j = j + 1

            for ratio in self.ratios:
                ratio_var = self.plot_vars.loc[sample, ratio]
                ratio_checkbox = tk.Checkbutton(plot_config_frame, variable=ratio_var)
                ratio_checkbox.deselect()
                ratio_checkbox.grid(row=i, column=j, padx='1', pady='5', )
                j = j + 1
                ratio_color = self.colors.loc[sample, ratio]
                ratio_color_button = tk.Button(plot_config_frame, bg=ratio_color, text=None,
                                               command=partial(self.handle_color_button, sample, ratio))
                ratio_color_button.grid(row=i, column=j, padx='5', pady='5', )
                self.color_buttons.loc[sample, ratio] = ratio_color_button
                j = j + 1

            if self.well_plate.has_autofluorescence():
                if self.well_plate.has_control_for_sample(sample):
                    af_var = tk.Variable()
                    af_checkbox = tk.Checkbutton(plot_config_frame, variable=af_var)
                    af_checkbox.deselect()
                    self.plot_vars.loc[sample, "autofluorescence"] = af_var
                    af_checkbox.grid(row=i, column=j, padx='5', pady='5', )
                j = j + 1

            i = i + 1

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    def handle_color_button(self, sample, column):
        old_color = self.colors.loc[sample, column]
        _, hexcolor = askcolor(old_color, self.root, palette=dende.platereader.layout.PALETTE)
        if hexcolor is None:
            return
        self.colors.loc[sample, column] = hexcolor
        self.color_buttons.loc[sample, column].configure(bg=hexcolor)
        # self.root.configs.save_color_for_sample(sample, hexcolor)

    def prepare_data(self):
        plain_plots = []
        autofluorescence_plots = []
        ratio_plots = {"plain": [], "af": []}

        for i, sample in enumerate(self.samples):
            autofluorescence = False
            af_var = self.plot_vars.loc[sample, "autofluorescence"]
            if af_var and af_var.get() == "1":
                autofluorescence = True

            for preset_number, preset in list(self.presets.items()):
                color = self.colors.loc[sample, preset_number]
                if self.plot_vars.loc[sample, preset_number].get() == "1":
                    if autofluorescence:
                        autofluorescence_plots.append([sample, preset, color])
                    else:
                        plain_plots.append([sample, preset, color])

            for ratio in self.ratios:
                color = self.colors.loc[sample, ratio]
                if self.plot_vars.loc[sample, ratio].get() == "1":
                    p1, p2 = ratio.split("÷")
                    p1 = self.presets[int(p1)]
                    p2 = self.presets[int(p2)]
                    if autofluorescence:
                        ratio_plots["af"].append([sample, (p1, p2), color])
                    else:
                        ratio_plots["plain"].append([sample, (p1, p2), color])

        merged_data = self.well_plate.get_merged_data()

        return merged_data, ratio_plots, autofluorescence_plots, plain_plots

    def handle_plot_button(self):

        merged_data, ratio_plots, autofluorescence_plots, plain_plots = self.prepare_data()

        plot = MultichromaticFluorescencePlot(self.root, merged_data, self.multichromatic_fluorescence_settings)

        if ratio_plots["plain"]:
            plot.ratio_plot(ratio_plots["plain"])
        elif ratio_plots["af"]:
            plot.autofluorescence_ratio_plot(ratio_plots["af"], self.settings.control)
        elif autofluorescence_plots:
            plot.autofluorescence_plot(autofluorescence_plots, self.settings.control)
        elif plain_plots:
            plot.plot(plain_plots)
