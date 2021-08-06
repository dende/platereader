import logging
import tkinter as tk
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from dende.platereader.analysis.luminescence.settings import LuminescenceSettings
from dende.platereader.analysis.plot import Plot

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
        self.figsize = (12, 8)
        self.plain_plots = plain_plots
        self.diff_plots = diff_plots
        self.ox_treatments = ["H202"]
        self.red_treatmens = ["DTT", "DPS"]
        self.ratios = {"plain": {}, "af": {}}

        self.setup_figure()

    def plot(self):
        lines = []
        legends = []
        for lens_setting, sample, color in self.plain_plots:
            material, treatment = sample.material, sample.treatment
            self.calc_avg_std_sem(f"{lens_setting}!{sample}")
            self.plot_lines_with_errorbars(f"{lens_setting}!{sample}",
                                           error=f"{lens_setting}!{sample}-STD", color=color)
            self.plot_dots(f"{lens_setting}!{sample}", color=color)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{material} with {treatment} and {lens_setting}")
            else:
                legends.append(f"{material} with {lens_setting}")

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
                legends.append(f"{material} with {treatment} and corrected with filter")
            else:
                legends.append(f"{material} corrected with filter")

        self.ax.set_ylabel("Luminescence Intensity")
        plt.legend(lines, legends)
        plt.show()
