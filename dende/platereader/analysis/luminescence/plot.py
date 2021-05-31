import logging

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


logger = logging.getLogger(__name__)


class LuminescencePlot:

    def __init__(self, df, presets, plain_data, diff_data=None, title=None):
        self.df = df
        self.presets = presets
        self.figsize = (12, 8)
        self.plain_data = plain_data
        self.diff_data = diff_data
        self.title = title
        self.ox_treatments = ["H202"]
        self.red_treatmens = ["DTT", "DPS"]
        self.ratios = {"plain": {}, "af": {}}

    def plot_lines_with_errorbars(self, sample, error, color, ax=None):
        if error is not None:
            yerr = self.df[error]
        else:
            yerr = None
        return self.df[sample].plot(figsize=self.figsize, yerr=yerr, alpha=0.4, legend=False,
                                    grid=True, color=color, ax=ax)

    def plot_dots(self, sample, color, ax):
        return self.df[sample].plot(figsize=self.figsize, style=['o'], color=color, markersize=4,
                                    ax=ax, grid=True, legend=True)

    def calc_avg_std_sem(self, col_name):
        if col_name in self.df:
            logger.warning(f"Already calculated avg and errors for {col_name}")
            return
        col_names = [col for col in self.df if col.startswith(col_name)]
        self.df[col_name] = self.df[col_names].mean(axis=1)
        self.df[col_name + "-STD"] = self.df[col_names].std(axis=1)  # calculate the errors column
        self.df[col_name + "-SEM"] = self.df[col_names].sem(axis=1)  # calculate the errors column

    def plot(self):
        lines = []
        legends = []
        ax = None
        for preset_number, sample, color in self.plain_data:
            preset = self.presets[preset_number]
            try:
                line, treatment = sample.split("$")
            except ValueError:
                line, treatment = sample, None
            self.calc_avg_std_sem(f"{preset_number}${sample}")
            ax = self.plot_lines_with_errorbars(f"{preset_number}${sample}",
                                                error=f"{preset_number}${sample}-STD", color=color)
            self.plot_dots(f"{preset_number}${sample}", color=color, ax=ax)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{line} with {treatment} and {preset}")
            else:
                legends.append(f"{line} with {preset}")

        for p1, p2, sample, color in self.diff_data:
            try:
                line, treatment = sample.split("$")
            except ValueError:
                line, treatment = sample, None

            self.calc_avg_std_sem(f"{p1}${sample}")
            self.calc_avg_std_sem(f"{p2}${sample}")
            self.df[f"{p1}-{p2}"] = self.df[f"{p1}${sample}"] - self.df[f"{p2}${sample}"]
            ax = self.plot_lines_with_errorbars(f"{p1}-{p2}", error=None, color=color, ax=ax)
            self.plot_dots(f"{p1}-{p2}", color=color, ax=ax)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{line} with {treatment} and corrected with filter")
            else:
                legends.append(f"{line} corrected with filter")

        plt.legend(lines, legends)
        plt.show()
