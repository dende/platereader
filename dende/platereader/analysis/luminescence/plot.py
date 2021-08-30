import logging
import tkinter as tk
from typing import List

import pandas as pd
from matplotlib.lines import Line2D

import dende.platereader.analysis.luminescence.optic_settings as os
from dende.platereader.analysis.luminescence.settings import LuminescenceSettings
from dende.platereader.analysis.plot import Plot
import dende.platereader.analysis.sample as smpl

logger = logging.getLogger(__name__)


class LuminescencePlot(tk.Toplevel, Plot):

    def __init__(self, root: tk.Tk, df: pd.DataFrame, plain_plots: List[List], diff_plots: List[List],
                 settings: LuminescenceSettings, time_unit: str = "test"):
        super().__init__(root)
        self.df = df
        if time_unit not in ["Seconds", "Minutes"]:
            raise(Exception(f"Unknown time unit: {time_unit}"))
        self.time_unit = time_unit
        if self.time_unit == "Minutes":
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        self.settings = settings
        self.plain_plots = plain_plots
        self.diff_plots = diff_plots
        self.ox_treatments = ["H202", "DPS"]
        self.red_treatmens = ["DTT"]
        self.ratios = {"plain": {}, "af": {}}

        self.setup_figure()

    def plot(self):
        lines = []
        legends = []
        for lens_setting, sample, color in self.plain_plots:  # type: os.OpticPreset, smpl.Sample, str
            material, treatment = sample.material, sample.treatment
            self.calc_avg_std_sem(f"{lens_setting}!{sample}")
            self.plot_lines_with_errorbars(f"{lens_setting}!{sample}",
                                           error=f"{lens_setting}!{sample}-STD", color=color)
            self.plot_dots(f"{lens_setting}!{sample}", color=color)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                # get lens_settings as objects
                legends.append(f"{material.name} with {treatment} ({lens_setting.emission.get_description()})")
            else:
                legends.append(f"{material.name} ({lens_setting.emission.get_description()})")

        for p1, p2, sample, color in self.diff_plots:
            material, treatment = sample.material, sample.treatment

            self.calc_avg_std_sem(f"{p1}!{sample}")
            self.calc_avg_std_sem(f"{p2}!{sample}")
            self.df[f"{p1}!{p2}"] = self.df[f"{p1}!{sample}"] - self.df[f"{p2}!{sample}"]
            self.df[f"{p1}!{p2}-gauss-error"] = (
                                                       self.df[f"{p1}!{sample}-SEM"] ** 2 +
                                                       self.df[f"{p2}!{sample}-SEM"] ** 2
                                               ) ** .5

            self.plot_lines_with_errorbars(f"{p1}!{p2}", error=f"{p1}!{p2}-gauss-error", color=color)
            self.plot_dots(f"{p1}!{p2}", color=color)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{material.name} with {treatment}, corrected")
            else:
                legends.append(f"{material.name}, corrected")

        self.ax.set_ylabel("Luminescence Intensity")
        self.ax.legend(lines, legends)
