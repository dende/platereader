import logging
import tkinter as tk
from typing import List

import pandas as pd
from matplotlib.lines import Line2D

from dende.platereader.analysis.plot import Plot
from dende.platereader.analysis.sample import Sample, Material

logger = logging.getLogger(__name__)


class FluorescenceSpectrumPlot(tk.Toplevel, Plot):

    legends = List[str]
    lines = List[Line2D]

    def __init__(self, root: tk.Tk, df: pd.DataFrame, plain_data: List, autofluorescence_data=None, control=None,
                 title=None):
        super().__init__(root)
        self.geometry("1280x720")
        self.df = df
        self.plain_data = plain_data
        self.autofluorescence_data = autofluorescence_data
        self.control = control
        self.title = title
        self.ox_treatments = ["H202"]
        self.red_treatments = ["DTT", "DPS"]
        self.ratios = {"plain": {}, "af": {}}
        self.setup_figure()

    def plot(self):
        self.ax.clear()
        self.lines = []
        self.legends = []

        for sample, color in self.plain_data:
            material, treatment = sample.material, sample.treatment
            self.calc_avg_std_sem(sample)
            self.add_to_dynamic_ranges(sample)
            self.plot_lines_with_errorbars(sample, error=f"{sample}-STD", color=color)
            self.plot_dots(sample, color=color)
            self.lines.append(Line2D([0], [0], color=color))
            if treatment:
                self.legends.append(f"{material} with {treatment}")
            else:
                self.legends.append(f"{material}")

        if self.autofluorescence_data:
            self.plot_af()

        dynamic_ranges = self.calc_dynamic_ranges()

        if dynamic_ranges:
            for dr_type, dr_lines in dynamic_ranges.items():
                for material, dynamic_range in dr_lines.items():
                    self.lines.append(Line2D([0], [0], linestyle='none', mfc='black', mec='none', marker=r'$\delta$'))
                    if dr_type == "plain":
                        self.legends.append(f"{material}: {dynamic_range:.2f}")
                    elif dr_type == "af":
                        self.legends.append(f"{material}, corrected for autofluorescence: {dynamic_range:.2f}")

        self.ax.set_ylabel("Fluorescence Intensity")
        self.ax.legend(self.lines, self.legends, markerscale=2)

    def plot_af(self):

        baseline_calculated = False
        if self.autofluorescence_data:
            for sample, color in self.autofluorescence_data:
                material, treatment = sample.material, sample.treatment
                baseline = Sample(Material(self.control, True), treatment)
                if not baseline_calculated:
                    self.calc_avg_std_sem(baseline)
                    baseline_calculated = True
                self.calc_avg_std_sem(sample)
                self.df[f"{sample}" + "-adjusted"] = self.df[f"{sample}"] - self.df[f"{baseline}"]
                self.add_to_dynamic_ranges(sample, af=True)
                self.df[f"{sample}" + "-gauss-error"] = (
                                                                self.df[f"{sample}-SEM"] ** 2 +
                                                                self.df[f"{baseline}-SEM"] ** 2
                                                        ) ** .5
                self.plot_lines_with_errorbars(f"{sample}-adjusted", error=f"{sample}-gauss-error", color=color)
                self.plot_dots(f"{sample}-adjusted", color=color)
                self.lines.append(Line2D([0], [0], color=color))
                if treatment:
                    self.legends.append(f"{material} with {treatment}, corrected for autofluorescence")
                else:
                    self.legends.append(f"{material}, corrected for autofluorescence")

    def calc_dynamic_ranges(self):
        dynamic_ranges = {}
        for dr_type, lines in self.ratios.items():
            for line, treatment_types in lines.items():
                if "red" in treatment_types and "ox" in treatment_types:
                    if dr_type not in dynamic_ranges:
                        dynamic_ranges[dr_type] = {}
                    dynamic_ranges[dr_type][line] = treatment_types["ox"] / treatment_types["red"]

        return dynamic_ranges

    def add_to_dynamic_ranges(self, sample, af=False):
        material, treatment = sample.material, sample.treatment
        if not treatment:
            return
        dr_type = "af" if af else "plain"
        treatment_type = None
        if material.name not in self.ratios[dr_type]:
            self.ratios[dr_type][material.name] = {}
        if treatment.name in self.ox_treatments:
            treatment_type = "ox"
        elif treatment.name in self.red_treatments:
            treatment_type = "red"
        if treatment_type:
            self.ratios[dr_type][material.name][treatment_type] = self.df[f"{sample}"][405] / self.df[f"{sample}"][488]
