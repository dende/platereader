import logging
import tkinter as tk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from dende.platereader.analysis.multichromatic_fluorescence.settings import MultichromaticFluorescenceSettings
from dende.platereader.analysis.plot import Plot
from dende.platereader.analysis.sample import Sample, Material

logger = logging.getLogger(__name__)


class MultichromaticFluorescencePlot(tk.Toplevel, Plot):

    def __init__(self, root: tk.Tk, df: pd.DataFrame, settings: MultichromaticFluorescenceSettings,
                 time_in_minutes=True):
        super().__init__(root)
        self.geometry("1280x720")
        self.df = df
        self.figsize = (12, 8)
        self.settings = settings
        self.time_in_minutes = time_in_minutes
        self.setup_figure()

    def plot(self, configs):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index
        legends = []
        lines = []

        for sample, lens_setting, color in configs:
            sample_cols = [col for col in self.df if col.startswith(f"{lens_setting}!{sample}§")]
            self.df[f"{sample}"] = self.df[sample_cols].mean(axis=1)  # caluclate the new mean column
            self.df[f"{sample}-STD"] = self.df[sample_cols].std(axis=1)  # calculate the errors column
            self.df[f"{sample}-SEM"] = self.df[sample_cols].sem(axis=1)  # calculate the errors column
            self.df[f"{sample}"].plot(ax=self.ax, yerr=self.df[f"{sample}-STD"], alpha=0.4, color=color, legend=False)
            lines.append(Line2D([0], [0], color=color))
            legends.append(f"{sample.get_description()} at {lens_setting}")
            self.df[f"{sample}"].plot(ax=self.ax, style=['o'], color=color, markersize=4, grid=True, legend=True)

        self.ax.set_ylabel("Fluorescence Intensity")
        self.ax.legend(lines, legends)

    def autofluorescence_plot(self, config, control, time_in_minutes=True):
        if time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        legends = []
        lines = []
        for sample, lens_setting, color in config:
            ls_sample = f"{lens_setting}!{sample}"  # lens_setting + baseline
            baseline = Sample(Material(control, True), sample.treatment)
            ls_baseline = f"{lens_setting}!{baseline}"  # lens_setting + baseline
            if baseline not in self.df.columns:
                baseline_cols = [col for col in self.df if col.startswith(f"{ls_baseline}§")]
                self.df[ls_baseline] = self.df[baseline_cols].mean(axis=1)  # caluclate the new mean column
                self.df[f"{ls_baseline}-STD"] = self.df[baseline_cols].std(axis=1)
                self.df[f"{ls_baseline}-SEM"] = self.df[baseline_cols].sem(axis=1)
            sample_cols = [col for col in self.df if col.startswith(f"{lens_setting}!{sample}§")]
            self.df[ls_sample] = self.df[sample_cols].mean(axis=1)  # caluclate the new mean column
            self.df[ls_sample + "-STD"] = self.df[sample_cols].std(axis=1)
            self.df[ls_sample + "-SEM"] = self.df[sample_cols].sem(axis=1)
            self.df[ls_sample + "-adjusted"] = self.df[ls_sample] - self.df[ls_baseline]
            self.df[ls_sample + "-gaussian-error"] = (
                                                             self.df[ls_sample + "-SEM"] ** 2 +
                                                             self.df[f"{lens_setting}!{baseline}-SEM"] ** 2
                                                     ) ** 0.5
            self.df[ls_sample + "-adjusted"].plot(figsize=(12, 8),
                                                  yerr=self.df[ls_sample + "-gaussian-error"],
                                                  alpha=0.4,
                                                  legend=False, grid=True, color=color)
            lines.append(Line2D([0], [0], color=color))
            legends.append(f"{sample.get_description()} at {lens_setting}nm, corrected for autofluorescence")
            self.df[ls_sample + "-adjusted"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                                  ax=self.ax, grid=True, legend=True)

        self.ax.set_ylabel("Fluorescence Intensity")
        plt.legend(lines, legends)
        plt.show()

    def autofluorescence_ratio_plot(self, configs, control, time_in_minutes=True):
        raise NotImplementedError()
        # for sample, color in configs:
        #     ls_sample = f"{lens_setting}!{sample}"  # lens_setting + baseline
        #     baseline = Sample(Material(control, True), sample.treatment)
        #     ls_baseline = f"{lens_setting}!{baseline}"  # lens_setting + baseline
        #
        #     if ls_baseline not in df.columns:
        #         baseline_cols = [col for col in df if col.startswith(f"{ls_baseline}§")]
        #         df[f"{ls_baseline}"] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
        #         df[f"{ls_baseline}-STD"] = df[baseline_cols].std(axis=1)
        #         df[f"{ls_baseline}-SEM"] = df[baseline_cols].sem(axis=1)
        #     sample_cols = [col for col in df if col.startswith(f"{ls_sample}§")]
        #     df[f"{ls_sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        #     df[f"{ls_sample}-STD"] = df[sample_cols].std(axis=1)
        #     df[f"{ls_sample}-SEM"] = df[sample_cols].sem(axis=1)
        #     df[f"{ls_sample}-adjusted"] = df[f"{ls_sample}"] - df[f"{ls_baseline}"]
        #     df[f"{ls_sample}-gaussian-error"] = (df[f"{ls_sample}-SEM"] ** 2 + df[f"{ls_baseline}-SEM"] ** 2) ** .5
        #
        # for sample, color in config:
        #     df[f"{sample}-ratio"] = df[f"{dividend}!{sample}-adjusted"] / df[f"{divisor}!{sample}-adjusted"]
        #     df[f"{sample}-ratio-gaussian-error"] = df[f"{sample}-ratio"] * (
        #             (df[f"{dividend}!{sample}-gaussian-error"] / df[f"{dividend}!{sample}"]) ** 2 + (
        #             df[f"{divisor}!{sample}-gaussian-error"] / df[f"{divisor}!{sample}"]) ** 2
        #                ) ** .5
        #     ax = df[f"{sample}-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
        #                                     yerr=df[f"{sample}-ratio-gaussian-error"], color=color)
        #     lines.append(Line2D([0], [0], color=color))
        #     legends.append(f"ratio for {sample.get_description()}, corrected for autofluorescence")
        #     df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
        #                                ax=ax, grid=True, legend=True)

    def ratio_plot(self, configs):
        if self.time_in_minutes:
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        legends = []
        lines = []
        for sample, ratio, color in configs:
            dividend, divisor = ratio.split("÷")
            dividend = self.settings.optic_settings.presets[int(dividend)]
            divisor = self.settings.optic_settings.presets[int(divisor)]

            self.ax.set_ylabel(f"Fluorescence Intensity ratio {{{dividend.excitation.wavelength}}}nm / "
                               f"{{{divisor.excitation.wavelength}}}nm")

            self.calc_avg_std_sem(f"{dividend}!{sample}")
            self.calc_avg_std_sem(f"{divisor}!{sample}")

            self.df[f"{ratio}-ratio"] = self.df[f"{dividend}!{sample}"] / self.df[f"{divisor}!{sample}"]
            self.df[f"{ratio}-ratio-error"] = self.df[f"{ratio}-ratio"] * (
                    (self.df[f"{dividend}!{sample}-STD"] / self.df[f"{dividend}!{sample}"]) ** 2 +
                    (self.df[f"{divisor}!{sample}-STD"] / self.df[f"{divisor}!{sample}"]) ** 2
            ) ** .5
            self.df[f"{ratio}-ratio"].plot(ax=self.ax, alpha=0.4, legend=False, grid=True,
                                           yerr=self.df[f"{ratio}-ratio-error"], color=color)
            lines.append(Line2D([0], [0], color=color))

            legends.append(f"ratio for {sample.get_description()}")
            self.df[f"{ratio}-ratio"].plot(ax=self.ax, style=['o'], color=color, markersize=4, grid=True, legend=True)

        self.ax.legend(labels=legends)
