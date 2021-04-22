import logging

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from dende.platereader import Plot

logger = logging.getLogger(__name__)


class SpectrumPlot(Plot):

    def __init__(self, df, plain_data, autofluorescence_data=None, control=None, title=None):
        super().__init__(df)
        self.plain_data = plain_data
        self.autofluorescence_data = autofluorescence_data
        self.control = control
        self.title = title
        self.ox_treatments = ["H202"]
        self.red_treatmens = ["DTT", "DPS"]
        self.ratios = {"plain": {}, "af": {}}

    def calc_avg_std_sem(self, col_name):
        col_names = [col for col in self.df if col.startswith(col_name)]
        self.df[col_name] = self.df[col_names].mean(axis=1)
        self.df[col_name + "-STD"] = self.df[col_names].std(axis=1)  # calculate the errors column
        self.df[col_name + "-SEM"] = self.df[col_names].sem(axis=1)  # calculate the errors column

    def plot(self):
        lines = []
        legends = []
        ax = None
        for sample, color in self.plain_data:
            line, treatment = sample.split("$")
            self.calc_avg_std_sem(sample)
            self.add_to_dynamic_ranges(sample)
            ax = self.plot_lines_with_errorbars(sample, error=f"{sample}-STD", color=color)
            self.plot_dots(sample, color=color, ax=ax)
            lines.append(Line2D([0], [0], color=color))
            legends.append(f"{line} with {treatment}")

        if self.autofluorescence_data:
            for sample, color in self.autofluorescence_data:
                line, treatment = sample.split("$")
                baseline = f"{self.control}${treatment}"
                self.calc_avg_std_sem(baseline)
                self.calc_avg_std_sem(sample)
                self.df[sample + "-adjusted"] = self.df[sample] - self.df[f"{baseline}"]
                self.add_to_dynamic_ranges(sample + "-adjusted", af=True)
                self.df[sample + "-gauss-error"] = (
                                                    self.df[f"{sample}-SEM"] ** 2 +
                                                    self.df[f"{baseline}-SEM"] ** 2
                                                   ) ** .5
                ax = self.plot_lines_with_errorbars(f"{sample}-adjusted", error=f"{sample}-gauss-error", color=color)
                self.plot_dots(f"{sample}-adjusted", color=color, ax=ax)
                lines.append(Line2D([0], [0], color=color))
                legends.append(f"{line} {treatment}, corrected for autofluorescence")

        dynamic_ranges = self.calc_dynamic_ranges()

        if dynamic_ranges:
            for dr_type, dr_lines in dynamic_ranges.items():
                for line, dynamic_range in dr_lines.items():
                    lines.append(Line2D([0], [0], linestyle='none', mfc='black', mec='none', marker=r'$\delta$'))
                    if dr_type == "plain":
                        legends.append(f"{line}: {dynamic_range:.2f}")
                    elif dr_type == "af":
                        legends.append(f"{line}, corrected for autofluorescence: {dynamic_range:.2f}")

        # todo(dende): dynamic range of autofluorescence corrected sample is note being calculated
        plt.legend(lines, legends, markerscale=2)
        plt.show()

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
        line, treatment = sample.split("$")
        dr_type = "plain"
        treatment_type = None
        if af:
            dr_type = "af"
            treatment, _ = treatment.split('-')
        if line not in self.ratios[dr_type]:
            self.ratios[dr_type][line] = {}
        if treatment in self.ox_treatments:
            treatment_type = "ox"
        elif treatment in self.red_treatmens:
            treatment_type = "red"
        if treatment_type:
            self.ratios[dr_type][line][treatment_type] = self.df[sample][405] / self.df[sample][488]
