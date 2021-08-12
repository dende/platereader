import logging
import tkinter as tk
from functools import partial
from itertools import cycle
from tkinter import ttk

import pandas as pd
from tkcolorpicker import askcolor

import dende.platereader.analysis.luminescence.plot as lup
import dende.platereader.layout
import dende.platereader.layout.tabbed_frame as tf
import dende.platereader.analysis.luminescence.settings as lus
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
        self.well_mapping = self.well_plate.get_well_mapping()
        self.samples = sorted(self.well_mapping.keys())
        self.luminescence_settings = self.well_plate.proto_info.settings  # type: lus.LuminescenceSettings
        self.presets = [f"{preset.preset_number}" for preset in
                        self.luminescence_settings.optic_settings.presets.values()]
        self.colorcycle = cycle(dende.platereader.layout.PALETTE)

        self.listbox.delete(0, tk.END)

        self.labels = ["Samples"]
        for i, (preset_number, setting) in enumerate(self.luminescence_settings.optic_settings.presets.items()):
            self.labels.append(f"Plot preset {preset_number}")
            self.labels.append("Color")
            self.listbox.insert(i, f"Preset {preset_number}: {setting}")

        if self.luminescence_settings.optic_settings.has_filter_setting() \
                and self.luminescence_settings.optic_settings.has_no_filter_setting():
            filter_key, filter_setting = self.luminescence_settings.optic_settings.get_filter_setting()
            no_filter_key, no_filter_setting = self.luminescence_settings.optic_settings.get_no_filter_setting()
            self.labels.append(f"Plot preset {no_filter_key} - preset {filter_key}")
            self.labels.append("Color")
            self.presets.append(f"{no_filter_key}-{filter_key}")

        self.plot_vars = pd.DataFrame(index=self.samples, columns=self.presets)
        self.colors = pd.DataFrame(index=self.samples, columns=self.presets)
        self.color_buttons = pd.DataFrame(index=self.samples, columns=self.presets)

        self.time_unit = tk.StringVar(value="Seconds")

        for sample in self.samples:
            self.colors.loc[sample, :] = [next(self.colorcycle) for _ in range(self.colors.shape[1])]
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
        _, hexcolor = askcolor(old_color, self.root, palette=dende.platereader.layout.PALETTE)
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
                        p1, p2 = preset.split("-")
                        p1 = self.luminescence_settings.optic_settings.presets[int(p1)]
                        p2 = self.luminescence_settings.optic_settings.presets[int(p2)]
                        diff_plots.append([p1, p2, sample, color])
                    except (ValueError, AttributeError):
                        preset = self.luminescence_settings.optic_settings.presets[int(preset)]
                        plain_plots.append([preset, sample, color])

        plot_data = self.well_plate.get_merged_data()
        luminescence_plot = lup.LuminescencePlot(self.root, plot_data, plain_plots, diff_plots,
                                                 self.luminescence_settings, self.time_unit.get())
        luminescence_plot.plot()
