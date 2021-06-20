import logging
import re
import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.colorchooser import askcolor
import matplotlib as plt
import pandas as pd
from itertools import cycle

from dende.platereader.analysis.luminescence.plot import LuminescencePlot
from dende.platereader.layout.tabbed_frame import TabbedFrame

logger = logging.getLogger(__name__)


class PlotFrame(TabbedFrame):
    filter_settings = {}
    data = None

    def __init__(self, notebook, settings, well_plate, proto_info, listbox):
        super().__init__(notebook, settings, "Plot")
        self.well_plate = well_plate
        self.well_mapping = self.well_plate.get_well_mapping()
        self.samples = sorted(self.well_mapping.keys())
        self.luminescence_settings = proto_info.settings
        self.presets = [f"{preset}" for preset in self.luminescence_settings.optic_settings.presets.values()]
        colorcycle = cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

        listbox.delete(0, tk.END)

        self.labels = ["Samples"]
        i = 0
        for preset_number, setting in self.luminescence_settings.optic_settings.presets.items():
            self.labels.append(f"Plot preset {preset_number}")
            self.labels.append("Color")
            listbox.insert(i, f"Preset {preset_number}: {setting}")
            i = i + 1

        if self.luminescence_settings.optic_settings.has_filter_setting() \
                and self.luminescence_settings.optic_settings.has_no_filter_setting():
            filter_key, filter_setting = self.luminescence_settings.optic_settings.get_filter_setting()
            no_filter_key, no_filter_setting = self.luminescence_settings.optic_settings.get_no_filter_setting()
            self.labels.append(f"Plot preset {no_filter_key} - preset {filter_key}")
            self.labels.append("Color")
            self.presets.append(f"{no_filter_setting}|{filter_setting}")

        self.plot_vars = pd.DataFrame(index=self.samples, columns=self.presets)
        self.colors = pd.DataFrame(index=self.samples, columns=self.presets)
        self.color_buttons = pd.DataFrame(index=self.samples, columns=self.presets)

        self.time_unit = tk.StringVar(value="Seconds")

        for sample in self.samples:
            self.colors.loc[sample, :] = [next(colorcycle) for _ in range(self.colors.shape[1])]
            for preset in self.presets:
                self.plot_vars.loc[sample, preset] = tk.Variable()

    def draw(self):

        plot_config_frame = ttk.Frame(self.frame, width=400)
        plot_config_frame.pack(side=tk.TOP, fill="y", expand=1)

        # draw the labels
        for i, text in enumerate(self.labels):
            label = ttk.Label(plot_config_frame, text=text)
            label.grid(row=0, column=i, padx='5', pady='5', sticky='ew')

        sep = ttk.Separator(plot_config_frame, orient=tk.HORIZONTAL)
        sep.grid(row=1, columnspan=len(self.labels), sticky="ew")

        for i, sample in enumerate(self.samples):
            label = ttk.Label(plot_config_frame, text=sample.get_description())
            label.grid(row=i+2, column=0, padx='5', pady='5', sticky='ew')

            for j, preset in enumerate(self.presets):
                plot_var = self.plot_vars.loc[sample, preset]
                plot_checkbox = tk.Checkbutton(plot_config_frame, variable=plot_var)
                plot_checkbox.select()
                plot_checkbox.grid(row=i+2, column=(j*2)+1, padx='5', pady='5', )

                color = self.colors.loc[sample, preset]
                color_button = tk.Button(plot_config_frame, bg=color, text=None,
                                         command=partial(self.handle_color_button, sample, preset))
                color_button.grid(row=i+2, column=(j*2)+2, padx='5', pady='5', )
                self.color_buttons.loc[sample, preset] = color_button

        plot_button = ttk.Button(self.frame, text="Plot", command=self.handle_plot_button)
        plot_button.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)
        for unit in ["Seconds", "Minutes"]:
            unit_button = ttk.Radiobutton(self.frame, text=unit, variable=self.time_unit, value=unit)
            unit_button.pack(side=tk.BOTTOM, anchor=tk.S)

    def handle_color_button(self, sample, preset):
        old_color = self.colors.loc[sample, preset]
        _, hexcolor = askcolor(old_color)
        self.colors.loc[sample, preset] = hexcolor
        self.color_buttons.loc[sample, preset].configure(bg=hexcolor)

    def handle_plot_button(self):

        plain_plots = []
        diff_plots = []

        for i, sample in enumerate(self.samples):
            for j, preset in enumerate(self.presets):
                color = self.colors.loc[sample, preset]
                plot_var = self.plot_vars.loc[sample, preset]
                if plot_var.get() == "1":
                    try:
                        p1, p2 = preset.split("|")
                        diff_plots.append([p1, p2, sample, color])
                    except (ValueError, AttributeError):
                        plain_plots.append([preset, sample, color])

        plot_data = self.well_plate.get_merged_data()
        luminescence_plot = LuminescencePlot(plot_data, self.time_unit.get(), self.luminescence_settings.optic_settings.presets, plain_plots,
                                             diff_plots)
        luminescence_plot.plot()
