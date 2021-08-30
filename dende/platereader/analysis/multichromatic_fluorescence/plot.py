import logging
import tkinter as tk
from functools import partial

import pandas as pd
from matplotlib.lines import Line2D

from dende.platereader.analysis.multichromatic_fluorescence.optic_settings import OpticPreset
from dende.platereader.analysis.multichromatic_fluorescence.settings import MultichromaticFluorescenceSettings
from dende.platereader.analysis.plot import Plot
from dende.platereader.analysis.sample import Sample, Material, Treatment

logger = logging.getLogger(__name__)


class MultichromaticFluorescencePlot(tk.Toplevel, Plot):

    def __init__(self, root: tk.Tk, df: pd.DataFrame, settings: MultichromaticFluorescenceSettings,
                 time_in_minutes=True):
        super().__init__(root)
        self.geometry("1280x720")
        self.df = df
        self.settings = settings
        self.time_in_minutes = time_in_minutes
        self.setup_figure()

        self.ox_treatments = [Treatment("H202"), Treatment("DPS")]
        self.red_treatments = [Treatment("DTT")]

        self.dynamic_ranges = []

    def plot(self, configs):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index
        legends = []
        lines = []

        for sample, lens_setting, color in configs:  # type: Sample, OpticPreset, str
            column = f"{lens_setting}!{sample}"
            self.calc_avg_std_sem(column)
            lines.append(Line2D([0], [0], color=color))
            legends.append(f"{sample.get_description()} at {lens_setting.excitation.get_description()}")
            self.plot_lines_with_errorbars(column, error=f"{column}-STD", color=color)
            self.plot_dots(column, color=color)

        self.ax.set_ylabel("Fluorescence Intensity")
        self.ax.legend(lines, legends)

    def autofluorescence_plot(self, config, control):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        legends = []
        lines = []
        for sample, lens_setting, color in config:
            ls_sample = f"{lens_setting}!{sample}"
            baseline = Sample(Material(control, True), sample.treatment)
            ls_baseline = f"{lens_setting}!{baseline}"
            self.calc_avg_std_sem(ls_sample)
            self.calc_avg_std_sem(ls_baseline)
            self.df[ls_sample + "-adjusted"] = self.df[ls_sample] - self.df[ls_baseline]
            self.df[ls_sample + "-gaussian-error"] = (
                                                             self.df[ls_sample + "-STD"] ** 2 +
                                                             self.df[f"{lens_setting}!{baseline}-STD"] ** 2
                                                     ) ** 0.5
            lines.append(Line2D([0], [0], color=color))
            legends.append(f"{sample.get_description()} at {lens_setting}nm, corrected")
            column = f"{ls_sample}-adjusted"
            self.plot_lines_with_errorbars(column, error=f"{ls_sample}-gaussian-error", color=color)
            self.plot_dots(column, color=color)

        self.ax.set_ylabel("Fluorescence Intensity")
        self.ax.legend(lines, legends)

    def autofluorescence_ratio_plot(self, configs, control):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        legends = []
        lines = []
        for sample, ratios, color in configs:
            dividend, divisor = ratios  # type: OpticPreset, OpticPreset
            ratio = f"{dividend.preset_number}÷{divisor.preset_number}"

            dividend_sample = f"{dividend}!{sample}"
            divisor_sample = f"{divisor}!{sample}"

            dividend_baseline = f"{dividend}!{Sample(Material(control, True), sample.treatment)}"
            divisor_baseline = f"{dividend}!{Sample(Material(control, True), sample.treatment)}"

            self.ax.set_ylabel(f"Fluorescence Intensity ratio {dividend.excitation.wavelength}nm / "
                               f"{divisor.excitation.wavelength}nm")

            self.calc_avg_std_sem(dividend_sample)
            self.calc_avg_std_sem(divisor_sample)
            self.calc_avg_std_sem(dividend_baseline)
            self.calc_avg_std_sem(divisor_baseline)

            self.df[dividend_sample + "-adjusted"] = self.df[dividend_sample] - self.df[dividend_baseline]
            self.df[dividend_sample + "-gaussian-error"] = (
                                                             self.df[f"{dividend_sample}-STD"] ** 2 +
                                                             self.df[f"{dividend_baseline}-STD"] ** 2
                                                     ) ** 0.5

            self.df[divisor_sample + "-adjusted"] = self.df[divisor_sample] - self.df[dividend_baseline]
            self.df[divisor_sample + "-gaussian-error"] = (
                                                             self.df[f"{divisor_sample}-STD"] ** 2 +
                                                             self.df[f"{dividend_baseline}-STD"] ** 2
                                                     ) ** 0.5

            self.df[f"{ratio}!{sample}"] = self.df[f"{dividend_sample}-adjusted"]/self.df[f"{divisor_sample}-adjusted"]
            self.df[f"{ratio}!{sample}-ratio-error"] = self.df[f"{ratio}!{sample}"] * (
                    (self.df[dividend_sample + "-gaussian-error"] / self.df[dividend_sample]) ** 2 +
                    (self.df[divisor_sample + "-gaussian-error"] / self.df[divisor_sample]) ** 2
            ) ** .5

            lines.append(Line2D([0], [0], color=color))
            legends.append(f"ratio for {sample.get_description()}")

            self.plot_lines_with_errorbars(f"{ratio}!{sample}", error=f"{ratio}!{sample}-ratio-error", color=color)
            self.plot_dots(f"{ratio}!{sample}", color=color)

        self.ax.legend(lines, legends)

        self.canvas.mpl_connect('button_press_event', partial(self.onclick, configs, lines, legends))

    def ratio_plot(self, configs):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        legends = []
        lines = []
        for sample, ratios, color in configs:
            dividend, divisor = ratios  # type: OpticPreset, OpticPreset
            ratio = f"{dividend.preset_number}÷{divisor.preset_number}"
            dividend = self.settings.optic_settings.presets[int(dividend.preset_number)]
            divisor = self.settings.optic_settings.presets[int(divisor.preset_number)]

            self.ax.set_ylabel(f"Fluorescence Intensity ratio {dividend.excitation.wavelength}nm / "
                               f"{divisor.excitation.wavelength}nm")

            self.calc_avg_std_sem(f"{dividend}!{sample}")
            self.calc_avg_std_sem(f"{divisor}!{sample}")

            self.df[f"{ratio}!{sample}"] = self.df[f"{dividend}!{sample}"] / self.df[f"{divisor}!{sample}"]
            self.df[f"{ratio}!{sample}-ratio-error"] = self.df[f"{ratio}!{sample}"] * (
                    (self.df[f"{dividend}!{sample}-STD"] / self.df[f"{dividend}!{sample}"]) ** 2 +
                    (self.df[f"{divisor}!{sample}-STD"] / self.df[f"{divisor}!{sample}"]) ** 2
            ) ** .5

            lines.append(Line2D([0], [0], color=color))
            legends.append(f"ratio for {sample.get_description()}")

            self.plot_lines_with_errorbars(f"{ratio}!{sample}", error=f"{ratio}!{sample}-ratio-error", color=color)
            self.plot_dots(f"{ratio}!{sample}", color=color)

        self.ax.legend(lines, legends)

        self.canvas.mpl_connect('button_press_event', partial(self.onclick, configs, lines, legends))

    def onclick(self, configs, lines, legends, event):
        # todo calculate dynamic range when there is more than two lines
        xdata = event.xdata
        if len(configs) != 2:
            logger.info("can only calculate dynamic range for 2 samples")
            return
        if configs[0][0].material != configs[1][0].material:
            logger.info("can only calculate dynamic range for identical material")
            return
        if configs[0][1] != configs[1][1]:
            logger.info("can only calculate dynamic range for same ratio")
            return
        ratios = configs[0][1]
        dividend, divisor = ratios  # type: OpticPreset, OpticPreset
        ratio = f"{dividend.preset_number}÷{divisor.preset_number}"
        if (configs[0][0].treatment in self.red_treatments and configs[1][0].treatment not in self.ox_treatments) or \
           (configs[0][0].treatment in self.ox_treatments and configs[1][0].treatment not in self.red_treatments):
            logger.info("can only calculate dynamic range when theres oxidizing and reducing treatment")
            return
        if configs[0][0].treatment in self.red_treatments:
            reduced_sample = configs[0][0]  # type: Sample
            oxidized_sample = configs[1][0]  # type: Sample
        else:
            oxidized_sample = configs[0][0]  # type: Sample
            reduced_sample = configs[1][0]  # type: Sample

        index = self.df.index.get_loc(xdata, "nearest")
        oxidized_column = self.df.columns.get_loc(f"{ratio}!{oxidized_sample}")
        reduced_column = self.df.columns.get_loc(f"{ratio}!{reduced_sample}")
        oxidized_value = self.df.iloc[index, oxidized_column]
        reduced_value = self.df.iloc[index, reduced_column]

        dynamic_range = oxidized_value / reduced_value
        self.dynamic_ranges.append(dynamic_range)

        self.ax.vlines(x=xdata, ymin=reduced_value, ymax=oxidized_value, colors='#555', lw=2, label='delta')
        marker = r'$\delta_{' + f"t{len(self.dynamic_ranges)}" r'}$'
        # get this shit bigger
        lines.append(Line2D([0], [0], linestyle='none', mfc='black', mec='none', marker=marker, markersize=14))
        legends.append(f"{dynamic_range:.3f}")

        self.ax.legend(lines, legends)

        self.canvas.draw_idle()
